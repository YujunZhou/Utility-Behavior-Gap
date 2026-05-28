"""Minimal OpenRouter chat-completion client."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from utility_behavior_gap.constants import ACTORS
from utility_behavior_gap.io_utils import load_env_file
from utility_behavior_gap.paths import ROOT


def actor_env_name(actor: str) -> str:
    token = actor.upper().replace("-", "_").replace(".", "_")
    return f"ACTOR_MODEL_{token}"


def load_runtime_env() -> None:
    load_env_file(ROOT / ".env")


def require_openrouter_key() -> str:
    load_runtime_env()
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key or key == "xxx":
        raise RuntimeError(
            "Set OPENROUTER_API_KEY in .env before running live API calls. "
            "Use .env.example as the template."
        )
    return key


def actor_model_id(actor: str) -> str:
    load_runtime_env()
    env_name = actor_env_name(actor)
    model = os.environ.get(env_name, "").strip()
    if not model or model == "xxx":
        raise RuntimeError(f"Set {env_name} in .env to an OpenRouter model id.")
    return model


def judge_model_ids() -> list[str]:
    load_runtime_env()
    raw = os.environ.get("JUDGE_MODELS", "").strip()
    models = [value.strip() for value in raw.split(",") if value.strip() and value.strip() != "xxx"]
    if not models:
        raise RuntimeError("Set JUDGE_MODELS in .env to one or more OpenRouter model ids.")
    return models


def configured_actor_models() -> dict[str, str]:
    return {actor: actor_model_id(actor) for actor in ACTORS}


class OpenRouterClient:
    def __init__(self, *, timeout_s: float = 120.0, max_retries: int = 3) -> None:
        load_runtime_env()
        self.api_key = require_openrouter_key()
        self.base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.site_url = os.environ.get("OPENROUTER_SITE_URL", "").strip()
        self.app_name = os.environ.get("OPENROUTER_APP_NAME", "Utility-Behavior Gap Reproduction").strip()

    def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.site_url and self.site_url != "xxx":
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        for attempt in range(1, self.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if attempt == self.max_retries or exc.code < 500:
                    raise RuntimeError(f"OpenRouter request failed ({exc.code}): {detail}") from exc
            except urllib.error.URLError as exc:
                if attempt == self.max_retries:
                    raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
            time.sleep(min(2**attempt, 10))
        raise RuntimeError("OpenRouter request failed after retries")


def response_text(response: dict[str, Any]) -> str:
    return str(response["choices"][0]["message"].get("content", ""))
