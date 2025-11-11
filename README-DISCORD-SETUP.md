# Discord Bot Setup for Kickback Project

This project has a **project-specific** Discord MCP bot configured via `.clauderc`.

## Quick Start

### 1. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it "The Ghost of Christmas Hash"
3. Go to "Bot" tab → Click "Add Bot"
4. **Enable Intents:**
   - ✅ MESSAGE CONTENT INTENT (Required!)
   - ✅ SERVER MEMBERS INTENT
   - ✅ PRESENCE INTENT
5. Click "Reset Token" → Copy the token 
6. Go to OAuth2 → URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Permissions: View Channels, Send Messages, Read Message History, Manage Messages, Manage Channels, Manage Threads, Add Reactions
7. Copy the generated URL → Open in browser → Add bot to your Discord server

### 2. Configure `.clauderc`

Edit `C:\Users\figon\zeebot\kickback\.clauderc`:

```json
{
  "mcpServers": {
    "discord-kickback": {
      "command": "C:\\Users\\figon\\zeebot\\discord-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["-m", "discord_mcp"],
      "env": {
        "DISCORD_TOKEN": "paste_your_actual_bot_token_here",
        "DEFAULT_SERVER_ID": "paste_your_server_id_here"
      }
    }
  }
}
```

**To get your Server ID:**
- Enable Developer Mode (Discord Settings → Advanced)
- Right-click your server icon → Copy ID

### 3. Set Up Channel Mappings (Optional but Recommended)

Create `C:\Users\figon\zeebot\discord-mcp-server\channel_mappings.json`:

```json
{
  "channels": {
    "ppk": "YOUR_PPK_CHANNEL_ID",
    "general": "YOUR_GENERAL_CHANNEL_ID",
    "dev": "YOUR_DEV_CHANNEL_ID"
  },
  "description": "Kickback project channels"
}
```

**To get Channel IDs:**
- Right-click each channel → Copy ID
- Paste into the mappings file

### 4. Restart Claude Code

Close and reopen Claude Code to load the new configuration.

### 5. Test It!

In Claude Code (while in kickback project):

```
"Send a test message to ppk channel saying 'Bot is online!'"
```

Or with channel ID:
```
"Send a message to channel 1234567890 saying 'Hello!'"
```

---

## Available Commands

Once configured, you can tell Claude:

### Send Messages:
- "Post this to PPK channel"
- "Send a message to general saying 'Meeting in 5 minutes'"

### Read Messages:
- "Read the last 10 messages from ppk"
- "What are the recent messages in dev channel?"

### Create Threads:
- "Create a thread in general called 'Project Discussion'"
- "Start a thread in ppk from message 123456789"

### Add Reactions:
- "Add a thumbs up to message 987654321 in general"
- "React with 🎉 to the last message in ppk"

### Get Server Info:
- "Show me all channels in the server"
- "List the members in this Discord"

### Manage Channels:
- "Create a new channel called 'sprint-planning'"
- "Create a category called 'Development'"

---

## Tools Available (21 Total)

✅ send_message - Send to channels (supports names!)
✅ read_messages - Read from channels (supports names!)
✅ create_thread - Create threads (supports names!)
✅ moderate_message - Delete messages/timeout users
✅ add_reaction / add_multiple_reactions / remove_reaction
✅ create_text_channel / delete_channel
✅ set_channel_permissions / create_category
✅ get_server_info / list_members
✅ create_role / delete_role / list_roles / add_role / remove_role
✅ get_user_info / kick_user / ban_user

---

## Project-Specific Behavior

**This bot is ONLY available in the kickback project:**
- ✅ Works: In `C:\Users\figon\zeebot\kickback\`
- ❌ Doesn't work: In other projects or global Claude Code

**Why?** The `.clauderc` file is project-specific!

---

## Troubleshooting

### Bot doesn't show up in tools:
- Verify `.clauderc` is in the kickback project root
- Restart Claude Code
- Check that the path to python.exe is correct

### "Could not resolve channel 'ppk'":
- Create `channel_mappings.json` (see step 3)
- Or use channel ID directly: `"Send to channel 1234567890"`

### "Discord client not ready":
- Check DISCORD_TOKEN is correct
- Verify MESSAGE CONTENT INTENT is enabled
- Check bot was added to the server

### Permission errors:
- Verify bot has required permissions in Discord
- Check bot's role is high enough in the server hierarchy

---

## Security Notes

⚠️ **DO NOT commit `.clauderc` with your bot token to git!**

Add to `.gitignore`:
```
.clauderc
```

Use a template instead:
```json
{
  "mcpServers": {
    "discord-kickback": {
      "command": "C:\\Users\\figon\\zeebot\\discord-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["-m", "discord_mcp"],
      "env": {
        "DISCORD_TOKEN": "YOUR_TOKEN_HERE",
        "DEFAULT_SERVER_ID": "YOUR_SERVER_ID_HERE"
      }
    }
  }
}
```

---

## Additional Documentation

- **Channel Mappings:** `discord-mcp-server/CHANNEL_MAPPING_GUIDE.md`
- **Full Setup:** `discord-mcp-server/SETUP_GUIDE.md`
- **Scoping Features:** `discord-mcp-server/SCOPING_GUIDE.md`
- **Fork README:** `discord-mcp-server/README-FORKED.md`

---

## Need Help?

1. Check logs in bot terminal
2. Review documentation in `discord-mcp-server/` directory
3. Test bot directly: `cd discord-mcp-server && venv\Scripts\python -m discord_mcp`

---

🎯 **Project-specific Discord bot configured for Kickback!**
