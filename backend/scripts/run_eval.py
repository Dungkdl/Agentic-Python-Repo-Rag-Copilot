"""Evaluation runner for repository QA behavior."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys

from src.evaluation.eval_runner import (
    evaluate_response,
    load_eval_cases,
    summarize_eval_results,
)
from src.evaluation.metrics import (
    answer_non_empty,
    compute_latency_seconds,
    compute_source_precision,
    is_llm_failure,
    is_router_fallback,
    now_seconds,
    safe_average,
    validate_citations,
)
from src.indexing.codebase_indexer import build_codebase_agent
from src.core.settings import RETRIEVAL_MODE_ACCURATE, RETRIEVAL_MODE_FAST
from src.core.config import EVAL_CASES_PATH, COMPANY_REPOS_DIR


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TeeWriter:
    """Write console output to multiple streams."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def setup_eval_log() -> tuple[Path, object, object, object]:
    """Mirror stdout/stderr to a timestamped evaluation log file."""
    backend_root = Path(__file__).resolve().parents[1]
    log_dir = backend_root / "logs" / "evaluation"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"run_eval_{timestamp}.log"
    log_file = log_path.open("w", encoding="utf-8", errors="replace")

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TeeWriter(original_stdout, log_file)
    sys.stderr = TeeWriter(original_stderr, log_file)

    return log_path, log_file, original_stdout, original_stderr


def resolve_repo_path(repo_path: str) -> Path:
    """Resolve repository paths used by eval cases."""
    path = Path(repo_path)

    if path.exists():
        return path

    # Fallback: try resolving as a company repo by folder name
    repo_name = Path(repo_path).name
    company_fallback = COMPANY_REPOS_DIR / repo_name

    if company_fallback.exists():
        return company_fallback

    return path


def build_indexed_repos(cases, retrieval_mode: str):
    """Index each repository referenced by eval cases once for one retrieval mode."""
    cases_by_repo = defaultdict(list)

    for case in cases:
        cases_by_repo[case.repo_id].append(case)

    indexed_repos = {}

    for repo_id, repo_cases in cases_by_repo.items():
        repo_path = resolve_repo_path(repo_cases[0].repo_path)

        print("\n" + "=" * 100)
        print(f"Indexing repo: {repo_id}")
        print(f"Repo path: {repo_path}")

        indexed = build_codebase_agent(
            repo_path=repo_path,
            collection_name=f"eval_{repo_id}",
            reset_collection=True,
            use_llm=False,
            retrieval_mode=retrieval_mode,
            use_llm_router=True,
            save_metadata=False,
        )

        docs_text_count = indexed.doc_count + getattr(indexed, "text_count", 0)

        print(f"Python files:        {indexed.file_count}")
        print(f"Docs/Text files:     {docs_text_count}")
        print(f"JSON files:          {getattr(indexed, 'json_count', 0)}")
        print(f"Ignored files:       {indexed.ignored_file_count}")
        print(f"Total chunks:        {indexed.chunk_count}")

        indexed_repos[repo_id] = indexed

    return indexed_repos


def get_actual_response_sources(response):
    """Return raw response sources for extended metrics."""
    return getattr(response, "sources", []) or []


def get_expected_case_sources(case):
    """Return expected sources from an eval case."""
    return getattr(case, "expected_sources", []) or []


def print_result(result, extended_metrics):
    """Print one evaluation result in a human-readable format."""
    status = (
        "PASS"
        if (
            result.query_type_correct
            and result.expected_sources_all_found
            and result.file_hit_rate == 1.0
            and result.answer_non_empty
            and result.answer_keyword_recall == 1.0
            and not result.forbidden_keyword_hit
            and result.abstention_correct is not False
            and not extended_metrics["max_latency_exceeded"]
        )
        else "FAIL"
    )

    print("\n" + "-" * 100)
    print(f"{result.id} - {status}")
    print(f"Repo: {result.repo_id}")
    print(f"Question: {result.question}")

    print(f"\nExpected query type: {result.expected_query_type}")
    print(f"Actual query type:   {result.actual_query_type}")
    print(f"Query type correct:  {result.query_type_correct}")

    print("\nExpected sources:")
    for source in result.expected_sources:
        print(f"- {source}")

    print("\nActual sources:")
    if result.actual_sources:
        for source in result.actual_sources:
            print(f"- {source}")
    else:
        print("- No sources")

    print(f"\nSource hit count: {result.source_hit_count}/{len(result.expected_sources)}")
    print(f"Source recall:    {result.source_recall:.2f}")

    print("\nExtended metrics:")
    print(f"Source precision:  {extended_metrics['source_precision']:.2f}")
    print(f"File hit rate:     {result.file_hit_rate:.2f}")
    print(f"Keyword recall:    {result.answer_keyword_recall:.2f}")
    print(f"Forbidden hit:     {result.forbidden_keyword_hit}")
    print(f"Abstention correct:{result.abstention_correct}")
    print(f"Citation validity: {extended_metrics['citation_validity_rate']:.2f}")
    print(f"Latency seconds:   {extended_metrics['latency_seconds']:.2f}")
    print(f"Max latency hit:   {extended_metrics['max_latency_exceeded']}")
    print(f"Answer non-empty:  {extended_metrics['answer_non_empty']}")
    print(f"Router fallback:   {extended_metrics['router_fallback']}")
    print(f"LLM failure:       {extended_metrics['llm_failure']}")

    invalid_citations = extended_metrics.get("invalid_citations") or []

    if invalid_citations:
        print("\nInvalid citations:")
        for item in invalid_citations:
            print(f"- {item['reason']}: {item['source']}")


