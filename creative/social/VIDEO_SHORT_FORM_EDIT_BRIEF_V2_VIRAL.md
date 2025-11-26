# SHORT-FORM VIRAL VIDEO EDIT BRIEF V2 - "WE BEAT CORPORATIONS"
**Created:** 2025-11-23
**Post Date:** TBD
**Platforms:** Instagram Reels, TikTok, Facebook Reels
**Length:** 60-75 seconds (STRICT)
**Owner:** Gilbert
**Status:** READY FOR EXECUTION

---

## CRITIQUES FROM V1 INCORPORATED

✅ **NO trailing video/setup** - Surgical cuts ONLY of Seren speaking
✅ **NO other speaker dialogue** - Cut out ALL direction/conversation
✅ **Captions: 5 words max** per screen
✅ **Captions: CENTER aligned** (not bottom)
✅ **Captions: Smaller font** than V1
✅ **Spelling: Kanna (not Cana), Seren (not Sarin)**

---

## VIRAL VIDEO STRUCTURE (60-75 seconds total)

### **SEGMENT 1: HOOK - "Beat Corporations" (8-10s)**
**Source:** Video 3 (`PXL_20251121_183509744.mp4`)
**Exact Timestamps:** `00:02:08.100` → `00:02:20.140`
**Duration:** 12.04 seconds
**Target Quote:** "Kanna Crew, you guys have outdone every year. You've outdone yourself, and you've actually outdone other programs that donate to us, which is pretty great because we have some large corporations coming in."

**Cutting Strategy:**
- **START:** Word "Kanna" at 00:02:08.100
- **END:** Word "corporations" at 00:02:20.140
- This captures the FULL validation without setup

**Caption Strategy (5 words max per line):**
```
"Kanna Crew you guys have"
"outdone every year you've outdone"
"yourself and you've actually outdone"
"other programs that donate to"
"us which is pretty great"
"because we have some large"
"corporations coming in"
```

---

### **SEGMENT 2: WHO IS SEREN (10-12s)**
**Source:** Video 1 (`PXL_20251121_183132720.mp4`)
**Exact Timestamps:** `00:00:47.010` → `00:00:58.590`
**Duration:** 11.58 seconds
**Target Quote:** "Hey, my name is Seren. I'm the community engagement manager here at Sojourner Center. That means I run the donation resource center as well as work with all the volunteers."

**Cutting Strategy:**
- Find word "Hey" → Start there
- End after "volunteers"
- Skip the longer explanation about shelter services

**Caption Strategy:**
```
"Hey my name is"
"Seren I'm the community"
"engagement manager here at"
"Sojourner Center that means"
"I run the donation"
"resource center"
```

---

### **SEGMENT 3: TEEN GAP INSIGHT (15-18s)**
**Source:** Video 2 (`PXL_20251121_183321828.mp4`)
**Exact Timestamps:** `00:01:24.170` → `00:01:40.610`
**Duration:** 16.44 seconds
**Target Quote:** "So if you're thinking infant, we also need infant to 17 years old. So think about those kids. Maybe the ones we won't remember. We don't know what they might like, you might know."

**Cutting Strategy:**
- START: "infant to"
- END: "you might know"
- This is the core educational message about teens being forgotten

**Caption Strategy:**
```
"We also need infant"
"to 17 years old"
"Think about those kids"
"Maybe the ones we"
"won't remember we don't"
"know what they might"
"like you might know"
```

---

### **SEGMENT 4: TRACK RECORD GRAPHICS (15s)**
**Type:** MOTION GRAPHICS / TEXT OVERLAY
**No video clip - pure graphics**

**Visual:**
```
Animated rising bar chart:
2022 (KK3): $4,200 ↑
2023 (KK4): $5,500 ↑
2024 (KK5): $6,500 ↑
2025 (KK6): $7,000+ GOAL! 🎯
```

**Background:** Subtle green/gold gradient or static frame from Seren segments

**Text Overlay:**
```
"CONSISTENT GROWTH"
"LARGEST INDIVIDUAL DONOR"
"ALL K'S, NO C'S"
```

**Music:** Upbeat, inspirational swell

---

### **SEGMENT 5: CALL TO ACTION (10-12s)**
**Type:** TEXT OVERLAY + GRAPHICS
**No video clip**

**Visual:**
```
3 WAYS TO HELP:

1. 🎁 DONATE A TOY
   Teen gifts: headphones, gift cards, hoodies

2. 📦 DROP OFF AT 15+ LOCATIONS
   kannakickback.com/locations

3. 🎉 JOIN US DEC 6
   KannaKickback 6 Event
   2-6 PM • Ginza Gold Canyon
```

**QR Code:** Bottom right corner → kannakickback.com

---

## TECHNICAL SPECS

**Video Dimensions:** 1080x1920px (9:16 vertical)
**Frame Rate:** 60fps
**Codec:** H.264, CRF 23
**Audio:** AAC 192k

**Caption Specs:**
- **Font:** Arial Bold
- **Size:** 20pt (smaller than V1 which was 24pt)
- **Position:** CENTER of screen (Alignment=5 in ASS format)
- **Color:** White (#FFFFFF)
- **Outline:** Black, 2px thick
- **Max words:** 5 per caption card
- **Duration:** ~1-2 seconds per caption

---

## EXACT FFMPEG EXTRACTION COMMANDS

### Segment 1: Beat Corporations
```bash
ffmpeg -ss 00:02:08.100 -i PXL_20251121_183509744.mp4 \
  -to 00:02:20.140 \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 192k \
  viral_segment1_beat_corporations.mp4 -y
```

### Segment 2: Seren Intro
```bash
ffmpeg -ss 00:00:47.010 -i PXL_20251121_183132720.mp4 \
  -to 00:00:58.590 \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 192k \
  viral_segment2_seren_intro.mp4 -y
```

### Segment 3: Teen Gap
```bash
ffmpeg -ss 00:01:24.170 -i PXL_20251121_183321828.mp4 \
  -to 00:01:40.610 \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 192k \
  viral_segment3_teen_gap.mp4 -y
```

---

## CAPTION FILE FORMAT

**File:** `viral_combined_captions.srt`

**Style Requirements:**
- 5 words maximum per subtitle entry
- Break at natural speech pauses
- Center-aligned
- Smaller font (20pt vs 24pt in V1)

**Example Entry:**
```
1
00:00:00,100 --> 00:00:01,790
Kanna Crew you guys

2
00:00:01,790 --> 00:00:03,460
have outdone every year
```

---

## TIMELINE & EXECUTION STEPS

1. ✅ Fix JSON spelling (Kanna, Seren)
2. ✅ Analyze word-level timestamps
3. ✅ Create this V2 viral brief
4. ⏳ Extract 3 tight surgical clips
5. ⏳ Create 5-word caption SRT file
6. ⏳ Concatenate clips
7. ⏳ Format as vertical 1080x1920
8. ⏳ Burn in captions (centered, 20pt)
9. ⏳ Review final output

---

## SUCCESS CRITERIA

✅ **Duration:** 60-75 seconds (STRICT)
✅ **No trailing video:** Only Seren speaking, no setup
✅ **No other speakers:** Cut out ALL direction
✅ **Captions:** 5 words max, centered, 20pt
✅ **Spelling:** Kanna, Seren (corrected)
✅ **Clean cuts:** Frame-accurate, no jarring edits
✅ **Vertical format:** 1080x1920, optimized for mobile

---

**STATUS:** Ready for extraction → Execute now!
