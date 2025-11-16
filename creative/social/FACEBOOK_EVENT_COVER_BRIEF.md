# KannaKickback 6 - Facebook Event Cover Photo

**Created:** 2025-11-16
**Platform:** Facebook Event Cover
**Final Dimensions:** 1920x1005 pixels (after upscaling/cropping)
**Generation Dimensions:** 1344x768 pixels (16:9 aspect ratio via Gemini)

---

## ⚠️ IMPORTANT: Two-Step Process Required

**Why?** Gemini 2.5 Flash Image can only generate up to 1344x768 at 16:9 ratio.

**Workflow:**
1. Generate at 16:9 (1344x768) using visual-creator
2. Upscale to 1920x1080 using PIL/Pillow
3. Center-crop to 1920x1005 for Facebook specs

---

## Image Specifications

### Generation Settings (Step 1)
- **Dimensions:** 1344x768 pixels
- **Aspect Ratio:** 16:9
- **Format:** PNG
- **Model:** google/gemini-2.5-flash-image-preview (Nano Banana)

### Final Output (Step 2)
- **Dimensions:** 1920x1005 pixels
- **Aspect Ratio:** 1.91:1
- **Format:** PNG
- **Max File Size:** 8MB
- **Platform:** Facebook Event Cover

---

## Design Requirements

### Visual Composition

**Layout:** Horizontal/landscape format optimized for 16:9
- KannaKlaus character positioned **center-left** (safe zone for mobile cropping)
- Festive holiday background with cannabis-friendly elements
- Cannabis leaf snowflakes falling across the scene
- Toy boxes/wrapped presents visible in foreground or around KannaKlaus
- Warm, inviting holiday atmosphere with soft lighting
- Background: Festive holiday scene (workshop, decorated space, or snowy outdoor scene)

**Important:** Keep all critical elements **centered vertically and horizontally** - Facebook crops differently on mobile vs desktop.

### Character Design: KannaKlaus

- Red Santa suit with white fur trim
- Long beard (possibly with braids/beads for character)
- Classic Santa hat
- Cannabis leaf patterns on suit (subtle, tasteful)
- Friendly, jolly, welcoming expression
- Holding or surrounded by wrapped toy presents
- Optional: Work apron over suit if in "workshop" setting

### Text Overlays

**Position:** All text centered for mobile safety

**Main Headline (Top Center, Extra Large, Bold):**
```
KANNA KICKBACK 6
```
- Font: Bold, festive, impactful (Bebas Neue or Impact style)
- Color: White (#FFFFFF) with thick black outline for maximum readability
- Size: Very large, dominant headline

**Subheadline (Below main headline):**
```
Holiday Party & Charity Toy Drive
```
- Font: Clean sans-serif (Helvetica/Arial style)
- Color: Festive Gold (#FFD700) or White (#FFFFFF)
- Size: Medium, complementary to headline

**Event Details (Center, below subheadline):**
```
📅 SATURDAY, DECEMBER 6TH • 2-6 PM
📍 GINZA, GOLD CANYON, AZ
🎟️ FREE EVENT
```
- Font: Clean, readable sans-serif
- Color: White (#FFFFFF)
- Include emoji icons for visual breaks

**Tagline (Bottom Center):**
```
Fun first. Charity always.
```
- Font: Hand-drawn or brush style for emphasis
- Color: Cannabis Green (#4CAF50) or Holiday Red (#C41E3A)
- Size: Medium, memorable closing

### Color Palette

**Primary Colors:**
- Forest Green (#2D5016) - backgrounds, main elements
- Cannabis Green (#4CAF50) - accents, highlights

**Accent Colors:**
- Holiday Red (#C41E3A) - festive elements, KannaKlaus suit
- Festive Gold (#FFD700) - premium touches, highlights, text

**Neutral Colors:**
- Cream (#FFF8DC) - soft backgrounds
- White (#FFFFFF) - text, high contrast
- Black (#000000) - text outlines, shadows

**Background:** Warm festive tones with gradient (reds, greens, golds blending)

### Decorative Elements

- Cannabis leaf snowflakes falling throughout scene
- Wrapped toy presents (various sizes)
- Holiday ornaments (subtle background decoration)
- Soft bokeh/glow effects for festive atmosphere
- Optional: String lights or garland

### Style Notes

- **Mood:** Festive, welcoming, community-focused, cannabis-positive but wholesome
- **Tone:** Professional but playful
- **Vibe:** Holiday celebration meets charity mission
- **Cannabis elements:** Present but not overwhelming (this is a family-friendly charity event)
- **Text readability:** HIGH priority - use thick outlines, high contrast
- **Composition:** Balanced, not cluttered, room to breathe
- **Quality:** High-end, polished, social media ready

### Negative Prompts (Things to Avoid)

- Corporate or sterile look
- Too serious or harsh
- Overly childish
- Cluttered or messy composition
- Low contrast text (must be highly readable)
- Off-brand colors
- Aggressive or dark themes
- Cheap-looking graphics

---

## Brand Guidelines Reference

**Project:** KannaKickback 6
**Beneficiary:** Sojourner Center (domestic violence support)
**Branding Rule:** All K's, no C's (KannaKrew, KannaKickback, KannaKlaus)
**Mission:** Fun first. Charity always.

**Track Record:**
- 2022 (KK3): $4,200 in toys
- 2023 (KK4): $5,500 in toys
- 2024 (KK5): $6,500 in toys
- 2025 (KK6) GOAL: $7,000+ in toys

---

## Post-Processing Instructions (Step 2)

After visual-creator generates 1344x768 image:

1. **Upscale** using PIL/Pillow Lanczos to 1920x1080 (maintains 16:9)
2. **Crop** center to 1920x1005:
   - Top margin: 37px
   - Bottom margin: 38px
   - Keep center 1005px height
3. **Save** as PNG with high quality (95+)
4. **Verify** file size < 8MB

**Python snippet:**
```python
from PIL import Image

img = Image.open("kk6_cover_1344x768.png")
img_upscaled = img.resize((1920, 1080), Image.LANCZOS)
top_margin = (1080 - 1005) // 2  # 37px
img_final = img_upscaled.crop((0, top_margin, 1920, 1005 + top_margin))
img_final.save("kk6_event_cover_final.png", quality=95)
```

---

## File Output

**Generation output:** `/kickback/creative/social/images/facebook/kk6_cover_1344x768.png`
**Final output:** `/kickback/creative/social/images/facebook/kk6_event_cover_1920x1005.png`

---

## Usage Notes

- This cover photo will be used for the KK6 Facebook event page
- Must look good on both desktop and mobile
- Text must be readable at all screen sizes
- Should capture festive + charity + cannabis-friendly vibe
- First impression for potential attendees - make it count!

---

**Status:** Ready for generation
**Next Step:** Invoke visual-creator agent to generate base image at 16:9
