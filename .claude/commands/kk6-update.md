---
description: "Update tracking documents (TASK_TRACKER, WORKING_NOTES, FORM_SUBMISSIONS) with work completed in this session"
allowed-tools: ["Read", "Grep", "Task"]
argument-hint: "[optional: summary of what was completed]"
---

# KK6 Session Update Command

This command helps you update all KK6 tracking documents after a work session.

## Phase 1: Extract Information from Session

Read these files to understand current state:

**Core Tracking Files:**
- @TASK_TRACKER.md
- @WORKING_NOTES.md (first 300 lines)
- @communications/KK6_FORM_SUBMISSIONS_TRACKER.md

Take note of:
- Current "Days Until Event" value
- Latest date entry in WORKING_NOTES
- Recent tasks marked as TODO
- Current RSVP count

## Phase 2: Identify What Changed This Session

Based on our conversation, identify:

### Tasks Completed (to mark ✅ DONE)
- Which tasks from TASK_TRACKER are now complete?
- What deliverables were created?
- What research was finished?

### New Tasks Created (to add to TASK_TRACKER)
- New action items discovered
- Follow-ups needed
- Blockers identified

### Decisions Made (for WORKING_NOTES entry)
- Strategy decisions
- Technical choices
- Budget allocations
- Contact information obtained

### Form Submissions (for FORM_SUBMISSIONS_TRACKER)
- New RSVPs received
- Vendor applications
- Box host applications
- Contact form messages

### Content Created (for content trackers)
- Social posts generated
- Email templates created
- Design files completed
- Videos edited

### Budget Changes (for BUDGET_TRACKER)
- New expenses
- Items purchased
- Donations received

## Phase 3: User Confirmation

Present findings in this format:

```
📝 PROPOSED UPDATES FOR KK6 TRACKING DOCUMENTS

════════════════════════════════════════════════════════════

📋 TASK_TRACKER.md CHANGES:

MARK AS ✅ DONE:
- [ ] [Task name] (was 🔴 TODO in WEEK X section)
- [ ] [Task name] (was 🟡 HIGH PRIORITY)

ADD NEW TASKS:
- [ ] [New task] | Owner: [name] | Due: [date] | Section: WEEK X

UPDATE COUNTS/METRICS:
- Days Until Event: [old] → [new]
- Budget spent: $[old] → $[new]

════════════════════════════════════════════════════════════

📝 WORKING_NOTES.md CHANGES:

ADD NEW DATED ENTRY (at top):
Date: [TODAY - get from system]

✅ COMPLETED TODAY:
- [Item 1]
- [Item 2]

🔴 BLOCKERS RESOLVED:
- [Item if any]

📋 DECISIONS MADE:
- [Decision 1]
- [Decision 2]

📁 KEY FILES CREATED/UPDATED:
- [File path] - [description]

🔴 NEXT IMMEDIATE ACTIONS:
- [Action 1]
- [Action 2]

════════════════════════════════════════════════════════════

📊 KK6_FORM_SUBMISSIONS_TRACKER.md CHANGES:

ADD NEW RSVPS:
- [Name] | [Email] | [Phone] | [Date] | Status: ✅ CONFIRMED

ADD NEW VENDORS:
- [Name] | [Business] | [Email] | [Details]

UPDATE SUMMARY STATS:
- Total RSVPs: [old] → [new]
- Total Vendors: [old] → [new]

════════════════════════════════════════════════════════════

📌 GIT COMMIT:
Message: "Update tracking: [X tasks done, Y decisions, Z new RSVPs] - [date]"

════════════════════════════════════════════════════════════

👉 Ready to apply these updates? (y/n)
   - Type 'y' to proceed with updates
   - Type 'n' to cancel
   - Or specify what to change
```

**Wait for user response.**

If user says NO or requests changes:
- Ask what needs adjustment
- Revise the update plan
- Present again for confirmation

If user says YES:
- Proceed to Phase 4

## Phase 4: Execute Updates via Agent

Use the Task tool to delegate file updates to an agent:

**Task Tool Parameters:**
- **subagent_type:** "general-purpose"
- **description:** "Update KK6 tracking documents"
- **prompt:** (see below)

**Agent Prompt:**

