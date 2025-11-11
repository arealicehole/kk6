# K
## 2025-11-11 (EARLY MORNING UPDATE)

### EMAIL AUTOMATION SYSTEM COMPLETE

**Claude can now manage KannaKrew email operations!**

### What Was Built:
- **Email Reading:** MCP email client connected to admin@kannakrew.com (SiteGround IMAP/SMTP)
- **Email Sending:** Direct Resend API integration for sending from admin@kannakrew.com
- **Scheduled Sending:** Emails can be scheduled up to 30 days in advance via Resend API
- **Two Resend Accounts:**
  - Account #1: kannakickback.com (website contact forms)
  - Account #2: kannakrew.com (email outreach & scheduling)

### Technical Setup:
- **MCP Server:** mcp-email-client installed and configured
- **Resend Domain:** kannakrew.com verified with SPF/DKIM records
- **API Access:** Direct curl-based API calls (no Netlify functions needed)
- **Environment Variable:** RESEND_API_KEY_KANNAKREW set for API authentication

### Capabilities Now Available:
- Read inbox, search emails, send immediate, schedule future, reply to emails

### Issues Resolved:
- Fixed MCP server package, env variable names, scheduling parameter, config priority

### Testing Completed:
- Inbox reading: 10 emails retrieved successfully
- Immediate sending: Email delivered
- Scheduled sending: Email properly queued
- API authentication: kannakrew.com domain verified

### Next Steps:
- Use for real vendor outreach campaigns
- Monitor spam folder - may need to warm up domain

---

ANNA KICKBACK 6 - WORKING NOTES
**Live document for daily updates, decisions, and changes**

---

## 2025-11-10 (EVENING UPDATE)

### 🎉 WEBSITE DEPLOYED TO PRODUCTION!

**✅ SITE IS LIVE:** https://kannakickback.com

