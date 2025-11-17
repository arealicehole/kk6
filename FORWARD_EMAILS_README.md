# Email Forwarder - Standalone Script

This script does exactly what the Pipedream workflow does, but you can run it locally whenever you want.

## What It Does

1. Fetches all received emails from Resend
2. Checks which ones haven't been forwarded yet (tracks in `forward-tracker.json`)
3. Forwards new emails directly to mail.kannakrew.com via SMTP
4. Updates tracker file so emails only get forwarded once

## How to Use

### First Time Setup:

```bash
cd C:\Users\figon\zeebot\kickback
npm install nodemailer
```

### Run It Anytime:

```bash
node forward-resend-emails.js
```

That's it! It will:
- Tell you how many emails it found
- Show you which ones are new
- Forward them one by one
- Save progress so you don't get duplicates

### Run It on a Schedule:

You can set up a Windows Task Scheduler task to run this every 5 minutes, or just run it manually whenever you want to check for new emails.

## Output Example

```
🚀 Starting email forwarder...

📋 Loaded 13 processed email IDs

📥 Fetching emails from Resend...
✅ Found 15 total emails in Resend

🆕 Found 2 new emails to forward

[1/2] Processing: New RSVP from Sleepy Cheefin
   From: sleepycheefin@example.com
   Date: 2025-01-15T12:34:56Z
   ✅ Forwarded successfully

[2/2] Processing: Vendor Application
   From: vendor@example.com
   Date: 2025-01-16T09:12:34Z
   ✅ Forwarded successfully

✅ Successfully forwarded 2 emails
📋 Total tracked emails: 15
```

## Files Created

- `forward-tracker.json` - Keeps track of which emails have been forwarded (don't delete this!)

## Why This Works vs. Curl

The Pipedream workflow uses the Resend SDK which handles authentication differently than raw curl commands. This script uses Node's `fetch` API which works the same way Pipedream does.
