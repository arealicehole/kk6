# No-Code Solution: Resend Email Forwarding with Pipedream

**Perfect for non-developers or quick testing**
**Setup Time:** 15-30 minutes
**Cost:** FREE (100K invocations/month)

---

## What is Pipedream?

Pipedream is a free workflow automation platform (like Zapier, but better for developers and free). It lets you connect APIs without writing code.

**Why Pipedream for this project:**
- Free tier is VERY generous (100K invocations/month)
- Built-in Resend integration
- Easy email sending via SMTP
- Automatic webhook hosting (no deployment needed)
- Can edit code if you want, but not required

---

## Step-by-Step Setup Guide

### Step 1: Create Pipedream Account

1. Go to https://pipedream.com/
2. Click "Sign up free"
3. Use Google/GitHub login (fastest)
4. No credit card required

### Step 2: Create New Workflow

1. Click "New Workflow" in dashboard
2. Choose "Start from scratch"
3. Name it: "Resend Email Forwarder"

### Step 3: Set Up HTTP Trigger (Webhook)

1. **Trigger Type:** Select "HTTP / Webhook"
2. **Event:** Select "New Requests (POST)"
3. **Copy the webhook URL:**
   - Will look like: `https://xyz.m.pipedream.net`
   - Save this URL - you'll need it for Resend

**Test the trigger:**
- Pipedream shows "Waiting for test event"
- We'll test after configuring Resend

### Step 4: Add Resend Account Connection

1. Click "+ Add Step"
2. Search for "Resend"
3. Select "Resend" app
4. Click "Connect Account"
5. Enter your Resend API key:
   - Get from: https://resend.com/api-keys
   - Click "Create API Key" if needed
   - Copy key (starts with `re_`)
   - Paste into Pipedream

### Step 5: Add Code Step - Parse Email ID

1. Click "+ Add Step"
2. Select "Node.js"
3. Name it: "Extract Email Data"
4. Paste this code:

```javascript
export default defineComponent({
  async run({ steps, $ }) {
    // Get email ID from webhook
    const emailId = steps.trigger.event.body.data.email_id;
    const eventType = steps.trigger.event.body.type;

    // Only process email.received events
    if (eventType !== 'email.received') {
      $.export("skip", true);
      return { skip: true, reason: `Event type is ${eventType}, not email.received` };
    }

    // Export for next steps
    $.export("email_id", emailId);
    $.export("metadata", steps.trigger.event.body.data);

    return {
      email_id: emailId,
      from: steps.trigger.event.body.data.from,
      to: steps.trigger.event.body.data.to,
      subject: steps.trigger.event.body.data.subject,
    };
  },
});
```

### Step 6: Add Resend - Get Email Content

1. Click "+ Add Step"
2. Search "Resend"
3. Select "Retrieve Email" action
4. Configure:
   - **Account:** Select your connected Resend account
   - **Email ID:** Click "Use data from previous step"
     - Select: `steps.extract_email_data.$return_value.email_id`

**This retrieves the full email body from Resend**

### Step 7: Add Code Step - Format Email for Forwarding

1. Click "+ Add Step"
2. Select "Node.js"
3. Name it: "Format Forwarded Email"
4. Paste this code:

```javascript
export default defineComponent({
  async run({ steps, $ }) {
    const emailData = steps.resend_retrieve_email.$return_value;
    const metadata = steps.extract_email_data.$return_value;

    // Create forwarding header
    const forwardingHeader = `
      <div style="background: #f0f0f0; padding: 10px; margin-bottom: 20px; border-left: 4px solid #007bff;">
        <strong>Forwarded Email</strong><br>
        <strong>From:</strong> ${emailData.from}<br>
        <strong>To:</strong> ${emailData.to}<br>
        <strong>Subject:</strong> ${emailData.subject}<br>
        <strong>Date:</strong> ${new Date().toLocaleString()}<br>
      </div>
    `;

    const forwardingHeaderText = `
