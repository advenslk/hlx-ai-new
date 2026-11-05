# HELZERX AI Support - Discord Bot Setup Guide

This guide walks through creating and configuring your Discord Application in the [Discord Developer Portal](https://discord.com/developers/applications) for HELZERX AI Support.

---

## 1. Create Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** in the top right.
3. Enter Name: **`HELZERX AI Support`** and accept the Developer Terms.
4. (Optional) Set description and upload the official HELZERX dark logo.

---

## 2. Configure Bot & Privileged Gateway Intents

1. Navigate to the **Bot** tab in the left sidebar.
2. Under **Token**, click **Reset Token** and copy your token. Save it in your `.env` file as `DISCORD_TOKEN`.
3. Scroll down to **Privileged Gateway Intents**:
   - ✅ **Presence Intent**: Optional
   - ✅ **Server Members Intent**: **REQUIRED** (Must be enabled so the bot can read member roles and set ticket channel permissions)
   - ✅ **Message Content Intent**: **REQUIRED** (Must be enabled so the bot can read customer issues and provide AI diagnosis)
4. Click **Save Changes**.

---

## 3. Generate OAuth2 Invite URL

1. Navigate to **OAuth2** > **URL Generator** in the left sidebar.
2. Under **Scopes**, select:
   - ✅ `bot`
   - ✅ `applications.commands` (Enables `/ticket`, `/panel`, `/setup`, etc.)
3. Under **Bot Permissions**, select:
   - ✅ **Administrator** (recommended for full ticket category & permission control)
   - *Or minimal granular permissions:*
     * Manage Channels
     * Manage Roles
     * View Channels
     * Send Messages
     * Send Messages in Threads
     * Manage Messages
     * Embed Links
     * Attach Files
     * Read Message History
     * Use External Emojis
     * Add Reactions
4. Copy the generated URL at the bottom and open it in your browser to invite the bot to your Discord Server.

---

## 4. Obtain Server & Channel IDs

Enable **Developer Mode** in your Discord Client:
- **User Settings** > **Advanced** > Toggle **Developer Mode** ON.

Right-click the following in your server to copy their Snowflake IDs:
- **Your Server**: Right-click server icon > **Copy Server ID** (`DISCORD_GUILD_ID`)
- **Ticket Category**: Right-click category header > **Copy Category ID** (`TICKET_CATEGORY_ID`)
- **Support Staff Role**: Server Settings > Roles > Right-click Support Role > **Copy Role ID** (`SUPPORT_ROLE_IDS`)
- **Transcript Archive Channel**: Right-click `#transcripts` channel > **Copy Channel ID** (`TRANSCRIPT_CHANNEL_ID`)
- **Staff Logs Channel**: Right-click `#staff-logs` channel > **Copy Channel ID** (`STAFF_LOG_CHANNEL_ID`)

---

## 5. Deploy the Support Panel

Once the bot is online in your server, run the slash command in your public support channel (e.g., `#🎫-open-a-ticket`):

```bash
/panel
```

This will embed the persistent HELZERX support panel with the department dropdown menu.
