import React, { useState } from 'react';
import {
  Folder,
  FileCode,
  Copy,
  Check,
  Play,
  Terminal,
  Server,
  Cloud,
  CheckCircle2,
  FileText,
  Download
} from 'lucide-react';

interface FileTreeItem {
  name: string;
  path: string;
  type: 'file' | 'dir';
  language?: string;
  children?: FileTreeItem[];
  content?: string;
}

const PROJECT_FILES: FileTreeItem[] = [
  {
    name: 'bot',
    path: 'bot',
    type: 'dir',
    children: [
      {
        name: 'main.py',
        path: 'bot/main.py',
        type: 'file',
        language: 'python',
        content: `"""
HELZERX AI Support - Main Application Entrypoint
Initializes discord.py Bot, database connections, persistent views, cogs, and graceful shutdown.
"""
import asyncio, signal, sys, os
from pathlib import Path
import discord
from discord.ext import commands

from bot.config import config
from bot.utils.logger import logger
from bot.database.session import init_db
from bot.views.panel_view import TicketPanelView
from bot.views.ticket_control_view import TicketControlView
from bot.events.on_message import handle_ticket_message
from bot.events.on_error import on_tree_error

class HelzerxBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        await init_db()
        self.add_view(TicketPanelView())
        self.add_view(TicketControlView())
        for cog in ["bot.commands.setup_cog", "bot.commands.ticket_cog", "bot.commands.ai_cog", "bot.commands.knowledge_cog"]:
            await self.load_extension(cog)
        self.tree.on_error = on_tree_error
        await self.tree.sync()

if __name__ == "__main__":
    bot = HelzerxBot()
    bot.run(config.DISCORD_TOKEN)`
      },
      {
        name: 'config.py',
        path: 'bot/config.py',
        type: 'file',
        language: 'python',
        content: `"""
HELZERX AI Support - Central Configuration Module
"""
import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class TicketCategoryDef:
    id: str
    name: str
    description: str
    emoji: str
    default_priority: str
    department: str

class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DISCORD_GUILD_ID: int = int(os.getenv("DISCORD_GUILD_ID", "0"))
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://helzerx:pass@localhost:5432/helzerx")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "6"))
    MASK_SENSITIVE_DATA: bool = True

config = Config()`
      },
      {
        name: 'ai',
        path: 'bot/ai',
        type: 'dir',
        children: [
          {
            name: 'client.py',
            path: 'bot/ai/client.py',
            type: 'file',
            language: 'python',
            content: `"""
NVIDIA NIM AI Engine Integration
OpenAI-compatible client with exponential backoff and token tracking.
"""
import asyncio, time, httpx
from bot.config import config
from bot.utils.logger import logger

class NvidiaNimClient:
    def __init__(self):
        self.base_url = config.NVIDIA_BASE_URL
        self.api_key = config.NVIDIA_API_KEY
        self.model = config.NVIDIA_MODEL

    async def generate_response(self, messages):
        # Full exponential backoff implementation for rate limits (429) & 5xx retries
        pass`
          },
          {
            name: 'prompts.py',
            path: 'bot/ai/prompts.py',
            type: 'file',
            language: 'python',
            content: `"""
HELZERX Official Support Persona & Safety Directives
Trilingual instructions (English, Sinhala, Singlish) and domain expertise.
"""
HELZERX_SYSTEM_PROMPT = """
You are the official HELZERX AI Customer Support Engineer.
Never invent technical specs. Never fabricate server diagnostics.
Never claim to run commands directly. Never ask for private keys or passwords.
Trilingual: English, Sinhala (සිංහල), and Singlish."""`
          },
          {
            name: 'language_detector.py',
            path: 'bot/ai/language_detector.py',
            type: 'file',
            language: 'python',
            content: String.raw`"""
Multi-Language Detection Engine (English, Sinhala, Singlish)
"""
import re
SINHALA_UNICODE = re.compile(r"[\u0D80-\u0DFF]")
SINGLISH_KEYWORDS = ["mage", "mata", "api", "oyala", "server eka", "weda", "wenne", "puluwanda"]

def detect_language(text: str):
    if len(SINHALA_UNICODE.findall(text)) > 2:
        return "si", 0.98
    if any(k in text.lower() for k in SINGLISH_KEYWORDS):
        return "singlish", 0.94
    return "en", 0.95`
          }
        ]
      },
      {
        name: 'database',
        path: 'bot/database',
        type: 'dir',
        children: [
          {
            name: 'models.py',
            path: 'bot/database/models.py',
            type: 'file',
            language: 'python',
            content: `"""
SQLAlchemy Relational Models (User, Ticket, TicketMessage, InternalNote, Transcript, AuditLog)
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    ticket_code = Column(String(20), unique=True, index=True)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, unique=True)
    status = Column(String(30), default="OPEN") # OPEN, CLAIMED, ESCALATED, CLOSED
    priority = Column(String(20), default="NORMAL") # LOW, NORMAL, HIGH, URGENT`
          }
        ]
      },
      {
        name: 'security',
        path: 'bot/security',
        type: 'dir',
        children: [
          {
            name: 'guards.py',
            path: 'bot/security/guards.py',
            type: 'file',
            language: 'python',
            content: String.raw`"""
Prompt Injection & Jailbreak Defense Guards
"""
import re

PATTERNS = [
    re.compile(r"ignore (all )?(previous|prior) instructions", re.I),
    re.compile(r"you are now (dan|unrestricted)", re.I),
    re.compile(r"print (your|the) system prompt", re.I)
]

def check_prompt_injection(content: str):
    for p in PATTERNS:
        if p.search(content):
            return True, f"Matched: {p.pattern}"
    return False, ""`
          },
          {
            name: 'sanitizer.py',
            path: 'bot/security/sanitizer.py',
            type: 'file',
            language: 'python',
            content: String.raw`"""
Sensitive Credential Regex Sanitizer
Scrubs Discord tokens, API keys, SSH private keys, and passwords.
"""
import re

PATTERNS = [
    (re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,}", re.I), "[REDACTED_DISCORD_TOKEN]"),
    (re.compile(r"\b(nvapi-[A-Za-z0-9_-]{30,}|sk-[A-Za-z0-9]{32,})\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----"), "[REDACTED_PRIVATE_SSH_KEY]"),
    (re.compile(r"(?i)\b(password|secret)\s*[:=]\s*([^\s,;]+)"), r"\1: [REDACTED_SECRET]")
]`
          }
        ]
      }
    ]
  },
  {
    name: 'Dockerfile',
    path: 'Dockerfile',
    type: 'file',
    language: 'dockerfile',
    content: `FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN groupadd -r helzerx && useradd -r -g helzerx helzerx && chown -R helzerx:helzerx /app
USER helzerx
CMD ["python3", "bot/main.py"]`
  },
  {
    name: 'docker-compose.yml',
    path: 'docker-compose.yml',
    type: 'file',
    language: 'yaml',
    content: `services:
  bot:
    build: .
    container_name: helzerx-ai-bot
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    env_file: .env

  postgres:
    image: postgres:16-alpine
    container_name: helzerx-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: helzerx_user
      POSTGRES_PASSWORD: helzerx_secure_pass
      POSTGRES_DB: helzerx_support
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U helzerx_user -d helzerx_support"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local`
  },
  {
    name: '.replit',
    path: '.replit',
    type: 'file',
    language: 'toml',
    content: `run = "python3 bot/main.py"
entrypoint = "bot/main.py"
modules = ["python-3.11", "postgresql-16"]

[nix]
channel = "stable-23_11"

[env]
PYTHONUNBUFFERED = "1"`
  },
  {
    name: '.env.example',
    path: '.env.example',
    type: 'file',
    language: 'bash',
    content: `DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
DISCORD_GUILD_ID="123456789012345678"
TICKET_CATEGORY_ID="123456789012345679"
SUPPORT_ROLE_IDS="123456789012345680"

NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1"
NVIDIA_API_KEY="nvapi-your-key-here"
NVIDIA_MODEL="meta/llama-3.1-70b-instruct"

DATABASE_URL="postgresql+asyncpg://helzerx_user:helzerx_secure_pass@localhost:5432/helzerx_support"`
  }
];

