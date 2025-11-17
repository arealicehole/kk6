# Resend Email Configuration - Quick Start Guide

**Problem:** Emails received by Resend don't appear in webmail (mail.kannakrew.com)

**Solution:** Webhook-based email forwarding from Resend to webmail

**Research Date:** 2025-11-17

---

## TL;DR - Choose Your Solution

### Option 1: No-Code Solution (RECOMMENDED FOR QUICK START)

**Use Pipedream** - Free, no deployment, 15-30 min setup

**Best for:**
- Non-developers
- Quick testing
- Low to medium volume (<100K emails/month)
- No infrastructure management

**Follow:** `resend-pipedream-no-code-setup.md`

---

### Option 2: Custom Webhook (RECOMMENDED FOR PRODUCTION)

**Deploy your own webhook** - Full control, professional

**Best for:**
- Developers
- High volume (>100K emails/month)
- Full customization needed
- Already have hosting

**Follow:** `resend-webhook-implementation.js`

---

### Option 3: Simple Dual System (NOT RECOMMENDED)

**Point MX to webmail, use Resend manually**

**Best for:**
- Temporary solution only
- Very low email volume
- Willing to check two places

**Problem:** Form submissions won't work, must check Resend dashboard separately

---

## Decision Matrix

| Feature | Pipedream | Custom Webhook | Dual System |
|---------|-----------|----------------|-------------|
| Setup Time | 30 min | 2-4 hours | 5 min |
| Technical Skill | None | Medium | Low |
| Monthly Cost | FREE | $0-20 | $0 |
| Email Limit | 100K/month | Unlimited | N/A |
| Maintenance | None | Low | None |
| Reliability | High | Very High | Medium |
| Customization | Medium | Full | None |
| Form Integration | Yes | Yes | NO |
| **RECOMMENDED?** | **YES** | **YES** | NO |

---

## The Problem Explained Simply

```
Current Situation:
┌──────────────────────────────────────────────┐
│ Email sent to admin@kannakrew.com            │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ MX records point to Resend                   │
│ (Resend receives ALL emails)                 │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ Email stored in Resend dashboard             │
│ ✓ Visible in Resend                          │
│ ✗ NOT visible in webmail                     │
│ ✗ MCP tool can't see it                      │
└──────────────────────────────────────────────┘
```

```
Solution with Webhook Forwarding:
┌──────────────────────────────────────────────┐
│ Email sent to admin@kannakrew.com            │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ Resend receives email + sends webhook        │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ Webhook retrieves full email content         │
│ (via Resend API)                             │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ Webhook forwards via SMTP to webmail         │
│ (mail.kannakrew.com)                         │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ Email appears in webmail inbox               │
│ ✓ Visible in webmail                         │
│ ✓ MCP tool can read via IMAP                 │
│ ✓ User can check in one place                │
└──────────────────────────────────────────────┘
```

---

## Step-by-Step: Pipedream Solution (FASTEST)

### 1. Create Pipedream Account (2 min)
- Go to https://pipedream.com
- Sign up free (no credit card)

### 2. Create Workflow (3 min)
- New Workflow → HTTP/Webhook trigger
- Copy webhook URL (save for later)

### 3. Add Steps (10 min)
- **Step 1:** Filter for `email.received` events
- **Step 2:** Resend → Retrieve Email
- **Step 3:** Email → Send Email (SMTP to webmail)

### 4. Configure Resend (5 min)
- Resend Dashboard → Webhooks
- Add webhook with Pipedream URL
- Select `email.received` event

### 5. Test (5 min)
- Send email to admin@kannakrew.com
- Check Pipedream logs
- Check webmail inbox

### 6. Configure MCP Tool (5 min)
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

**Total Time:** 30 minutes
**Cost:** FREE
**Difficulty:** Easy (no coding)

---

## Step-by-Step: Custom Webhook (PRODUCTION)

### 1. Choose Hosting Platform (10 min)
- **Vercel** (recommended for Next.js)
- **Railway** (easiest deployment)
- **Cloudflare Workers** (fastest performance)