```
You are updating KK6 tracking documents after a work session.

IMPORTANT: Read each file completely before making edits to ensure accurate updates.

═══════════════════════════════════════════════════════════

FILES TO UPDATE:

1. TASK_TRACKER.md

   MARK THESE AS ✅ DONE (find and update status):
   [LIST TASKS TO MARK DONE]

   ADD THESE NEW TASKS (to appropriate WEEK section):
   [LIST NEW TASKS WITH OWNER, DUE DATE, NOTES]

   UPDATE HEADER:
   - Last Updated: [TODAY'S DATE]
   - Days Until Event: [NEW COUNT]

   UPDATE BUDGET SECTION (if applicable):
   - Spent: $[OLD] → $[NEW]
   - Add rows for new expenses

═══════════════════════════════════════════════════════════

2. WORKING_NOTES.md

   ADD NEW DATED ENTRY AT TOP (line 6, after "---"):

   ## [TODAY'S DATE] - [SESSION SUMMARY TITLE]

   ### ✅ COMPLETED TODAY:
   [LIST COMPLETED ITEMS]

   ### 🔴 BLOCKERS RESOLVED:
   [LIST IF ANY]

   ### 📋 DECISIONS MADE:
   [LIST DECISIONS]

   ### 📁 KEY FILES CREATED/UPDATED:
   [LIST FILES]

   ### 🔴 NEXT IMMEDIATE ACTIONS:
   [LIST NEXT ACTIONS]

   ---

═══════════════════════════════════════════════════════════

3. communications/KK6_FORM_SUBMISSIONS_TRACKER.md

   ADD NEW RSVPS (to EVENT RSVPs table):
   [RSVP DATA ROWS]

   ADD NEW VENDORS (to VENDOR APPLICATIONS table):
   [VENDOR DATA ROWS]

   UPDATE SUMMARY STATS SECTION:
   - Total Real RSVPs: [NEW COUNT]
   - Total Vendor Applications: [NEW COUNT]
   - Update conversion stats if applicable

   REMOVE DUPLICATES: Check for duplicate emails before adding

═══════════════════════════════════════════════════════════

4. GIT COMMIT

   After all files are updated:

   git add TASK_TRACKER.md WORKING_NOTES.md communications/KK6_FORM_SUBMISSIONS_TRACKER.md
   git commit -m "[COMMIT MESSAGE FROM USER CONFIRMATION]"

   DO NOT PUSH - just commit locally.

═══════════════════════════════════════════════════════════

RETURN THIS SUMMARY:

## ✅ KK6 Tracking Documents Updated

**Files Modified:**
- TASK_TRACKER.md: [X tasks marked done, Y tasks added]
- WORKING_NOTES.md: [New entry for DATE]
- KK6_FORM_SUBMISSIONS_TRACKER.md: [Z new RSVPs, W new vendors]

**Git Commit:**
- Message: "[COMMIT MESSAGE]"
- Status: ✅ Committed (not pushed)

**Next Steps:**
[Suggest 1-2 next actions based on updated tracking docs]
```

## Phase 5: Post-Update Summary

After agent completes, show user:

```
✅ KK6 TRACKING DOCUMENTS UPDATED SUCCESSFULLY!

[Agent's return summary will appear here]

═══════════════════════════════════════════════════════════

🔍 VERIFY UPDATES:
Run one of these commands to check the changes:
- /kk6-status (quick 30-second briefing)
- /kk6-agenda (comprehensive status)
- /kk6-blockers (check for new blockers)

📌 GIT STATUS:
Changes committed locally. When ready to push:
Run: git push origin master

═══════════════════════════════════════════════════════════
```

---

## Usage Examples

```bash
# Simple update (will analyze conversation and prompt for details)
/kk6-update

# With context hint (helps focus extraction)
/kk6-update "Finished email template and created 2 social posts, got 3 RSVPs"

# After major session
/kk6-update "Big progress day - Facebook strategy complete, POST #6 generated"

# Quick task completion
/kk6-update "Marked 5 tasks done from this morning"
```

---

## Notes

- This command coordinates the update process but delegates actual file writing to an agent (safer)
- Always shows you what will change before making changes
- Commits to git automatically (but doesn't push - you control that)
- Can be run after any work session to keep tracking docs current
- Works with all KK6 tracking documents
