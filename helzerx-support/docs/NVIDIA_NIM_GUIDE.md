# HELZERX AI Support - NVIDIA NIM Configuration Guide

HELZERX utilizes **NVIDIA NIM** (NVIDIA Inference Microservice) to power its high-speed, enterprise-grade AI technical diagnostics.

---

## 1. What is NVIDIA NIM?

NVIDIA NIM provides self-hosted and cloud-hosted inference microservices optimized for state-of-the-art open-source LLMs (Meta Llama 3.1/3.3, Mistral, Mixtral) with TensorRT-LLM acceleration. It exposes an **OpenAI-compatible API** at:

```
https://integrate.api.nvidia.com/v1
```

---

## 2. Obtaining an NVIDIA NIM API Key

1. Visit the NVIDIA API Catalog: [https://build.nvidia.com/](https://build.nvidia.com/)
2. Sign in with your NVIDIA Developer account.
3. Select any supported LLM, such as **`meta/llama-3.1-70b-instruct`** or **`meta/llama-3.3-70b-instruct`**.
4. Click **Get API Key** in the top-right toolbar.
5. Generate and copy your API key (it begins with `nvapi-`).
6. Paste it into your `.env` file:
   ```env
   NVIDIA_API_KEY="nvapi-your-key-here"
   ```

---

## 3. Supported & Recommended Models

| Model Slug | Recommended Use Case | Context Window |
| :--- | :--- | :--- |
| `meta/llama-3.1-70b-instruct` | **Default / Production** - Best balance of deep technical reasoning & low latency | 128k tokens |
| `meta/llama-3.3-70b-instruct` | Advanced systems troubleshooting & complex network topology | 128k tokens |
| `meta/llama-3.1-8b-instruct` | High-throughput, ultra-low latency simple triage | 128k tokens |
| `mistralai/mixtral-8x22b-instruct` | Multilingual & long-form technical documentation analysis | 64k tokens |

Configure your chosen model in `.env`:
```env
NVIDIA_MODEL="meta/llama-3.1-70b-instruct"
```

---

## 4. Testing Connectivity

Run the automated diagnostic script to verify your key and measure round-trip latency:

```bash
python3 scripts/test_nvidia_connection.py
```

Expected output:
```
============================================================
  HELZERX AI SUPPORT - NVIDIA NIM HEALTH CHECK
============================================================
Target Base URL: https://integrate.api.nvidia.com/v1
Target Model:    meta/llama-3.1-70b-instruct
API Key Present: Yes
------------------------------------------------------------
Status:   ONLINE
Healthy:  True
Latency:  184.2 ms
============================================================
```

---

## 5. Built-in Resilience & Fallback

The HELZERX bot includes enterprise resilience patterns:
1. **Exponential Backoff**: Automatically catches HTTP 429 (rate-limit) and HTTP 5xx errors with exponential jitter backoff (`1.5s`, `3.0s`, `6.0s`).
2. **Offline Fallback**: If the key is omitted or the provider is temporarily unavailable, the bot activates its internal diagnostic triage without crashing ticket sessions.
3. **Token Usage Monitoring**: Tracks cumulative prompt and completion tokens accessible via `/ai-status`.
