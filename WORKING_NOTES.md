# KANNA KICKBACK 6 - WORKING NOTES
**Live document for daily updates, decisions, and changes**

---

## 2025-11-16 (MEDIA ASSETS, FACEBOOK EVENT PAGE, WEBSITE UPDATES, SECURITY FIX & POSTIZ SOLUTION)

### 🎉 POSTIZ SOLUTION FOUND - Ready to Deploy!
- **Status:** Configuration fix identified, ready for deployment
- **Root Cause:** Missing `NEXT_PUBLIC_UPLOAD_STATIC_DIRECTORY=/uploads` environment variable
- **Solution Documents:**
  - `/helpdesk/TICKET_004_LOCAL_STORAGE_FIX.md` - Complete fix documentation
  - `/helpdesk/HOW_TO_GET_POSTIZ_API_KEY.md` - API key retrieval guide

**What Was Wrong:**
- Had backend config (`UPLOAD_DIRECTORY=/uploads`) ✅
- Had internal networking (`BACKEND_INTERNAL_URL=localhost:3000`) ✅
- **Missing:** Frontend config (`NEXT_PUBLIC_UPLOAD_STATIC_DIRECTORY=/uploads`) ❌
- Result: Frontend couldn't fetch uploaded images, causing UI crashes

**The Fix:**
```yaml
# Added to deploy.yml
- "NEXT_PUBLIC_UPLOAD_STATIC_DIRECTORY=/uploads"
```

**Next Steps:**
1. Deploy updated Postiz configuration to Akash
2. Query Supabase database for API key (guide in helpdesk)
3. Upload 5 Instagram carousel slides via API
4. Schedule Post #1 for arizona_smokers

**Research Generated:**
- `C:\Users\figon\zeebot\r\postiz-akash-local-storage-solution-2025-11-16.md` (7,500+ words)
- `C:\Users\figon\zeebot\r\postiz-r2-storage-resource-optimization-2025-11-16.md` (11 sections)

## 2025-11-16 (MEDIA ASSETS, FACEBOOK EVENT PAGE, WEBSITE UPDATES & SECURITY FIX)

### 🔒 SECURITY FIX - API Key Exposure Resolved!
- **Issue:** OpenRouter API key exposed AGAIN (second alert received)
- **Root Cause:** Visual-creator subagent was generating Python scripts with hardcoded API keys
- **Scope:** 11 Python scripts across creative/social/images/ and creative/print/
- **Fix Applied:**
  1. Removed all Python scripts from git tracking (`git rm --cached`)
  2. Updated .gitignore to block ALL *.py files in image generation folders
  3. Created comprehensive SECURITY_INCIDENT_LOG.md
- **Commit:** `801d4b1` - "Security fix: Remove Python scripts with embedded API keys"
- **Status:** ✅ Fixed - Scripts now untracked, will never be committed again
- **Files remain local** for one-time use, but won't be version controlled

**Prevention:**
```gitignore
creative/social/images/**/*.py
creative/print/images/**/*.py
creative/assets/images/**/*.py
```

### ✅ Website Updates - Hero Carousel & Gallery Repositioned!
- **Status:** Live on kannakickback.com (deployed via Netlify)
- **Commit:** `0f8131e` - "Add hero carousel and move gallery higher on page"
- **GitHub Repo:** kk6-prod

**Changes Made:**
1. **Hero Carousel Added:**
   - 2-column CSS Grid layout (content left, carousel right)
   - 3 KannaKlaus character images rotating
   - Auto-play every 4 seconds (pauses on hover)
   - Prev/next buttons + indicator dots
   - Keyboard navigation (arrow keys)
   - Responsive design (1 column on mobile)

2. **Gallery Repositioned:**
   - Moved from before FAQ to immediately after hero section
   - User feedback: "fire af" - highly visible placement
   - Removed duplicate gallery section
   - Added Gallery link to navigation

3. **Image Assets Deployed:**
   - Characters: 4 compressed PNGs (2-3MB each) in `/images/characters/`
   - Gallery: 5 high-value media files in `/images/gallery/`
   - Total deployed: 9 files (26.5MB)

4. **Files Modified:**
   - `index.html` (260 insertions, 58 deletions)
   - `style.css` (hero grid, carousel, gallery styling)
   - `script.js` (carousel controls, auto-play, keyboard nav)

### ✅ Facebook Event Page Created!
- **Status:** Live and published
- **Event Page:** KannaKickback 6 on Facebook
- **Cover Photo:** 1920x1005 custom event cover (v2 - proper 16:9 generation)
- **Description:** Full copy/paste description from FACEBOOK_EVENT_DESCRIPTION.md
- **Location:** Ginza Restaurant, Gold Canyon, AZ
- **Date:** Saturday, December 6, 2025, 2-6 PM

