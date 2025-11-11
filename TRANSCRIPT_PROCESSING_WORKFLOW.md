# TRANSCRIPT PROCESSING WORKFLOW

## When New Transcripts Arrive

Follow this checklist every time new transcripts are added to ensure nothing gets missed.

---

## STEP 1: INTAKE & RELEVANCE CHECK

### Actions:
1. **List all new files** in `raw/t/` folder
2. **Quick scan each transcript** (first 100-200 lines)
3. **Determine relevance:**
   - ✅ **KEEP** if mentions: KK6, Kickback, toy drive, event planning, vendors, marketing, Sojourner, dates/timeline
   - ❌ **DELETE** if: Completely unrelated (other projects, personal stuff, off-topic)
   - 🤔 **SKIM FURTHER** if unclear

### Output:
- List of kept transcripts with dates
- List of deleted transcripts (for record)

---

## STEP 2: EXTRACT KEY INFO FROM EACH TRANSCRIPT

For each relevant transcript, extract:

### 🎯 Decisions Made
- What was decided?
- Who made the decision?
- Does it change existing plans?

### 📋 Action Items
- What needs to be done?
- Who owns it?
- What's the deadline?

### 💰 Budget/Money Talk
- New expenses mentioned?
- Budget changes?
- Revenue opportunities?

### 👥 People & Contacts
- New contacts mentioned?
- Vendor names?
- Partner commitments?

### 📅 Timeline Changes
- Date changes?
- New deadlines?
- Schedule updates?

### ❓ Questions/Blockers
- What's unclear?
- What's blocking progress?
- What needs follow-up?

### 💡 New Ideas
- Content ideas?
- Marketing angles?
- Event features?

---

## STEP 3: UPDATE WORKING_NOTES.md

### Add new daily entry at top:
```markdown
## 2025-[DATE]

### Summary:
- [Brief overview of what was discussed in transcript(s)]
- [Key takeaways]

### Decisions Made:
- [List all decisions that were made]

### Action Items:
1. [New task] - Owner: [Name] - Due: [Date]
2. [New task] - Owner: [Name] - Due: [Date]

### Issues/Blockers:
- [Any new blockers or issues]

### Notes:
- [Additional relevant info]
- Processed transcript(s): [filenames]
```

### Update existing sections:
- **DECISIONS LOG** - Add any major decisions
- **CONTACT INFO COLLECTED** - Add new contacts
- **VENDOR COMMITMENTS** - Update vendor status
- **BOX LOCATIONS** - Add new locations
- **QUESTIONS TO RESOLVE** - Add new questions or mark resolved

---

## STEP 4: UPDATE TASK_TRACKER.md

### Add new tasks:
- Check which week they belong to (Week 1, 2, 3, 4)
- Add to appropriate section with:
  - Status: TODO/IN_PROGRESS/DONE
  - Task description
  - Owner
  - Due date
  - Notes

### Update existing tasks:
- Mark tasks as DONE if mentioned as complete
- Update deadlines if changed
- Add notes if new info provided

### Update trackers:
- **EMAIL OUTREACH TRACKER** - Add sent emails, responses
- **BOX PLACEMENT TRACKER** - Update placed boxes
- **CONTENT POSTING TRACKER** - Mark posted content
- **BUDGET TRACKER** - Add new expenses or revenue
- **BLOCKERS & ISSUES** - Update or resolve

---

## STEP 5: CHECK IF MASTER_REFERENCE NEEDS UPDATE

Ask: Does the transcript contain info that changes the master reference?

### If YES, note in WORKING_NOTES.md:
```markdown
⚠️ MASTER_REFERENCE UPDATE NEEDED:
- [What section needs updating]
- [What changed]
- [Link to transcript with info]
```

### Common updates:
- Event date/time/location changed
- Budget changed significantly
- New partners/vendors confirmed
- Marketing plan pivoted
- Timeline shifted

**DO NOT UPDATE MASTER_REFERENCE YET** - just flag it for batch update later

---

## STEP 6: CHECK IF NEW DELIVERABLES NEEDED

Does the transcript mention work that needs files created?

### Examples:
- "We need to create [X]" → Create design brief or template
- "Send email to [Y]" → Create email template if not exists
- "Make social post about [Z]" → Add to content calendar
- "Design [Thing]" → Create design brief in appropriate folder

### Actions:
- Create placeholder files in appropriate directories
- Add creation tasks to TASK_TRACKER.md
- Note in WORKING_NOTES.md

---

## STEP 7: UPDATE COMMUNICATIONS/OPERATIONS AS NEEDED

