"""
HELZERX AI Support - SQLAlchemy Database Models
Full enterprise schema supporting PostgreSQL (production) and SQLite (testing/local).
"""
from __future__ import annotations

import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime,
    ForeignKey, Float, Enum, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=True)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    tickets = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.creator_id")
    assigned_tickets = relationship("Ticket", back_populates="claimed_by", foreign_keys="Ticket.claimed_by_id")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_code = Column(String(20), unique=True, nullable=False, index=True) # e.g. HZX-8429
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, unique=True, nullable=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category = Column(String(50), nullable=False, default="general") # general, technical, vps, etc.
    status = Column(String(30), nullable=False, default="OPEN", index=True) # OPEN, CLAIMED, ESCALATED, CLOSED
    priority = Column(String(20), nullable=False, default="NORMAL", index=True) # LOW, NORMAL, HIGH, URGENT
    department = Column(String(100), nullable=True)

    initial_subject = Column(String(255), nullable=True)
    initial_description = Column(Text, nullable=True)
    server_identifier = Column(String(100), nullable=True) # Node, IP, or Service ID

    claimed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ai_enabled = Column(Boolean, default=True)
    ai_turn_count = Column(Integer, default=0)
    customer_language = Column(String(20), default="en") # en, si, singlish

    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    close_reason = Column(Text, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="tickets")
    claimed_by = relationship("User", foreign_keys=[claimed_by_id], back_populates="assigned_tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    internal_notes = relationship("InternalNote", back_populates="ticket", cascade="all, delete-orphan", order_by="InternalNote.created_at")
    transcript = relationship("TicketTranscript", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("CustomerFeedback", back_populates="ticket", uselist=False, cascade="all, delete-orphan")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    discord_message_id = Column(BigInteger, nullable=True)
    author_id = Column(BigInteger, nullable=False)
    author_name = Column(String(100), nullable=False)
    author_role = Column(String(20), nullable=False) # customer, ai, staff, system

    content = Column(Text, nullable=False)
    detected_language = Column(String(20), nullable=True)
    tokens_prompt = Column(Integer, default=0)
    tokens_completion = Column(Integer, default=0)
    has_sanitization = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="messages")


class InternalNote(Base):
    """Staff-only internal communication attached to tickets; NEVER visible to customers."""
    __tablename__ = "internal_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    staff_id = Column(BigInteger, nullable=False)
    staff_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="internal_notes")


class KnowledgeDocument(Base):
    """RAG-enabled documentation, FAQs, and verified HELZERX technical specifications."""
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(20), default="md") # md, txt, pdf, faq
    tags = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class TicketTranscript(Base):
    __tablename__ = "ticket_transcripts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, unique=True)
    ticket_code = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=True)
    html_content = Column(Text, nullable=False)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="transcript")


class CustomerFeedback(Base):
    __tablename__ = "customer_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(BigInteger, nullable=False)
    rating = Column(Integer, nullable=False) # 1 to 5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="feedback")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False, index=True) # TICKET_CREATED, TICKET_CLAIMED, AI_ESCALATED, etc.
    actor_id = Column(BigInteger, nullable=False)
    actor_name = Column(String(100), nullable=False)
    ticket_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
