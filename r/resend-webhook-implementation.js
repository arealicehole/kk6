/**
 * Resend Inbound Email Webhook - Ready to Deploy
 *
 * This webhook receives emails from Resend and forwards them to your webmail server
 * Deploy to: Vercel, Cloudflare Workers, or any Node.js hosting
 *
 * Setup Instructions:
 * 1. Deploy this file to your hosting platform
 * 2. Set environment variables (see below)
 * 3. Add webhook URL to Resend dashboard
 * 4. Test with an email to your domain
 */

// ============================================
// REQUIRED ENVIRONMENT VARIABLES
// ============================================
// RESEND_API_KEY=re_xxxxxxxxxxxx
// WEBMAIL_HOST=mail.kannakrew.com
// WEBMAIL_PORT=465
// WEBMAIL_USER=admin@kannakrew.com
// WEBMAIL_PASSWORD=your_webmail_password
// FORWARD_TO_EMAIL=admin@kannakrew.com
// WEBHOOK_SECRET=your_resend_webhook_secret (optional, for signature verification)

// ============================================
// DEPENDENCIES
// ============================================
// npm install resend nodemailer svix

import { Resend } from 'resend';
import nodemailer from 'nodemailer';
import { Webhook } from 'svix';

// ============================================
// CONFIGURATION
// ============================================

const resend = new Resend(process.env.RESEND_API_KEY);

// Configure SMTP transport for webmail forwarding
const transport = nodemailer.createTransport({
  host: process.env.WEBMAIL_HOST,
  port: parseInt(process.env.WEBMAIL_PORT),
  secure: true, // Use SSL/TLS
  auth: {
    user: process.env.WEBMAIL_USER,
    pass: process.env.WEBMAIL_PASSWORD,
  },
});

// ============================================
// WEBHOOK HANDLER (Next.js App Router)
// ============================================

export async function POST(request) {
  try {
    // 1. Verify webhook signature (recommended for security)
    if (process.env.WEBHOOK_SECRET) {
      const payload = await request.text();
      const headers = {
        'svix-id': request.headers.get('svix-id'),
        'svix-timestamp': request.headers.get('svix-timestamp'),
        'svix-signature': request.headers.get('svix-signature'),
      };

      const wh = new Webhook(process.env.WEBHOOK_SECRET);

      try {
        wh.verify(payload, headers);
      } catch (err) {
        console.error('Webhook signature verification failed:', err);
        return Response.json(
          { error: 'Invalid signature' },
          { status: 401 }
        );
      }

      // Parse the verified payload
      const event = JSON.parse(payload);
    } else {
      // No signature verification (not recommended for production)
      const event = await request.json();
    }

    // 2. Check if this is an email.received event
    if (event.type !== 'email.received') {
      console.log(`Ignoring event type: ${event.type}`);
      return Response.json({ received: true });
    }

    const emailId = event.data.email_id;
    const metadata = event.data;

    console.log(`Received email: ${emailId} from ${metadata.from}`);

    // 3. Retrieve full email content from Resend
    const emailData = await resend.emails.receiving.get(emailId);

    if (!emailData) {
      throw new Error(`Failed to retrieve email: ${emailId}`);
    }

    // 4. Handle attachments if present
    let attachments = [];

    if (metadata.attachments && metadata.attachments.length > 0) {
      console.log(`Processing ${metadata.attachments.length} attachments`);

      for (const attachment of metadata.attachments) {
        try {
          // Retrieve attachment content
          const attachmentData = await resend.emails.receiving.getAttachment(
            emailId,
            attachment.id
          );

          attachments.push({
            filename: attachment.filename,
            content: Buffer.from(attachmentData.content, 'base64'),
            contentType: attachment.content_type,
          });

          console.log(`Attachment retrieved: ${attachment.filename}`);
        } catch (error) {
          console.error(`Failed to retrieve attachment ${attachment.filename}:`, error);
          // Continue with other attachments
        }
      }
    }

    // 5. Prepare forwarded email
    const forwardedSubject = `${emailData.subject}`;

    // Add forwarding information to email body
    const forwardingHeader = `
      <div style="background: #f0f0f0; padding: 10px; margin-bottom: 20px; border-left: 4px solid #007bff;">
        <strong>Forwarded Email</strong><br>
        <strong>From:</strong> ${emailData.from}<br>
        <strong>To:</strong> ${emailData.to.join(', ')}<br>
        <strong>Subject:</strong> ${emailData.subject}<br>
        <strong>Date:</strong> ${new Date(metadata.created_at).toLocaleString()}<br>
      </div>
    `;

    const forwardingHeaderText = `
========================================
FORWARDED EMAIL
========================================
From: ${emailData.from}
To: ${emailData.to.join(', ')}
Subject: ${emailData.subject}
Date: ${new Date(metadata.created_at).toLocaleString()}
========================================

`;

    // 6. Forward email via SMTP to webmail
    const info = await transport.sendMail({
      from: `"Email Forwarding" <${process.env.WEBMAIL_USER}>`,
      to: process.env.FORWARD_TO_EMAIL,
      subject: forwardedSubject,
      text: forwardingHeaderText + (emailData.text || ''),
      html: forwardingHeader + (emailData.html || emailData.text || ''),
      headers: {
        'X-Original-From': emailData.from,
        'X-Original-To': emailData.to.join(', '),
        'X-Original-Subject': emailData.subject,
        'X-Original-Message-ID': metadata.message_id,
        'X-Forwarded-By': 'Resend Webhook',
        'X-Resend-Email-ID': emailId,
      },
      // Set reply-to to original sender
      replyTo: emailData.from,
      attachments: attachments,
    });

    console.log(`Email forwarded successfully: ${info.messageId}`);
    console.log(`From: ${emailData.from} → To: ${process.env.FORWARD_TO_EMAIL}`);

    // 7. Return success response
    return Response.json({
      success: true,
      emailId: emailId,
      messageId: info.messageId,
      forwarded: true,
    });

  } catch (error) {
    console.error('Webhook error:', error);

    // Return error response (Resend will retry on 5xx errors)
    return Response.json(
      {
        success: false,
        error: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
      },
      { status: 500 }
    );
  }
}