### 2. Deploy Webhook (1-2 hours)
- Copy code from `resend-webhook-implementation.js`
- Set environment variables
- Deploy to platform
- Get webhook URL

### 3. Configure Resend (5 min)
- Same as Pipedream option above

### 4. Test and Monitor (30 min)
- Send test emails
- Check logs
- Set up error alerts
- Document for team

**Total Time:** 2-4 hours
**Cost:** FREE (with free hosting tiers)
**Difficulty:** Medium (requires coding)

---

## DNS Configuration

### Current (Problem State):
```
kannakrew.com MX 9 inbound-smtp.us-east-1.amazonaws.com
```
All emails → Resend (but don't appear in webmail)

### After Webhook Setup (Solution):
```
kannakrew.com MX 9 inbound-smtp.us-east-1.amazonaws.com
```
All emails → Resend → Webhook → Webmail ✓

**No DNS change needed!** Webhook handles forwarding.

---

## What Gets Fixed

### Before (Current Problem):

**Form Submissions:**
- Website form → Resend API ✓
- Email in Resend dashboard ✓
- Email in webmail ✗
- MCP tool sees email ✗

**Regular Emails:**
- Email to admin@kannakrew.com
- Resend receives ✓
- Email in Resend dashboard ✓
- Email in webmail ✗
- MCP tool sees email ✗

### After (With Webhook):

**Form Submissions:**
- Website form → Resend API ✓
- Email in Resend dashboard ✓
- Webhook forwards to webmail ✓
- Email in webmail ✓
- MCP tool sees email ✓

**Regular Emails:**
- Email to admin@kannakrew.com
- Resend receives ✓
- Email in Resend dashboard ✓
- Webhook forwards to webmail ✓
- Email in webmail ✓
- MCP tool sees email ✓

**Everything works in ONE place!**

---

## Required Information

Before starting, gather these:

### Resend:
- [ ] API Key (from https://resend.com/api-keys)
- [ ] Domain verified (kannakrew.com)
- [ ] MX records pointing to Resend

### Webmail:
- [ ] SMTP host: mail.kannakrew.com
- [ ] SMTP port: 465 (SSL) or 587 (TLS)
- [ ] IMAP host: mail.kannakrew.com
- [ ] IMAP port: 993
- [ ] Username: admin@kannakrew.com
- [ ] Password: (your webmail password)

### MCP Tool:
- [ ] Current configuration file location
- [ ] Credentials (same as webmail above)

---

## Testing Checklist

After setup, test these scenarios:

### Basic Email:
- [ ] Send email to admin@kannakrew.com
- [ ] Email appears in Resend dashboard (within 30 sec)
- [ ] Webhook executes (check logs)
- [ ] Email appears in webmail (within 1 min)
- [ ] MCP tool can read email via IMAP

### With Attachments:
- [ ] Send email with PDF attachment
- [ ] Email forwards correctly
- [ ] Attachment included in forwarded email
- [ ] Can download attachment from webmail

### Reply Functionality:
- [ ] Receive forwarded email
- [ ] Click "Reply" in webmail
- [ ] Reply goes to ORIGINAL sender (not webhook)
- [ ] Reply-to header is correct

### Form Submissions:
- [ ] Submit form on website
- [ ] Form email sent via Resend API
- [ ] Email appears in Resend dashboard
- [ ] Webhook forwards to webmail
- [ ] Email readable in webmail
- [ ] MCP tool can see it

### MCP Tool:
- [ ] List inbox emails (should see forwarded emails)
- [ ] Read specific email
- [ ] Send new email
- [ ] Reply to email

---

## Monitoring

### What to Monitor:

**Resend Dashboard:**
- Webhook delivery status
- Failed webhook attempts
- Email receive volume

**Webhook Logs:**
- Successful forwards
- Failed forwards
- Error messages
- Execution time

**Webmail:**
- All emails appearing
- No duplicates
- Attachments working
- Reply-to headers correct

### Set Up Alerts:

**Webhook Failures:**
- Configure in Pipedream/hosting platform
- Email notification on error
- Slack/Discord notification (optional)

**Email Delays:**
- Monitor average forward time
- Alert if >30 seconds
- Check webhook performance

---

## Troubleshooting Common Issues

### "Webhook not receiving events"

**Check:**
1. Webhook URL correct in Resend?
2. Webhook event set to `email.received`?
3. Webhook endpoint accessible publicly?
4. Check Resend webhook logs

**Fix:**
- Test webhook URL in browser (should return 200)
- Use ngrok for local testing
- Check firewall/security settings

---

### "Email not forwarding to webmail"

**Check:**
1. SMTP credentials correct?
2. SMTP port correct (465 or 587)?
3. Webmail server accepting connections?
4. Check webhook execution logs

**Fix:**
- Test SMTP connection separately:
  ```bash
  telnet mail.kannakrew.com 465
  ```
- Verify credentials in webmail
- Check webmail spam folder
- Review webhook error logs

---

### "MCP tool can't see emails"

**Check:**
1. IMAP configured correctly?
2. Connecting to mail.kannakrew.com:993?
3. Emails actually in webmail inbox?
4. IMAP credentials same as webmail login?

**Fix:**
- Test IMAP connection:
  ```bash
  telnet mail.kannakrew.com 993
  ```
- Check webmail folders (Spam, Archive, etc.)
- Verify MCP config file
- Try webmail login directly first

---

### "Attachments not working"

**Check:**
1. Attachment retrieval code added?
2. Base64 encoding correct?
3. Attachment size limits?
4. Webmail server attachment limits?

**Fix:**
- Add attachment handling code (see full guide)
- Check attachment size (<10MB usually safe)
- Test with small attachment first
- Review webhook logs for attachment errors

---

## Cost Breakdown

### Setup Costs:
- **Pipedream:** FREE
- **Custom Webhook:** FREE (using free hosting)
- **Domain/DNS:** Already have
- **Webmail:** Already have

### Monthly Costs:
- **Resend:** FREE tier (100 emails/day) or $20/month
- **Pipedream:** FREE tier (100K invocations) or $19/month
- **Hosting:** FREE tier available on Vercel/Railway
- **Domain/Webmail:** Already paying

**Total Monthly Cost:** $0-40 depending on volume

### Cost Optimization:
- Start with all free tiers
- Upgrade only when you hit limits
- Custom webhook = no per-invocation costs
- Self-hosting = free unlimited

---

## Upgrade Paths

### Starting Out:
1. Use Pipedream free tier (easiest)
2. Test thoroughly
3. Monitor usage

### Growing:
1. Approach 100K emails/month? Deploy custom webhook
2. Need faster response? Switch to Cloudflare Workers
3. Want more control? Self-host on your server

### Scale:
1. High volume? Custom webhook on dedicated server
2. Multiple domains? Multi-tenant webhook
3. Complex logic? Custom business rules

---

## Support and Resources

### Documentation:
- **Main Guide:** `resend-email-configuration-solution.md`
- **Code Implementation:** `resend-webhook-implementation.js`
- **No-Code Guide:** `resend-pipedream-no-code-setup.md`

### External Resources:
- **Resend Docs:** https://resend.com/docs/dashboard/receiving/introduction
- **Pipedream Docs:** https://pipedream.com/docs
- **Resend Discord:** https://resend.com/discord

### Need Help?
1. Check troubleshooting section
2. Review execution logs
3. Test each component separately
4. Ask in Resend Discord community

---

## Success Criteria

You'll know it's working when:

- [ ] Emails to admin@kannakrew.com appear in webmail
- [ ] Form submissions appear in webmail
- [ ] MCP tool can read ALL emails via IMAP
- [ ] MCP tool can send emails via SMTP
- [ ] Reply-to headers work correctly
- [ ] Attachments forward properly
- [ ] No emails missing or delayed >1 minute
- [ ] Webhook logs show 100% success rate

---

## Next Actions

**Choose your path:**

### Path A: Quick Start (Pipedream)
1. ☐ Read `resend-pipedream-no-code-setup.md`
2. ☐ Create Pipedream account
3. ☐ Build workflow (30 min)
4. ☐ Test and verify
5. ☐ Configure MCP tool
6. ☐ Done!

### Path B: Production (Custom Webhook)
1. ☐ Read `resend-email-configuration-solution.md`
2. ☐ Choose hosting platform
3. ☐ Deploy webhook code (2-4 hours)
4. ☐ Configure environment variables
5. ☐ Test and monitor
6. ☐ Configure MCP tool
7. ☐ Set up alerts
8. ☐ Done!

### Path C: Testing First
1. ☐ Start with Pipedream (30 min)
2. ☐ Test thoroughly (1 day)
3. ☐ If satisfied, keep it
4. ☐ If need more control, deploy custom webhook
5. ☐ Migrate to custom solution

**Recommendation:** Start with Pipedream (Path C), then decide.

---

## Timeline

### Minimum Viable Solution (30 minutes):
- Pipedream workflow
- Basic forwarding
- No attachments
- Manual testing

### Production-Ready Solution (4 hours):
- Custom webhook deployed
- Attachment handling
- Error handling and retries
- Monitoring and alerts
- Documentation

### Enterprise Solution (1-2 days):
- High-availability setup
- Load balancing
- Advanced error handling
- Dashboard for monitoring
- Team documentation
- Disaster recovery plan

---

## Final Recommendation

**For kannakrew.com, I recommend:**

1. **Week 1:** Deploy Pipedream solution
   - Quick setup (30 min)
   - Test thoroughly
   - Verify email volume

2. **Week 2-4:** Monitor and optimize
   - Track usage
   - Check for issues
   - Optimize forwarding rules

3. **Month 2:** Decide on long-term
   - If <100K emails/month → Keep Pipedream
   - If >100K emails/month → Deploy custom webhook
   - If complex needs → Custom webhook

**This approach:**
- Gets you working FAST (30 min)
- Costs nothing initially
- Easy to upgrade later
- No infrastructure management
- Full flexibility to change

**Start here:** `resend-pipedream-no-code-setup.md`

---

## Questions?

Common questions answered:

**Q: Will this break my website forms?**
A: No! Forms continue working exactly as before.

**Q: Will I lose any emails during setup?**
A: No! Resend stores all emails, even if webhook is down.

**Q: What if webhook fails?**
A: Emails stay in Resend dashboard, webhook retries automatically.

**Q: Can I see emails in both places?**
A: Yes! Resend dashboard AND webmail both have copies.

**Q: What about spam/security?**
A: Resend handles spam filtering, webhook forwards everything.

**Q: How fast is forwarding?**
A: Usually <5 seconds from Resend to webmail.

**Q: What if I exceed free tier?**
A: Upgrade to paid ($19-20/month) or deploy custom webhook.

**Q: Can I use different SMTP for sending?**
A: Yes! Use Resend SMTP for sending, webmail IMAP for reading.

**Q: Is this production-ready?**
A: Yes! Pipedream has 99.9% uptime, used by thousands of companies.

**Q: Can I customize forwarding logic?**
A: Yes! Add custom code steps in Pipedream or use custom webhook.

---

## Summary

**Problem:** Resend receives emails, but they don't appear in webmail

**Solution:** Webhook forwards emails from Resend to webmail via SMTP

**Best Option:** Start with Pipedream (free, no-code, 30 min setup)

**Result:** All emails in one place, MCP tool works perfectly

**Get Started:** Read `resend-pipedream-no-code-setup.md`

**Questions:** Check main guide `resend-email-configuration-solution.md`

---

**Ready to begin? Pick your guide and start!**

- 🚀 **Quick Start:** `resend-pipedream-no-code-setup.md`
- 🔧 **Production:** `resend-webhook-implementation.js`
- 📚 **Deep Dive:** `resend-email-configuration-solution.md`
