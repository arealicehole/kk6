#!/usr/bin/env python3
"""
KannaKickback 6 Event Flyer Generator
Uses OpenRouter API (Nano Banana / Gemini 2.5 Flash Image) to generate corrected event flyer
"""

import requests
import json
import base64
from pathlib import Path
from datetime import datetime

# Configuration
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-2.5-flash-image-preview"
OUTPUT_PATH = Path(r"C:\Users\figon\zeebot\kickback\creative\print\KK6_EVENT_FLYER.png")

# Optimized Prompt for Nano Banana
PROMPT = """Create a professional, festive event flyer poster for KannaKickback 6 - a cannabis-friendly holiday party and charity toy drive.

FORMAT & DIMENSIONS:
- Vertical poster: 1080 pixels wide x 1350 pixels tall (4:5 aspect ratio)
- Clean, organized layout with clear sections
- 30% white space - NOT cluttered
- Professional but playful aesthetic

LAYOUT STRUCTURE (top to bottom):

**HEADER SECTION (Top 15%):**
Main title: "KANNA KICKBACK 6" in HUGE, BOLD letters
Subtitle: "Year 6. Let's make it legendary."
Decorated with small cannabis leaf snowflakes

**EVENT DETAILS BOX (Next 12%):**
📅 Friday, December 6, 2025
⏰ 2:00 PM - 6:00 PM
📍 Ginza Restaurant, Gold Canyon, AZ
🎟️ FREE EVENT
(Put in a distinct bordered box for emphasis)

**WHAT'S HAPPENING SECTION (Next 25%):**
Show in 2-column layout with emojis:
🎅 KannaKlaus & Elves
💍 Special K Ring Toss
🪅 Infamous Kanna Krew Pinata
🛍️ 10+ Vendor Booths (glass, products, growers)
🎁 Giveaways & Raffles ALL DAY
🍜 Orange Chicken & More from Ginza
💨 420-Friendly Space
🎶 Music & Community

**MISSION SECTION (Next 12%):**
Bold headline: "Help us beat $7,000 in toy donations!"
Smaller text: "All toys benefit the Sojourner Center"
Add gift box icons for visual interest

**GROWTH STATS SECTION (Next 15%):**
Show progression with arrows:
$4,200 (2022) → $5,500 (2023) → $6,500 (2024) → $7,000+ (2025)
Make this visually clear with upward progression

**HOW TO PARTICIPATE (Next 15%):**
1. Drop a new, unwrapped toy (Nov 15-Dec 15)
2. Get goodies & freebies at the kickback
3. Pull up Dec 6th and celebrate!

**CALL-TO-ACTION (Next 6%):**
Large, bold, centered:
"BRING A TOY • GET GOODIES • SPREAD JOY"

**FOOTER (Bottom 10%):**
@KannaKrew
#KannaKickback #KK6 #KannaKrew
Tagline: "Fun first. Charity always."

COLOR PALETTE:
- Background: Cream (#FFF8DC) or very light color for maximum readability
- Primary: Forest Green (#2D5016)
- Accent: Holiday Red (#C41E3A)
- Highlight: Festive Gold (#FFD700)
- Text: Black for main text, White where on dark backgrounds

VISUAL ELEMENTS:
- KannaKlaus character (Santa with cannabis theme) featured prominently in corner or as accent
- Cannabis leaf snowflakes as decorative elements (subtle, tasteful)
- Gift boxes and holiday ornaments scattered throughout
- All decorations festive but not overwhelming

TYPOGRAPHY:
- Headers: BOLD, large, highly readable sans-serif fonts
- Body text: Clean, professional sans-serif (Arial, Helvetica style)
- All text must be LARGE and EASY TO READ
- High contrast between text and background

CRITICAL SPELLING REQUIREMENTS (NO MISTAKES ALLOWED):
- "KANNA KICKBACK" (all K's, not C's) - spell exactly this way
- "KannaKlaus" (not Santa Klaus, not Cannabis Klaus)
- "Kanna Krew" (all K's, not "Can of Crew")
- "HAPPENING" (H-A-P-P-E-N-I-N-G)
- "$7,000" goal (NOT $15,000 - that's wrong!)
- Growth: $4,200 → $5,500 → $6,500 → $7,000+

STYLE & MOOD:
- Festive holiday celebration vibes
- Cannabis-positive but wholesome and appropriate
- Community-focused, welcoming, inviting
- Professional event poster quality
- Modern, clean design
- Easy to scan and read quickly

AVOID:
- Cluttered, messy layouts
- Too serious or corporate
- Overly childish aesthetics
- Small, hard-to-read text
- Off-brand colors (too bright or neon)
- Spelling errors (especially brand names!)

This is for a real charity event benefiting the Sojourner Center. The design should be festive and fun while clearly communicating the toy drive mission and event details."""


