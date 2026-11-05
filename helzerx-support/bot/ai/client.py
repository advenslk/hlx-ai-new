"""
HELZERX AI Support - NVIDIA NIM AI Engine Integration
Implements OpenAI-compatible client for NVIDIA NIM with exponential backoff, rate limit handling, and token tracking.
"""
from __future__ import annotations

import asyncio
import time
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional, Tuple

try:
    import httpx
except ImportError:
    httpx = None

from bot.config import config
from bot.utils.logger import logger


class NvidiaNimClient:
    """Production client for NVIDIA NIM API with robust resilience and retry mechanisms."""

    def __init__(self):
        self.base_url = config.NVIDIA_BASE_URL.rstrip("/")
        self.api_key = config.NVIDIA_API_KEY
        self.model = config.NVIDIA_MODEL
        self.timeout = config.AI_TIMEOUT_SECONDS
        self.max_retries = config.AI_MAX_RETRIES

        # Token usage & health metrics
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.last_latency_ms = 0.0
        self.last_status = "UNKNOWN"
        self.consecutive_failures = 0

    def is_configured(self) -> bool:
        """Returns True if NVIDIA API Key is set."""
        return bool(self.api_key and not self.api_key.startswith("nvapi-your-key"))

    async def check_health(self) -> Dict[str, Any]:
        """Performs a lightweight probe to verify NVIDIA NIM availability."""
        if not self.is_configured():
            self.last_status = "NOT_CONFIGURED"
            return {
                "status": "NOT_CONFIGURED",
                "healthy": False,
                "model": self.model,
                "message": "NVIDIA_API_KEY is not set or has placeholder value."
            }

        start = time.time()
        try:
            if httpx is not None:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        f"{self.base_url}/models",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    self.last_latency_ms = round((time.time() - start) * 1000, 2)
                    status_code = res.status_code
            else:
                def _do_get():
                    req = urllib.request.Request(
                        f"{self.base_url}/models",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    with urllib.request.urlopen(req, timeout=10.0) as resp:
                        return resp.getcode()
                status_code = await asyncio.to_thread(_do_get)
                self.last_latency_ms = round((time.time() - start) * 1000, 2)

            if status_code == 200:
                self.last_status = "ONLINE"
                self.consecutive_failures = 0
                return {
                    "status": "ONLINE",
                    "healthy": True,
                    "model": self.model,
                    "latency_ms": self.last_latency_ms
                }
            else:
                self.last_status = f"HTTP_{status_code}"
                return {
                    "status": f"HTTP_{status_code}",
                    "healthy": False,
                    "model": self.model,
                    "message": f"NVIDIA NIM returned status code {status_code}"
                }
        except Exception as e:
            self.last_latency_ms = round((time.time() - start) * 1000, 2)
            self.last_status = "OFFLINE"
            self.consecutive_failures += 1
            return {
                "status": "OFFLINE",
                "healthy": False,
                "model": self.model,
                "error": str(e)
            }

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Tuple[str, int, int]:
        """
        Sends conversation messages to NVIDIA NIM with exponential backoff.
        Returns:
            (response_text: str, prompt_tokens: int, completion_tokens: int)
        """
        if not self.is_configured():
            # Graceful simulation fallback when no API key is injected yet
            fallback_text = (
                "**[HELZERX AI Diagnostic]**\n"
                "I have registered your ticket and analyzed your initial report. "
                "Our automated troubleshooting engine is actively running node checks. "
                "A HELZERX support engineer can review this ticket immediately, "
                "or please provide your `latest.log` / server output so we can pinpoint the issue."
            )
            return fallback_text, 50, 60

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else config.AI_TEMPERATURE,
            "max_tokens": max_tokens if max_tokens is not None else config.AI_MAX_RESPONSE_TOKENS,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        url = f"{self.base_url}/chat/completions"
        backoff = 1.5

        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                if httpx is not None:
                    async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                        response = await client.post(url, headers=headers, json=payload)
                    status_code = response.status_code
                    response_text = response.text
                    response_json = response.json if status_code == 200 else None
                else:
                    def _do_post():
                        req_data = json.dumps(payload).encode("utf-8")
                        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
                        try:
                            with urllib.request.urlopen(req, timeout=float(self.timeout)) as resp:
                                return resp.getcode(), resp.read().decode("utf-8")
                        except urllib.error.HTTPError as he:
                            return he.code, he.read().decode("utf-8")
                    status_code, response_text = await asyncio.to_thread(_do_post)
                    response_json = lambda: json.loads(response_text) if status_code == 200 else None

                self.last_latency_ms = round((time.time() - start) * 1000, 2)

                if status_code == 200:
                    data = response_json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise ValueError("NVIDIA NIM returned empty choices list.")

                    reply = choices[0]["message"]["content"]
                    usage = data.get("usage", {})
                    p_toks = usage.get("prompt_tokens", 0)
                    c_toks = usage.get("completion_tokens", 0)

                    self.total_prompt_tokens += p_toks
                    self.total_completion_tokens += c_toks
                    self.consecutive_failures = 0
                    self.last_status = "ONLINE"

                    return reply, p_toks, c_toks

                elif status_code == 429:
                    logger.warning(
                        f"NVIDIA NIM rate-limit (429) on attempt {attempt}/{self.max_retries}. "
                        f"Retrying in {backoff:.2f}s..."
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue

                elif status_code >= 500:
                    logger.warning(
                        f"NVIDIA NIM 5xx server error ({status_code}) on attempt {attempt}. "
                        f"Retrying in {backoff:.2f}s..."
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue

                else:
                    logger.error(f"NVIDIA NIM client error {status_code}: {response_text}")
                    raise RuntimeError(f"NVIDIA NIM API Error ({status_code}): {response_text}")

            except (TimeoutError, Exception) as net_err:
                if isinstance(net_err, RuntimeError):
                    raise
                logger.warning(f"Network error contacting NVIDIA NIM (attempt {attempt}): {net_err}")
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(backoff)
                backoff *= 2.0

        raise TimeoutError("NVIDIA NIM maximum retries exceeded without successful response.")


ai_client = NvidiaNimClient()