// ============================================
// TEST ENDPOINT (for local testing)
// ============================================

export async function GET() {
  return Response.json({
    status: 'Resend webhook endpoint is running',
    timestamp: new Date().toISOString(),
    config: {
      webmailHost: process.env.WEBMAIL_HOST,
      webmailPort: process.env.WEBMAIL_PORT,
      webmailUser: process.env.WEBMAIL_USER,
      forwardTo: process.env.FORWARD_TO_EMAIL,
      hasResendKey: !!process.env.RESEND_API_KEY,
      hasWebhookSecret: !!process.env.WEBHOOK_SECRET,
    },
  });
}

// ============================================
// ALTERNATIVE: Cloudflare Workers Version
// ============================================

/*
// For Cloudflare Workers, use this structure:

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  try {
    const event = await request.json()

    if (event.type !== 'email.received') {
      return new Response('OK', { status: 200 })
    }

    const emailId = event.data.email_id

    // Fetch email content from Resend
    const emailResponse = await fetch(
      `https://api.resend.com/emails/receiving/${emailId}`,
      {
        headers: {
          'Authorization': `Bearer ${RESEND_API_KEY}`,
        },
      }
    )

    const emailData = await emailResponse.json()

    // Forward via SMTP (use MailChannels or similar for Cloudflare Workers)
    // ... implementation depends on SMTP provider

    return new Response('OK', { status: 200 })

  } catch (error) {
    return new Response(error.message, { status: 500 })
  }
}
*/

// ============================================
// ALTERNATIVE: Express.js Version
// ============================================

/*
// For Express.js, use this structure:

const express = require('express');
const { Resend } = require('resend');
const nodemailer = require('nodemailer');

const app = express();
app.use(express.json());

const resend = new Resend(process.env.RESEND_API_KEY);

const transport = nodemailer.createTransport({
  host: process.env.WEBMAIL_HOST,
  port: parseInt(process.env.WEBMAIL_PORT),
  secure: true,
  auth: {
    user: process.env.WEBMAIL_USER,
    pass: process.env.WEBMAIL_PASSWORD,
  },
});

app.post('/webhooks/resend-inbound', async (req, res) => {
  try {
    const event = req.body;

    if (event.type !== 'email.received') {
      return res.json({ received: true });
    }

    const emailId = event.data.email_id;
    const emailData = await resend.emails.receiving.get(emailId);

    // Forward email logic here (same as above)

    res.json({ success: true });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
*/

// ============================================
// TESTING LOCALLY WITH NGROK
// ============================================