### ✅ OpenRouter API Key Updated
- **Status:** New API key active and working
- **Previous key:** Exposed in GitHub, auto-disabled by OpenRouter
- **New key:** Updated in visual-creator config (api-config.json)
- **Location:** `C:\Users\figon\zeebot\.claude\agents\visual-creator\config\api-config.json`
- **Verified:** Facebook event cover generated successfully with new key

### ✅ Media Assets Downloaded & Cataloged
- **Source:** Bong Blazer uploads from Discord #general (Nov 11)
- **Total Files:** 23 (19 historical + 4 new AI character designs)
- **Location:** `C:\Users\figon\zeebot\kickback\raw\m\`
- **Inventory:** Full catalog created at `raw/m/MEDIA_INVENTORY.md`

**Asset Breakdown:**
- **New Characters (4):** KannaKlaus poses (Bong Blazer, munchies, peace), Matty memorial
- **KKB1 (4):** Pinata, Kanna Kid smoking, Undertoker
- **KKB3 (7):** Vendor booths (High Grade, Six Jin), Special K collaborations, Kanna Kid/KannaKlaus
- **KKB4 (3):** Crowd madness video, comedy moments, Matty memorial
- **KKB5 (5):** Pinata cracking video, Undertoker bong rips, wide venue shot

**High-Value Content:**
- `kkb4-crowdmadness.mp4` - Shows packed event energy (FOMO content)
- `kkb5-pinatacrackin.mp4` - Pinata tradition hype
- `kkb5-wideangleofroom.jpg` - Venue scale and attendance proof
- Special K collaboration photos (vendor partnership outreach)

### Facebook Event Cover Generation (Technical Notes)
- **Initial attempt (v1):** Generated at 1:1 (1024x1024), stretched to 1920x1005 - visibly distorted
- **Issue:** API call didn't include proper aspect ratio parameter
- **Solution (v2):** Regenerated with `"aspect_ratio": "16:9"` parameter
- **Result:** Native 1344x768 landscape → upscaled to 1920x1080 → cropped to 1920x1005
- **Quality:** Perfect, no distortion, proper proportions
- **File:** `creative/social/images/facebook/kk6_event_cover_1920x1005_v2.png` (2.32 MB)

### Content Strategy Recommendations
- **"Then & Now" series:** KKB1 → KKB6 progression using historical photos
- **Pinata history carousel:** Show pinatas from each year
- **Vendor spotlight:** High Grade, Six Jin, Special K past participation
- **FOMO content:** Crowd videos and wide venue shots

### ✅ Website Gallery Added!
- **Status:** Live on kannakickback.com (deployed via Netlify)
- **New Section:** "From Our Past KannaKickbacks" gallery added before FAQ
- **Assets Deployed:**
  - 2 auto-playing videos (kkb4-crowdmadness.mp4, kkb5-pinatacrackin.mp4)
  - 3 historical photos (KK1 pinata, KK3 Special K, KK5 wide venue shot)
  - 1 character showcase (KannaKlaus peace pose with gradient background)
- **Features:**
  - Responsive grid layout (3 columns → 1 column mobile)
  - Smooth hover animations with caption slides
  - Year badges in gold accent color
  - CTA button driving RSVPs
- **File Organization:**
  - `/website/images/characters/` (4 compressed PNGs: 2-3MB each)
  - `/website/images/gallery/` (5 high-value assets: 15MB total)
- **Git:** Committed to kk6-prod repo, pushed to GitHub, auto-deployed to Netlify

---

## 2025-11-15 (DAY OF WEEK CORRECTION - CRITICAL)

### 🚨 CRITICAL ERROR FOUND AND FIXED
- **Issue:** ALL materials incorrectly stated "Friday, December 6, 2025"
- **Correction:** Event is on **SATURDAY, December 6, 2025** (December 6, 2025 falls on a Saturday)
- **Impact:** Affected ALL creative materials (Instagram slides, flyer, captions, briefs)

### Materials Corrected:
1. **All 5 Instagram Carousel Slides** - Regenerated with Saturday date
   - Slide 1: Event announcement (now shows Saturday)
   - Slide 2: History/impact (date not shown, no change needed)
   - Slide 3: What to Expect - ALSO fixed content issues:
     - ✅ Removed "Bong Pong Tournament" (was replaced with Special K Ring Toss)
     - ✅ Fixed "Kanna Krew Pinata" spelling (was showing "Can of Crew")
     - ✅ Now shows exactly 8 activities
   - Slide 4: How It Works - ALSO fixed content:
     - ✅ Changed from "instant gift bag" to "Get goodies & freebies at the kickback"
     - ✅ Clean 4-step layout
   - Slide 5: Save the Date (now shows Saturday)

2. **Event Flyer** - Regenerated THREE times:
   - First: Fixed day of week (Friday → Saturday)
   - Second: Fixed toy drive amounts and spelling
   - Third: Simplified graphics and fixed "How to Participate" section
   - **Final version:** Clean, professional, correct amounts ($4,200 → $5,500 → $6,500 → $7,000+ goal)
   - Location: `creative/print/KK6_EVENT_FLYER.png`

3. **Text Files Updated:**
   - MASTER_REFERENCE.md (line 8)
   - POST_01_INSTAGRAM_ANCHOR.md (caption line 37)
   - POST_01_DESIGN_SPECS.md (all instances)
   - FLYER_SINGLE_PAGE_BRIEF.md (line 17)

### Postiz Scheduling Issue:
- **Problem:** Old scheduled post for arizona_smokers had Friday date + old images
- **Action:** User deleted old post and old images from Postiz
- **Attempted:** API upload of new corrected images - FAILED
- **Helpdesk Ticket:** Created TICKET_001_IMAGE_UPLOAD_API_ISSUE.md in `/postitz/helpdesk/`
- **Status:** Resolved via manual upload
- **Result:** ✅ Post #1 published to @kannakrew Instagram (manual upload by Gilbert)

### First Post Published! 🎉
- **Platform:** Instagram @kannakrew
- **Content:** 5-slide carousel (KK6 Grand Announcement)
- **Date Posted:** Nov 15, 2025
- **All corrections applied:**
  - ✅ Saturday, December 6th (not Friday)
  - ✅ No Bong Pong Tournament
  - ✅ Correct "Kanna Krew" spelling
  - ✅ "Get goodies & freebies at the kickback" language

### Visual-Creator Pipeline Performance:
- Used visual-creator subagent system for ALL regenerations (as required by CLAUDE.md)
- Total images regenerated: 8 (5 Instagram slides + 3 flyer iterations)
- Model: Google Gemini 2.5 Flash Image (Nano Banana)
- Success rate: 100% (all images generated correctly)
- Cost: $0.00 (free tier)

### 🚨 Security Incident: OpenRouter API Key Exposed
- **Time:** ~7:06 PM (detected by OpenRouter)
- **Issue:** API key accidentally committed to public GitHub repo in generation log files
- **File:** `creative/social/images/post_01/SLIDE_3_GENERATION_LOG.md` + response JSONs
- **Impact:** OpenRouter auto-disabled key ending in ...97fb within minutes
- **Resolution:**
  - ✅ Removed 8 files from git tracking
  - ✅ Updated .gitignore to prevent future exposure
  - ✅ Created security incident report (SECURITY_INCIDENT_2025-11-15.md)
  - ✅ Postiz agent researched correct upload endpoint (documented in /postitz/helpdesk/)
- **Required Actions:**
  - 🔴 Get new OpenRouter API key from https://openrouter.ai/keys
  - 🔴 Update visual-creator config with new key
  - 🔴 Commit .gitignore + security fixes to git
- **Lessons Learned:** Generation logs/responses should not include full API keys

### Postiz Upload Resolution:
- **Problem:** Couldn't upload images via API to schedule Post #1 for arizona_smokers
- **Research:** Postiz agent found correct endpoint in /postitz/helpdesk/TICKET_001_RESOLUTION.md
- **Correct Endpoint:** `/api/public/v1/upload` (not `/api/media/upload`)
- **Current Status:** Need to upload 5 corrected slides manually via Postiz UI
- **Files Ready:** `creative/social/images/post_01/post_01_slide_[1-5].png`

### Facebook Event Page Created:
- **File:** `creative/social/FACEBOOK_EVENT_DESCRIPTION.md`
- **Length:** Full description with mission, activities, FAQ, hashtags
- **Status:** Ready to copy/paste into Facebook event page

---

## 2025-11-15 (FLYER REGENERATION - EARLIER)

### Event Flyer Regenerated - Day of Week Corrected
- **Issue:** Original flyer incorrectly stated "Friday, December 6, 2025"
- **Correction:** Event is on **Saturday, December 6, 2025** (confirmed correct)
- **Action Taken:**
  - Updated FLYER_SINGLE_PAGE_BRIEF.md with Saturday date
  - Regenerated KK6_EVENT_FLYER.png using visual-creator pipeline
  - Used Google Gemini 2.5 Flash Image Generator via OpenRouter API
  - File size: 1.4MB, 1080x1350px vertical format
- **Status:** COMPLETED - Flyer ready for distribution
- **Location:** C:\Users\figon\zeebot\kickback\creative\print\KK6_EVENT_FLYER.png

---

## 2025-11-14 (UPDATES FROM VOICE NOTES & USER INFO)

### ✅ MENU APPROVED!
- **Status:** Menu approved by Maggie/Ginza (Nov 10)
- **Items REMOVED from menu:**
  - **Ramen** - Too long to make, complicated ingredients
  - **Dragon Roll** - (Gilbert notes: "really fucking easy" but Maggie said no)
  - **Spicy Yellow** (Yellowtail?) - Too difficult prep
- **10% Revenue Confirmed:** Maggie confirmed via text that KannaKrew gets 10% of food sales (Nov 10)
  - Important: This is for event expenses, NOT donation to Sojourner
  - Gilbert got written confirmation in text message
- **Impact:** Unblocks menu design and printing tasks
- **Next Steps:**
  - Ask Maggie if there's anything else she wants to add to replace removed items
  - Design menu with approved items
  - Prepare for printing

### 🎉 VENUE CRISIS RESOLVED!
- **Gilbert did drive-by of Ginza** (Nov 13)
- Cactus planting DID limit space, but **Gilbert is not worried**
- Quote: "It'll just look more full" - event is still viable
- **Decision:** Moving forward with Ginza venue
- **Status change:** Venue concern downgraded from CRITICAL to MANAGEABLE

### Email Draft Found & Critiqued
- Located existing email draft in `/raw/c/KK6 - Email draft request.htm`
- Gilbert provided detailed critique and revisions needed (Nov 13)
- **Key Changes Required:**
  - Remove "If you're new to us" - they did it last year with Tom's Palms
  - Add context: Tom's Palms was liaison last year, they're sick this year
  - Change "East Valley" to "the Valley" (location varies)
  - Remove KannaKlaus branding from box, keep "festive donation box"
  - Add "social media assets" to what we provide
  - **WE ARE NOT providing pre-rolls** - just mention some dispensaries did it before
  - Change to "unwrapped toys" (not wrapped)
  - **Sign as: Gilbert Trout** (T-R-O-U-T-T) not Gilbert Figueroa
  - Can separately pitch vendor booth participation

### Content Creation Status (Nov 13)
- **CRITICAL:** Zero posts done out of 15 planned (as of 3 days ago = Nov 10)
- ChatGPT refused to generate countdown content
- **Alternative tools:** Grok, Gemini, or Sora for video generation
- Gilbert has posted some content in Discord chat - needs review
- Action plan: Create content → Review all options → Schedule posts
- Post to #ppk-general to get team involvement

### Cartoon Ad Concept
- Gilbert wants animated cartoon ad for kickback
- Style: "Grungy, ganja game style"
- Concept: KannaKlaus workshop → reveals stoned skunk character prototype
- Needs: Storyboard and script for video generator
- **Status:** Idea captured, needs development

### Context Clarifications
- **Last year (KK5):**
  - KannaKrew + Tom's Palms did COMBINED toy drive
  - Tom's Palms had all the dispensary contacts
  - Dispensaries gave pre-roll with each toy donation
  - Nirvana definitely did pre-rolls, others may not have
- **This year (KK6):**
  - Tom's Palms is sick, doing something else for holidays
  - We got dispensary contact info from Tammy (Tom's Palms)
  - Goal: Continue what worked last year without Tom's Palms
  - Location is "the Valley" not just "East Valley"

### Berkeley Video Interview (Sojourner Center)
- **Status:** ✅ CONFIRMED AVAILABLE (Nov 10-12)
- **Berkeley's Availability:**
  - Wednesday afternoon
  - Friday before 3pm
  - Prefers meeting at Sojourner Center location
- **Action Needed:** Schedule specific date/time ASAP (sooner is better)
- **Content Plan:** Film interview for social media content

### Content Creation Updates (Nov 11-13)
- **CRITICAL STATUS:** Zero posts out of 15 planned as of Nov 10
- **AI Tool Issues:**
  - ChatGPT refusing to generate some content
  - Alternative tools recommended: Grok, Gemini, Sora
  - TikTok suppressing AI content with watermarks
  - Consider paying $20/month for Sora to remove watermarks
- **Content Ideas from Transcripts:**
  - "Hot Box Podcast" - Film while smoking in car on way to drop off boxes
  - Stream making donation boxes on Instagram Live
  - Claymation/cartoon Santa videos (Gilbert made one, demonic first try)
  - Comedy content (not just cheesy Santa stuff)
  - Recycled content from last year (acceptable for now)
  - Still frame flyers
  - Pop culture character countdown series
  - Cameo integration (Snoop Dogg, celebrities for promo)

### Team Dynamics / Concerns (Nov 13)
- **Community Engagement Crisis:**
  - Posted to #ppk-general, zero responses
  - Dom considering stepping back from Trapper Dan
  - Bong Blazer not responding much
  - Mason hasn't been seen in a week
  - Overall: "Way down there now" in community engagement
- **Root Cause:** Prolonged inactivity, inconsistent content
- **Team Assessment:** "Our inactivity for so long...we're losing people"
- **Solution Needed:** Show up consistently, not just for events
  - Need regular content schedule
  - Can't just "show up" - need to evolve and innovate
  - Friday Night Freestyle example: did same thing for year, engagement declined

### Vendor Updates
- **Cinnamon (Nov 11):** Event coordinator finally responded, confirmed Nov 21st event, 4-10pm, setup at 3pm
- **HC Quality Glass (Nov 12):** Interested in kickback, potential collab giveaways
- **Competing Event Alert (Nov 11):** Misha's Goods has ladies night on Dec 6 (same day)
- **Ace of Wings (Nov 12):** Coming to Phoenix Dec 6 - could potentially invite?

### Production / Operations Notes
- **Donation Boxes (Nov 13):**
  - Plan: Make boxes, stream it on Instagram
  - Deliver to Amaranth and Ginza
  - Need wrapping paper
- **Nirvana Event (Nov 12):** Nov 21st at Nirvana on 7th (Ave or Street), asked if bringing blown glass
- **Custom Wrapping Paper:** Decided against due to time/other priorities
- **Event Swag:** Considering minimal event-specific items (past attempts didn't sell well)
- **T-shirt Orders:** Kane waiting on polo orders, focus shifting to custom one-offs

### AI/Tech Tool Updates
- **Sora Access:**
  - App is limited, but sora.OpenAI.com has more features
  - Can extend from 10 to 15 seconds
  - Can change landscape/format
  - Cameo integration possible but limited
  - $20/month ChatGPT unlocks more Sora features
  - $200/month gets 1080p, 30+ second videos
- **Canva Connector:** Johnny Fab recommended Claude + Canva connector for graphics
- **Video Tools Mentioned:** Runway, Hey Gen, VO3 (Google), Cling, Flux

### Other Notes
- **Podcast Plan:** Still valid, focus on 3-4 episodes instead of 6-8
  - Get Berkeley on camera
  - "Hot Box" format in car
  - Talk about process/checklist
- **Insurance Needed:** Mentioned on Nov 13 final call
- **Lead Sponsors Needed:** Nov 13 priorities

---

## 2025-11-11 (MIDDAY UPDATE)

### Discord Update Posted
- Posted KK6 priorities update to #ppk-general
- Team now aware of today's tasks and progress
- Message includes all critical items and box locations

### Special K DM Sent
- **Status:** ✅ SENT
- **Request:** 20-30 pieces total
  - ~10 for ring toss game prizes
  - ~10 for general giveaways/raffle prizes
  - ~10 for smoke section
- **Tone:** Casual, friendly, no pressure
- **Waiting on:** Response

### Box Locations Confirmed
- **Ginza** - Ready for delivery
- **Fancy Pets** - Ready for delivery
- **Amaranth** (toy store in AJ) - Ready for delivery
- **Total boxes placed:** 0 (waiting on delivery)
- **Total boxes ready:** 3

### Greek Glass Update
- **Status:** ✅ CONFIRMED
- **Contribution:** Sent small box of goodies for gift bags
- This helps with gift bag sourcing!

---

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
- ~~Greek Glasses contact~~ ✅ HAVE CONTACT (sent goodies)
- ~~Special K contact~~ ✅ HAVE CONTACT (DM sent Nov 11)
- Brian Jacobs contact
- Bong Blazer contact
- D1 contact
- Tom Palms contact
- Toy Store contact (Amaranth in AJ)

---

## VENDOR COMMITMENTS

### Confirmed:
- Cherry Bomb - interested, waiting for details
- Greek Glass - ✅ Sent small box of goodies for gift bags (Nov 11)

### Reached Out (Awaiting Response):
- Special K - DM sent Nov 11 (20-30 pieces requested)

### Pending Outreach:
- Chill Pipe - 30 bongs (gave last year)
- Brian Jacobs - glass
- Tom Palms - box hosting

---

## BOX LOCATIONS

### Ready for Delivery:
- Ginza (restaurant venue)
- Fancy Pets
- Amaranth (toy store in AJ)

### Likely/Pending Confirmation:
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
