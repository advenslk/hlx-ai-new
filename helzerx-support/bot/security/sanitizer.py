"""
HELZERX AI Support - Sensitive Data Sanitizer
Scrubs sensitive tokens, passwords, private keys, and API secrets from ticket chats & transcripts.
"""
from __future__ import annotations

import re
from typing import Tuple

# Regex patterns for common sensitive secrets
PATTERNS = [
    # Discord Bot Tokens
    (re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,}", re.IGNORECASE), "[REDACTED_DISCORD_TOKEN]"),
    # Generic API Keys (OpenAI, NVIDIA, GitHub, Stripe)
    (re.compile(r"\b(nvapi-[A-Za-z0-9_-]{30,}|sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36})\b"), "[REDACTED_API_KEY]"),
    # AWS Access Key IDs
    (re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), "[REDACTED_AWS_KEY]"),
    # RSA / OpenSSH Private Keys
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "[REDACTED_PRIVATE_SSH_KEY]"),
    # Password key-value pairs (e.g. password = "secret", pass: 1234)
    (re.compile(r"(?i)\b(password|passwd|secret|rcon\.password|db_password)\s*[:=]\s*([^\s,;]+)"), r"\1: [REDACTED_SECRET]"),
    # MySQL / Postgres Connection Strings with credentials
    (re.compile(r"postgres(?:ql)?:\/\/[^:]+:[^@]+@"), "postgresql://[USER]:[REDACTED_PASSWORD]@"),
    (re.compile(r"mysql:\/\/[^:]+:[^@]+@"), "mysql://[USER]:[REDACTED_PASSWORD]@"),
]


def sanitize_sensitive_data(content: str) -> Tuple[str, bool]:
    """
    Scans and redacts sensitive credentials from customer or staff messages.
    Returns:
        (sanitized_text, had_redaction: bool)
    """
    if not content:
        return "", False

    sanitized = content
    modified = False

    for pattern, replacement in PATTERNS:
        new_text, count = pattern.subn(replacement, sanitized)
        if count > 0:
            sanitized = new_text
            modified = True

    return sanitized, modified
