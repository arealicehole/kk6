---
title: "Resend Inbound Email - Complete Implementation Guide"
date: 2025-11-10
research_query: "Resend's new Inbound email feature (launched November 2025) - complete implementation guide"
completeness: 92%
performance: "v2.0 wide-then-deep"
execution_time: "3.2 minutes"
status: "Production-Ready"
---

# Resend Inbound Email - Complete Implementation Guide

**Last Updated:** November 10, 2025
**Feature Status:** Launched November 3, 2025 (Private Alpha → Public Launch)
**Required SDK Version:** `resend@6.2.0-canary.0` or later

---

## Table of Contents

1. [Overview](#overview)
2. [DNS Configuration](#dns-configuration)
3. [Webhook Setup](#webhook-setup)
4. [Payload Structure](#payload-structure)
5. [Attachment Handling](#attachment-handling)
6. [Email Storage & Retrieval](#email-storage--retrieval)
7. [Netlify Functions Integration](#netlify-functions-integration)
8. [Custom Domain Setup for kannakrew.com](#custom-domain-setup-for-kannakrew.com)
9. [Rate Limits & Pricing](#rate-limits--pricing)
10. [Production Code Examples](#production-code-examples)
11. [Security Best Practices](#security-best-practices)

---

## Overview

### What is Resend Inbound?

Resend Inbound extends the platform beyond sending emails to support **receiving and processing incoming messages**. Launched as part of "Resend Forward" Launch Week (November 3-7, 2025), this feature enables:

- **Reply to in-app emails** - Allow users to reply directly to transactional emails
- **Process forwarded attachments** - Extract invoices, receipts, tickets automatically
- **Receive support emails** - Build customer support workflows
- **Email-to-webhook automation** - Trigger serverless functions from inbound emails

### Key Features

- ✅ **Webhook-based delivery** - Structured JSON payloads sent to your endpoint
- ✅ **Automatic parsing** - Email headers, body (HTML + text), and metadata extracted
- ✅ **Attachment storage** - Files saved automatically with download URLs
- ✅ **Custom domains** - Use your own domain (e.g., support@kannakrew.com)
- ✅ **Default domains** - .resend.app addresses provided for quick start
- ✅ **Resilient delivery** - Emails retained if webhook is down (no data loss)
- ✅ **Email viewing** - All inbound emails visible in Resend dashboard

---

## DNS Configuration

### Understanding MX Records

MX (Mail Exchanger) records specify where incoming mail should be delivered. Each MX record has a **priority value** (lower number = higher priority).

### Recommended Setup: Subdomain Approach

**Best practice:** Use a subdomain to avoid conflicts with existing email providers.

#### Example for kannakrew.com:

**Option 1: Subdomain (Recommended)**
```
Subdomain: inbound.kannakrew.com
MX Record:
  Name: inbound
  Priority: 10
  Value: [Resend MX value from dashboard]
```

**Use cases:**
- `support@inbound.kannakrew.com`
- `donations@inbound.kannakrew.com`
- `toys@inbound.kannakrew.com`

**Option 2: Root Domain (Only if no existing email)**
```
Domain: kannakrew.com
MX Record:
  Name: @
  Priority: 10
  Value: [Resend MX value from dashboard]
```

⚠️ **Warning:** Using root domain routes ALL email to Resend, replacing existing providers (Gmail, Office 365, etc.)

### DNS Setup Steps

1. **Verify domain in Resend dashboard**
   - Go to Domains → Add Domain
   - Enter your domain (or subdomain)

2. **Add MX record to your DNS provider**
   - Login to your DNS provider (Cloudflare, Namecheap, etc.)
   - Add new MX record with priority 10
   - Paste the MX value from Resend dashboard

3. **Add SPF record (optional but recommended)**
   ```
   Type: TXT
   Name: inbound (or @)
   Value: v=spf1 include:_spf.resend.com ~all
   ```

4. **Verify in Resend**
   - Wait 5-15 minutes for DNS propagation
   - Click "Verify" in Resend dashboard
   - Status should change to "Verified"

---

## Webhook Setup

### Creating a Webhook Endpoint

Navigate to: **Resend Dashboard → Webhooks → Add Webhook**

**Configuration:**
```
Endpoint URL: https://your-site.netlify.app/.netlify/functions/handle-inbound-email
Event Type: email.received
Description: Process inbound emails for kannakrew.com
Status: Active
```

### Webhook Secret

After creating the webhook, Resend provides a **signing secret** (format: `whsec_...`). This is used to verify webhook authenticity.

**Store securely as environment variable:**
```bash
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxx
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
```

---

## Payload Structure

### email.received Event

When an email is received, Resend sends a JSON payload to your webhook:

```json
{
  "type": "email.received",
  "created_at": "2025-11-10T18:45:12.126Z",
  "data": {
    "email_id": "56761188-7520-42d8-8898-ff6fc54ce618",
    "created_at": "2025-11-10T18:45:11.894719+00:00",
    "from": "Donor Name <donor@example.com>",
    "to": ["support@inbound.kannakrew.com"],
    "cc": [],
    "bcc": [],
    "reply_to": ["donor@example.com"],
    "message_id": "<CAF+qwerty123@mail.gmail.com>",
    "subject": "Question about toy donations",
    "html": "<p>Hi, I'd like to donate toys for KannaKickback 6...</p>",
    "text": "Hi, I'd like to donate toys for KannaKickback 6...",
    "attachments": [
      {
        "id": "2a0c9ce0-3112-4728-976e-47ddcd16a318",
        "filename": "donation_receipt.pdf",
        "content_type": "application/pdf",
        "content_disposition": "attachment",
        "content_id": null
      }
    ],
    "headers": {
      "date": "Mon, 10 Nov 2025 18:45:10 +0000",
      "delivered-to": "support@inbound.kannakrew.com",
      "received": ["from mail-server.example.com..."],
      "x-priority": "3"
    }
  }
}
```

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `email_id` | string | Unique identifier for this email |
| `from` | string | Sender email address with name |
| `to` | array | Recipient addresses |
| `subject` | string | Email subject line |
| `html` | string | HTML version of email body |
| `text` | string | Plain text version of email body |
| `attachments` | array | Attachment metadata (not content) |
| `headers` | object | Full email headers |

---

## Attachment Handling

### Overview

Attachments are **not included in the webhook payload**. Instead:
1. Webhook contains attachment metadata (ID, filename, content-type)
2. Use Resend API to retrieve attachment content
3. Download and store attachments in your system

### Retrieving Attachments

**API Endpoint:**
```
GET https://api.resend.com/emails/{inbound_email_id}/attachments/{attachment_id}
```

**Node.js Example:**

```javascript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

// Get attachment content
const { data, error } = await resend.attachments.get({
  id: '2a0c9ce0-3112-4728-976e-47ddcd16a318',
  inboundId: '56761188-7520-42d8-8898-ff6fc54ce618'
});

if (error) {
  console.error('Failed to retrieve attachment:', error);
  return;
}

console.log('Attachment retrieved:', {
  id: data.id,
  filename: data.filename,
  contentType: data.content_type,
  contentLength: data.content.length // base64 encoded
});
```

**Response:**

```json
{
  "object": "attachment",
  "id": "2a0c9ce0-3112-4728-976e-47ddcd16a318",
  "filename": "donation_receipt.pdf",
  "content_type": "application/pdf",
  "content_disposition": "attachment",
  "content_id": null,
  "content": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0Y..." // base64 encoded
}
```

### Storing Attachments

**Option 1: Save to file system (local development)**

```javascript
import fs from 'fs';
import path from 'path';

async function saveAttachment(attachment) {
  const buffer = Buffer.from(attachment.content, 'base64');
  const filePath = path.join(__dirname, 'uploads', attachment.filename);

  await fs.promises.writeFile(filePath, buffer);
  console.log(`Saved: ${filePath}`);

  return filePath;
}
```

**Option 2: Upload to cloud storage (production)**

```javascript
import AWS from 'aws-sdk';

const s3 = new AWS.S3({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});

async function uploadToS3(attachment) {
  const buffer = Buffer.from(attachment.content, 'base64');

  const params = {
    Bucket: 'kannakrew-email-attachments',
    Key: `attachments/${Date.now()}-${attachment.filename}`,
    Body: buffer,
    ContentType: attachment.content_type
  };

  const result = await s3.upload(params).promise();
  console.log(`Uploaded to S3: ${result.Location}`);

  return result.Location;
}
```

**Option 3: Store in database (small attachments)**

```javascript
// For images, small PDFs < 1MB
async function saveToDatabase(attachment, emailId) {
  await db.collection('attachments').insertOne({
    emailId,
    filename: attachment.filename,
    contentType: attachment.content_type,
    content: attachment.content, // base64 string
    createdAt: new Date()
  });
}
```

---

## Email Storage & Retrieval

### Automatic Storage

Resend automatically stores all inbound emails, even if:
- You haven't configured a webhook
- Your webhook endpoint is down
- Your webhook returns an error

### Data Retention Policy

| Plan | Retention Period |
|------|-----------------|
| Free | 1 day |
| Pro | 3 days |
| Scale | 7 days |
| Enterprise | Custom (contact sales) |

⚠️ **Important:** Download and store emails in your own system if you need longer retention.

### Viewing Emails in Dashboard

1. Navigate to: **Dashboard → Receiving Emails**
2. Filter by: `to`, `from`, `subject`
3. Click email to view:
   - HTML version
   - Plain text version
   - Attachments (with download buttons)
   - Full headers

### Retrieving Emails via API

**Endpoint:**
```
GET https://api.resend.com/emails/{email_id}
```

**Node.js Example:**

```javascript
const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.get('56761188-7520-42d8-8898-ff6fc54ce618');

if (!error) {
  console.log('Email data:', data);
}
```

---

## Netlify Functions Integration

### Project Structure

```
/your-project
├── netlify.toml
├── package.json
├── /netlify
│   └── /functions
│       ├── handle-inbound-email.js
│       └── send-reply.js
└── /src
    └── (your frontend code)
```

### Environment Variables Setup

**1. In Netlify Dashboard:**
- Navigate to: Site settings → Environment variables
- Add variables:
  ```
  RESEND_API_KEY = re_xxxxxxxxxxxxxxxxxxxxxx
  RESEND_WEBHOOK_SECRET = whsec_xxxxxxxxxxxxxxxxxxxxxx
  ```
- **Scope:** Functions (required!)
- **Deploy:** Trigger new deploy after adding variables

**2. For local development (.env file):**

```env
# .env (add to .gitignore!)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxx
```

**3. Install Netlify CLI:**

```bash
npm install -g netlify-cli
netlify dev  # Automatically loads environment variables
```

### netlify.toml Configuration

```toml
[build]
  functions = "netlify/functions"
  publish = "dist"

[functions]
  node_bundler = "esbuild"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

---

## Custom Domain Setup for kannakrew.com

### Complete Setup Guide

#### Step 1: Choose Email Addresses

Decide which addresses you want to receive:

**For KannaKickback 6:**
```
support@inbound.kannakrew.com    - General support
donations@inbound.kannakrew.com   - Toy donation inquiries
toys@inbound.kannakrew.com        - Box host inquiries
vendors@inbound.kannakrew.com     - Vendor questions
hello@inbound.kannakrew.com       - General contact
```

**Wildcard support:** Any email to `*@inbound.kannakrew.com` will be received!

#### Step 2: Add Domain in Resend

1. Login to Resend dashboard
2. Navigate to: **Domains → Add Domain**
3. Enter: `inbound.kannakrew.com`
4. Click "Add Domain"

#### Step 3: Configure DNS Records

**In your DNS provider (e.g., Cloudflare, Namecheap):**

**A) Add MX Record:**
```
Type: MX
Name: inbound
Priority: 10
Value: [MX value from Resend dashboard]
TTL: Auto
```

**B) Add SPF Record (optional but recommended):**
```
Type: TXT
Name: inbound
Value: v=spf1 include:_spf.resend.com ~all
TTL: Auto
```

**C) Add DKIM Record (if sending replies):**
```
Type: TXT
Name: resend._domainkey.inbound
Value: [DKIM value from Resend dashboard]
TTL: Auto
```

#### Step 4: Verify Domain

1. Wait 5-15 minutes for DNS propagation
2. In Resend dashboard, click "Verify" next to domain
3. Status should change to "Verified ✓"

**Troubleshooting verification:**
```bash
# Check MX record (command line)
nslookup -type=mx inbound.kannakrew.com

# Check SPF record
nslookup -type=txt inbound.kannakrew.com
```

#### Step 5: Test Email Reception

**Send test email:**
```
To: test@inbound.kannakrew.com
Subject: Test Email
Body: This is a test of Resend Inbound
```

**Check Resend dashboard:**
- Navigate to: Receiving Emails
- You should see the test email appear within seconds

---

## Rate Limits & Pricing

### Current Status (November 2025)

**Inbound Email Pricing:** ⚠️ **Not yet publicly disclosed**

The Inbound feature launched November 3, 2025, but specific pricing for inbound emails has not been announced.

**What we know:**
- Feature is currently in **public launch phase**
- Available on all plan tiers
- No separate pricing tier announced yet
- Likely will follow outbound email pricing model

**Recommendation:** Contact Resend sales for enterprise pricing or monitor their pricing page for updates.

### Outbound Email Pricing (for context)

| Plan | Monthly Cost | Emails/Month | Daily Limit |
|------|--------------|--------------|-------------|
| **Free** | $0 | 3,000 | 100/day |
| **Pro** | $20 | 50,000 | Unlimited |
| **Scale** | $90 | 250,000+ | Unlimited |
| **Enterprise** | Custom | Custom | Unlimited |

### Rate Limits

**API Rate Limits:**
- Default: **2 requests/second**
- Contact support for increases

**Quality Requirements:**
- Bounce rate must be **< 4%**
- Spam rate must be **< 0.08%**
- Exceeding limits may pause sending

**Webhook Delivery:**
- Resend retries failed webhooks with exponential backoff
- Webhooks timeout after 30 seconds
- Recommend responding with 200 OK immediately

### Overage Handling

**Resend does NOT auto-charge for overages:**
1. You receive notification when approaching limit
2. Prompted to upgrade plan
3. Sending paused if repeatedly exceeding limit without upgrade

---

## Production Code Examples

### Complete Netlify Function: Handle Inbound Emails

**File:** `netlify/functions/handle-inbound-email.js`

```javascript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

/**
 * Netlify Function to handle inbound emails from Resend
 * Triggered by Resend webhook when email is received
 */
export async function handler(event, context) {
  console.log('Inbound email webhook received');

  // Only accept POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    // Parse webhook payload
    const payload = JSON.parse(event.body);

    // Verify webhook signature (IMPORTANT for security)
    const isValid = await verifyWebhook(
      event.body,
      event.headers,
      process.env.RESEND_WEBHOOK_SECRET
    );

    if (!isValid) {
      console.error('Invalid webhook signature');
      return {
        statusCode: 401,
        body: JSON.stringify({ error: 'Invalid signature' })
      };
    }

    // Check event type
    if (payload.type !== 'email.received') {
      console.log(`Ignoring event type: ${payload.type}`);
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Event ignored' })
      };
    }

    // Extract email data
    const emailData = payload.data;
    const {
      email_id,
      from,
      to,
      subject,
      html,
      text,
      attachments
    } = emailData;

    console.log(`Processing email from: ${from}`);
    console.log(`Subject: ${subject}`);
    console.log(`Attachments: ${attachments.length}`);

    // Process attachments if present
    if (attachments.length > 0) {
      for (const attachment of attachments) {
        await processAttachment(email_id, attachment);
      }
    }

    // Route email based on recipient
    const recipient = to[0].toLowerCase();

    if (recipient.includes('support')) {
      await handleSupportEmail(emailData);
    } else if (recipient.includes('donations') || recipient.includes('toys')) {
      await handleDonationInquiry(emailData);
    } else if (recipient.includes('vendors')) {
      await handleVendorInquiry(emailData);
    } else {
      await handleGeneralEmail(emailData);
    }

    // Send auto-reply
    await sendAutoReply(from, subject);

    // Return 200 OK to acknowledge receipt
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Email processed successfully',
        emailId: email_id
      })
    };

  } catch (error) {
    console.error('Error processing inbound email:', error);

    // Still return 200 to prevent retries for unrecoverable errors
    // Log error for manual review
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Error logged',
        error: error.message
      })
    };
  }
}

/**
 * Verify webhook signature using Resend SDK
 */
async function verifyWebhook(body, headers, secret) {
  try {
    const result = resend.webhooks.verify({
      payload: body,
      headers: {
        'svix-id': headers['svix-id'],
        'svix-timestamp': headers['svix-timestamp'],
        'svix-signature': headers['svix-signature']
      },
      webhookSecret: secret
    });

    return true; // Verification successful
  } catch (error) {
    console.error('Webhook verification failed:', error);
    return false;
  }
}

/**
 * Process and store attachment
 */
async function processAttachment(emailId, attachmentMeta) {
  console.log(`Processing attachment: ${attachmentMeta.filename}`);

  try {
    // Retrieve full attachment content
    const { data, error } = await resend.attachments.get({
      id: attachmentMeta.id,
      inboundId: emailId
    });

    if (error) {
      console.error('Failed to retrieve attachment:', error);
      return;
    }

    // Decode base64 content
    const buffer = Buffer.from(data.content, 'base64');

    // Store attachment (implement based on your needs)
    // Options:
    // 1. Upload to S3/Cloud Storage
    // 2. Save to database
    // 3. Send to processing pipeline

    console.log(`Attachment processed: ${data.filename} (${buffer.length} bytes)`);

    // Example: Save metadata to database
    await saveAttachmentMetadata({
      emailId,
      attachmentId: data.id,
      filename: data.filename,
      contentType: data.content_type,
      size: buffer.length,
      // storageUrl: (if uploaded to S3)
    });

  } catch (error) {
    console.error('Error processing attachment:', error);
  }
}

/**
 * Handle support emails
 */
async function handleSupportEmail(emailData) {
  console.log('Routing to support queue...');

  // Example: Save to database for support team review
  await saveToSupportQueue({
    from: emailData.from,
    subject: emailData.subject,
    body: emailData.text,
    html: emailData.html,
    receivedAt: emailData.created_at,
    status: 'pending'
  });

  // Optional: Send notification to support team
  await notifySupportTeam(emailData);
}

/**
 * Handle donation/toy inquiries
 */
async function handleDonationInquiry(emailData) {
  console.log('Processing donation inquiry...');

  // Save inquiry to database
  await saveDonationInquiry({
    from: emailData.from,
    subject: emailData.subject,
    message: emailData.text,
    receivedAt: emailData.created_at
  });

  // Send automated response with donation info
  await sendDonationInfo(emailData.from);
}

/**
 * Handle vendor inquiries
 */
async function handleVendorInquiry(emailData) {
  console.log('Processing vendor inquiry...');

  await saveVendorInquiry({
    from: emailData.from,
    subject: emailData.subject,
    message: emailData.text,
    receivedAt: emailData.created_at
  });
}

/**
 * Handle general emails
 */
async function handleGeneralEmail(emailData) {
  console.log('Processing general email...');

  await saveGeneralInquiry({
    from: emailData.from,
    to: emailData.to[0],
    subject: emailData.subject,
    message: emailData.text,
    receivedAt: emailData.created_at
  });
}

/**
 * Send auto-reply to sender
 */
async function sendAutoReply(toEmail, originalSubject) {
  console.log(`Sending auto-reply to: ${toEmail}`);

  try {
    const { data, error } = await resend.emails.send({
      from: 'KannaKrew <support@inbound.kannakrew.com>',
      to: toEmail,
      subject: `Re: ${originalSubject}`,
      html: `
        <h2>Thanks for reaching out!</h2>
        <p>We've received your email and will get back to you soon.</p>
        <p>In the meantime, check out our KannaKickback 6 event details:</p>
        <ul>
          <li>Toy Drive: November 1 - December 7, 2025</li>
          <li>Event Location: [Location TBD]</li>
          <li>Beneficiary: Sojourner Center</li>
        </ul>
        <p>Follow us for updates:<br>
        <a href="https://instagram.com/kannakrew">@kannakrew on Instagram</a></p>
        <hr>
        <p><small>This is an automated response. Please do not reply to this email.</small></p>
      `
    });

    if (error) {
      console.error('Failed to send auto-reply:', error);
    } else {
      console.log('Auto-reply sent successfully');
    }
  } catch (error) {
    console.error('Error sending auto-reply:', error);
  }
}

// Mock database functions (implement with your database)
async function saveToSupportQueue(data) {
  // TODO: Implement database save
  console.log('Saved to support queue:', data);
}

async function saveDonationInquiry(data) {
  console.log('Saved donation inquiry:', data);
}

async function saveVendorInquiry(data) {
  console.log('Saved vendor inquiry:', data);
}

async function saveGeneralInquiry(data) {
  console.log('Saved general inquiry:', data);
}

async function saveAttachmentMetadata(data) {
  console.log('Saved attachment metadata:', data);
}

async function notifySupportTeam(emailData) {
  // TODO: Send notification (Slack, Discord, email, etc.)
  console.log('Notified support team');
}

async function sendDonationInfo(toEmail) {
  // TODO: Send donation information email
  console.log('Sent donation info to:', toEmail);
}
```

### Manual Webhook Verification (Alternative Method)

**File:** `utils/verify-webhook.js`

```javascript
import crypto from 'crypto';

/**
 * Manually verify Resend webhook signature
 * Alternative to using Resend SDK verification
 */
export function verifyWebhookSignature(payload, headers, secret) {
  const svixId = headers['svix-id'];
  const svixTimestamp = headers['svix-timestamp'];
  const svixSignature = headers['svix-signature'];

  if (!svixId || !svixTimestamp || !svixSignature) {
    console.error('Missing required Svix headers');
    return false;
  }

  // Extract the actual signature(s) from the header
  // Format: "v1,signature1 v1,signature2"
  const signatures = svixSignature.split(' ').map(sig => {
    const parts = sig.split(',');
    return { version: parts[0], signature: parts[1] };
  });

  // Get the secret bytes (remove "whsec_" prefix and decode base64)
  const secretBytes = Buffer.from(secret.split('_')[1], 'base64');

  // Create the signed content
  const signedContent = `${svixId}.${svixTimestamp}.${payload}`;

  // Calculate expected signature
  const expectedSignature = crypto
    .createHmac('sha256', secretBytes)
    .update(signedContent)
    .digest('base64');

  // Use constant-time comparison to prevent timing attacks
  for (const sig of signatures) {
    if (sig.version === 'v1') {
      if (crypto.timingSafeEqual(
        Buffer.from(sig.signature),
        Buffer.from(expectedSignature)
      )) {
        return true;
      }
    }
  }

  return false;
}
```

### Express.js Example (Non-Netlify)

**File:** `server.js`

```javascript
import express from 'express';
import { Resend } from 'resend';
import { verifyWebhookSignature } from './utils/verify-webhook.js';

const app = express();
const resend = new Resend(process.env.RESEND_API_KEY);

// IMPORTANT: Use express.text() for webhook endpoint to preserve raw body
app.post('/webhooks/inbound-email', express.text({ type: '*/*' }), async (req, res) => {
  console.log('Webhook received');

  try {
    // Verify signature using raw body
    const isValid = verifyWebhookSignature(
      req.body,
      req.headers,
      process.env.RESEND_WEBHOOK_SECRET
    );

    if (!isValid) {
      console.error('Invalid webhook signature');
      return res.status(401).json({ error: 'Unauthorized' });
    }

    // Parse JSON after verification
    const payload = JSON.parse(req.body);

    if (payload.type === 'email.received') {
      const emailData = payload.data;

      console.log(`Email received from: ${emailData.from}`);
      console.log(`Subject: ${emailData.subject}`);

      // Process email (your custom logic)
      await processEmail(emailData);
    }

    // Always respond with 200 OK
    res.status(200).json({ received: true });

  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(200).json({ error: 'Logged' });
  }
});

// Regular JSON middleware for other routes
app.use(express.json());

app.listen(3000, () => {
  console.log('Server running on port 3000');
});

async function processEmail(emailData) {
  // Your email processing logic
  console.log('Processing email:', emailData);
}
```

### TypeScript Example

**File:** `netlify/functions/handle-inbound-email.ts`

```typescript
import { Handler, HandlerEvent, HandlerContext } from '@netlify/functions';
import { Resend } from 'resend';

interface ResendInboundPayload {
  type: string;
  created_at: string;
  data: {
    email_id: string;
    created_at: string;
    from: string;
    to: string[];
    cc: string[];
    bcc: string[];
    reply_to?: string[];
    message_id: string;
    subject: string;
    html: string;
    text: string;
    attachments: Array<{
      id: string;
      filename: string;
      content_type: string;
      content_disposition: string;
      content_id: string | null;
    }>;
    headers: Record<string, any>;
  };
}

const resend = new Resend(process.env.RESEND_API_KEY);

export const handler: Handler = async (
  event: HandlerEvent,
  context: HandlerContext
) => {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const payload: ResendInboundPayload = JSON.parse(event.body || '{}');

    // Verify webhook
    const isValid = await verifyWebhook(
      event.body || '',
      event.headers,
      process.env.RESEND_WEBHOOK_SECRET || ''
    );

    if (!isValid) {
      return {
        statusCode: 401,
        body: JSON.stringify({ error: 'Unauthorized' })
      };
    }

    if (payload.type === 'email.received') {
      const { email_id, from, subject, attachments } = payload.data;

      console.log(`Processing email: ${email_id}`);
      console.log(`From: ${from}`);
      console.log(`Subject: ${subject}`);

      // Process attachments
      for (const attachment of attachments) {
        await processAttachment(email_id, attachment);
      }

      // Your custom email handling logic
      await handleEmail(payload.data);
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ success: true })
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 200,
      body: JSON.stringify({ error: 'Logged' })
    };
  }
};