### If transcript mentions:

**Email sent/responses:**
- Update `communications/emails/` tracking sections
- Log in TASK_TRACKER email tracker

**Vendor commitments:**
- Update `operations/vendors/` (when created)
- Note in TASK_TRACKER vendor section

**Box placement:**
- Update `operations/boxes/` (when created)
- Note in TASK_TRACKER box tracker

**Budget expenses:**
- Update `operations/budget/` (when created)
- Note in TASK_TRACKER budget section

---

## STEP 8: IDENTIFY CONFLICTS OR CHANGES

### Check for:
- **Contradictions** with existing plans
- **Timeline conflicts** with current schedule
- **Budget concerns** vs. existing budget
- **Scope creep** - new features beyond original plan

### If found:
1. **Flag in WORKING_NOTES.md** under Issues/Blockers
2. **Add to TASK_TRACKER** under "BLOCKERS & ISSUES"
3. **Note decision needed** - highlight for team discussion

---

## STEP 9: FINAL CHECKLIST

Before marking transcript processing as complete:

- [ ] Transcript kept or deleted with reason noted
- [ ] Key info extracted (decisions, tasks, contacts, dates)
- [ ] WORKING_NOTES.md updated with new daily entry
- [ ] All sections of WORKING_NOTES updated (decisions, contacts, vendors, etc.)
- [ ] TASK_TRACKER.md updated (new tasks, completed tasks, trackers)
- [ ] Master reference update flagged if needed (don't edit yet)
- [ ] New deliverable files created or flagged
- [ ] Communications/operations docs updated as needed
- [ ] Conflicts/changes identified and flagged
- [ ] TodoWrite tool used to track transcript processing task

---

## QUICK REFERENCE: WHAT GOES WHERE

| Type of Info | Where It Goes | File Location |
|--------------|---------------|---------------|
| Daily activity log | WORKING_NOTES.md | Root |
| New tasks | TASK_TRACKER.md | Root |
| Decisions | WORKING_NOTES.md → Decisions Log | Root |
| Contacts | WORKING_NOTES.md → Contact Info | Root |
| Email tracking | TASK_TRACKER.md → Email Tracker | Root |
| Vendor updates | TASK_TRACKER.md → Vendor Tracker | Root |
| Box placement | TASK_TRACKER.md → Box Tracker | Root |
| Budget changes | TASK_TRACKER.md → Budget Tracker | Root |
| Content ideas | WORKING_NOTES.md → Content Ideas | Root |
| Master reference changes | Flag in WORKING_NOTES (update later) | Root |
| New email templates | Create file | communications/emails/ |
| New social posts | Create file | creative/social/ |
| New design briefs | Create file | creative/print/ |
| Box tracking docs | Create file | operations/boxes/ |
| Vendor docs | Create file | operations/vendors/ |
| Budget docs | Create file | operations/budget/ |

---

## AUTOMATION CHECKLIST (For Claude)

When processing transcripts, use this flow:

```
1. Read all new files in raw/t/
2. For each file:
   a. Scan for KK6 relevance
   b. If not relevant → delete and note
   c. If relevant → extract key info (checklist above)
3. Update WORKING_NOTES.md (new entry + all sections)
4. Update TASK_TRACKER.md (new tasks + all trackers)
5. Flag MASTER_REFERENCE updates if needed
6. Create new files in appropriate directories if needed
7. Use TodoWrite to track the transcript processing work
8. Summarize findings for user
```

---

## EXAMPLE OUTPUT TO USER

After processing transcripts, provide summary like this:

```
📋 TRANSCRIPT PROCESSING COMPLETE

TRANSCRIPTS PROCESSED:
✅ Kept 3 transcripts (relevant to KK6)
❌ Deleted 1 transcript (off-topic: farm project)

KEY FINDINGS:
🎯 Decisions Made:
- [Decision 1]
- [Decision 2]

📋 New Action Items:
- [Task 1] - Due: [Date]
- [Task 2] - Due: [Date]

💰 Budget Updates:
- [Expense 1]: $[amount]

👥 New Contacts:
- [Contact name]: [info]

⚠️ BLOCKERS/ISSUES:
- [Issue 1]

📝 DOCUMENTS UPDATED:
- WORKING_NOTES.md (new entry for [date])
- TASK_TRACKER.md ([X] new tasks added)
- [Other files updated]

⚠️ NEEDS ATTENTION:
- [Anything requiring user decision or action]
```

---

**Last Updated:** 2025-11-09
**Review:** Update this workflow if it's not working efficiently
