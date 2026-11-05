"""
HELZERX AI Support - Smart Ticket Classifier
Analyzes ticket context to determine intent, category, technical complexity, urgency, and priority.
"""
from __future__ import annotations

import re
from typing import Dict, Any


class TicketClassification:
    def __init__(
        self,
        intent: str,
        category: str,
        complexity: str,
        urgency: str,
        priority: str,
        department: str,
        is_human_escalation_needed: bool = False
    ):
        self.intent = intent
        self.category = category
        self.complexity = complexity
        self.urgency = urgency
        self.priority = priority
        self.department = department
        self.is_human_escalation_needed = is_human_escalation_needed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "category": self.category,
            "complexity": self.complexity,
            "urgency": self.urgency,
            "priority": self.priority,
            "department": self.department,
            "is_human_escalation_needed": self.is_human_escalation_needed
        }


def classify_ticket(subject: str, description: str, category_hint: str = "general") -> TicketClassification:
    """
    Evaluates customer subject and description to classify priority and urgency.
    Follows Section 7 rules: Priority levels LOW, NORMAL, HIGH, URGENT.
    """
    text = f"{subject or ''} {description or ''}".lower()

    # Urgency indicators
    urgent_keywords = [
        "down", "offline", "crashed", "ddos", "attack", "outage", "production down",
        "emergency", "urgent", "hacked", "data loss", "ransomware", "unreachable",
        "entire network down", "wings died"
    ]
    high_keywords = [
        "cannot connect", "error 502", "oom", "out of memory", "boot loop", "ssl failed",
        "kernel panic", "packet loss", "overheating", "pterodactyl 500", "billing double charge"
    ]
    low_keywords = [
        "partner", "sponsor", "affiliate", "how to install plugin", "question about",
        "recommendation", "pricing inquiry", "curious"
    ]
    human_keywords = [
        "human", "real person", "agent", "talk to staff", "call staff", "escalate", "representative"
    ]

    is_human = any(k in text for k in human_keywords)

    # Determine Urgency & Priority
    if any(k in text for k in urgent_keywords):
        urgency = "CRITICAL"
        priority = "URGENT"
        complexity = "HIGH"
    elif any(k in text for k in high_keywords):
        urgency = "HIGH"
        priority = "HIGH"
        complexity = "MEDIUM"
    elif any(k in text for k in low_keywords):
        urgency = "LOW"
        priority = "LOW"
        complexity = "LOW"
    else:
        urgency = "NORMAL"
        priority = "NORMAL"
        complexity = "MEDIUM"

    # Category and department mapping
    cat = category_hint.lower()
    if "mine" in text or "paper" in text or "purpur" in text or "spigot" in text or "forge" in text:
        cat = "minecraft"
        department = "Game Server Operations"
    elif "vps" in text or "kvm" in text or "kernel" in text:
        cat = "vps"
        department = "Infrastructure Team"
    elif "dedicated" in text or "bare metal" in text or "ipmi" in text or "idrac" in text:
        cat = "dedicated"
        department = "Infrastructure Team"
    elif "invoice" in text or "payment" in text or "refund" in text or "card" in text:
        cat = "billing"
        department = "Billing & Finance"
    elif "partnership" in text or "sponsor" in text:
        cat = "partnership"
        department = "Management"
    else:
        department = "Technical Support"

    return TicketClassification(
        intent="Technical Resolution" if cat in ["minecraft", "vps", "technical", "dedicated"] else "Account/Inquiry",
        category=cat,
        complexity=complexity,
        urgency=urgency,
        priority=priority,
        department=department,
        is_human_escalation_needed=is_human
    )