### Deployment Details:
- **Repo Created:** Private GitHub repo `kk6-prod` (https://github.com/arealicehole/kk6-prod)
- **Hosting:** Netlify with custom domain
- **DNS Configured:** A record (75.2.60.5) and CNAME (www → kannakickback.netlify.app)
- **SSL:** ✅ Working with auto-renewal enabled
- **Domain Verified:** Both Netlify AND Resend domains verified
- **Forms Tested:** All 4 forms (RSVP, Vendor, Box Host, General) working and sending emails to admin@kannakrew.com

### Bug Fixes Deployed:
1. **Fixed contact.js email:** Changed default from `hello@` to `admin@kannakrew.com`
2. **Fixed form submission bug:** Users can now submit multiple forms in same session
   - **Root Cause:** Button re-enable was delayed in setTimeout (5 seconds)
   - **Fix:** Button now re-enables immediately after successful submission
   - **Result:** Users can switch form tabs and submit again without refresh

### Technical Stack Confirmed:
- **Frontend:** Static HTML/CSS/JS
- **Backend:** Netlify serverless functions
- **Email:** Resend API (domain verified: kannakickback.com)
- **Deployment:** GitHub → Netlify auto-deploy
- **Environment Variables Set:**
  - `RESEND_API_KEY` ✅
  - `CONTACT_EMAIL=admin@kannakrew.com` ✅

### What Works:
- ✅ All pages loading correctly (index.html, partners.html)
- ✅ Mobile responsive design
- ✅ All 4 contact forms functional
- ✅ Email notifications arriving
- ✅ SSL certificate active
- ✅ Custom domain routing
- ✅ Multi-form submissions in same session

### Next Steps:
- Share live site with team for feedback
- Add confirmed box locations as they come in
- Test all forms again from different devices
- Monitor Resend dashboard for email deliverability

---

## 2025-11-10

### Summary:
- **🚨 VENUE CRISIS**: Ginza patio renovated WITHOUT notice - cactus planted in ground, cutting usable space in HALF
- Stage area moved/rearranged (antique rug on dirt)
- Capacity concerns - may only fit vendors in wooden beam section now
- Sojourner contact confirmed: Berkeley (480-518-4527) - Assistant Director of Community Engagement
- Sojourner date reconfirmed: Dec 8-20 acceptance window
- Pinata ordered: Giant ornament design, ~$100 for life-size version
- AI content system created for kickback (auto-generates social posts)
- Urgent: Need flyer, video, or paid ads out ASAP
- Toy boxes need to get to locations immediately
- **✅ WEBSITE COMPLETED**: Full KannaKickback.com site built and ready to deploy!
- **✅ WEBSITE AUDIT COMPLETED**: Transformed site into hybrid pitch deck + event page
- **✅ ADDED CRITICAL SECTIONS**: FAQ, About KannaKrew, Event Day Schedule
- **⏸️ PARTNERS PAGE ON HOLD**: Built `/partners.html` but needs design refinement

### Decisions Made:
- **PINATA**: Going with giant ornament design, ~$100 for life-size
- **SOJOURNER OUTREACH**: Requested on-camera interview for video content
- Keeping Dec 15 as toy drive cutoff (within their Dec 8-20 window)
- **WEBSITE STRATEGY**: Single site with two audiences
  - Main site (index.html): Community-focused, fun language, no demographics/ROI talk
  - Partners page (partners.html): Pitch deck with business data, demographics, testimonials
  - Strategy: Attendees never see corporate speak, partners get all the data they need
  - Partners page on hold pending design improvements

### Action Items:
1. **🚨 URGENT**: Schedule Ginza walkthrough to assess venue changes - Due: ASAP
2. **🚨 URGENT**: Talk to Maggie about venue renovations without notice - Due: ASAP
3. Send pinata design (ornament) to vendor with logo/branding specs - Due: Nov 10
4. ✅ **Schedule video interview with Berkeley** - She's available! Need to propose date/time/location - Due: Nov 11
5. Create flyer/video/paid ad - Due: Nov 10-11 (CRITICAL)
6. Get toy boxes to locations - Due: Nov 13
7. ✅ **Deploy kannakickback.com** - Website files ready in /website folder - Due: Nov 10-11
8. Set up Resend account and get API key for contact forms - Due: Nov 11
9. Update website with confirmed box locations as they're added - Ongoing

### Issues/Blockers:
- **🔴 CRITICAL**: Ginza venue capacity cut in HALF by unexpected cactus planting
  - Cactus planted directly in ground (not in movable buckets as agreed)
  - May only fit vendors in small wooden section
  - Stage moved to accommodate new layout
  - Discussing if event is still viable at this location
- Menu still not approved by Maggie
- Need new venue photos to assess damage
- Capacity concerns: Can we still fit 10 vendor booths + guests?

### Notes:
- Processed 4 transcripts from Nov 10 (deleted 1 non-relevant)
- Berkeley at Sojourner is key contact for toy donations
- Pinata vendor has email, waiting on design confirmation
- AI system can now auto-generate Instagram posts (already created Post #1)

**Website Audit & Enhancements:**
- Researched best practices for event pages vs pitch decks, created hybrid framework
- **Main Site Additions (index.html):**
  - FAQ section with 3 categories: Event, Donating, Partnering (15+ questions answered)
  - About KannaKrew section: Mission, history timeline KK1-KK6, contact info
  - Event Day Schedule: Detailed 2PM-6PM timeline with 8 time blocks
  - Cleaned up corporate language ("limited space" → "reach out soon")
  - Added strategic CTAs linking to partners page
- **Partners Page Created (partners.html):**
  - Community reach data (attendance growth, demographics, social reach)
  - Partnership options: Vendor (FREE booths), Box Host (FREE), Sponsor (custom packages)
  - 6 value propositions for partners (targeted audience, growth, brand association, etc.)
  - Track record timeline showing KK1 (2020) → KK6 (2025) with donation amounts
  - Testimonial section (placeholder quotes ready for real testimonials)
  - 3 application forms: Vendor, Box Host, Sponsor inquiry
  - **STATUS**: Built but design needs refinement - on hold for now
- **Strategy Success**: Main site stays fun/community-focused, business data hidden on partners page
- **Files Updated**: index.html, style.css, partners.html, partners.css
- Team is getting anxious about timeline - only 26 days left
- Considering whether to cancel event due to venue issues
- **Discord #ppk-general checked:** Posted as Ghost of Christmas Hash (Nov 10)
- **FLYER DISTRIBUTION OPP:** Nov 29 - Stoner talent show at Lacuna (5pm) - perfect for ground game
- Discord shows team was asking about posts/marketing on Nov 5 - people are waiting for content!

### Website Built Today (Nov 10):
- **Location:** `/website` folder in project
- **Stack:** Static HTML/CSS/JS + Netlify serverless functions
- **Features:**
  - Full responsive design (mobile, tablet, desktop)
  - Cannabis/holiday themed (green, red, gold colors)
  - Modular sections: About, Donate, Events, Partners, Contact
  - 3 contact forms: Vendor application, Box host signup, General inquiry
  - Form handling via Resend API (serverless function)
  - Timeline of toy drive dates
  - Impact stats from previous years
  - Easy to edit and update content
- **Ready to deploy:** Just need to push to GitHub and connect to Netlify
- **Domain ready:** kannakickback.com already owned
- **Next steps:** Set up Resend account, deploy to Netlify, add box locations as confirmed

---

## 2025-11-09

### Summary:
- Organized all transcripts and chat files into /raw folder
- Read through all planning materials (Nov meetings, Oct calls, chat files)
- Created project structure with tracking docs
- ✅ **CRITICAL INFO RECEIVED:** Sojourner Center toy drop-off window confirmed!

### Decisions Made:
- ✅ **TOY DRIVE TIMELINE CONFIRMED**
  - Box placement: Week of Nov 11-15
  - Collection period: Nov 15 - Dec 15, 2025 (exactly 1 month)
  - Sojourner Center accepts toys Dec 8-20
  - We're cutting off public collection Dec 15
  - Gives us 1-2 days to collect from all boxes and deliver to Sojourner by Dec 16-17
  - This unblocks ALL vendor and dispensary emails!

### Action Items for Tomorrow:
1. ✅ ~~Call Sojourner Center~~ DONE - Dec 15 cutoff set
2. Gilbert calls Maggie for menu approval
3. Start flyer design (MUST include Dec 15 date)
4. Create donation boxes
5. **SEND EMAILS NOW** - Dispensaries and vendors (no longer blocked!)

### Issues/Blockers:
- ✅ ~~Sojourner Center cutoff date unknown~~ RESOLVED - Dec 15!
- 🔴 Menu not approved (blocking design/print)
- 🟡 Behind schedule on box placement (should've started 11/11)

### Notes:
- All transcripts now in /raw folder: /raw/t for transcripts, /raw/c for chat files
- Marketing plan from Nov 6 meeting is solid
- Need to assign content calendar (who posts what)
- **DIRECTORY RESTRUCTURE:** Organized all files into clean structure (communications, creative, operations)
  - Email templates → communications/emails/
  - Social post content → creative/social/
  - Flyer brief → creative/print/
  - See README.md for navigation guide

---

## 2025-11-08

### Summary:
[Placeholder - add daily notes here]

### Decisions Made:
[Log any choices made]

### Action Items:
[What needs to happen tomorrow]

### Issues/Blockers:
[What's stopping progress]

### Notes:
[Any other relevant info]

---

## DECISIONS LOG

### Toy Drive Cutoff Date:
- **Status:** ✅ DECIDED
- **Decision:** December 15, 2025
- **Date Decided:** November 9, 2025
- **Rationale:** Sojourner Center accepts donations Dec 8-20. Cutting off Dec 15 gives us a week to collect all boxes and deliver by Dec 16-17.
- **Impact:** UNBLOCKS all vendor emails, dispensary outreach, box placement coordination

### Custom Wrapping Paper:
- **Status:** PENDING
- **Discussion:** Mentioned Nov 6 - would be cool for sales potential
- **Decision Needed By:** Nov 15 (if ordering)
- **Notes:** Would have Kanna Claus design, could sell rolls

### Pinata Design:
- **Status:** ✅ DECIDED
- **Decision:** Giant ornament design (like Christmas ornament)
- **Size:** Life-size (~$100 version)
- **Style:** 70s claymation Rudolph vibes
- **Date Decided:** November 10, 2025
- **Vendor:** Dosaria pinata shop (has Gilbert's email)
- **Next Step:** Send final design with logo/branding specs

### Dispensary Worker Incentive:
- **Status:** PENDING
- **Options:**
  1. First 15 with dispensary ID get special kit
  2. Raffle for all dispensary workers
  3. Hats instead of shirts (dress code friendly)
- **Decision Needed By:** Nov 20
- **Notes:** Hats might be best - easier to distribute, dress code compliant

### Venue Layout:
- **Status:** ⚠️ CRISIS - Needs immediate resolution
- **Issue:** Ginza owner's dad planted cactus in patio ground without notice
- **Impact:** Cut usable space in HALF, stage moved
- **Original Agreement:** Cactus in movable buckets
- **Actual:** Planted directly in ground with terrace planters
- **Concern:** Can we still fit 10 vendor booths + 100+ guests?
- **Next Step:** Walkthrough with photos, talk to Maggie ASAP

### Transportation:
- **Status:** PENDING/ISSUE
- **Discussion:** School bus people ghosted
- **Decision Needed:** Do we need alternative transportation? For what?
- **Notes:** Unclear if this was for guests or for box pickup

### Podcast Recording Start:
- **Status:** PENDING
- **Decision:** When to record Episode 1?
- **Recommendation:** Week of Nov 16
- **Notes:** Need 6-7 episodes before Dec 6

---

## CONTACT INFO COLLECTED

### Confirmed:
- **Maggie** (Ginza owner) - Gilbert has contact
- **Cherry Bomb** - Responded via Instagram/Facebook
- **Sojourner Center** - Main: (602) 244-0997
  - **Berkeley** - Assistant Director of Community Engagement - **480-518-4527** (cell) - Key contact for toy donations
    - ✅ **Confirmed available for on-camera interview** - "depending on when and where"
    - Need to propose: date, time, location
  - **Jill** - Main receptionist
- **Pinata Vendor** (Dosaria location) - Has Gilbert's email, working on ornament design

### Need to Find:
- Chill Pipe contact
- Greek Glasses contact
- Special K contact
- Brian Jacobs contact
- Bong Blazer contact
- D1 contact
- Tom Palms contact
- Toy Store contact

---

## VENDOR COMMITMENTS

### Confirmed:
- Cherry Bomb - interested, waiting for details

### Pending:
- Chill Pipe - 30 bongs (gave last year)
- Greek Glasses - bongs (sent stuff before)
- Special K - 20 bongs (NOTE: might owe them payment from last year)
- Brian Jacobs - glass
- Tom Palms - box hosting

### Reached Out:
- None yet

---

## BOX LOCATIONS

### Confirmed:
- Toy Store (confirmed willing)

### Likely:
- Tom Palms
- Cherry Bomb

### To Contact:
- East Valley dispensaries (need list)
- Smoke shops
- Food joints

---

## CONTENT IDEAS CAPTURED

From transcripts/meetings:
- Map video showing all 6 KK locations over the years
- Fake AI documentary about Kanna Claus origin
- Crane game highlight reels from past events
- Countdown series with AI-generated pop culture characters
- Vendor spotlight posts
- Toy collection progress updates ("We're at $X in toys!")
- Behind-the-scenes prep content
- Podcast clips (1-min reels)

---

## QUESTIONS TO RESOLVE

1. ✅ ~~**When is Sojourner Center's cutoff date for toy delivery?**~~ RESOLVED: Dec 8-20 window, our cutoff Dec 15
2. **Does Maggie approve the menu?** 🔴 CRITICAL
3. **Do we owe Special K money from last year?** 🟡 IMPORTANT
4. **What was the transportation issue?** 🟢 CLARIFY
5. **Where exactly are the vendor booth areas?** (Patio + dirt overflow)
6. **Do we have a target attendance number?**
7. **Who owns what in the content calendar?** (Gilbert, Speaker A, Dom split)

---

## RANDOM NOTES & IDEAS

- Nov 6 meeting mentioned "ramen addition" - what is this?
- Consider making Kanna Claus a recurring character (AI avatar?)
- Podcast could become annual tradition, not just KK6
- Glass blowers might form their own community through this
- Arizona glass community seems tight-knit, leverage that
- "All K's, no C's" branding is strong, lean into it
- Sojourner Center connection is personal - emphasize in storytelling

---

## MEETING RECAP: NOV 6, 2025 (Big Planning Session)

**Attendees:** Gilbert, Speaker A, Dom (via Discord)

**Key Points:**
- Marketing plan finalized (15 posts, every other day)
- Target: Beat $6,500 in toys
- Toy drive: Nov 1 - Dec 7 (end date TBD)
- Location: Ginza, Gold Canyon, 2-6pm Dec 6
- Content split: 5 posts each (Gilbert, Speaker A, Dom)
- Tone: Wholesome, fun, not too weed-heavy
- Paid ads 2 weeks before
- Vendor goal: 10 booths
- Dispensary worker incentive discussed

**Action Items from Meeting:**
- Design flyer
- Create donation boxes
- Finalize menu
- Send vendor emails
- Send dispensary emails
- Start content creation
- Launch social campaign Nov 7 (DELAYED)

---

## PARKING LOT (Future Ideas)

- Explore making this a bigger event each year
- Consider other charities or causes for future KKs
- Document everything for KK7 planning
- Build relationships with vendors for year-round partnerships
- Create Kanna Claus as permanent mascot/character
- Annual podcast series tradition?
- Expand to other Arizona cities?

---

**Instructions:**
- Add daily updates at the top
- Log all decisions in DECISIONS LOG
- Track contact info as you collect it
- Note any new ideas in PARKING LOT
- Move resolved questions out
- Keep this messy and real - it's a working doc!

**Last Updated:** 2025-11-09 @ [time]
**Next Update:** Daily
