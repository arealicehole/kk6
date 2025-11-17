# Complete Solution: Resend Email Configuration for kannakrew.com

**Research Date:** 2025-11-17
**Domain:** kannakrew.com
**Current Email:** admin@kannakrew.com

---

## Executive Summary

After comprehensive research, here's the GOOD NEWS: **Resend DOES support email forwarding** through their Inbound Email feature and API. However, it requires webhook + API integration, not traditional email forwarding.

**The Problem:**
- Resend receives emails (MX records point to them)
- Emails visible in Resend dashboard
- User can't see them in webmail (mail.kannakrew.com)
- MCP tool can't see them via IMAP

**The Solution:**
We need to implement a webhook-based forwarding system that automatically forwards all emails received by Resend to your webmail server via SMTP.

---

## Understanding Resend's Inbound Email System

### How Resend Receives Emails:

1. **MX Record Points to Resend:**
   - `kannakrew.com MX 9 inbound-smtp.us-east-1.amazonaws.com`
   - All emails to `*@kannakrew.com` route to Resend

2. **Resend Processes Email:**
   - Parses content, headers, attachments
   - Stores email in Resend dashboard
   - Sends webhook notification to your endpoint

3. **Webhook Contains Metadata ONLY:**
   - Email ID, sender, recipient, subject, timestamp
   - Does NOT include email body or attachments
   - Designed for serverless environments with size limits

4. **Full Content Retrieved via API:**
   - Use email ID from webhook to call Receiving API
   - Fetches HTML body, plain text, headers
   - Separate Attachments API for files

---

## Recommended Architecture

### Option 1: Webhook-Based Forwarding (RECOMMENDED)

**Flow:**
```
Email sent to admin@kannakrew.com
         ↓
Resend MX receives email
         ↓
Resend stores email + sends webhook
         ↓
Your webhook endpoint receives notification
         ↓
Endpoint calls Resend Receiving API (get email body)
         ↓
Endpoint calls Resend Attachments API (if attachments exist)
         ↓
Endpoint sends email via SMTP to mail.kannakrew.com
         ↓
Email appears in webmail
         ↓
MCP tool can read via IMAP
```

**Components Needed:**
1. Webhook endpoint (can be hosted anywhere)
2. Resend API integration
3. SMTP client to forward to mail.kannakrew.com
4. MCP tool configured for webmail IMAP/SMTP

**Pros:**
- All emails visible in webmail
- MCP tool works seamlessly
- Form submissions continue working
- Full control over forwarding logic

**Cons:**
- Requires hosting a webhook endpoint
- Slight delay in email delivery (usually <5 seconds)
- Need to handle failures/retries

---

### Option 2: MCP Tool with Dual Email Systems (SIMPLER, BUT LIMITED)

**Flow:**
```
Form submissions → Resend API → Resend Dashboard
                                        ↓
                         User manually checks Resend dashboard

Regular emails → MX to mail.kannakrew.com → Webmail → MCP tool
```

**MX Records:**
```
kannakrew.com MX 10 mail.kannakrew.com
kannakrew.com MX 20 inbound-smtp.us-east-1.amazonaws.com (backup)
```

**MCP Configuration:**
- SMTP: mail.kannakrew.com:465 (for sending)
- IMAP: mail.kannakrew.com:993 (for reading)

**Pros:**
- No webhook development needed
- Simple configuration
- MCP tool works immediately

**Cons:**
- Form submissions only visible in Resend dashboard
- Must check two places for emails
- Resend only receives emails if primary server down

---

### Option 3: Subdomain Strategy (CLEAN SEPARATION)

**Flow:**
```
forms@kannakrew.com     → MX to Resend → Webhook forwarding
admin@kannakrew.com     → MX to mail.kannakrew.com → Webmail
support@kannakrew.com   → MX to mail.kannakrew.com → Webmail
```

**MX Records:**
```
forms.kannakrew.com     MX 9 inbound-smtp.us-east-1.amazonaws.com
kannakrew.com           MX 10 mail.kannakrew.com
```

**Website Forms:** Submit to `forms@kannakrew.com`

**Pros:**
- Clean separation of concerns
- No forwarding needed for forms
- Regular email works normally
- Easy to understand

