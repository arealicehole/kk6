---
description: "Quick KK6 status check: blocking tasks, timeline, next actions"
allowed-tools: ["Read", "Grep"]
---

# KannaKickback 6 - Quick Status Check

You are providing a rapid status briefing for crunch time event planning.

## 1. Read Critical Tracking Files

**TASK_TRACKER.md:**
- Extract "Days Until Event" value
- Find all 🔴 CRITICAL and 🔴 TODO items
- Identify blocking tasks (top section)
- Note this week's due dates

**WORKING_NOTES.md (first 300 lines):**
- Read latest date entry (top of file)
- Extract "NEXT IMMEDIATE ACTIONS" section
- Find any blockers mentioned
- Note recent completions (✅)

**KK6_FORM_SUBMISSIONS_TRACKER.md:**
- Total RSVPs count
- Any new submissions since last check

## 2. Synthesize 30-Second Briefing

Output format:

```
⏰ COUNTDOWN: [X days until Dec 6]

✅ RECENT WINS:
- [1-3 key completions from working notes]

🚨 BLOCKING NOW:
- [Critical blockers preventing progress]

📋 THIS WEEK MUST-DO:
- [Top 3-5 tasks due this week with dates]

⚡ NEXT 3 ACTIONS:
1. [Most urgent action]
2. [Second priority]
3. [Third priority]
```

**Keep it scannable, actionable, and under 1 minute to read.**
