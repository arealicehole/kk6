# KannaKickback 6 - Custom Commands

This directory contains slash commands for efficient KK6 project management.

## Available Commands

### `/kk6-status`
**Quick status check** - Get a 30-second briefing of blocking tasks, timeline, and next actions.

**Use when:**
- Starting your work session
- Checking in during the day
- Need quick reference to priorities

**Output:** Scannable status in <1 minute read time

---

### `/kk6-agenda`
**Comprehensive agenda** - Deep analysis of all tasks, timeline, and department status.

**Use when:**
- Weekly planning sessions
- Need complete picture of project
- Assessing if you're on track
- Planning resource allocation

**Output:** Full project dashboard with all departments

---

### `/kk6-blockers`
**Blocker analysis** - Focus on what's preventing progress and how to unblock.

**Use when:**
- Feeling stuck
- Need to prioritize unblocking work
- Planning coordination with team
- Identifying quick wins

**Output:** Categorized blockers with resolution plans

---

### `/kk6-agent`
**Launch planning agent** - Spawn a specialized agent for deep analysis and task execution.

**Use when:**
- Need AI to do research/analysis
- Want to execute multiple tasks autonomously
- Complex multi-step planning needed
- Synthesizing information from many sources

**Output:** Agent runs autonomously and reports back with findings

---

### `/kk6-update`
**Update tracking documents** - Update TASK_TRACKER, WORKING_NOTES, and FORM_SUBMISSIONS with work from this session.

**Use when:**
- Ending a work session
- Completed multiple tasks
- Made important decisions
- Received form submissions (RSVPs, vendors)
- Created deliverables

**How it works:**
1. Analyzes current conversation
2. Reads tracking files to understand current state
3. Shows you proposed updates
4. Asks for confirmation
5. Delegates to agent for file updates
6. Commits changes to git (doesn't push)

**Arguments:**
```bash
# Simple (will prompt for details)
/kk6-update

# With context hint
/kk6-update "Finished Facebook strategy and POST #6"
```

**Output:** Updated tracking docs + git commit summary

---

## Command Syntax

```bash
# Basic usage
/kk6-status

# With arguments (where supported)
/kk6-agenda week2

# Chaining (run multiple commands)
/kk6-status
/kk6-blockers
```

## Tips

1. **Start each day with `/kk6-status`** - Quick orientation
2. **Use `/kk6-agenda` weekly** - Comprehensive planning
3. **Run `/kk6-blockers` when stuck** - Find unblocking actions
4. **Launch `/kk6-agent` for complex work** - Autonomous execution
5. **End sessions with `/kk6-update`** - Keep tracking docs current

## Customization

To modify commands:
1. Edit the `.md` file in `.claude/commands/`
2. Changes take effect immediately
3. Test with `/command-name`

## Adding New Commands

Create a new `.md` file in this directory:

```markdown
---
description: "What this command does"
allowed-tools: ["Read", "Grep"]  # Optional
---

Command prompt here...
```

File name becomes command name (e.g., `my-command.md` → `/my-command`)
