#!/usr/bin/env node
/**
 * Standalone Email Forwarder
 * Fetches new emails from Resend and forwards them to mail.kannakrew.com via SMTP
 *
 * Usage: node forward-resend-emails.js
 *
 * Tracks processed emails in forward-tracker.json to avoid duplicates
 */

const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// Configuration
const RESEND_API_KEY = 're_5RBepRp2_Pmi8ccadxi5LqrPHSPFUtEz2';
const SMTP_HOST = 'mail.kannakrew.com';
const SMTP_PORT = 465;
const SMTP_USER = 'admin@kannakrew.com';
const SMTP_PASS = 'Rebelde123';
const TRACKER_FILE = path.join(__dirname, 'forward-tracker.json');

// Load processed email IDs
function loadProcessedIds() {
  try {
    if (fs.existsSync(TRACKER_FILE)) {
      const data = fs.readFileSync(TRACKER_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('Error loading tracker file:', error.message);
  }
  return [];
}

// Save processed email IDs
function saveProcessedIds(ids) {
  try {
    fs.writeFileSync(TRACKER_FILE, JSON.stringify(ids, null, 2));
  } catch (error) {
    console.error('Error saving tracker file:', error.message);
  }
}

// Fetch received emails from Resend
async function fetchReceivedEmails() {
  try {
    const response = await fetch('https://api.resend.com/emails/receiving', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Resend API error: ${error.message || response.statusText}`);
    }

    const result = await response.json();
    return result.data || [];
  } catch (error) {
    console.error('Error fetching emails from Resend:', error.message);
    throw error;
  }
}

// Fetch full email content
async function fetchEmailContent(emailId) {
  try {
    const response = await fetch(`https://api.resend.com/emails/receiving/${emailId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Resend API error: ${error.message || response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching email content for ${emailId}:`, error.message);
    throw error;
  }
}

// Forward email via SMTP
async function forwardEmail(email, emailContent, transporter) {
  const mailOptions = {
    from: '"Resend Forward" <admin@kannakrew.com>',
    to: 'admin@kannakrew.com',
    subject: `[FWD] ${email.subject}`,
    html: `
      <div style="background: #f5f5f5; padding: 10px; border-left: 4px solid #0070f3; margin-bottom: 20px;">
        <p style="margin: 5px 0;"><strong>From:</strong> ${email.from}</p>
        <p style="margin: 5px 0;"><strong>To:</strong> ${Array.isArray(email.to) ? email.to.join(', ') : email.to}</p>
        <p style="margin: 5px 0;"><strong>Subject:</strong> ${email.subject}</p>
        <p style="margin: 5px 0;"><strong>Date:</strong> ${email.created_at}</p>
      </div>
      ${emailContent.html || emailContent.text || 'No content available'}
    `,
    text: `
==== FORWARDED EMAIL ====
From: ${email.from}
To: ${Array.isArray(email.to) ? email.to.join(', ') : email.to}
Subject: ${email.subject}
Date: ${email.created_at}
========================

${emailContent.text || emailContent.html || 'No content available'}
    `,
    headers: {
      'X-Original-From': email.from,
      'X-Original-To': Array.isArray(email.to) ? email.to.join(', ') : email.to,
      'X-Original-Subject': email.subject,
      'X-Forwarded-By': 'Standalone-Email-Forwarder'
    }
  };

  await transporter.sendMail(mailOptions);
}

// Main execution
async function main() {
  console.log('🚀 Starting email forwarder...\n');

  // Load tracker
  const processedIds = loadProcessedIds();
  console.log(`📋 Loaded ${processedIds.length} processed email IDs\n`);

  // Create SMTP transporter
  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: SMTP_PORT,
    secure: true,
    auth: {
      user: SMTP_USER,
      pass: SMTP_PASS
    }
  });

  try {
    // Fetch received emails
    console.log('📥 Fetching emails from Resend...');
    const receivedEmails = await fetchReceivedEmails();
    console.log(`✅ Found ${receivedEmails.length} total emails in Resend\n`);

    // Filter new emails
    const newEmails = receivedEmails.filter(email => !processedIds.includes(email.id));
    console.log(`🆕 Found ${newEmails.length} new emails to forward\n`);

    if (newEmails.length === 0) {
      console.log('✨ All caught up! No new emails to forward.');
      return;
    }

    // Process each new email
    const newlyProcessedIds = [];
    for (let i = 0; i < newEmails.length; i++) {
      const email = newEmails[i];
      console.log(`[${i + 1}/${newEmails.length}] Processing: ${email.subject}`);
      console.log(`   From: ${email.from}`);
      console.log(`   Date: ${email.created_at}`);

      try {
        // Fetch full content
        const emailContent = await fetchEmailContent(email.id);

        // Forward via SMTP
        await forwardEmail(email, emailContent, transporter);

        newlyProcessedIds.push(email.id);
        console.log(`   ✅ Forwarded successfully\n`);
      } catch (error) {
        console.error(`   ❌ Failed: ${error.message}\n`);
      }
    }

    // Update tracker
    if (newlyProcessedIds.length > 0) {
      const updatedIds = [...processedIds, ...newlyProcessedIds];
      saveProcessedIds(updatedIds);
      console.log(`\n✅ Successfully forwarded ${newlyProcessedIds.length} emails`);
      console.log(`📋 Total tracked emails: ${updatedIds.length}`);
    }

  } catch (error) {
    console.error('\n❌ Fatal error:', error.message);
    process.exit(1);
  }
}

// Run
main().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});
