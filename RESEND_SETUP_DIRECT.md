# Resend Direct API Setup for Scheduled Emails

Created: 2025-11-10

## Overview

Claude sends emails directly to Resend API - no Netlify functions, no middleware, just direct API calls.

**Two Resend Accounts:**
- **Account #1:** kannakickback.com (website forms)
- **Account #2:** kannakrew.com (email outreach & scheduling)

---

## ✅ Already Done (You said 1-3 complete):

1. ✅ Created 2nd Resend account
2. ✅ Added DNS records for kannakrew.com
3. ✅ Got API key

---

## Step 4: Add API Key to Environment

**Windows (PowerShell):**

```powershell
# Add to your PowerShell profile for persistence
notepad $PROFILE

# Add this line:
$env:RESEND_API_KEY_KANNAKREW = "re_your_api_key_here"
```

**Or add temporarily for this session:**
```powershell
$env:RESEND_API_KEY_KANNAKREW = "re_your_api_key_here"
```

**Git Bash (what you're using now):**

```bash
# Add to ~/.bashrc for persistence
echo 'export RESEND_API_KEY_KANNAKREW="re_your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# Or just for this session:
export RESEND_API_KEY_KANNAKREW="re_your_api_key_here"
```

**Verify it's set:**
```bash
echo $RESEND_API_KEY_KANNAKREW
```

---

## How Claude Uses It

### Send Immediate Email

I'll run:
```bash
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY_KANNAKREW" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "admin@kannakrew.com",
    "to": "vendor@example.com",
    "subject": "KK6 Vendor Invitation",
    "html": "<p>Hi! We would love to have you at KannaKickback 6...</p>"
  }'
```

### Send Scheduled Email

Same but with `scheduledAt`:
```bash
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY_KANNAKREW" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "admin@kannakrew.com",
    "to": "vendor@example.com",
    "subject": "KK6 Reminder",
    "html": "<p>Just a reminder...</p>",
    "scheduledAt": "2025-11-15T17:00:00Z"
  }'
```

**Timestamp format:**
- ISO 8601: `YYYY-MM-DDTHH:mm:ssZ`
- Always UTC timezone (Z at end)
- Example: `2025-11-15T17:00:00Z` = Nov 15 at 10am Arizona time

---

## Testing Right Now

**Give me your API key and I'll test it:**

Tell me: `export RESEND_API_KEY_KANNAKREW="re_..."`

Or just run it yourself and then I can use it:
```bash
export RESEND_API_KEY_KANNAKREW="re_your_actual_key"
```

Then I'll send a test email to verify everything works!

---

## What You Can Tell Me

**Immediate send:**
- "Send email to vendor@example.com asking about booth space"

**Scheduled send:**
- "Send email to 10 vendors next Friday at 9am"
- "Schedule follow-up email for Monday morning"
- "Send reminder 2 days before the event"

**I'll handle:**
- Crafting professional email copy
- Converting "Friday 9am" to UTC timestamp
- Making direct Resend API call
- Confirming it's scheduled

---

## Resend Dashboard

Check scheduled emails at: https://resend.com/emails

Filter by:
- **Scheduled** - Emails waiting to send
- **Sent** - Already delivered
- **Failed** - Issues to fix

---

## Why This is Better

✅ No Netlify function to maintain
✅ No deployment needed
✅ Direct API = faster
✅ Fewer moving parts
✅ Same functionality

You were right - Netlify was overkill!

---

## What's Next

1. **Set the environment variable** (Step 4 above)
2. **Restart Claude Code** (so I can test email reading)
3. **I'll test Resend sending** with a test email
4. **Then you can use it for real outreach!**