========================================
FORWARDED EMAIL
========================================
From: ${emailData.from}
To: ${emailData.to}
Subject: ${emailData.subject}
========================================

`;

    // Prepare email content
    const htmlBody = forwardingHeader + (emailData.html || emailData.text || 'No content');
    const textBody = forwardingHeaderText + (emailData.text || 'No content');

    $.export("html", htmlBody);
    $.export("text", textBody);
    $.export("subject", emailData.subject);
    $.export("original_from", emailData.from);

    return {
      html: htmlBody,
      text: textBody,
      subject: emailData.subject,
      from: emailData.from,
    };
  },
});
```

### Step 8: Add Email Step - Send via SMTP

1. Click "+ Add Step"
2. Search "Email"
3. Select "Send Email" action (by Pipedream)
4. Configure SMTP settings:

**SMTP Configuration:**
```
Host: mail.kannakrew.com
Port: 465
Secure: YES (toggle on)
Username: admin@kannakrew.com
Password: your_webmail_password
```

**Email Configuration:**
```
From: admin@kannakrew.com
To: admin@kannakrew.com
Subject: {{ steps.format_forwarded_email.$return_value.subject }}
Text: {{ steps.format_forwarded_email.$return_value.text }}
HTML: {{ steps.format_forwarded_email.$return_value.html }}
Reply-To: {{ steps.format_forwarded_email.$return_value.from }}
```

**Important:** Use the "Use data from previous step" button to reference the formatted email data.

### Step 9: Test the Workflow

1. Click "Deploy" to save workflow
2. Copy your webhook URL from Step 3
3. Go to Resend Dashboard → Webhooks
4. Create new webhook:
   - URL: Your Pipedream webhook URL
   - Events: Select `email.received`
   - Save
5. Send test email to your domain (e.g., admin@kannakrew.com)
6. Check Pipedream dashboard for execution logs
7. Check your webmail for forwarded email

---

## Alternative: Simpler Version (No Code at All)

If the above seems too complex, here's an EVEN SIMPLER version using Pipedream's built-in steps:

### Simplified Workflow:

1. **Trigger:** HTTP/Webhook (same as above)

2. **Step 1 - Filter Events:**
   - Add "Filter" step
   - Condition: `steps.trigger.event.body.type equals email.received`
   - This skips non-email events

3. **Step 2 - Resend Get Email:**
   - Action: Resend → Retrieve Email
   - Email ID: `steps.trigger.event.body.data.email_id`

4. **Step 3 - Send Email:**
   - Action: Email → Send Email
   - From: admin@kannakrew.com
   - To: admin@kannakrew.com
   - Subject: `steps.resend_retrieve_email.$return_value.subject`
   - HTML: `steps.resend_retrieve_email.$return_value.html`
   - Reply-To: `steps.resend_retrieve_email.$return_value.from`

**That's it!** Only 3 steps, no code.

---

## Advanced: Handle Attachments

If you need to forward attachments too, add these steps:

### After "Get Email Content" step:

**Step A - Get Attachments:**

1. Add "Node.js" step
2. Name: "Retrieve Attachments"
3. Code:

```javascript
export default defineComponent({
  async run({ steps, $ }) {
    const metadata = steps.extract_email_data.$return_value.metadata;
    const attachments = metadata.attachments || [];

    if (attachments.length === 0) {
      $.export("has_attachments", false);
      return { has_attachments: false };
    }

    // Get Resend API client
    const { Resend } = require('resend');
    const resend = new Resend(this.resend.$auth.api_key);

    const emailId = steps.extract_email_data.$return_value.email_id;
    const attachmentData = [];

    for (const attachment of attachments) {
      try {
        const data = await resend.emails.receiving.getAttachment(
          emailId,
          attachment.id
        );

        attachmentData.push({
          filename: attachment.filename,
          content: data.content, // Already base64
          contentType: attachment.content_type,
        });
      } catch (error) {
        console.error(`Failed to get attachment: ${attachment.filename}`, error);
      }
    }

    $.export("attachments", attachmentData);
    $.export("has_attachments", true);

    return {
      has_attachments: true,
      attachments: attachmentData,
    };
  },
});
```

