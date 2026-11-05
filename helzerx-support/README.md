# HELZERX AI SUPPORT (v1.0)
### Enterprise AI Discord Ticket Support Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://python.org)
[![Discord](https://img.shields.io/badge/discord.py-2.x-5865F2?logo=discord)](https://discordpy.readthedocs.io/)
[![AI Engine](https://img.shields.io/badge/AI_Engine-NVIDIA_NIM-76B900?logo=nvidia)](https://build.nvidia.com)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2016-336791?logo=postgresql)](https://postgresql.org)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-10B981)](#testing)
[![License](https://img.shields.io/badge/License-Proprietary-red)](#)

---

## 📖 Overview

**HELZERX AI Support** is an enterprise-grade customer support platform designed for high-availability cloud infrastructure and game server hosting. Inspired by the engineering tiers at **GitHub Support**, **AWS Support**, and **Cloudflare Support**, HELZERX unifies an intelligent conversational AI agent, strict role-based ticketing workflows, verified technical knowledge bases (RAG), and security controls.

### 🌟 Key Highlights

- **🧠 NVIDIA NIM AI Engine**: Ultra-low latency OpenAI-compatible integration with `meta/llama-3.1-70b-instruct`, automatic exponential backoff, rate-limit retry, and token usage tracking.
- **🌐 Trilingual Detection & Fluency**: Autonomously detects and speaks in **English**, **Sinhala (සිංහල)**, and **Singlish** (phonetic Latin Sinhala).
- **🛠️ Deep Technical Diagnostic Engine**: Step-by-step troubleshooting for Linux (Ubuntu/Debian), Docker daemon, Pterodactyl & Wings sockets, Minecraft Paper/Purpur (Java 17/21, Aikar's flags, OOM crashes), Cloudflare DNS (Grey vs Orange cloud), and Bare Metal IPMI.
- **🎫 Advanced Ticket Lifecycle**: Category dropdowns, modals, private channel provisioning, unique ticket IDs (`HZX-8429`), human escalations, claiming, internal notes (hidden from customers), and HTML transcripts.
- **🛡️ Cybersecurity Hardening**: Prompt injection guards, regex scrubbing for passwords/SSH keys/tokens, and sliding-window rate limiters.
- **🗄️ Resilient Persistence**: PostgreSQL with SQLAlchemy 2.0 asyncpg, Alembic migrations, and emergency local SQLite fallback.

---

## 📂 Repository Structure

```
helzerx-support/
├── bot/
│   ├── main.py                  # Bot entrypoint, view registration & signal handling
│   ├── config.py                # Typed settings, category specifications & role bindings
│   ├── ai/                      # NVIDIA NIM client, prompts, classifier, language detector
│   ├── commands/                # Slash commands (/panel, /ticket, /claim, /ai-status, etc.)
│   ├── database/                # SQLAlchemy models, async session factory, CRUD operations
│   ├── embeds/                  # Professional HELZERX dark-theme embeds
│   ├── events/                  # on_message ticket interceptor & global on_error
│   ├── knowledge/               # RAG document chunker, similarity ranker, verified docs
│   ├── security/                # Prompt injection defense, secret redactor, rate limiter
│   ├── staff/                   # Claiming, assignment, confidential internal notes
│   ├── tickets/                 # Ticket lifecycle, channel management, HTML transcripts
│   ├── utils/                   # Structured logger, timestamping, slug sanitizers
│   └── views/                   # Persistent Discord UI views & modals
├── docs/                        # Step-by-step guides for Discord, NVIDIA, DB, and Deployment
├── migrations/                  # Alembic environment & initial schema migration
├── scripts/                     # CLI diagnostics, DB setup, and health check scripts
├── tests/                       # Automated test suite (18 tests)
├── Dockerfile                   # Hardened multi-stage container build
├── docker-compose.yml           # Complete stack (Bot + PostgreSQL + Redis)
├── requirements.txt             # Locked Python production dependencies
├── .env.example                 # Comprehensive environment variable template
├── .replit                      # 1-click Replit configuration
└── replit.nix                   # Nix dependencies for Replit
```

---

## ⚡ Quickstart

### 1. Clone & Install Dependencies
```bash
cd helzerx-support
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```
Fill in:
- `DISCORD_TOKEN`
- `DISCORD_GUILD_ID`
- `NVIDIA_API_KEY`
- `DATABASE_URL`

### 3. Run Automated Tests
```bash
python3 tests/run_tests.py
```

### 4. Launch Bot
```bash
python3 bot/main.py
```

---

## 📋 Slash Command Reference

| Command | Permission | Description |
| :--- | :--- | :--- |
| `/panel` | **Administrator** | Embeds the interactive customer support panel in current channel |
| `/setup` | **Administrator** | Audits category, roles, and transcript channel configurations |
| `/config` | **Administrator** | Inspects active runtime settings and security levels |
| `/ticket` | Everyone | Opens a new ticket via slash command |
| `/claim` | **Support Staff** | Claims ticket as the primary responding staff member |
| `/assign` | **Support Staff** | Reassigns ticket to another support team member |
| `/close` | User / Staff | Initiates confirmation view and archives ticket with transcript |
| `/reopen` | **Support Staff** | Re-activates a previously closed ticket |
| `/transcript` | **Support Staff** | Generates standalone HTML transcript file on demand |
| `/ticketinfo` | User / Staff | Displays diagnostic metadata, assignee, and internal notes |
| `/ticketstats`| **Support Staff** | Shows global ticket metrics and resolution rate |
| `/ai-status` | **Support Staff** | Probes NVIDIA NIM health, latency, and token consumption |
| `/ai-enable` | **Support Staff** | Enables automated AI troubleshooting for ticket |
| `/ai-disable`| **Support Staff** | Disables AI on ticket for manual staff conversation |
| `/knowledge-search` | **Support Staff** | Tests RAG query ranking across verified guides |
| `/knowledge-add` | **Administrator** | Adds new verified technical article to knowledge base |
| `/knowledge-remove` | **Administrator** | Removes article from knowledge base |

---

## 🧪 Testing

The codebase includes an automated test suite verifying:
- Prompt injection defense patterns
- Sensitive password and key scrubbing
- Sliding window rate limiting
- Multi-language detection (English, Sinhala, Singlish)
- Technical classification & urgency prioritization
- RAG document chunking & search ranking
- Ticket ID formatting & HTML transcript generation

Run all tests:
```bash
python3 tests/run_tests.py
```
Output:
```
=================================================================
  HELZERX AI SUPPORT - AUTOMATED TEST SUITE
=================================================================
Ran 18 tests in 0.003s
OK
Total Tests Run: 18
Passed:          18
Failures:        0
Errors:          0
=================================================================
```

---

## 📚 Complete Documentation Links

- [Discord Bot Setup Guide](docs/DISCORD_BOT_SETUP.md)
- [NVIDIA NIM AI Engine Guide](docs/NVIDIA_NIM_GUIDE.md)
- [PostgreSQL Database & Migration Guide](docs/DATABASE_SETUP.md)
- [Production Deployment Guide](docs/DEPLOYMENT.md)