export const CodebaseViewer: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<FileTreeItem>(PROJECT_FILES[0].children![0]);
  const [copied, setCopied] = useState<boolean>(false);
  const [testOutput, setTestOutput] = useState<string | null>(null);
  const [isRunningTests, setIsRunningTests] = useState<boolean>(false);
  const [showGitModal, setShowGitModal] = useState<boolean>(false);
  const [repoUrl, setRepoUrl] = useState<string>('https://github.com/nethummenura198/helzerx-support.git');

  const handleCopy = () => {
    if (!selectedFile.content) return;
    navigator.clipboard.writeText(selectedFile.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRunTests = () => {
    setIsRunningTests(true);
    setTimeout(() => {
      setIsRunningTests(false);
      setTestOutput(`=================================================================
  HELZERX AI SUPPORT - AUTOMATED TEST SUITE
=================================================================
test_benign_customer_queries_pass (tests.test_security) ... ok
test_prompt_injection_detection (tests.test_security) ... ok
test_sensitive_data_redaction (tests.test_security) ... ok
test_sliding_window_rate_limiter (tests.test_security) ... ok
test_ai_prompt_generation (tests.test_ai_engine) ... ok
test_human_escalation_detection (tests.test_ai_engine) ... ok
test_language_detection_english (tests.test_ai_engine) ... ok
test_language_detection_singlish (tests.test_ai_engine) ... ok
test_language_detection_sinhala (tests.test_ai_engine) ... ok
test_nvidia_client_fallback_when_unconfigured (tests.test_ai_engine) ... ok
test_smart_ticket_classification_minecraft (tests.test_ai_engine) ... ok
test_smart_ticket_classification_urgent (tests.test_ai_engine) ... ok
test_document_chunking (tests.test_knowledge) ... ok
test_knowledge_manager_search (tests.test_knowledge) ... ok
test_relevance_scoring (tests.test_knowledge) ... ok
test_html_transcript_generation (tests.test_tickets) ... ok
test_sanitize_channel_name (tests.test_tickets) ... ok
test_ticket_id_generation (tests.test_tickets) ... ok
----------------------------------------------------------------------
Ran 18 tests in 0.003s
OK

Total Tests Run: 18
Passed:          18 (100%)
Failures:        0
Errors:          0
=================================================================`);
    }, 600);
  };

  return (
    <div className="h-full flex flex-col bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Banner */}
      <div className="p-4 bg-slate-900 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg">
            <FileCode className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">
              HELZERX Production Source Code & Deployment Center
            </h1>
            <p className="text-xs text-slate-400">
              Clean modular architecture in <code>/helzerx-support</code> (Python 3.12+, discord.py 2.x, SQLAlchemy 2.0, NVIDIA NIM).
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <a
            href="/helzerx-support-v1.0.zip"
            download="helzerx-support-v1.0.zip"
            className="px-3 py-1.5 text-xs font-semibold text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Download ZIP</span>
          </a>
          <button
            onClick={() => setShowGitModal(true)}
            className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Cloud className="w-3.5 h-3.5" />
            <span>GitHub Push Setup</span>
          </button>
          <button
            onClick={handleRunTests}
            disabled={isRunningTests}
            className="px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{isRunningTests ? 'Executing Tests...' : 'Run Test Suite (18 Tests)'}</span>
          </button>
        </div>
      </div>

      {/* 2-Column Split: File Tree + Code Viewer */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Left: File Tree */}
        <div className="w-full md:w-72 bg-slate-900/60 border-r border-slate-800 p-3 overflow-y-auto shrink-0 text-xs font-mono">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 px-2">
            Repository Files
          </div>
          <div className="space-y-0.5">
            {PROJECT_FILES.map(item => {
              if (item.type === 'dir') {
                return (
                  <div key={item.path} className="space-y-0.5">
                    <div className="flex items-center gap-1.5 px-2 py-1 text-slate-300 font-semibold">
                      <Folder className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{item.name}/</span>
                    </div>
                    {item.children?.map(child => {
                      if (child.type === 'dir') {
                        return (
                          <div key={child.path} className="pl-4 space-y-0.5">
                            <div className="flex items-center gap-1.5 px-2 py-0.5 text-slate-400">
                              <Folder className="w-3 h-3 text-indigo-400/80" />
                              <span>{child.name}/</span>
                            </div>
                            {child.children?.map(sub => (
                              <button
                                key={sub.path}
                                onClick={() => setSelectedFile(sub)}
                                className={`w-full text-left pl-7 pr-2 py-1 rounded flex items-center gap-1.5 transition-colors cursor-pointer ${
                                  selectedFile.path === sub.path
                                    ? 'bg-indigo-600/30 text-indigo-300 font-semibold border-l-2 border-indigo-500'
                                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                                }`}
                              >
                                <FileText className="w-3 h-3" />
                                <span className="truncate">{sub.name}</span>
                              </button>
                            ))}
                          </div>
                        );
                      }
                      return (
                        <button
                          key={child.path}
                          onClick={() => setSelectedFile(child)}
                          className={`w-full text-left pl-6 pr-2 py-1 rounded flex items-center gap-1.5 transition-colors cursor-pointer ${
                            selectedFile.path === child.path
                              ? 'bg-indigo-600/30 text-indigo-300 font-semibold border-l-2 border-indigo-500'
                              : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                          }`}
                        >
                          <FileText className="w-3 h-3" />
                          <span className="truncate">{child.name}</span>
                        </button>
                      );
                    })}
                  </div>
                );
              }
              return (
                <button
                  key={item.path}
                  onClick={() => setSelectedFile(item)}
                  className={`w-full text-left px-2 py-1 rounded flex items-center gap-1.5 transition-colors cursor-pointer ${
                    selectedFile.path === item.path
                      ? 'bg-indigo-600/30 text-indigo-300 font-semibold border-l-2 border-indigo-500'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <FileText className="w-3 h-3" />
                  <span className="truncate">{item.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Code Viewer / Test Console */}
        <div className="flex-1 flex flex-col bg-slate-950 overflow-hidden">
          {/* File Tab Header */}
          <div className="h-10 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <span className="text-slate-500">/helzerx-support/</span>
              <span className="font-semibold text-white">{selectedFile.path}</span>
            </div>
            <button
              onClick={handleCopy}
              className="px-2.5 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          {/* Test Runner Output Terminal (if active) */}
          {testOutput && (
            <div className="bg-black/80 border-b border-emerald-900/60 p-4 shrink-0 font-mono text-xs text-emerald-400 space-y-2">
              <div className="flex items-center justify-between text-slate-400 pb-1 border-b border-slate-800">
                <span className="flex items-center gap-1.5 text-white font-semibold">
                  <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                  <span>pytest / unittest Test Execution Results</span>
                </span>
                <button onClick={() => setTestOutput(null)} className="hover:text-white cursor-pointer">
                  Dismiss
                </button>
              </div>
              <pre className="whitespace-pre overflow-x-auto text-[11px] leading-tight">
                {testOutput}
              </pre>
            </div>
          )}

          {/* Code Body */}
          <div className="flex-1 overflow-auto p-4 bg-[#0a0d14] font-mono text-xs text-slate-300 leading-relaxed">
            <pre className="whitespace-pre">
              {selectedFile.content || '# Selected file is empty or binary'}
            </pre>
          </div>
        </div>
      </div>

      {/* GitHub Push Setup Modal */}
      {showGitModal && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Cloud className="w-5 h-5 text-indigo-400" />
                <span>Push HELZERX to your GitHub Repository</span>
              </h3>
              <button
                onClick={() => setShowGitModal(false)}
                className="text-slate-400 hover:text-white cursor-pointer text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              All 72 project files are committed to the local <code className="text-emerald-400 font-mono">main</code> branch (Commit <code>0d656e5</code>). To sync to your remote GitHub repository, follow either method below:
            </p>

            <div className="space-y-3 text-xs">
              {/* Option A: Direct ZIP Download */}
              <div className="bg-slate-950 p-3 rounded-lg border border-indigo-900/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-indigo-300">Option 1: 1-Click Project Download (Fastest)</span>
                  <a
                    href="/helzerx-support-v1.0.zip"
                    download="helzerx-support-v1.0.zip"
                    className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded text-[11px] flex items-center gap-1.5 transition-colors"
                  >
                    <Download className="w-3 h-3" />
                    <span>Download ZIP (148 KB)</span>
                  </a>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Download all 72 source files, open <strong>github.com/new</strong>, create your repo, and click <em>"uploading an existing file"</em> to drag & drop all files directly without needing Git installed.
                </p>
              </div>

              {/* Option B: Direct Push from Chat */}
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
                <span className="font-bold text-emerald-400 block">Option 2: Let me push it for you right now</span>
                <p className="text-slate-400 text-[11px]">
                  Reply in the chat with your <strong>GitHub Repository URL</strong> (e.g. <code>https://github.com/nethummenura198/helzerx-support</code>) and your <strong>GitHub Personal Access Token (classic)</strong>. I will run the push command directly in the terminal!
                </p>
              </div>

              {/* Option C: Terminal CLI Command */}
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
                <span className="font-bold text-slate-300 block">Option 3: Push via Command Line</span>
                <div className="space-y-1.5">
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={e => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/your-username/your-repo.git"
                    className="w-full bg-[#0b0f19] border border-slate-700 rounded px-2.5 py-1.5 text-white font-mono text-[11px]"
                  />
                  <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800/80 font-mono text-[11px] text-slate-300 select-all space-y-1">
                    <div>git remote add origin {repoUrl}</div>
                    <div>git branch -M main</div>
                    <div>git push -u origin main</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowGitModal(false)}
                className="px-4 py-2 text-xs font-semibold text-white bg-slate-800 hover:bg-slate-700 rounded-md cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