**Step B - Update Send Email Step:**

In the "Send Email" step, add:
- **Attachments:** `{{ steps.retrieve_attachments.$return_value.attachments }}`

---

## Configuration for MCP Email Tool

Once emails are forwarding to webmail, configure MCP tool:

```json
{
  "smtp": {
    "host": "mail.kannakrew.com",
    "port": 465,
    "secure": true,
    "auth": {
      "user": "admin@kannakrew.com",
      "pass": "your_password"
    }
  },
  "imap": {
    "host": "mail.kannakrew.com",
    "port": 993,
    "secure": true,
    "auth": {
      "user": "admin@kannakrew.com",
      "pass": "your_password"
    }
  }
}
```

**MCP tool will now:**
- Read emails from webmail IMAP (including forwarded ones)
- Send emails via webmail SMTP
- See ALL emails in one place

---

## Testing Checklist

- [ ] Pipedream workflow created and deployed
- [ ] Webhook URL copied from Pipedream
- [ ] Webhook configured in Resend dashboard
- [ ] Resend account connected to Pipedream
- [ ] SMTP credentials correct in Pipedream
- [ ] Test email sent to admin@kannakrew.com
- [ ] Workflow executed successfully in Pipedream
- [ ] Email forwarded to webmail
- [ ] Email visible in webmail inbox
- [ ] MCP tool can read forwarded email
- [ ] Reply-to header is correct (replies go to original sender)

---

## Monitoring and Troubleshooting

### View Execution Logs:

1. Go to Pipedream dashboard
2. Click on your workflow
3. Click "Events" tab
4. See all webhook executions with full logs

### Common Issues:

**Webhook not receiving events:**
- Check webhook URL is correct in Resend
- Verify webhook event is `email.received`
- Check Resend webhook delivery logs

**Email not forwarding:**
- Check SMTP credentials in Pipedream
- Verify SMTP port (465 with secure=true)
- Check execution logs in Pipedream for errors
- Test SMTP connection separately

**Attachments not working:**
- Ensure attachment retrieval code is added
- Check attachment size limits
- Verify base64 encoding is correct

**Workflow timing out:**
- Large attachments may cause timeouts
- Consider adding timeout handling
- Split attachment processing into separate workflow

---

## Pipedream Features You'll Love

### 1. Built-in Testing:
- Test each step individually
- See output data from each step
- Debug easily with logs

### 2. Version Control:
- Every workflow save creates a version
- Roll back to previous versions
- No lost work

### 3. Error Alerts:
- Get email when workflow fails
- Configure retry policies
- Automatic error logging

### 4. Free Tier Limits:
- 100K invocations/month (plenty!)
- 30-second timeout per execution
- 512MB memory

### 5. No Deployment Needed:
- Webhook instantly available
- No server management
- No downtime

---

## Cost Comparison

### Pipedream FREE Tier:
- 100K invocations/month
- = 3,333 emails per day
- = 139 emails per hour
- **Perfect for most use cases**

### If You Exceed Free Tier:
- Upgrade to Developer plan: $19/month
- 500K invocations/month
- Or deploy your own webhook (see main guide)

---

## Alternative No-Code Platforms

### Zapier
**Pros:** Very beginner-friendly, huge app ecosystem
**Cons:** Free tier only 100 tasks/month (not enough)
**Cost:** $20/month for 750 tasks

**Setup:**
1. Trigger: Webhooks by Zapier → Catch Hook
2. Action 1: Code by Zapier → Run JavaScript (to parse webhook)
3. Action 2: Email by Zapier → Send Outbound Email

