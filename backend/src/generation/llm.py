"""LLM client abstractions used by the application.

The current production implementation wraps the DeepSeek API through its
OpenAI-compatible chat completions endpoint. The interface is intentionally
small to keep router and answer generation loosely coupled.
"""

import os
from typing import Optional

from dotenv import load_dotenv
import requests


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

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a plain-text answer from a system prompt and user prompt."""
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.0,
            },
            timeout=60,
        )
        response.raise_for_status()

        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            raise ValueError("DeepSeek response did not include any choices.")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise ValueError("DeepSeek response did not include message content.")

        return content.strip()