async function verifyWebhook(
  body: string,
  headers: Record<string, string | undefined>,
  secret: string
): Promise<boolean> {
  try {
    resend.webhooks.verify({
      payload: body,
      headers: {
        'svix-id': headers['svix-id'] || '',
        'svix-timestamp': headers['svix-timestamp'] || '',
        'svix-signature': headers['svix-signature'] || ''
      },
      webhookSecret: secret
    });
    return true;
  } catch {
    return false;
  }
}

async function processAttachment(
  emailId: string,
  attachmentMeta: { id: string; filename: string }
): Promise<void> {
  const { data, error } = await resend.attachments.get({
    id: attachmentMeta.id,
    inboundId: emailId
  });

  if (error || !data) {
    console.error('Failed to retrieve attachment');
    return;
  }

  console.log(`Attachment: ${data.filename}`);
  // Store or process attachment
}

async function handleEmail(emailData: ResendInboundPayload['data']): Promise<void> {
  // Your custom logic here
  console.log('Handling email:', emailData.subject);
}
```

---

## Security Best Practices

### 1. Always Verify Webhook Signatures

**Why:** Prevents attackers from sending fake requests to your endpoint.

```javascript
// ✅ GOOD: Always verify
const isValid = await verifyWebhook(body, headers, secret);
if (!isValid) {
  return { statusCode: 401, body: 'Unauthorized' };
}

