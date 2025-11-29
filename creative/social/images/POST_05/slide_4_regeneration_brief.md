# POST_05 Slide 4 Regeneration Brief

**Purpose:** Regenerate slide 4 with corrected punctuation (simple dash instead of em-dash)

**Output Location:** C:/Users/figon/zeebot/kickback/creative/social/images/POST_05/slide_4_v3.png

## Design Specifications

**Layout:**
- Split layout: Dark green vertical bar on left, white/light gray background on right
- Aspect ratio: 1:1 (Instagram carousel)
- Resolution: 2K

**Left Side - Timeline Bar:**
- Color: Dark green (#1B4D3E)
- Width: ~20% of canvas
- Text: "2024" in vertical orientation
- Text color: Gold/metallic gold
- Font: Bold, clean sans-serif

**Right Side - Main Content:**
- Background: White or light gray (#F5F5F5)
- Padding: Generous margins from edges

**Top Section - Icon + Arrow:**
- Community icon: Dark green (#1B4D3E) circle showing simplified silhouettes of people holding hands in a ring
- Growth arrow: Gold/metallic gold arrow pointing upward diagonally
- Arrangement: Icon on left, arrow on right, aligned horizontally

**Headline:**
- Text: "Community Tradition"
- Font: Elegant serif, italic
- Color: Forest green (#2D5F4D)
- Size: Large, prominent
- Position: Below icon section

**Body Stats (3 bullet points):**
- Text color: Dark gray (#333333)
- Font: Clean sans-serif
- Size: Medium, readable
- Content:
  - "$6,500 in toys donated"
  - "Event attendance doubled"
  - "People asking in October: When is KK6?"

**Quote (Bottom):**
- Text: "It's not just us anymore - it's all of us"
- CRITICAL: Use simple dash/hyphen character (-), NOT em-dash (—)
- Font: Serif, italic
- Color: RED (#CC0000 or similar vibrant red)
- Size: Medium-large
- Position: Bottom of canvas with comfortable margin

## Brand Colors
- Dark Green: #1B4D3E
- Forest Green: #2D5F4D
- Gold: #D4AF37 or metallic gold
- Red: #CC0000
- Dark Gray: #333333
- Light Gray: #F5F5F5

## Typography
- Headlines: Serif fonts, italic for emphasis
- Body: Clean sans-serif
- Maintain readability at mobile sizes

## Critical Requirements
1. **Use simple dash character (-)** in the quote, not em-dash
2. Clean, professional layout with proper spacing
3. Icons should be simple, recognizable silhouettes
4. Text must be crisp and legible
5. Maintain visual hierarchy: Icon → Headline → Stats → Quote

## API Configuration
- API: Kie.ai Nano Banana Pro
- Endpoint: https://api.kie.ai/api/v1/jobs/createTask
- Poll: https://api.kie.ai/api/v1/jobs/recordInfo?taskId=xxx
- Auth: Bearer [STORED IN ENV]
- Model: nano-banana-pro
- Aspect ratio: 1:1
- Output format: png