**Cons:**
- Forms still need webhook forwarding to appear in webmail
- Requires updating website form code

---

## RECOMMENDED SOLUTION: Option 1 Implementation

### Step 1: Configure Resend Inbound Domain

1. **Add Custom Domain in Resend Dashboard:**
   - Go to Receiving tab → Add Domain
   - Enter: `kannakrew.com`

2. **Add MX Record to DNS:**
   ```
   Type: MX
   Name: @
   Value: inbound-smtp.us-east-1.amazonaws.com
   Priority: 9
   TTL: 300 (or Auto)
   ```

3. **Verify Domain:**
   - Wait for DNS propagation (5-30 minutes)
   - Resend will verify MX record automatically

### Step 2: Create Webhook Endpoint

You'll need to host a webhook endpoint that:
1. Receives `email.received` events from Resend
2. Fetches full email content via Resend API
3. Forwards email via SMTP to mail.kannakrew.com

**Hosting Options:**
- Vercel Serverless Function (recommended, free tier)
- Cloudflare Workers (free tier)
- Railway.app (free tier)
- Your own server
- DigitalOcean Functions

**Sample Webhook Code (Node.js/Next.js):**

```javascript
// app/api/webhooks/resend-inbound/route.js
import { Resend } from 'resend';
import nodemailer from 'nodemailer';

const resend = new Resend(process.env.RESEND_API_KEY);

// Configure SMTP transport for webmail
const transport = nodemailer.createTransport({
  host: 'mail.kannakrew.com',
  port: 465,
  secure: true,
  auth: {
    user: 'admin@kannakrew.com',
    pass: process.env.WEBMAIL_PASSWORD,
  },
});

export async function POST(request) {
  try {
    // 1. Parse webhook event
    const event = await request.json();

    if (event.type !== 'email.received') {
      return Response.json({ received: true });
    }

    const emailId = event.data.email_id;

    // 2. Retrieve full email content from Resend
    const emailData = await resend.emails.receiving.get(emailId);

    // 3. Handle attachments if present
    let attachments = [];
    if (event.data.attachments && event.data.attachments.length > 0) {
      for (const attachment of event.data.attachments) {
        const attachmentData = await resend.emails.receiving.getAttachment(
          emailId,
          attachment.id
        );
        attachments.push({
          filename: attachment.filename,
          content: Buffer.from(attachmentData.content, 'base64'),
          contentType: attachment.content_type,
        });
      }
    }

    // 4. Forward email via SMTP
    await transport.sendMail({
      from: `"Forwarded Email" <admin@kannakrew.com>`,
      to: 'admin@kannakrew.com',
      subject: emailData.subject,
      text: emailData.text,
      html: emailData.html,
      headers: {
        'X-Original-From': emailData.from,
        'X-Original-To': emailData.to,
        'X-Forwarded-By': 'Resend Webhook',
      },
      attachments: attachments,
    });

    console.log(`Forwarded email: ${emailId}`);
    return Response.json({ success: true });

  } catch (error) {
    console.error('Webhook error:', error);
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
```

**Environment Variables Needed:**
```env
RESEND_API_KEY=re_xxxxxxxxxxxx
WEBMAIL_PASSWORD=your_webmail_password
```

### Step 3: Configure Webhook in Resend

1. **Get Your Webhook URL:**
   - Deploy your endpoint first
   - Example: `https://your-site.vercel.app/api/webhooks/resend-inbound`

2. **Add Webhook in Resend Dashboard:**
   - Go to Webhooks → Create Webhook
   - URL: Your endpoint URL
   - Events: Select `email.received`
   - Save webhook

3. **Test Webhook:**
   - Send test email to admin@kannakrew.com
   - Check Resend dashboard for webhook delivery status
   - Verify email appears in webmail

### Step 4: Configure MCP Email Tool

**Keep Current Configuration:**
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

**Why:** With webhook forwarding, emails will arrive in webmail, so IMAP will see them normally.

### Step 5: Alternative - Send via Resend SMTP

**If you want MCP tool to send via Resend:**

