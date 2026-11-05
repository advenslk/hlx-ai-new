"""Initial HELZERX schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-10-31 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('discord_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('is_staff', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discord_id')
    )
    op.create_index(op.f('ix_users_discord_id'), 'users', ['discord_id'], unique=True)

    # Tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_code', sa.String(length=20), nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('initial_subject', sa.String(length=255), nullable=True),
        sa.Column('initial_description', sa.Text(), nullable=True),
        sa.Column('server_identifier', sa.String(length=100), nullable=True),
        sa.Column('claimed_by_id', sa.Integer(), nullable=True),
        sa.Column('ai_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('ai_turn_count', sa.Integer(), nullable=True, default=0),
        sa.Column('customer_language', sa.String(length=20), nullable=True, default='en'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('closed_by_id', sa.Integer(), nullable=True),
        sa.Column('close_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['claimed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('channel_id'),
        sa.UniqueConstraint('ticket_code')
    )
    op.create_index(op.f('ix_tickets_ticket_code'), 'tickets', ['ticket_code'], unique=True)
    op.create_index(op.f('ix_tickets_status'), 'tickets', ['status'], unique=False)
    op.create_index(op.f('ix_tickets_priority'), 'tickets', ['priority'], unique=False)

    # Ticket Messages
    op.create_table(
        'ticket_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('discord_message_id', sa.BigInteger(), nullable=True),
        sa.Column('author_id', sa.BigInteger(), nullable=False),
        sa.Column('author_name', sa.String(length=100), nullable=False),
        sa.Column('author_role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('detected_language', sa.String(length=20), nullable=True),
        sa.Column('tokens_prompt', sa.Integer(), nullable=True, default=0),
        sa.Column('tokens_completion', sa.Integer(), nullable=True, default=0),
        sa.Column('has_sanitization', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticket_messages_ticket_id'), 'ticket_messages', ['ticket_id'], unique=False)

    # Internal Notes (Staff only)
    op.create_table(
        'internal_notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.BigInteger(), nullable=False),
        sa.Column('staff_name', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Knowledge Documents
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=20), nullable=True, default='md'),
        sa.Column('tags', sa.String(length=255), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Ticket Transcripts
    op.create_table(
        'ticket_transcripts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('ticket_code', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_id')
    )

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('actor_id', sa.BigInteger(), nullable=False),
        sa.Column('actor_name', sa.String(length=100), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('ticket_transcripts')
    op.drop_table('knowledge_documents')
    op.drop_table('internal_notes')
    op.drop_table('ticket_messages')
    op.drop_table('tickets')
    op.drop_table('users')