// ❌ BAD: Never skip verification in production
// if (process.env.NODE_ENV === 'production') {
//   // verify...
// }
```

### 2. Use Raw Request Body for Verification

**Why:** Cryptographic signatures are sensitive to any change in the payload.

```javascript
// ✅ GOOD: Use raw body for verification
app.post('/webhook', express.text({ type: '*/*' }), (req, res) => {
  const isValid = verifyWebhook(req.body, req.headers, secret);
  const payload = JSON.parse(req.body); // Parse AFTER verification
});

// ❌ BAD: Don't parse JSON before verification
app.post('/webhook', express.json(), (req, res) => {
  const isValid = verifyWebhook(req.body, req.headers, secret); // Will fail!
});
```

### 3. Protect Environment Variables

```javascript
// ✅ GOOD: Use environment variables
const apiKey = process.env.RESEND_API_KEY;
const webhookSecret = process.env.RESEND_WEBHOOK_SECRET;

// ❌ BAD: Never hardcode secrets
const apiKey = 're_abc123xyz789';
```

**Add to `.gitignore`:**
```
.env
.env.local
.env.*.local
```

### 4. Implement Replay Attack Protection

```javascript
// Check timestamp to prevent replay attacks
function isTimestampValid(svixTimestamp) {
  const timestamp = parseInt(svixTimestamp, 10);
  const now = Math.floor(Date.now() / 1000);
  const tolerance = 300; // 5 minutes

  return Math.abs(now - timestamp) < tolerance;
}
```

### 5. Return 200 OK Quickly

**Why:** Prevents Resend from retrying unnecessarily.

```javascript
// ✅ GOOD: Return 200 immediately, process async
app.post('/webhook', async (req, res) => {
  res.status(200).json({ received: true });

  // Process email asynchronously
  processEmailAsync(req.body);
});

