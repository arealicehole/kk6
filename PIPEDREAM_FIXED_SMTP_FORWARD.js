import { axios } from "@pipedream/platform"
import nodemailer from "nodemailer"

export default defineComponent({
  name: "Forward New Received Emails via SMTP",
  description: "Check for new emails in Resend account and forward them DIRECTLY to mail.kannakrew.com via SMTP (bypassing MX loop). Tracks processed emails to avoid duplicates.",
  type: "action",
  props: {
    resend: {
      type: "app",
      app: "resend",
    },
    data_store: {
      type: "data_store",
      label: "Data Store",
      description: "Data store to track processed email IDs"
    },
    smtp_password: {
      type: "string",
      label: "SMTP Password",
      description: "Password for admin@kannakrew.com",
      secret: true,
      default: "Rebelde123"
    }
  },
  async run({ $ }) {
    // Get list of processed email IDs from data store
    const processedEmailIds = (await this.data_store.get("processed_emails")) || [];

    // Get received emails from Resend
    const receivedEmailsResponse = await axios($, {
      method: "GET",
      url: "https://api.resend.com/emails/receiving",
      headers: {
        Authorization: `Bearer ${this.resend.$auth.api_key}`,
        "Content-Type": "application/json",
      },
    });

    const receivedEmails = receivedEmailsResponse.data || [];
    let newEmailsCount = 0;
    const newlyProcessedIds = [];

    // Create SMTP transporter - DIRECTLY to mail.kannakrew.com (NOT through Resend!)
    const transporter = nodemailer.createTransport({
      host: "mail.kannakrew.com",
      port: 465,
      secure: true, // SSL
      auth: {
        user: "admin@kannakrew.com",
        pass: this.smtp_password
      }
    });

    // Process each email
    for (const email of receivedEmails) {
      // Skip if already processed
      if (processedEmailIds.includes(email.id)) {
        continue;
      }

      try {
        // Get full email content
        const emailContentResponse = await axios($, {
          method: "GET",
          url: `https://api.resend.com/emails/receiving/${email.id}`,
          headers: {
            Authorization: `Bearer ${this.resend.$auth.api_key}`,
            "Content-Type": "application/json",
          },
        });

        const emailContent = emailContentResponse;

        // Get attachments if any
        let attachments = [];
        if (email.attachments && email.attachments.length > 0) {
          const attachmentsResponse = await axios($, {
            method: "GET",
            url: `https://api.resend.com/emails/receiving/${email.id}/attachments`,
            headers: {
              Authorization: `Bearer ${this.resend.$auth.api_key}`,
              "Content-Type": "application/json",
            },
          });

          // Download and encode attachments
          for (const attachment of attachmentsResponse.data || []) {
            const attachmentDetailsResponse = await axios($, {
              method: "GET",
              url: `https://api.resend.com/emails/receiving/${email.id}/attachments/${attachment.id}`,
              headers: {
                Authorization: `Bearer ${this.resend.$auth.api_key}`,
                "Content-Type": "application/json",
              },
            });

            if (attachmentDetailsResponse.download_url) {
              const fileResponse = await axios($, {
                method: "GET",
                url: attachmentDetailsResponse.download_url,
                responseType: "arraybuffer"
              });

              const buffer = Buffer.from(fileResponse);
              attachments.push({
                filename: attachment.filename,
                content: buffer.toString('base64'),
                contentType: attachment.content_type,
              });
            }
          }
        }

        // Forward the email via SMTP (NOT Resend API!)
        const mailOptions = {
          from: `"Resend Forward" <admin@kannakrew.com>`,
          to: "admin@kannakrew.com", // This will deliver directly via SMTP, NOT through MX/Resend
          subject: `[FWD] ${email.subject}`,
          html: `
            <div style="background: #f5f5f5; padding: 10px; border-left: 4px solid #0070f3; margin-bottom: 20px;">
              <p style="margin: 5px 0;"><strong>From:</strong> ${email.from}</p>
              <p style="margin: 5px 0;"><strong>To:</strong> ${email.to.join(', ')}</p>
              <p style="margin: 5px 0;"><strong>Subject:</strong> ${email.subject}</p>
              <p style="margin: 5px 0;"><strong>Date:</strong> ${email.created_at}</p>
            </div>
            ${emailContent.html || emailContent.text || 'No content available'}
          `,
          text: `
==== FORWARDED EMAIL ====
From: ${email.from}
To: ${email.to.join(', ')}
Subject: ${email.subject}
Date: ${email.created_at}
========================

${emailContent.text || emailContent.html || 'No content available'}
          `,
          attachments: attachments,
          // Preserve original headers
          headers: {
            'X-Original-From': email.from,
            'X-Original-To': email.to.join(', '),
            'X-Original-Subject': email.subject,
            'X-Forwarded-By': 'Pipedream-Resend-SMTP-Forwarder'
          }
        };

        // Send via SMTP
        await transporter.sendMail(mailOptions);

        newlyProcessedIds.push(email.id);
        newEmailsCount++;

      } catch (error) {
        console.error(`Failed to process email ${email.id}:`, error);
        throw error; // Re-throw to see full error in Pipedream logs
      }
    }

    // Update data store with newly processed email IDs
    if (newlyProcessedIds.length > 0) {
      const updatedProcessedIds = [...processedEmailIds, ...newlyProcessedIds];
      await this.data_store.set("processed_emails", updatedProcessedIds);
    }

    $.export("$summary", `Successfully forwarded ${newEmailsCount} new ${newEmailsCount === 1 ? 'email' : 'emails'} via SMTP to mail.kannakrew.com`);

    return {
      total_received_emails: receivedEmails.length,
      new_emails_forwarded: newEmailsCount,
      newly_processed_ids: newlyProcessedIds,
      total_processed_count: processedEmailIds.length + newlyProcessedIds.length
    };
  },
});
