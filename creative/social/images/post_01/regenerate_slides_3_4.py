#!/usr/bin/env python3
"""
Regenerate Slides 3 and 4 for KannaKickback 6 Instagram Post
Uses OpenRouter API with Google Gemini 2.5 Flash Image (Nano Banana)
"""

import requests
import json
import base64
import time
from pathlib import Path
from PIL import Image
from io import BytesIO

# Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-image-preview"
OUTPUT_DIR = Path(__file__).parent

# Prompts
SLIDE_3_PROMPT = """Create a festive Instagram post graphic (1024x1024px, square 1:1 aspect ratio) listing KannaKickback 6 event activities.

TITLE SECTION (Top):
- "WHAT'S HAPPENING AT KK6?" (large, bold, white text, centered)
- Festive decorative border frame around entire design

MAIN CONTENT - Activity List (Center):
Display exactly 8 items in a vertical list format with icons on left, text on right:

🎅 KannaKlaus & Elves
💍 Special K Ring Toss
🪅 Infamous Kanna Krew Pinata
🛍️ 10+ Vendor Booths
🎁 Giveaways & Raffles
🍜 Orange Chicken from Ginza
💨 420-Friendly Space
✨ VIBES

Each line:
- Icon/emoji on the left (actual emoji characters, large and colorful)
- Activity text on the right (white text, medium-bold weight)
- Evenly spaced vertically
- Left-aligned format
- Good spacing between items for easy reading

BOTTOM TEXT:
"Free to attend. Bring a toy, get goodies at the kickback." (smaller white text, centered)

STYLE & COMPOSITION:
- Festive red and green background with gradient or pattern
- Ornate decorative border frame (gold and green flourishes, holiday themed)
- Clean, list-based layout with excellent readability
- Energetic, festive, easy-to-scan design
- Holiday party invitation aesthetic

COLOR PALETTE:
- Background: Holiday red (#C41E3A) to forest green (#2D5016) gradient
- Border: Festive gold (#FFD700) with green accents
- Text: White (#FFFFFF) for maximum contrast and readability
- Emojis: Full color, vibrant

TYPOGRAPHY:
- Title: Bold, festive font (Impact or Bebas Neue style)
- Activity text: Clean sans-serif (Helvetica/Arial style), medium-bold
- Bottom tagline: Clean sans-serif, regular weight

LAYOUT DETAILS:
- Title takes top 15% of canvas
- Decorative border frames entire image (ornate, holiday style)
- Activity list takes center 70% of canvas
- Bottom tagline takes bottom 10%
- Ample padding inside border for clean appearance

MOOD:
- Fun and festive
- Energetic and exciting
- Cannabis-friendly but wholesome
- Holiday celebration vibes
- Easy to read at a glance
- Inviting and welcoming

CRITICAL REQUIREMENTS:
- Use EXACTLY 8 activity items (no more, no less)
- Do NOT include "Bong Pong Tournament" or any 9th item
- Spell "Kanna Krew" correctly (K-A-N-N-A K-R-E-W) - NOT "Can of Crew"
- All emojis must be visible and colorful
- Text must be highly legible and readable

AVOID:
- Adding extra activities beyond the 8 listed
- Misspelling "Kanna Krew" as "Can of Crew" or any other variation
- Cluttered composition
- Text that's too small to read
- Poor contrast or hard-to-read text
- Off-brand colors
- Corporate or sterile aesthetics"""