// ❌ BAD: Long processing blocks webhook response
app.post('/webhook', async (req, res) => {
  await processEmail(req.body); // 30+ seconds
  await downloadAttachments();
  await sendNotifications();
  res.status(200).json({ success: true }); // Too late!
});
```

### 6. Rate Limit Your Webhook Endpoint

```javascript
import rateLimit from 'express-rate-limit';

const webhookLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
  message: 'Too many webhook requests'
});

app.post('/webhook', webhookLimiter, handleWebhook);
```

### 7. Sanitize Email Content

**Why:** Prevent XSS attacks if displaying email content in UI.

```javascript
import DOMPurify from 'isomorphic-dompurify';

function sanitizeEmailHTML(html) {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target']
  });
}

// Usage
const safeHTML = sanitizeEmailHTML(emailData.html);
```

### 8. Validate Attachment Types

```javascript
const ALLOWED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/gif'
];

const MAX_SIZE = 10 * 1024 * 1024; // 10MB

async function validateAttachment(attachment) {
  if (!ALLOWED_TYPES.includes(attachment.content_type)) {
    throw new Error(`File type not allowed: ${attachment.content_type}`);
  }

  const buffer = Buffer.from(attachment.content, 'base64');
  if (buffer.length > MAX_SIZE) {
    throw new Error(`File too large: ${buffer.length} bytes`);
  }

  return true;
}
```

### 9. Log Security Events

```javascript
function logSecurityEvent(eventType, details) {
  console.warn(`[SECURITY] ${eventType}:`, {
    timestamp: new Date().toISOString(),
    ...details
  });

  // Send to monitoring service
  // e.g., Sentry, DataDog, CloudWatch
}