/*
1. Install ngrok: npm install -g ngrok
2. Start your local server: npm run dev
3. Expose with ngrok: ngrok http 3000
4. Copy the ngrok URL (e.g., https://abc123.ngrok.io)
5. Add webhook in Resend dashboard: https://abc123.ngrok.io/api/webhooks/resend-inbound
6. Send test email to your domain
7. Check console logs for webhook activity
*/

// ============================================
// DEPLOYMENT INSTRUCTIONS
// ============================================

/*
VERCEL DEPLOYMENT:

1. Create new Next.js project or use existing:
   npx create-next-app@latest resend-webhook
   cd resend-webhook

2. Install dependencies:
   npm install resend nodemailer svix

3. Create file: app/api/webhooks/resend-inbound/route.js
   (Copy this file's content)

4. Create .env.local file:
   RESEND_API_KEY=re_xxxxxxxxxxxx
   WEBMAIL_HOST=mail.kannakrew.com
   WEBMAIL_PORT=465
   WEBMAIL_USER=admin@kannakrew.com
   WEBMAIL_PASSWORD=your_password
   FORWARD_TO_EMAIL=admin@kannakrew.com
   WEBHOOK_SECRET=your_webhook_secret

5. Deploy to Vercel:
   vercel deploy --prod

6. Add environment variables in Vercel dashboard

7. Get webhook URL: https://your-project.vercel.app/api/webhooks/resend-inbound

8. Configure in Resend dashboard

RAILWAY DEPLOYMENT:

1. Install Railway CLI: npm install -g @railway/cli

2. Create new project: railway init

3. Deploy: railway up

4. Add environment variables: railway variables set RESEND_API_KEY=re_xxx

5. Get URL from Railway dashboard

CLOUDFLARE WORKERS:

1. Install wrangler: npm install -g wrangler

2. Create worker: wrangler init resend-webhook

3. Copy Cloudflare Workers version (see above)

4. Deploy: wrangler publish

5. Add secrets: wrangler secret put RESEND_API_KEY
*/

// ============================================
// MONITORING AND DEBUGGING
// ============================================

/*
// Add these helpers for monitoring:

// Log all webhook events to a database
async function logWebhookEvent(event, status, error = null) {
  // Save to your database for audit trail
  await db.webhookLogs.create({
    emailId: event.data.email_id,
    from: event.data.from,
    to: event.data.to,
    subject: event.data.subject,
    status: status,
    error: error,
    timestamp: new Date(),
  });
}

// Send alert if webhook fails
async function sendAlert(error, emailId) {
  // Send email/SMS/Slack notification
  console.error(`ALERT: Webhook failed for email ${emailId}: ${error.message}`);
}

// Retry failed forwards
async function retryForward(emailId, attempt = 1) {
  if (attempt > 3) {
    await sendAlert(new Error('Max retries exceeded'), emailId);
    return;
  }

  try {
    await forwardEmail(emailId);
  } catch (error) {
    console.log(`Retry ${attempt} failed, retrying in ${attempt * 10} seconds...`);
    setTimeout(() => retryForward(emailId, attempt + 1), attempt * 10000);
  }
}
*/

// ============================================
// ERROR HANDLING BEST PRACTICES
// ============================================

/*
Common errors and solutions:

1. "Authentication failed" (SMTP)
   - Check WEBMAIL_USER and WEBMAIL_PASSWORD
   - Verify SMTP port (465 for SSL, 587 for STARTTLS)
   - Test SMTP connection separately

2. "Invalid API key" (Resend)
   - Verify RESEND_API_KEY starts with "re_"
   - Check key hasn't been revoked
   - Create new API key in Resend dashboard

3. "Email not found" (Resend API)
   - Resend may have temporary delays
   - Implement retry logic
   - Check email_id is correct

4. "Webhook signature verification failed"
   - Get webhook secret from Resend dashboard
   - Verify WEBHOOK_SECRET env var is set
   - Check clock skew (must be within 5 minutes)

5. "Connection timeout" (SMTP)
   - Check firewall rules
   - Verify WEBMAIL_HOST is accessible
   - Test with telnet: telnet mail.kannakrew.com 465

6. "Message size limit exceeded"
   - Check webmail server limits
   - Implement attachment size filtering
   - Compress large attachments

7. "Rate limit exceeded" (Resend)
   - Implement request queuing
   - Add exponential backoff
   - Check Resend plan limits
*/