```json
{
  "smtp": {
    "host": "smtp.resend.com",
    "port": 465,
    "secure": true,
    "auth": {
      "user": "resend",
      "pass": "re_xxxxxxxxxxxx"
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

**Benefits:**
- Send via Resend (better deliverability)
- Receive via webmail IMAP (see all emails)

---

## Quick Start: Minimal Implementation

If you want to get started quickly without hosting a webhook:

### Use Resend's Built-in Forward Feature (via API)

Resend doesn't have a UI-based forwarding feature, but you can use services like:

**Option A: Zapier/Make.com (No-Code Solution)**

1. **Create Zapier Zap:**
   - Trigger: Resend Webhook → Email Received
   - Action 1: Resend → Get Email Content
   - Action 2: Email by Zapier → Send Email
   - To: admin@kannakrew.com (via SMTP to mail.kannakrew.com)

2. **Configure Webhook:**
   - Use Zapier's webhook URL in Resend

3. **Done:** Emails auto-forward without coding

**Option B: Pipedream (Free Workflow Automation)**

1. **Create Pipedream Workflow:**
   - Source: HTTP API (for Resend webhook)
   - Step 1: Resend → Retrieve Email
   - Step 2: Email → Send Email (SMTP)

2. **Get Workflow URL:** Use as Resend webhook endpoint

3. **No hosting needed:** Pipedream hosts for free

---

## Testing Checklist

### Before Going Live:

- [ ] MX record points to Resend (DNS propagated)
- [ ] Domain verified in Resend dashboard
- [ ] Webhook endpoint deployed and accessible
- [ ] Webhook configured in Resend with correct URL
- [ ] Environment variables set (API key, webmail password)
- [ ] Test email sent to admin@kannakrew.com
- [ ] Email appears in Resend dashboard
- [ ] Webhook receives event (check logs)
- [ ] Email forwarded to webmail successfully
- [ ] Email visible in webmail inbox
- [ ] MCP tool can read email via IMAP
- [ ] MCP tool can send email via SMTP
- [ ] Attachments forward correctly
- [ ] Website forms still work

### After Going Live:

- [ ] Monitor webhook delivery status in Resend
- [ ] Check webmail for any missing emails
- [ ] Test reply-to headers are correct
- [ ] Verify spam filtering isn't breaking forwarding
- [ ] Set up alerts for webhook failures

---

## Resend API Reference

### Authentication
All API requests require Bearer token:
```bash
Authorization: Bearer re_xxxxxxxxxxxx
```

### List Received Emails
```bash
GET https://api.resend.com/emails/receiving
```

**Parameters:**
- `limit` (optional): Number of emails (1-100, default: 20)
- `after` (optional): Email ID for pagination
- `before` (optional): Email ID for pagination

**Response:**
```json
{
  "object": "list",
  "has_more": false,
  "data": [
    {
      "id": "4ef9a417-02e9-4d39-ad75-9611e0fcc33c",
      "to": ["admin@kannakrew.com"],
      "from": "customer@example.com",
      "subject": "Question about order",
      "created_at": "2025-11-17T20:30:00Z",
      "attachments": []
    }
  ]
}
```

### Retrieve Received Email
```bash
GET https://api.resend.com/emails/receiving/{email_id}
```

**Response:**
```json
{
  "id": "4ef9a417-02e9-4d39-ad75-9611e0fcc33c",
  "to": ["admin@kannakrew.com"],
  "from": "customer@example.com",
  "subject": "Question about order",
  "html": "<p>Email HTML body</p>",
  "text": "Email plain text body",
  "headers": {
    "Return-Path": "<customer@example.com>",
    "Date": "Mon, 17 Nov 2025 20:30:00 +0000"
  },
  "created_at": "2025-11-17T20:30:00Z"
}
```

### Retrieve Attachment
```bash
GET https://api.resend.com/emails/receiving/{email_id}/attachments/{attachment_id}
```

**Response:**
```json
{
  "id": "abc123",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 52428,
  "download_url": "https://..."
}
```

### Send Email (for Forwarding)
```bash
POST https://api.resend.com/emails
```

**Body:**
```json
{
  "from": "admin@kannakrew.com",
  "to": ["admin@kannakrew.com"],
  "subject": "Forwarded: Original Subject",
  "html": "<p>Email content</p>",
  "text": "Email content",
  "attachments": [
    {
      "filename": "file.pdf",
      "content": "base64_encoded_content"
    }
  ]
}
```

---

## Resend SMTP Configuration

If you want to use Resend for sending emails:

**SMTP Settings:**
```
Host: smtp.resend.com
Port: 465 (SMTPS/SSL)
   OR 587 (STARTTLS)
   OR 25 (STARTTLS)