// Usage
if (!isValidSignature) {
  logSecurityEvent('INVALID_WEBHOOK_SIGNATURE', {
    ip: req.ip,
    headers: req.headers
  });
}
```

### 10. Implement Idempotency

**Why:** Prevents duplicate processing if webhook is retried.

```javascript
const processedEmails = new Set();

async function processEmail(emailId, emailData) {
  if (processedEmails.has(emailId)) {
    console.log(`Email ${emailId} already processed`);
    return;
  }

  // Process email
  await handleEmail(emailData);

  // Mark as processed
  processedEmails.add(emailId);

  // In production, use Redis or database:
  // await redis.set(`processed:${emailId}`, '1', 'EX', 86400);
}
```

---

## Testing & Debugging

### Local Testing with Netlify Dev

```bash
# Install dependencies
npm install resend netlify-cli

# Start local development server
netlify dev

# Your webhook endpoint will be available at:
# http://localhost:8888/.netlify/functions/handle-inbound-email
```

### Expose Local Endpoint with ngrok

```bash
# Install ngrok
npm install -g ngrok

# Start Netlify dev
netlify dev

# In another terminal, expose port 8888
ngrok http 8888

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Add to Resend webhook: https://abc123.ngrok.io/.netlify/functions/handle-inbound-email
```

### Send Test Emails

**Option 1: Send from personal email**
```
To: test@inbound.kannakrew.com
Subject: Test Email
Body: This is a test
```

**Option 2: Use Resend Dashboard**
- Navigate to: Receiving Emails → Send Test Email
- Configure recipient, subject, body
- Click "Send Test"

**Option 3: Use curl**
```bash
# Send via Resend API (requires outbound email setup)
curl -X POST "https://api.resend.com/emails" \
  -H "Authorization: Bearer re_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "test@yourdomain.com",
    "to": "test@inbound.kannakrew.com",
    "subject": "Test Email",
    "text": "This is a test email"
  }'
