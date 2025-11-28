# KK6 AD CAMPAIGN TRACKER
**Last Updated:** 2025-11-27

---

## ACTIVE CAMPAIGNS

### Campaign 1: Emergency Carousel (LIVE)
| Field | Value |
|-------|-------|
| **Campaign ID** | 120240660415560608 |
| **Ad Set ID** | 120240660427060608 |
| **Ad Creative ID** | 1520876062575407 |
| **Ad ID** | 120240664205010608 |
| **Status** | ACTIVE - DO NOT MODIFY |
| **Budget** | $5/day |
| **Placements** | Facebook + Instagram (user corrected) |
| **Targeting** | Gold Canyon AZ area, 21+ (user corrected) |
| **Start Date** | Nov 27, 2025 |
| **End Date** | Dec 6, 2025 (event day) |

#### Carousel Cards:
1. "$6,500 IN TOYS DONATED Last Year"
2. "Benefiting SOJOURNER CENTER"
3. "FRIDAY DEC 6 | 2-6PM | GINZA ASIAN FUSION"
4. "BRING A TOY BRING A FRIEND MAKE A DIFFERENCE"

#### Primary Text:
> Last year, our community donated $6,500 in toys for families in need. This year, we're going even bigger. Join us Friday, Dec 6 for a FREE holiday celebration benefiting the Sojourner Center. Bring a toy, bring a friend, make a difference.

#### CORRECTIONS LOG:
| Date | Issue | Correction | By |
|------|-------|------------|-----|
| Nov 27 | Location set to Ukraine | Changed to Gold Canyon AZ area | User |
| Nov 27 | Facebook only | Added Instagram placements | User |

---

## LESSONS LEARNED / API NOTES

### Meta Marketing API Issues (Nov 27):
1. **Location targeting:** The API call didn't properly set geo_locations - defaulted to wrong region
2. **Placements:** Need to explicitly include Instagram in publisher_platforms
3. **Recommendation:** For future ads, verify settings in Ads Manager after API creation

### Correct API Parameters for Future:
```
geo_locations: {
  "cities": [{"key": "Gold Canyon, AZ area"}],
  "location_types": ["home"]
}
publisher_platforms: ["facebook", "instagram"]
facebook_positions: ["feed"]
instagram_positions: ["stream", "story"]
```

---

## PLANNED CAMPAIGNS

### Campaign 2: Video Ad (Party-Forward) - NOT STARTED
- **Brief:** creative/social/AD_CREATIVE_VIDEO_VERSION_B_PARTY_FORWARD.md
- **Priority:** Next up after carousel approved
- **Budget:** TBD
- **Notes:** 28-second video, highlight games/prizes/KannaKlaus

---

## PERFORMANCE TRACKING

### Campaign 1 Performance:
| Date | Reach | Impressions | Clicks | CTR | Spend |
|------|-------|-------------|--------|-----|-------|
| Nov 27 | 599 | 640 | 11 | 1.72% | \.14 |
| Nov 28 | | | | | |
| Nov 29 | | | | | |
| Nov 30 | | | | | |
| Dec 1 | | | | | |
| Dec 2 | | | | | |
| Dec 3 | | | | | |
| Dec 4 | | | | | |
| Dec 5 | | | | | |
| Dec 6 | | | | | |

---

## QUICK LINKS
- [Meta Ads Manager](https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=2268740843417554)
- [Ad Creative Briefs Summary](../creative/social/AD_CREATIVE_BRIEFS_SUMMARY.md)
- [Hyper-Local Ads Research](C:/Users/figon/zeebot/r/hyper-local-event-advertising-kk6-2025-11-26.md)
