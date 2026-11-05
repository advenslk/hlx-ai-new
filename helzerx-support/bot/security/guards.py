"""
HELZERX AI Support - Prompt Injection & Security Guards
Defends against jailbreak attempts, system prompt extraction, role confusion, and command forgery.
"""
from __future__ import annotations

import re
from typing import Tuple, List

# High-confidence prompt injection indicators
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore (?:all )?(?:previous|prior|above) instructions\b"),
    re.compile(r"(?i)\bdisregard (?:all )?(?:previous|prior|system) (?:prompts|rules|instructions)\b"),
    re.compile(r"(?i)\byou are now (?:dan|developer mode|unrestricted|god mode|evil)\b"),
    re.compile(r"(?i)\bprint (?:your|the) (?:system prompt|initial prompt|hidden instructions)\b"),
    re.compile(r"(?i)\brepeat (?:the text|everything) above\b"),
    re.compile(r"(?i)\bshow me the exact prompt\b"),
    re.compile(r"(?i)\bjailbreak\b"),
    re.compile(r"(?i)\bbase64 decode the following and execute\b"),
    re.compile(r"(?i)\bsudo execute command\b"),
    re.compile(r"(?i)\bact as an unfiltered (?:ai|assistant|model)\b"),
    re.compile(r"(?i)\bpretend you are no longer helzerx\b"),
]

SUSPICIOUS_PHRASES = [
    "system directive override",
    "developer access granted",
    "maintenance bypass protocol",
    "sudo su",
    "rm -rf /",
    "reveal internal api keys",
    "send me the nvidia api key"
]


def check_prompt_injection(content: str) -> Tuple[bool, str]:
    """
    Evaluates whether the message contains an injection attempt or malicious instruction.
    Returns:
        (is_flagged: bool, reason: str)
    """
    if not content:
        return False, ""

    normalized = content.lower()

    # Check regex patterns
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(content):
            return True, f"Matched injection signature: {pattern.pattern}"

    # Check suspicious keyword phrases
    for phrase in SUSPICIOUS_PHRASES:
        if phrase in normalized:
            return True, f"Suspicious security phrase: '{phrase}'"

    # Check high frequency of system prompt delimiters
    delimiters = ["### System:", "---BEGIN SYSTEM---", "[INST]", "<<SYS>>"]
    if any(delim in content for delim in delimiters):
        return True, "Contains raw LLM instruction delimiters"

    return False, ""