SLIDE_4_PROMPT = """Create an Instagram process graphic (1024x1024px, square 1:1 aspect ratio) explaining the KannaKickback 6 toy drive steps.

TITLE:
"HOW THE TOY DRIVE WORKS" (large, bold, forest green text, top center)

MAIN CONTENT - 4-Step Vertical Process Flow:

Display exactly 4 numbered steps in vertical flow from top to bottom, connected by gold downward arrows:

STEP 1: DROP A TOY
(Large green circle with white "1" inside)
Icon: Toy box or donation box illustration
Text lines:
- "Nov 15 - Dec 15 at dispensaries & community spots" (black text)
- "Locations: Ginza, Fancy Pets, Amaranth + more!" (black text)

↓ (Gold arrow pointing down)

STEP 2: PULL UP TO KK6
(Large green circle with white "2" inside)
Icon: Party/celebration icon (people celebrating or party popper)
Text line:
- "Get goodies & freebies at the kickback" (black text)

↓ (Gold arrow pointing down)

STEP 3: CELEBRATE
(Large green circle with white "3" inside)
Icon: Party popper or festive celebration icon
Text line:
- "Celebrate Dec 6th at the biggest Kickback yet" (black text)

↓ (Gold arrow pointing down)

STEP 4: WE DELIVER
(Large green circle with white "4" inside)
Icon: Delivery truck or heart with gift
Text line:
- "All toys go to Sojourner Center" (black text)

BOTTOM TAGLINE:
"Everybody wins. Everybody eats." (centered, gold text, medium-bold)

STYLE & COMPOSITION:
- Clean process diagram aesthetic
- Vertical flow layout, center-aligned
- Large numbered circles (forest green with white numbers)
- Simple, friendly icons for each step
- Gold downward arrows connecting steps
- Clean background (cream or white)
- Professional but approachable design
- Easy-to-follow instructional format

COLOR PALETTE:
- Background: Cream (#FFF8DC) or clean white (#FFFFFF)
- Step numbers/circles: Forest green (#2D5016) with white (#FFFFFF) numbers
- Arrows: Festive gold (#FFD700)
- Body text: Black (#000000) for maximum readability
- Bottom tagline: Gold (#FFD700)

TYPOGRAPHY:
- Title: Bold, festive font (Impact or Bebas Neue style)
- Step headers: Bold sans-serif (Helvetica/Arial style)
- Body text: Clean sans-serif, regular weight
- Bottom tagline: Medium-bold sans-serif

LAYOUT DETAILS:
- Title takes top 10% of canvas
- Each step evenly spaced vertically (4 steps = ~70% of canvas)
- Numbered circles: Large (60-80px diameter), left side of each step
- Icons: Medium size, positioned near step number
- Text: Right-aligned to icon/number, clear and readable
- Arrows: Medium size, centered between steps
- Bottom tagline: Bottom 10% of canvas

ICON STYLE:
- Simple, friendly, illustrative style
- Not too detailed or complex
- Consistent style across all 4 icons
- Complementary to clean diagram aesthetic

MOOD:
- Clear and instructional
- Friendly and welcoming
- Community-focused
- Easy to understand
- Professional but approachable
- Positive and uplifting

CRITICAL REQUIREMENTS:
- Step 2 MUST say "Get goodies & freebies at the kickback"
- Do NOT use language like "instant gift bag" or "bring a toy = gift bag"
- Do NOT say "New, unwrapped toy = gift bag with goodies" anywhere
- All 4 steps must be clearly visible and readable
- Numbers 1-4 must be clear and prominent
- Gold arrows must connect steps visually

AVOID:
- Using "gift bag" language in Step 2
- Cluttered or busy composition
- Text that's too small to read
- Poor alignment or uneven spacing
- Off-brand colors
- Corporate or sterile aesthetics
- Complex or confusing icons"""


