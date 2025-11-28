# KK6 ANALYTICS TRACKER
**Last Updated:** 2025-11-27

---

## GOOGLE ANALYTICS 4

### Access
- **Property ID:** G-G4V5SC2M7L
- **Dashboard:** [analytics.google.com](https://analytics.google.com)
- **Login:** Use Google account that owns the property

### What It Tracks
| Metric | Description | Where to Find |
|--------|-------------|---------------|
| **Users** | Unique visitors | Reports > Realtime or Engagement |
| **Sessions** | Total visits | Reports > Engagement > Overview |
| **Page Views** | Pages viewed | Reports > Engagement > Pages |
| **Bounce Rate** | Left without action | Reports > Engagement > Overview |
| **Avg Session Duration** | Time on site | Reports > Engagement > Overview |
| **Traffic Source** | Where visitors came from | Reports > Acquisition > Traffic Acquisition |
| **Geography** | Visitor locations | Reports > Demographics > Overview |
| **Device** | Mobile vs Desktop | Reports > Tech > Overview |

### Key Reports for KK6

#### 1. Ad Performance (Meta → Website)
**Path:** Reports > Acquisition > Traffic Acquisition
- Filter by Source = "facebook" or "instagram"
- Shows how many Meta ad clicks became site visits
- Compare to Meta Ads Manager click count

#### 2. RSVP Form Submissions
**Path:** Reports > Engagement > Events
- Look for form_submit or page_view on thank-you page
- Cross-reference with KK6_FORM_SUBMISSIONS_TRACKER.md

#### 3. Real-Time Visitors
**Path:** Reports > Realtime
- See who's on site RIGHT NOW
- Useful during ad launches or post drops

#### 4. Geographic Breakdown
**Path:** Reports > Demographics > Demographic Details
- Filter by City
- Verify ads reaching Gold Canyon / East Valley / Phoenix area

---

## WEBSITE DETAILS

### Hosting
| Field | Value |
|-------|-------|
| **Platform** | Netlify |
| **Domain** | kannakickback.com |
| **Repo** | github.com/arealicehole/kk6-prod |
| **Branch** | master |
| **Auto-Deploy** | Yes (on push to master) |

### Key Pages
| Page | URL | Purpose |
|------|-----|---------|
| Home | kannakickback.com | Main landing, RSVP form |
| Locations | kannakickback.com/locations | Box drop-off spots |
| Menu | kannakickback.com/#menu | Ginza menu section |

### Forms
| Form | Location | Sends To |
|------|----------|----------|
| RSVP | Homepage #rsvp section | Resend → admin@kannakrew.com |
| Vendor App | /vendor (if exists) | Resend → admin@kannakrew.com |
| Box Host App | /host (if exists) | Resend → admin@kannakrew.com |
| Contact | /contact or #contact | Resend → admin@kannakrew.com |

---

## TRACKING INTEGRATION

### Meta Ads → GA4 Flow
```
Meta Ad Click
    ↓
kannakickback.com (with UTM params)
    ↓
GA4 records: source=facebook, medium=paid
    ↓
User browses site
    ↓
RSVP form submit → Resend email → admin@kannakrew.com
    ↓
Add to KK6_FORM_SUBMISSIONS_TRACKER.md
```

### UTM Parameters (for tracking)
When creating ads or links, append these:
```
?utm_source=facebook&utm_medium=paid&utm_campaign=kk6_carousel
?utm_source=instagram&utm_medium=paid&utm_campaign=kk6_carousel
?utm_source=instagram&utm_medium=organic&utm_campaign=post_03
```

---

## DAILY TRACKING ROUTINE

### Quick Check (2 min)
1. Open [GA4 Realtime](https://analytics.google.com) - anyone on site?
2. Check email for new RSVPs
3. Glance at Meta Ads Manager for spend/reach

### Weekly Review (10 min)
1. **GA4 Traffic:** How many visitors this week?
2. **GA4 Sources:** Where did they come from?
3. **Meta Ads:** Total spend, reach, clicks, CTR
4. **RSVPs:** How many new? Update tracker
5. **Compare:** Ad clicks vs GA4 sessions (should be close)

---

## PERFORMANCE LOG

### Website Traffic
| Date | Users | Sessions | Top Source | Notes |
|------|-------|----------|------------|-------|
| Nov 27 | - | - | - | GA4 just installed, data pending |
| Nov 28 | | | | |
| Nov 29 | | | | |
| Nov 30 | | | | |
| Dec 1 | | | | |
| Dec 2 | | | | |
| Dec 3 | | | | |
| Dec 4 | | | | |
| Dec 5 | | | | |
| Dec 6 | | | | EVENT DAY |

### Conversion Funnel
| Stage | Count | Rate | Notes |
|-------|-------|------|-------|
| Ad Impressions | 640 | - | From Meta |
| Ad Clicks | 11 | 1.72% CTR | From Meta |
| Site Visits | TBD | TBD | From GA4 |
| RSVP Submissions | 19 | TBD | From tracker |

---

## CREDENTIALS & ACCESS

### Google Analytics
- **Property:** G-G4V5SC2M7L
- **Owner:** [your Google account]
- **Access:** analytics.google.com

### Netlify
- **Site:** kannakickback.com
- **Dashboard:** app.netlify.com
- **Repo:** github.com/arealicehole/kk6-prod

### Meta Ads
- **See:** operations/AD_CAMPAIGN_TRACKER.md
- **Access Token:** In .env as META_ACCESS_TOKEN

---

## TROUBLESHOOTING

### GA4 Not Showing Data
1. Check if script is in index.html `<head>`
2. Verify property ID matches (G-G4V5SC2M7L)
3. Wait 24-48 hours for first data
4. Use Realtime report to test immediately

### Form Submissions Not Arriving
1. Check Resend dashboard for delivery status
2. Check spam folder
3. Verify form action URL is correct
4. Check Pipedream workflow if using forwarding

### Ad Clicks Don't Match GA4 Sessions
- Normal: Some users bounce before GA loads
- Check: Are UTM params on ad links?
- Gap of 10-20% is typical

---

## QUICK LINKS

- [Google Analytics](https://analytics.google.com)
- [Meta Ads Manager](https://adsmanager.facebook.com)
- [Netlify Dashboard](https://app.netlify.com)
- [GitHub Repo](https://github.com/arealicehole/kk6-prod)
- [AD_CAMPAIGN_TRACKER.md](./AD_CAMPAIGN_TRACKER.md)
- [KK6_FORM_SUBMISSIONS_TRACKER.md](../communications/KK6_FORM_SUBMISSIONS_TRACKER.md)