def print_summary(title, results, extended_results):
    """Print aggregate evaluation metrics."""
    summary = summarize_eval_results(results)

    latencies = [
        item["latency_seconds"]
        for item in extended_results
    ]

    source_precisions = [
        item["source_precision"]
        for item in extended_results
    ]

    citation_validities = [
        item["citation_validity_rate"]
        for item in extended_results
    ]

    answer_non_empty_values = [
        1.0 if item["answer_non_empty"] else 0.0
        for item in extended_results
    ]

    router_fallback_values = [
        1.0 if item["router_fallback"] else 0.0
        for item in extended_results
    ]

    llm_failure_values = [
        1.0 if item["llm_failure"] else 0.0
        for item in extended_results
    ]

    max_latency_exceeded_values = [
        1.0 if item["max_latency_exceeded"] else 0.0
        for item in extended_results
    ]

    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    print(f"Number of cases:                 {int(summary['num_cases'])}")
    print(f"Query type accuracy:             {summary['query_type_accuracy']:.2%}")
    print(f"Average source recall:           {summary['avg_source_recall']:.2%}")
    print(f"Expected sources all found rate: {summary['expected_sources_all_found_rate']:.2%}")
    print(f"Average source precision:        {summary['avg_source_precision']:.2%}")
    print(f"Average file hit rate:           {summary['avg_file_hit_rate']:.2%}")
    print(f"Answer non-empty rate:           {summary['answer_non_empty_rate']:.2%}")
    print(f"Average keyword recall:          {summary['avg_answer_keyword_recall']:.2%}")
    print(f"Forbidden keyword hit rate:      {summary['forbidden_keyword_hit_rate']:.2%}")
    print(f"Abstention accuracy:             {summary['abstention_accuracy']:.2%}")

    print("\nExtended Evaluation Summary")
    print("-" * 100)
    print(f"Average source precision:        {safe_average(source_precisions):.2%}")
    print(f"Average citation validity:       {safe_average(citation_validities):.2%}")
    print(f"Average latency seconds:         {safe_average(latencies):.2f}")
    print(f"Max latency exceeded rate:       {safe_average(max_latency_exceeded_values):.2%}")
    print(f"Answer non-empty rate:           {safe_average(answer_non_empty_values):.2%}")
    print(f"Router fallback rate:            {safe_average(router_fallback_values):.2%}")
    print(f"LLM failure rate:                {safe_average(llm_failure_values):.2%}")


def run_single_mode_eval(retrieval_mode: str) -> None:
    """Run the repository QA evaluation suite for one retrieval mode."""
    eval_path = EVAL_CASES_PATH

    cases = load_eval_cases(eval_path)
    print(f"Loaded {len(cases)} eval cases")
    print(f"Retrieval mode: {retrieval_mode}")

    indexed_repos = build_indexed_repos(cases, retrieval_mode=retrieval_mode)
    results = []
    extended_results = []

    for case in cases:
        indexed = indexed_repos[case.repo_id]

        start_time = now_seconds()
        response = indexed.agent.answer(case.question)
        end_time = now_seconds()

        actual_sources = get_actual_response_sources(response)
        expected_sources = get_expected_case_sources(case)

        citation_metrics = validate_citations(
            repo_root=indexed.repo_path,
            sources=actual_sources,
        )

        raw_results = getattr(response, "raw_results", {}) or {}
        latency_seconds = compute_latency_seconds(start_time, end_time)
        max_latency_exceeded = (
            case.max_latency_seconds is not None
            and latency_seconds > case.max_latency_seconds
        )

        result = evaluate_response(
            case=case,
            response=response,
            latency_seconds=latency_seconds,
            raw_results=raw_results,
            citation_validity_rate=citation_metrics["citation_validity_rate"],
        )

        extended_metrics = {
            "id": result.id,
            "repo_id": result.repo_id,
            "latency_seconds": latency_seconds,
            "max_latency_exceeded": max_latency_exceeded,
            "source_precision": compute_source_precision(
                actual_sources=actual_sources,
                expected_sources=expected_sources,
            ),
            "citation_validity_rate": citation_metrics["citation_validity_rate"],
            "invalid_citations": citation_metrics["invalid_citations"],
            "answer_non_empty": answer_non_empty(getattr(response, "answer", "")),
            "router_fallback": is_router_fallback(raw_results),
            "llm_failure": is_llm_failure(raw_results),
        }

        results.append(result)
        extended_results.append(extended_metrics)

        print_result(result, extended_metrics)

    print_summary(
        f"Overall Evaluation Summary - {retrieval_mode}",
        results,
        extended_results,
    )

    repo_ids = sorted({result.repo_id for result in results})

    for repo_id in repo_ids:
        repo_results = [
            result
            for result in results
            if result.repo_id == repo_id
        ]

        repo_extended_results = [
            item
            for item in extended_results
            if item["repo_id"] == repo_id
        ]

        print_summary(
            f"Evaluation Summary - {repo_id} - {retrieval_mode}",
            repo_results,
            repo_extended_results,
        )


def main() -> None:
    """Run the repository QA evaluation suite for fast and accurate modes."""
    log_path, log_file, original_stdout, original_stderr = setup_eval_log()

    try:
        print(f"Evaluation log: {log_path}")

        for retrieval_mode in (RETRIEVAL_MODE_FAST, RETRIEVAL_MODE_ACCURATE):
            print("\n" + "#" * 100)
            print(f"Starting benchmark for retrieval mode: {retrieval_mode}")
            print("#" * 100)
            run_single_mode_eval(retrieval_mode)

        print(f"\nEvaluation log saved to: {log_path}")
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()


if __name__ == "__main__":
    main()
