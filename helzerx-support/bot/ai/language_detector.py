"""
HELZERX AI Support - Multi-Language Detection Engine
Accurately detects English, Sinhala (Unicode script), and Singlish (Sinhala phonetically written in Latin characters).
"""
from __future__ import annotations

import re
from typing import Tuple

# Sinhala Unicode Range: U+0D80 to U+0DFF
SINHALA_UNICODE_PATTERN = re.compile(r"[\u0D80-\u0DFF]")

# Common phonetic Singlish markers
SINGLISH_KEYWORDS = [
    r"\bmage\b", r"\bmata\b", r"\bapi\b", r"\boya\b", r"\boyala\b",
    r"\bserver eka\b", r"\bserver eke\b", r"\bweda\b", r"\bkaranna\b",
    r"\bwenne na\b", r"\bwenne ne\b", r"\bwada na\b", r"\bnehe\b",
    r"\behema\b", r"\bkohomada\b", r"\bmonawada\b", r"\bkiyala\b",
    r"\bticket eka\b", r"\bhelp ekak\b", r"\bpuluwanda\b", r"\bdanna\b",
    r"\bbalanna\b", r"\bhadala\b", r"\bdenna\b", r"\bstart wenne\b",
    r"\bstop wela\b", r"\bcrash wenawa\b", r"\bip eka\b", r"\bping eka\b",
    r"\blag wenawa\b", r"\brcon eka\b", r"\bport eka\b", r"\bhosting eka\b",
    r"\bpterodactyl wings\b", r"\bkenek\b", r"\bthiyenawa\b", r"\bnam\b"
]
SINGLISH_REGEX = re.compile("|".join(SINGLISH_KEYWORDS), re.IGNORECASE)


def detect_language(text: str) -> Tuple[str, float]:
    """
    Analyzes text and returns the detected language code and confidence.
    Returns:
        (language_code: "si" | "singlish" | "en", confidence: float)
    """
    if not text or not text.strip():
        return "en", 1.0

    # 1. Check for Sinhala Unicode characters
    sinhala_chars = len(SINHALA_UNICODE_PATTERN.findall(text))
    total_letters = len([c for c in text if c.isalpha()]) or 1

    if sinhala_chars > 2 or (sinhala_chars / total_letters) > 0.2:
        return "si", min(1.0, 0.6 + (sinhala_chars / total_letters) * 0.4)

    # 2. Check for Singlish phonetic markers
    singlish_matches = len(SINGLISH_REGEX.findall(text))
    if singlish_matches >= 2:
        return "singlish", min(1.0, 0.7 + (singlish_matches * 0.1))
    elif singlish_matches == 1:
        # Check if text is short and contains clear Singlish token
        words = text.strip().split()
        if len(words) <= 10:
            return "singlish", 0.75

    # 3. Default to English
    return "en", 0.95