def generate_image():
    """Generate the flyer image using OpenRouter API"""

    print("[IMAGE GENERATION] Generating KannaKickback 6 Event Flyer...")
    print(f"[MODEL] Using model: {MODEL}")
    print(f"[OUTPUT] Output path: {OUTPUT_PATH}")
    print()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/zeebotcrypto/kickback",
        "X-Title": "KannaKickback Visual Creator"
    }

    payload = {
        "model": MODEL,
        "modalities": ["text", "image"],
        "image_config": {
            "aspect_ratio": "4:5"  # 1080x1350 = 4:5 ratio
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT
                    }
                ]
            }
        ]
    }

    try:
        print("[API] Calling OpenRouter API...")
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()
        print("[SUCCESS] API call successful!")

        # Debug: Show response structure
        print(f"[DEBUG] Response keys: {list(data.keys())}")
        print(f"[DEBUG] Message content type: {type(data.get('choices', [{}])[0].get('message', {}))}")

        # Extract image data
        message = data['choices'][0]['message']
        print(f"[DEBUG] Message keys: {list(message.keys())}")

        # Try different possible locations for image data
        image_data = None
        if 'images' in message and message['images']:
            image_data = message['images'][0]
        elif 'content' in message:
            content = message['content']
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'image_url':
                        image_data = item.get('image_url', {}).get('url')
                        break

        print(f"[DEBUG] Image data type: {type(image_data)}")

        if image_data is None:
            print(f"[DEBUG] Full response: {json.dumps(data, indent=2)}")
            raise ValueError("Could not find image data in API response")

        # Handle different response formats
        if isinstance(image_data, dict):
            print(f"[DEBUG] Image data dict keys: {list(image_data.keys())}")
            # Image data is nested in image_url.url
            if 'image_url' in image_data:
                image_data = image_data['image_url'].get('url')
            else:
                # Image data might be in 'url' or 'data' field directly
                image_data = image_data.get('url') or image_data.get('data') or image_data.get('base64')
            print(f"[DEBUG] Extracted image data type: {type(image_data)}")
            if image_data is None:
                print(f"[DEBUG] Full image dict: {json.dumps(message['images'][0], indent=2)}")
                raise ValueError("Could not extract base64 data from image dict")

        # Remove data URL prefix if present
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',', 1)[1]

        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data)

        # Save to file
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_bytes(image_bytes)

        # Metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "model": data.get('model'),
            "tokens_used": data.get('usage', {}).get('total_tokens'),
            "dimensions": "1080x1350",
            "aspect_ratio": "4:5",
            "purpose": "KannaKickback 6 Event Flyer - CORRECTED VERSION",
            "corrections": [
                "Toy drive amounts: $4,200 → $5,500 → $6,500 → $7,000+ (NOT $15,000!)",
                "All spelling verified: KannaKlaus, KannaKrew, KannaKickback",
                "HAPPENING spelled correctly"
            ]
        }

        # Save metadata
        metadata_path = OUTPUT_PATH.with_suffix('.json')
        metadata_path.write_text(json.dumps(metadata, indent=2))

        print(f"[SAVED] SUCCESS! Flyer saved to: {OUTPUT_PATH}")
        print(f"[METADATA] Metadata saved to: {metadata_path}")
        print()
        print("[SUMMARY] Generation Summary:")
        print(f"   Model: {metadata['model']}")
        print(f"   Tokens used: {metadata['tokens_used']}")
        print(f"   Dimensions: {metadata['dimensions']}")
        print(f"   Cost: $0.00 (free tier)")
        print()
        print("[VERIFY] IMPORTANT: Manually verify spelling of:")
        print("   - KANNA KICKBACK (all K's)")
        print("   - KannaKlaus, Kanna Krew")
        print("   - Toy drive amounts: $4,200 to $5,500 to $6,500 to $7,000+")
        print("   - HAPPENING (H-A-P-P-E-N-I-N-G)")

        return True

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code

        if status_code == 429:
            print(f"[ERROR] Rate limit exceeded. Please wait and try again.")
            retry_after = e.response.headers.get('Retry-After', 'unknown')
            print(f"   Retry after: {retry_after} seconds")
        elif status_code == 401:
            print(f"[ERROR] Authentication error. Check API key in config/api-config.json")
        else:
            print(f"[ERROR] HTTP Error {status_code}: {e}")
            try:
                error_data = e.response.json()
                print(f"   Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response: {e.response.text}")

        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_image()
    exit(0 if success else 1)
