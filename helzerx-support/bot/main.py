"""
HELZERX AI Support - Main Application Entrypoint
Initializes discord.py Bot, database connections, persistent views, cogs, and graceful shutdown.
"""
from __future__ import annotations

import asyncio
import os
import signal
import sys
from pathlib import Path

# Ensure root path is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

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
    """Production Discord Bot for HELZERX AI Customer Support."""

    def __init__(self):
        # Enable required intents: Privileged Message Content & Guild Members
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        super().__init__(
            command_prefix="!", # Fallback prefix; primary interface is slash commands
            intents=intents,
            help_command=None,
            max_messages=1000
        )
        self.is_shutting_down = False

    async def setup_hook(self) -> None:
        """Executed during bot startup before connecting to Discord gateway."""
        logger.info("Initializing HELZERX AI Support Bot...")

        # 1. Initialize Database Schema
        try:
            await init_db()
        except Exception as db_err:
            logger.critical(f"Database initialization failed: {db_err}", exc_info=True)

        # 2. Register Persistent Views
        self.add_view(TicketPanelView())
        self.add_view(TicketControlView())
        logger.info("Persistent views registered (TicketPanelView, TicketControlView).")

        # 3. Load Extension Cogs
        cogs = [
            "bot.commands.setup_cog",
            "bot.commands.ticket_cog",
            "bot.commands.ai_cog",
            "bot.commands.knowledge_cog"
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded extension: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}", exc_info=True)

        # 4. Attach error handlers
        self.tree.on_error = on_tree_error

        # 5. Synchronize Slash Commands
        if config.DISCORD_GUILD_ID:
            guild_obj = discord.Object(id=config.DISCORD_GUILD_ID)
            self.tree.copy_global_to(guild=guild_obj)
            synced = await self.tree.sync(guild=guild_obj)
            logger.info(f"Synchronized {len(synced)} slash commands to Guild ID {config.DISCORD_GUILD_ID}")
        else:
            synced = await self.tree.sync()
            logger.info(f"Synchronized {len(synced)} global slash commands.")

    async def on_ready(self) -> None:
        """Fires when bot is fully connected and cache is ready."""
        logger.info(f"==================================================")
        logger.info(f"  HELZERX AI SUPPORT BOT ONLINE")
        logger.info(f"  Logged in as: {self.user.name} ({self.user.id})")
        logger.info(f"  Connected Guilds: {len(self.guilds)}")
        logger.info(f"  AI Model: {config.NVIDIA_MODEL}")
        logger.info(f"==================================================")

        # Immediate Guild Command Sync for VPS (makes commands visible in 1 second instead of waiting 1 hour)
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"✅ Auto-synced {len(synced)} slash commands to guild: {guild.name} ({guild.id})")
            except Exception as sync_err:
                logger.warning(f"Could not auto-sync commands to guild {guild.id}: {sync_err}")

        # Set presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="HELZERX Support Tickets | /ticket"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_message(self, message: discord.Message) -> None:
        """Global message listener."""
        if not message.author.bot and message.guild:
            content_lower = message.content.strip().lower()

            # 1. Admin !sync command
            if content_lower == "!sync" and message.author.guild_permissions.administrator:
                try:
                    self.tree.copy_global_to(guild=message.guild)
                    synced = await self.tree.sync(guild=message.guild)
                    await message.reply(f"✅ **Slash Commands Synced!** Successfully synced `{len(synced)}` commands to this server.")
                except Exception as err:
                    await message.reply(f"❌ Failed to sync slash commands: `{err}`")
                return

            # 2. Admin !panel-setup interactive builder command
            if content_lower == "!panel-setup" and message.author.guild_permissions.administrator:
                from bot.commands.setup_cog import build_builder_dashboard_embed, ContainerPanelBuilderView
                embed = build_builder_dashboard_embed()
                view = ContainerPanelBuilderView()
                await message.channel.send(embed=embed, view=view)
                return

            # 3. Admin !panel command
            if content_lower == "!panel" and message.author.guild_permissions.administrator:
                from bot.embeds.ticket_embeds import create_panel_embed
                from bot.views.panel_view import TicketPanelView
                embed = create_panel_embed()
                view = TicketPanelView()
                await message.channel.send(embed=embed, view=view)
                return

        await handle_ticket_message(message)
        await self.process_commands(message)

    async def close(self) -> None:
        """Graceful shutdown hook."""
        if self.is_shutting_down:
            return
        self.is_shutting_down = True
        logger.info("Initiating graceful shutdown of HELZERX AI Support...")
        await super().close()
        logger.info("Discord connection closed. Shutdown complete.")


def run_bot() -> None:
    """Entrypoint function with signal handling."""
    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        logger.warning(
            "DISCORD_TOKEN is not configured in .env! "
            "Please configure your bot token in .env to connect to Discord."
        )

    bot = HelzerxBot()

    def signal_handler(sig, frame):
        logger.info(f"Received termination signal ({sig}). Exiting...")
        asyncio.create_task(bot.close())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        bot.run(config.DISCORD_TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.critical("Invalid Discord Bot Token provided in .env!")
    except Exception as e:
        logger.critical(f"Fatal error running bot: {e}", exc_info=True)


if __name__ == "__main__":
    run_bot()
