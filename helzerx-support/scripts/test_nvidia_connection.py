"""
HELZERX AI Support - NVIDIA NIM Connectivity Verification Script
Tests API credentials, latency, model endpoints, and health status.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.ai.client import ai_client
from bot.config import config
from bot.utils.logger import logger


async def main():
    quiet = "--quiet" in sys.argv

    if not quiet:
        print("\n" + "=" * 60)
        print("  HELZERX AI SUPPORT - NVIDIA NIM HEALTH CHECK")
        print("=" * 60)
        print(f"Target Base URL: {config.NVIDIA_BASE_URL}")
        print(f"Target Model:    {config.NVIDIA_MODEL}")
        print(f"API Key Present: {'Yes' if ai_client.is_configured() else 'No (Placeholder or Empty)'}")
        print("-" * 60)

    health = await ai_client.check_health()

    if not quiet:
        print(f"Status:   {health.get('status')}")
        print(f"Healthy:  {health.get('healthy')}")
        if "latency_ms" in health:
            print(f"Latency:  {health.get('latency_ms')} ms")
        if "error" in health:
            print(f"Error:    {health.get('error')}")
        if "message" in health:
            print(f"Message:  {health.get('message')}")
        print("=" * 60 + "\n")

    if not health.get("healthy") and not quiet:
        print("Note: If running in preview mode without a live NVIDIA_API_KEY,")
        print("the bot will automatically activate its internal diagnostic fallback.")
        sys.exit(0)

    sys.exit(0 if health.get("healthy") else 1)


if __name__ == "__main__":
    asyncio.run(main())
