---
description: "Focus analysis: What's blocking KK6 progress right now?"
allowed-tools: ["Read", "Grep"]
---

# KannaKickback 6 - Blocker Analysis

You are identifying and analyzing blockers preventing event progress.

## 1. Read Tracking Files

**TASK_TRACKER.md:**
- Extract "BLOCKING TASKS" section
- Find all 🔴 CRITICAL items
- Read "BLOCKERS & ISSUES" section
- Note dependencies between tasks

**WORKING_NOTES.md:**
- Read latest entries for blocker mentions
- Find any issues or problems flagged
- Check for unresolved questions

## 2. Blocker Analysis

For each blocker, identify:
- **What it is** - Clear description
- **Impact** - What it's preventing
- **Owner** - Who can resolve it
- **Dependencies** - What else it affects
- **Solution** - How to unblock (if known)
- **Urgency** - How critical is it?

## 3. Categorize Blockers

**TYPE 1: Physical/Resource**
- Missing items (boxes, weed, materials)
- Budget constraints
- Vendor/partner availability

**TYPE 2: Coordination**
- Waiting for responses
- Scheduling conflicts
- Unclear ownership

**TYPE 3: Information**
- Missing contact info
- Unclear specifications
- Decision needed

**TYPE 4: Technical**
- System issues
- Tool problems
- Access problems

## 4. Output Format

```
🚨 KANNAKICKBACK 6 - BLOCKER REPORT
[X Critical Blockers] | [Y Total Issues]

## 🔴 CRITICAL BLOCKERS (Stopping Progress)

### Blocker: [Name]
- **Impact:** [What can't proceed]
- **Owner:** [Who resolves]
- **Dependencies:** [What else affected]
- **Solution:** [Action to unblock]
- **Urgency:** [Timeline]

[Repeat for each critical blocker]

## 🟡 HIGH-PRIORITY ISSUES (Need Attention)

[Same format for non-blocking but important issues]

## 📋 RESOLUTION PLAN

Recommended sequence to unblock:
1. [First action - unlocks most other work]
2. [Second action]
3. [etc.]

## ⚡ QUICK WINS (Can resolve today)

[List blockers that can be solved immediately]
```

**Focus on actionable solutions and clear ownership.**