Username: resend
Password: re_xxxxxxxxxxxx (your API key)
```

**Create API Key:**
1. Go to Resend Dashboard → API Keys
2. Click "Create API Key"
3. Name: "SMTP Access"
4. Copy key (starts with `re_`)
5. Use as SMTP password

---

## MX Record Strategies

### Strategy 1: Resend Primary (Current)

```
kannakrew.com MX 9 inbound-smtp.us-east-1.amazonaws.com
```

**Result:** All emails go to Resend first
**Best for:** Webhook forwarding setup
**Requires:** Webhook to forward to webmail

### Strategy 2: Webmail Primary

```
kannakrew.com MX 10 mail.kannakrew.com
kannakrew.com MX 20 inbound-smtp.us-east-1.amazonaws.com
```

**Result:** Emails go to webmail first, Resend as backup
**Best for:** Simple setup without webhooks
**Problem:** Form submissions won't work (Resend needs to receive)

### Strategy 3: Subdomain Split

```
forms.kannakrew.com     MX 9 inbound-smtp.us-east-1.amazonaws.com
kannakrew.com           MX 10 mail.kannakrew.com
```

**Result:** Form emails to forms@, everything else to webmail
**Best for:** Clean separation
**Requires:** Update website forms to use forms@kannakrew.com

---

## Troubleshooting

### Email Not Appearing in Resend Dashboard

**Check:**
- MX record DNS propagation: `dig kannakrew.com MX`
- Domain verified in Resend dashboard
- Email not caught by sender's spam filter
- Resend account limits not exceeded

### Webhook Not Receiving Events

**Check:**
- Webhook URL is publicly accessible (use ngrok for local testing)
- Webhook configured with `email.received` event
- Endpoint returns 200 status code
- Check Resend webhook delivery logs
- Verify endpoint handles POST requests

### Emails Not Forwarding to Webmail

**Check:**
- SMTP credentials correct for mail.kannakrew.com
- Port 465 accessible (firewall rules)
- Webmail server accepting SMTP connections
- Check webhook logs for SMTP errors
- Verify webmail not marking as spam

### MCP Tool Can't See Emails

**Check:**
- IMAP credentials correct
- IMAP connecting to mail.kannakrew.com:993
- Emails successfully forwarded to webmail
- IMAP inbox refresh delay
- Check webmail spam/junk folder

### Attachments Not Forwarding

**Check:**
- Attachment API calls in webhook code
- Base64 encoding correct
- Attachment size limits (webmail server)
- Content-Type headers preserved
- Memory limits in serverless function

---

## Cost Analysis

### Resend Pricing:
- **Free Tier:** 100 emails/day, 3,000/month
- **Paid:** Starting at $20/month for 50,000 emails
- **Inbound:** Included in all plans
- **Webhooks:** Unlimited, free

### Webhook Hosting:
- **Vercel:** Free tier (100GB bandwidth, 100K requests)
- **Cloudflare Workers:** Free tier (100K requests/day)
- **Pipedream:** Free tier (10K invocations/month)
- **Railway:** Free tier ($5 credit/month)

### Webmail Hosting:
- **Current:** Already have mail.kannakrew.com
- **No additional cost**

**Total Monthly Cost:** $0-20 (depending on email volume)

---

## Security Considerations

### Webhook Security:

1. **Verify Webhook Signature:**
   ```javascript
   // Resend includes signature in headers
   const signature = request.headers.get('svix-signature');
   // Verify using Resend's webhook secret
   ```

2. **Use HTTPS Only:**
   - Never use HTTP for webhook endpoint
   - Resend won't send to non-HTTPS in production

3. **Rate Limiting:**
   - Implement rate limits on webhook endpoint
   - Protect against spam/abuse

4. **Environment Variables:**
   - Never commit API keys to git
   - Use environment variable management
   - Rotate keys regularly

### Email Security:

1. **SPF Record:**
   ```
   v=spf1 include:_spf.resend.com ~all
   ```

2. **DKIM:** Configured automatically by Resend

3. **DMARC:**
   ```
   _dmarc.kannakrew.com TXT "v=DMARC1; p=quarantine; rua=mailto:admin@kannakrew.com"
   ```

---

## Alternative Solutions

### If You Don't Want to Use Resend for Receiving:

**Problem:** Website forms need to submit somewhere

**Solution 1: Formspree/Formspark**
- Use third-party form service
- Forms submit to their API
- They forward to your email
- Remove Resend MX records

**Solution 2: API-Only Forms**
- Forms call your own API endpoint
- API sends email via Resend SMTP
- No inbound email needed
- Keep MX at mail.kannakrew.com

**Solution 3: Cloudflare Email Routing**
- Free email forwarding service
- MX points to Cloudflare
- Auto-forwards to webmail
- No webhook needed
- But: Can't use Resend for forms

---

## Recommended Implementation Plan

### Phase 1: Testing (Week 1)

1. **Day 1:** Set up test subdomain (test.kannakrew.com)
2. **Day 2:** Deploy webhook endpoint to Vercel
3. **Day 3:** Configure Resend inbound for test subdomain
4. **Day 4:** Test forwarding with test emails
5. **Day 5:** Verify MCP tool can read forwarded emails

### Phase 2: Production (Week 2)

1. **Day 1:** Review and optimize webhook code
2. **Day 2:** Set up monitoring and alerts
3. **Day 3:** Switch MX records to production
4. **Day 4:** Monitor for 48 hours
5. **Day 5:** Full testing and documentation

### Phase 3: Optimization (Week 3)

1. Add retry logic for failed forwards
2. Implement email queuing for reliability
3. Set up dashboard for monitoring
4. Document troubleshooting procedures
5. Train team on new system

---

## Next Steps

### Immediate Actions:

1. **Choose Architecture:**
   - Option 1: Webhook forwarding (recommended)
   - Option 2: Dual email systems (simple)
   - Option 3: Subdomain split (clean)

2. **Set Up Webhook Hosting:**
   - Vercel (easiest for Next.js/Node.js)
   - Cloudflare Workers (fastest)
   - Pipedream (no-code option)

3. **Deploy Webhook Endpoint:**
   - Use sample code provided above
   - Test locally with ngrok first
   - Deploy to production

4. **Configure Resend:**
   - Add domain to Resend
   - Update MX records
   - Create webhook
   - Test end-to-end

5. **Update Documentation:**
   - Document new email flow
   - Update MCP tool configuration
   - Create troubleshooting guide

---

## Support Resources

### Resend Documentation:
- Inbound Emails: https://resend.com/docs/dashboard/receiving/introduction
- Forward Emails: https://resend.com/docs/dashboard/receiving/forward-emails
- API Reference: https://resend.com/docs/api-reference
- Webhooks: https://resend.com/docs/dashboard/webhooks/introduction

### Community Support:
- Resend Discord: https://resend.com/discord
- GitHub Discussions: https://github.com/resendlabs/resend-node
- Stack Overflow: Tag `resend`

### Alternative Services:
- Cloudflare Email Routing (free): https://developers.cloudflare.com/email-routing/
- ForwardEmail.net (open source): https://forwardemail.net/
- ImprovMX (free tier): https://improvmx.com/

---

## Conclusion

**TL;DR:**
1. Resend supports inbound email via webhooks
2. Webhooks send metadata only, not full email
3. Call Receiving API to get email body
4. Forward via SMTP to mail.kannakrew.com
5. MCP tool reads from webmail IMAP as normal

**Recommended Solution:**
- Deploy webhook endpoint (Vercel/Pipedream)
- Configure Resend inbound domain
- Auto-forward all emails to webmail
- Keep MCP tool on webmail IMAP/SMTP
- Everything works seamlessly

**Estimated Setup Time:** 2-4 hours
**Technical Difficulty:** Medium (requires webhook development)
**Ongoing Maintenance:** Low (monitor webhook logs)

---

**Questions or Need Help?**

Let me know if you need:
- Complete webhook code in different language (Python, PHP, etc.)
- Step-by-step Vercel deployment guide
- Pipedream no-code workflow setup
- Alternative architecture recommendations
- Help with DNS configuration
- Troubleshooting specific issues