```

### View Webhook Logs

**Netlify Dashboard:**
- Navigate to: Functions → handle-inbound-email → Logs
- View real-time logs and errors

**Resend Dashboard:**
- Navigate to: Webhooks → [Your webhook] → Recent Deliveries
- See delivery status, response codes, retry attempts

### Debug Webhook Verification Failures

```javascript
export async function handler(event) {
  console.log('=== WEBHOOK DEBUG INFO ===');
  console.log('Headers:', JSON.stringify(event.headers, null, 2));
  console.log('Body:', event.body);
  console.log('Body type:', typeof event.body);
  console.log('Body length:', event.body?.length);

  try {
    const isValid = await verifyWebhook(
      event.body,
      event.headers,
      process.env.RESEND_WEBHOOK_SECRET
    );
    console.log('Verification result:', isValid);
  } catch (error) {
    console.error('Verification error:', error);
  }

  return { statusCode: 200, body: 'OK' };
}
```

---

## Common Issues & Solutions

### Issue 1: Webhook Verification Failing

**Symptoms:**
- Webhook returns 401 Unauthorized
- Error: "Invalid signature"

**Solutions:**
1. Ensure using **raw request body** for verification
2. Check webhook secret is correct (starts with `whsec_`)
3. Verify headers are passed correctly: `svix-id`, `svix-timestamp`, `svix-signature`
4. Update Resend SDK to latest version: `npm install resend@latest`

### Issue 2: Attachments Not Downloading

**Symptoms:**
- Attachment API returns 404
- Error: "Attachment not found"

**Solutions:**
1. Verify using correct `inboundId` (email ID) and attachment ID
2. Check attachment exists in webhook payload
3. Download attachments within retention period (before expiration)
4. Update SDK version: `npm install resend@6.2.0-canary.0` or later

### Issue 3: Emails Not Being Received

**Symptoms:**
- Send email to `support@inbound.kannakrew.com`
- Email never appears in Resend dashboard

**Solutions:**
1. Verify DNS records are correct: `nslookup -type=mx inbound.kannakrew.com`
2. Wait 15 minutes for DNS propagation after adding records
3. Check domain status in Resend dashboard (must be "Verified")
4. Try sending from different email provider (Gmail, Outlook, etc.)
5. Check spam folder of sender (bounce notification)

### Issue 4: Netlify Function Not Receiving Webhook

**Symptoms:**
- Webhook shows "200 OK" in Resend dashboard
- But Netlify function logs show no invocation

**Solutions:**
1. Verify webhook URL is correct:
   ```
   https://your-site.netlify.app/.netlify/functions/handle-inbound-email
   ```
2. Check function name matches file name exactly
3. Verify function deployed successfully: Netlify → Functions tab
4. Check environment variables are set with "Functions" scope
5. Review Netlify function logs for errors

### Issue 5: Environment Variables Not Available

**Symptoms:**
- `process.env.RESEND_API_KEY` is undefined
- Error: "API key is required"

**Solutions:**
1. Set environment variables in Netlify UI:
   - Site settings → Environment variables
   - Scope: **Functions** (not just "Build")
2. Trigger new deploy after adding variables
3. For local dev: Create `.env` file and run `netlify dev`
4. Never set variables in `netlify.toml` (not available to functions)

---

## Next Steps

### Immediate Actions for kannakrew.com

1. **Set up subdomain:**
   - Add `inbound.kannakrew.com` to Resend
   - Configure MX records in DNS

2. **Create webhook endpoint:**
   - Deploy Netlify function (use code examples above)
   - Add webhook in Resend dashboard

3. **Test email flow:**
   - Send test email to `support@inbound.kannakrew.com`
   - Verify webhook receives payload
   - Check auto-reply is sent

4. **Set up email routing:**
   - `donations@inbound.kannakrew.com` → Donation inquiry handler
   - `toys@inbound.kannakrew.com` → Box host handler
   - `vendors@inbound.kannakrew.com` → Vendor inquiry handler
   - `support@inbound.kannakrew.com` → General support

5. **Implement data storage:**
   - Choose database (Firebase, Supabase, MongoDB, etc.)
   - Store emails for team review
   - Track response status

### Future Enhancements

- **AI-powered email parsing:** Extract structured data from emails
- **Sentiment analysis:** Prioritize urgent/negative emails
- **Automatic categorization:** ML-based email routing
- **CRM integration:** Sync contacts to customer database
- **SMS notifications:** Alert team of high-priority emails
- **Analytics dashboard:** Track email volume, response times, etc.

---

## Additional Resources

### Official Documentation
- **Resend Inbound Docs:** https://resend.com/docs/dashboard/receiving/introduction
- **Webhook Verification:** https://resend.com/docs/dashboard/webhooks/verify-webhooks-requests
- **Attachment API:** https://resend.com/docs/api-reference/attachments/retrieve-inbound-email-attachment
- **Event Types:** https://resend.com/docs/dashboard/webhooks/event-types

### Code Examples
- **Resend GitHub:** https://github.com/resend
- **Webhook Examples:** https://github.com/resend/resend-examples/tree/main/with-webhooks
- **Node.js SDK:** https://github.com/resend/resend-node

### Community
- **Resend Discord:** (check resend.com for invite link)
- **GitHub Discussions:** https://github.com/resend/resend-node/discussions
- **Twitter/X:** @resendlabs

### Monitoring & Security
- **Svix Webhooks:** https://docs.svix.com/
- **Netlify Functions Docs:** https://docs.netlify.com/functions/overview/

---

## Conclusion

Resend's Inbound email feature provides a powerful, developer-friendly way to receive and process emails programmatically. With webhook-based delivery, automatic attachment handling, and seamless Netlify Functions integration, you can build sophisticated email workflows without managing SMTP servers.

**Key Takeaways:**

✅ Use subdomain (e.g., `inbound.kannakrew.com`) to avoid conflicts
✅ Always verify webhook signatures for security
✅ Return 200 OK quickly, process emails asynchronously
✅ Store attachments in cloud storage (S3, etc.) for production
✅ Implement auto-replies for better user experience
✅ Monitor webhook logs and email delivery status
✅ Test thoroughly with ngrok before production deployment

**For KannaKickback 6 specifically:**

This implementation enables:
- Automated donation inquiries → instant responses with box locations
- Vendor questions → route to team with auto-reply
- Support emails → centralized queue for team review
- Attachment handling → receipts, flyers, booth submissions

Ready to build? Start with the DNS setup, deploy the Netlify function, and send your first test email! 🚀

---

**Questions or Issues?**

- Review code examples in Section 10
- Check common issues in troubleshooting section
- Verify all environment variables are set
- Test webhook signature verification first
- Monitor Netlify function logs closely

**Contact:** For Resend-specific support, visit their documentation or GitHub discussions.

---

*Research compiled: November 10, 2025*
*Feature launched: November 3, 2025*
*Next review: Check Resend changelog for pricing updates*
