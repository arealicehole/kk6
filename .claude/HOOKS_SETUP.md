# Optional: Automated Hooks for KK6

Hooks can automatically run commands at specific events. **These are optional** - slash commands work great without them.

## Option 1: Auto-Status on Session Start

Shows critical tasks automatically when you start Claude Code.

**Setup:**

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Quick KK6 status check: Read TASK_TRACKER.md and show me the 🔴 BLOCKING TASKS section and Days Until Event. Keep it under 5 lines."
          }
        ]
      }
    ]
  }
}
```

**Effect:** Every time you open Claude Code, you'll see blocking tasks automatically.

---

## Option 2: Auto-Update Working Notes After Tasks

Prompts you to update WORKING_NOTES.md after completing significant work.

**Setup:**

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "If this was a significant task completion (new content, sent email, major update), remind the user to update WORKING_NOTES.md with today's entry."
          }
        ]
      }
    ]
  }
}
```

**Effect:** After writing/editing files, Claude reminds you to log the work.

---

## Option 3: Daily Blocker Check Hook

Runs blocker analysis automatically at session start.

**Setup:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Check blockers: /kk6-blockers'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Effect:** Reminds you to check blockers each session.

---

## Option 4: Prevent Accidental API Key Commits

Block commits containing API keys or tokens.

**Setup:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "grep -iE '(api[_-]?key|token|secret|password).*=.*[A-Za-z0-9]{20}' || exit 0",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Effect:** Warns before writing files with exposed credentials.

---

## Security Note: Hook File Locations

| File | Visibility | Git |
|------|------------|-----|
| `.claude/settings.json` | Project-wide (shared) | ✅ Safe to commit |
| `.claude/settings.local.json` | Local only | ❌ Do NOT commit (add to .gitignore) |
| `~/.claude/settings.json` | User-wide (all projects) | N/A (in home directory) |

**Best practice:** Put shared hooks in `.claude/settings.json`, personal preferences in `.claude/settings.local.json`.

---

## Testing Hooks

1. Create `.claude/settings.json` with hook config
2. Reload Claude Code window
3. Trigger the hook event (start session, write file, etc.)
4. Check verbose logs if issues: Claude Code → Settings → Enable Debug Logging

---

## Recommended Setup for KK6

**Start simple:**
1. Use slash commands (`/kk6-status`, `/kk6-agenda`) - no hooks needed
2. Add `SessionStart` hook later if you want auto-status

**Don't use hooks for:**
- Complex logic (use slash commands instead)
- Anything that blocks your workflow
- Sensitive operations without testing first

**Good use cases:**
- Session start reminders
- Auto-formatting after saves
- Blocking dangerous operations
- Adding context automatically

---

## Current Hook Status

**Hooks configured:** None (hooks are optional)

**To enable:** Create `.claude/settings.json` with desired hook config from options above.

**To disable:** Remove or comment out hook config.

---

## More Info

See research docs:
- `/zeebot/r/` - General Claude Code research
- Official docs: [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