### Make.com (formerly Integromat)
**Pros:** Visual workflow builder, good free tier
**Cons:** Steeper learning curve than Zapier
**Cost:** Free for 1,000 operations/month

**Setup:**
1. Trigger: Webhooks → Custom Webhook
2. Module 1: HTTP → Make a Request (get email from Resend)
3. Module 2: Email → Send an Email

### n8n (Self-Hosted)
**Pros:** Open source, unlimited executions
**Cons:** Must self-host (requires technical knowledge)
**Cost:** FREE (self-hosted) or $20/month (cloud)

---

## Pro Tips

### 1. Use Pipedream Environment Variables:
Instead of hardcoding email addresses:
```javascript
const forwardTo = process.env.FORWARD_TO_EMAIL;
```

Add in workflow settings → Environment.

### 2. Add Rate Limiting:
If you get lots of emails, add a delay:
```javascript
await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
```

### 3. Filter Spam:
Add a step to check sender:
```javascript
const spamDomains = ['spam.com', 'junk.com'];
const senderDomain = steps.trigger.event.body.data.from.split('@')[1];

if (spamDomains.includes(senderDomain)) {
  $.flow.exit("Spam detected, skipping");
}
```

### 4. Log to Google Sheets:
Add a step to log all forwarded emails:
- Action: Google Sheets → Add Row
- Track: Date, From, To, Subject, Status

### 5. Send Slack Notifications:
Get notified when emails are forwarded:
- Action: Slack → Send Message to Channel
- Message: `New email from ${from}: ${subject}`

---

## Upgrade Path

When you outgrow Pipedream free tier:

**Option 1:** Upgrade Pipedream ($19/month)
**Option 2:** Deploy own webhook (see main guide)
**Option 3:** Switch to self-hosted n8n (free, unlimited)

---

## Support and Resources

### Pipedream:
- Documentation: https://pipedream.com/docs
- Community: https://pipedream.com/community
- Support: support@pipedream.com

### Resend:
- Documentation: https://resend.com/docs
- Discord: https://resend.com/discord

### This Project:
- Main guide: See `resend-email-configuration-solution.md`
- Code version: See `resend-webhook-implementation.js`

---

## Quick Start Checklist

Follow this order for fastest setup:

**Day 1 (30 minutes):**
- [ ] Create Pipedream account
- [ ] Create new workflow
- [ ] Set up HTTP webhook trigger
- [ ] Copy webhook URL

**Day 2 (30 minutes):**
- [ ] Connect Resend account to Pipedream
- [ ] Add email parsing steps
- [ ] Add email forwarding step
- [ ] Deploy workflow

**Day 3 (15 minutes):**
- [ ] Configure webhook in Resend dashboard
- [ ] Send test email
- [ ] Verify forwarding works
- [ ] Check webmail inbox

**Day 4 (15 minutes):**
- [ ] Configure MCP email tool
- [ ] Test reading emails
- [ ] Test sending emails
- [ ] Document setup

**Total time:** ~1.5 hours
**No coding required!**

---

## Next Steps

Once this is working:

1. **Add monitoring:** Set up alerts for failures
2. **Improve formatting:** Customize forwarded email appearance
3. **Handle edge cases:** Spam filtering, size limits, etc.
4. **Document for team:** Share how it works
5. **Plan for scale:** Monitor usage, plan for growth

---

## Conclusion

**Pipedream is perfect for:**
- Non-developers
- Quick prototyping
- Testing before building custom solution
- Low to medium email volumes
- Budget-conscious projects

**You should build custom webhook if:**
- Sending >100K emails/month
- Need sub-second latency
- Want full control over infrastructure
- Have complex business logic
- Already have hosting infrastructure

For most use cases, **Pipedream is the best choice** - it's free, fast to set up, and requires zero infrastructure management.

---

**Questions?**
- Check main guide for technical details
- Visit Pipedream community for workflow help
- Test locally with ngrok if needed (see main guide)