def generate_image(prompt, slide_name, attempt=1):
    """Generate image using OpenRouter API"""
    print(f"\n{'='*60}")
    print(f"Generating {slide_name} (Attempt {attempt}/3)")
    print(f"{'='*60}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/zeebot/kickback",
        "X-Title": "KannaKickback Visual Creator"
    }

    payload = {
        "model": MODEL,
        "modalities": ["text", "image"],
        "image_config": {
            "aspect_ratio": "1:1"
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        print(f"[*] Calling OpenRouter API...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        print(f"[+] API call successful")

        # Extract image from response
        image_data = data['choices'][0]['message']['images'][0]['image_url']['url']

        # Save response for debugging
        response_file = OUTPUT_DIR / f"{slide_name}_response_attempt_{attempt}.json"
        with open(response_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] Response saved to: {response_file.name}")

        return {
            "success": True,
            "image_data": image_data,
            "metadata": {
                "model": data.get('model'),
                "tokens": data.get('usage', {}).get('total_tokens'),
                "id": data.get('id')
            }
        }

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print(f"[-] HTTP Error {status_code}: {e}")

        if status_code == 429:
            print(f"[!] Rate limit exceeded. Waiting 60 seconds...")
            time.sleep(60)
            return {"success": False, "error": "rate_limit"}
        elif status_code == 401:
            print(f"[-] Authentication failed. Check API key.")
            return {"success": False, "error": "auth_error"}
        else:
            return {"success": False, "error": f"http_{status_code}"}

    except Exception as e:
        print(f"[-] Error: {e}")
        return {"success": False, "error": str(e)}


def save_image(base64_data, output_path):
    """Decode base64 image and save to file"""
    print(f"\n[+] Saving image to: {output_path}")

    # Remove data URL prefix if present
    if base64_data.startswith('data:image'):
        base64_data = base64_data.split(',', 1)[1]

    # Decode base64
    image_bytes = base64.b64decode(base64_data)

    # Open as PIL Image
    image = Image.open(BytesIO(image_bytes))

    # Check dimensions
    print(f"[*] Image size: {image.size[0]}x{image.size[1]}px")
    print(f"[*] Image format: {image.format}")
    print(f"[*] Image mode: {image.mode}")

    # Save as PNG
    image.save(output_path, 'PNG')

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[+] Saved! File size: {file_size_mb:.2f} MB")

    return True


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("KANNAKICKBACK 6 - SLIDE REGENERATION")
    print("Slides 3 & 4 with Critical Corrections")
    print("="*60)

    slides = [
        {
            "name": "slide_3",
            "prompt": SLIDE_3_PROMPT,
            "output": "post_01_slide_3.png",
            "description": "What to Expect (NO Bong Pong, fixed Kanna Krew spelling)"
        },
        {
            "name": "slide_4",
            "prompt": SLIDE_4_PROMPT,
            "output": "post_01_slide_4.png",
            "description": "How It Works (NO gift bag language)"
        }
    ]

    results = []

    for slide in slides:
        print(f"\n\n{'#'*60}")
        print(f"# {slide['description']}")
        print(f"{'#'*60}")

        # Try up to 3 attempts
        for attempt in range(1, 4):
            result = generate_image(slide['prompt'], slide['name'], attempt)

            if result['success']:
                output_path = OUTPUT_DIR / slide['output']
                if save_image(result['image_data'], output_path):
                    results.append({
                        "slide": slide['name'],
                        "status": "success",
                        "attempt": attempt,
                        "file": str(output_path)
                    })
                    print(f"\n[+] {slide['name']} generated successfully!")
                    break
            else:
                if result['error'] == 'rate_limit' and attempt < 3:
                    print(f"[!] Retrying after rate limit...")
                    continue
                else:
                    results.append({
                        "slide": slide['name'],
                        "status": "failed",
                        "attempt": attempt,
                        "error": result.get('error')
                    })
                    print(f"\n[-] {slide['name']} generation failed after {attempt} attempts")
                    break

        # Wait between slides to avoid rate limiting
        if slide != slides[-1]:
            print(f"\n[!] Waiting 5 seconds before next slide...")
            time.sleep(5)

    # Final report
    print(f"\n\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}")

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    print(f"\n[+] Successful: {len(successful)}/2")
    print(f"[-] Failed: {len(failed)}/2")

    if successful:
        print(f"\n[*] Generated files:")
        for r in successful:
            print(f"  - {Path(r['file']).name}")

    if failed:
        print(f"\n[!] Failed slides:")
        for r in failed:
            print(f"  - {r['slide']}: {r.get('error', 'unknown error')}")

    # Save manifest
    manifest = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "reason": "Critical content corrections",
        "changes": {
            "slide_3": [
                "REMOVED: Bong Pong Tournament",
                "FIXED: Kanna Krew spelling (was 'Can of Crew')",
                "Reduced from 9 to 8 activities"
            ],
            "slide_4": [
                "REMOVED: 'instant gift bag' language",
                "UPDATED: Step 2 to 'Get goodies & freebies at the kickback'"
            ]
        },
        "results": results
    }

    manifest_file = OUTPUT_DIR / "regeneration_manifest_v2.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\n[+] Manifest saved: {manifest_file.name}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
