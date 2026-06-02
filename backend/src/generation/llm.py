"""LLM client abstractions used by the application.

The current production implementation wraps the DeepSeek API through its
OpenAI-compatible chat completions endpoint. The interface is intentionally
small to keep router and answer generation loosely coupled.
"""

import os
from typing import Optional

from dotenv import load_dotenv
import openai


class DeepSeekLLM:
    """Wrapper around the DeepSeek API using its OpenAI-compatible endpoint."""

    def __init__(self, model: Optional[str] = None):
        load_dotenv()

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is missing. Add it to your .env file "
                "or disable LLM generation in the UI."
            )

        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.api_key = api_key

        # Configure OpenAI SDK to use DeepSeek's OpenAI-compatible endpoint
        openai.api_key = self.api_key
        if self.base_url:
            openai.api_base = self.base_url.rstrip("/") + "/v1"
        self.client = openai

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a plain-text answer from a system prompt and user prompt."""
        resp = self.client.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )

        # Normalize extraction across SDK response shapes
        choices = None
        if isinstance(resp, dict):
            choices = resp.get("choices")
        else:
            try:
                choices = resp.choices
            except Exception:
                choices = None

        if not choices:
            raise ValueError("DeepSeek/OpenAI response did not include any choices.")

        first = choices[0]
        content = None
        if isinstance(first, dict):
            content = (first.get("message") or {}).get("content") or first.get("text")
        else:
            try:
                content = first.message.content
            except Exception:
                try:
                    content = first.text
                except Exception:
                    content = None

        if not content:
            raise ValueError("DeepSeek/OpenAI response did not include message content.")

        return content.strip()
