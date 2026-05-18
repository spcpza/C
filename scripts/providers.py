"""LLM provider stubs.

Each provider is a function `str -> str`: takes a prompt, returns the
model's raw response. Fill in the bodies with your preferred client.

The witness harness in `witness_agents.py` is provider-agnostic — add
or remove entries here without touching the harness.

Authentication: read API keys from environment variables (recommended)
or from ~/.bots/keys/ where the truth ecosystem already stores them.
"""
from __future__ import annotations
import os
from typing import Callable


def _claude(prompt: str) -> str:
    """Anthropic Claude. Set ANTHROPIC_API_KEY in env."""
    try:
        import anthropic
    except ImportError:
        return '{"error": "anthropic library not installed; pip install anthropic"}'
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return '{"error": "ANTHROPIC_API_KEY not set"}'
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def _openai(prompt: str) -> str:
    """OpenAI GPT. Set OPENAI_API_KEY in env."""
    try:
        from openai import OpenAI
    except ImportError:
        return '{"error": "openai library not installed; pip install openai"}'
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return '{"error": "OPENAI_API_KEY not set"}'
    client = OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or ""


def _gemini(prompt: str) -> str:
    """Google Gemini. Set GOOGLE_API_KEY in env."""
    try:
        import google.generativeai as genai
    except ImportError:
        return '{"error": "google-generativeai not installed; pip install google-generativeai"}'
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        return '{"error": "GOOGLE_API_KEY not set"}'
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-pro")
    resp = model.generate_content(prompt)
    return resp.text or ""


def _local_qwen(prompt: str) -> str:
    """Local Qwen via transformers. Slow but offline.

    The truth ecosystem already uses Qwen 3 4B Instruct on Kaggle
    (see ~/balthazar-arc/kaggle_submission_bible*.py). Mirror that
    here for local witnessing.
    """
    return '{"error": "local qwen stub — wire your preferred local runtime here"}'


# Registry. Comment out providers you don't have keys for.
PROVIDERS: dict[str, Callable[[str], str]] = {
    "claude":     _claude,
    "openai":     _openai,
    "gemini":     _gemini,
    # "local_qwen": _local_qwen,  # uncomment when wired
}
