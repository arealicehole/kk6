# Resend Setup for Scheduled Emails (kannakrew.com)

Created: 2025-11-10

## Overview

This setup allows Claude to send scheduled emails from admin@kannakrew.com using Resend's API.

**You'll run TWO Resend accounts:**
- **Account #1:** kannakickback.com (existing - for website forms)
- **Account #2:** kannakrew.com (new - for email outreach and scheduling)

Both stay on free tier: 3,000 emails/month each.

---

## Step 1: Create New Resend Account

1. Go to https://resend.com/signup
2. Sign up with a **different email** than your first Resend account
   - Suggestion: Use a Gmail alias like `youremail+kannakrew@gmail.com`
3. Verify your email

---

## Step 2: Add kannakrew.com Domain

1. In Resend dashboard, click **Domains** → **Add Domain**
2. Enter: `kannakrew.com`
3. Resend will show DNS records to add

---

## Step 3: Add DNS Records

**Add these to your kannakrew.com DNS (wherever it's hosted):**

### SPF Record
```
Type: TXT
Name: @
Value: v=spf1 include:amazonses.com ~all
TTL: 3600
```

### DKIM Record
```
Type: TXT
Name: resend._domainkey
Value: [Resend will provide this - copy from dashboard]
TTL: 3600
```

**Note:** Keep your existing MX records pointing to SiteGround - don't change them!

---

## Step 4: Get API Key

1. In Resend dashboard, go to **API Keys**
2. Click **Create API Key**
3. Name it: `KannaKrew Email Outreach`
4. Permission: **Sending access**
5. Copy the API key (starts with `re_...`)

---

## Step 5: Add to Netlify

Since your website is at `arealicehole/kk6-prod`, we're setting up the Netlify function there:

1. Go to https://app.netlify.com
2. Find your site (kannakickback.com)
3. Go to **Site settings** → **Environment variables**
4. Add new variable:
   - **Key:** `RESEND_API_KEY_KANNAKREW`
   - **Value:** `re_...` (your API key from Step 4)
   - **Scopes:** Check "Functions"
5. Save

---

## Step 6: Deploy Function

The function is already created at:
```
website/netlify/functions/send-email-scheduled.js
```

Push to GitHub to deploy:

```bash
cd C:/Users/figon/zeebot/kickback/website
git add netlify/functions/send-email-scheduled.js
git commit -m "Add Resend scheduled email function for kannakrew.com"
git push origin master
```

Netlify will auto-deploy (takes ~1 minute).

---

## Step 7: Verify Domain in Resend

1. Wait 5-15 minutes for DNS to propagate
2. In Resend dashboard, click **Verify** next to kannakrew.com
3. Should show ✅ Verified

---

## How Claude Uses It

### Send Immediate Email
I call:
```
POST https://kannakickback.com/.netlify/functions/send-email-scheduled
{
  "to": "vendor@example.com",
  "subject": "KK6 Vendor Invitation",
  "body": "<p>Hello! We'd love to have you at KannaKickback 6...</p>"
}
```

### Send Scheduled Email
I call with `scheduledAt`:
```
POST https://kannakickback.com/.netlify/functions/send-email-scheduled
{
  "to": "vendor@example.com",
  "subject": "KK6 Reminder",
  "body": "<p>Just a reminder that KannaKickback 6 is next week...</p>",
  "scheduledAt": "2025-11-15T14:00:00Z"
}
```

The `scheduledAt` timestamp format:
- **ISO 8601 format:** `YYYY-MM-DDTHH:mm:ssZ`
- **Timezone:** Always use UTC (Z at the end)
- **Example:** "2025-11-15T14:00:00Z" = Nov 15, 2025 at 2:00 PM UTC (7:00 AM Arizona time)

---

## Testing

After setup, test with:

```bash
curl -X POST https://kannakickback.com/.netlify/functions/send-email-scheduled \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your-test-email@gmail.com",
    "subject": "Test from Resend",
    "body": "<p>This is a test email from admin@kannakrew.com</p>"
  }'
```

Should return:
```json
{
  "success": true,
  "message": "Email sent immediately",
  "id": "..."
}
```

---

## Resend Free Tier Limits

**Per account:**
- 3,000 emails/month
- 100 emails/day
- Unlimited scheduled emails (counts against monthly limit when sent)

**Both accounts combined:**
- 6,000 emails/month total
- Plenty for KannaKickback outreach

---

## Troubleshooting

**"Domain not verified":**
- Wait 15 minutes for DNS propagation
- Check DNS records are correct (use https://mxtoolbox.com)

**"API key invalid":**
- Make sure environment variable name is exactly: `RESEND_API_KEY_KANNAKREW`
- Redeploy site after adding env var

**"Email not sending":**
- Check Resend dashboard → Emails tab for delivery status
- Check Netlify function logs for errors

---

## What You Have Now

✅ SiteGround IMAP/SMTP → Claude reads your inbox
✅ Resend #1 (kannakickback.com) → Website contact forms
✅ Resend #2 (kannakrew.com) → Claude sends outreach emails with scheduling

**Claude can now:**
- Read your admin@kannakrew.com inbox (via MCP email client)
- Send immediate emails from admin@kannakrew.com (via Resend)
- Schedule emails for future sending (via Resend API)

---

## Example Usage

**You say:** "Send vendor outreach emails to these 10 dispensaries on November 15th at 9am Arizona time"

**Claude does:**
1. Crafts professional email
2. Calls Resend function with `scheduledAt: "2025-11-15T16:00:00Z"` (9am AZ = 4pm UTC)
3. Emails get queued in Resend
4. Resend sends them automatically on Nov 15 at 9am AZ

**You say:** "Check if any vendors replied"

**Claude does:**
1. Reads inbox via MCP email client
2. Searches for emails from dispensary domains
3. Summarizes responses
