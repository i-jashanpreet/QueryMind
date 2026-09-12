"""
Ollama service — communicates with the local Ollama HTTP API.
"""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")

# Generous timeout: local LLM inference can be slow on first load
_TIMEOUT = httpx.Timeout(timeout=120.0, connect=10.0)


def generate(prompt: str, system: str = "") -> str:
    """
    Send a prompt to Ollama and return the model's response text.

    Args:
        prompt:  The user-facing message.
        system:  An optional system-level instruction.

    Returns:
        The model's generated text (stripped of leading/trailing whitespace).

    Raises:
        httpx.ConnectError   – Ollama server unreachable.
        httpx.HTTPStatusError – Non-2xx response from Ollama.
    """
    payload: dict = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
    }

    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=_TIMEOUT,
    )
    response.raise_for_status()

    data: dict = response.json()
    return data.get("response", "").strip()


def is_available() -> bool:
    """Return True if the Ollama server responds to a simple health check."""
    try:
        r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
        return r.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False
