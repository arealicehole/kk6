#!/usr/bin/env python3
"""
Regenerate ONLY Slide 4 with very explicit step separation
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

# More explicit prompt with clear separation
SLIDE_4_PROMPT = """Create an Instagram process infographic (1024x1024px, square format) showing a 4-step toy drive process.

TITLE (Top, 10% of canvas):
"HOW THE TOY DRIVE WORKS" (large, bold, forest green #2D5016)

BACKGROUND:
Clean cream (#FFF8DC) or white background

MAIN CONTENT - Four distinct steps, vertically stacked:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP ONE (20% of canvas):
Large green circle with white "1"
Icon: Donation box with toys
Title: "DROP A TOY"
Text: "Nov 15 - Dec 15 at dispensaries & community spots"
Text: "Locations: Ginza, Fancy Pets, Amaranth + more!"
Gold arrow pointing down ↓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP TWO (20% of canvas):
Large green circle with white "2"
Icon: Celebration/party people
Title: "PULL UP TO KK6"
Text: "Get goodies & freebies at the kickback"
Gold arrow pointing down ↓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP THREE (20% of canvas):
Large green circle with white "3"
Icon: Party popper or confetti
Title: "CELEBRATE"
Text: "Celebrate Dec 6th at the biggest Kickback yet"
Gold arrow pointing down ↓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP FOUR (20% of canvas):
Large green circle with white "4"
Icon: Delivery truck or heart
Title: "WE DELIVER"
Text: "All toys go to Sojourner Center"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOTTOM TAGLINE (Bottom 10%):
"Everybody wins. Everybody eats." (gold #FFD700, centered)

CRITICAL LAYOUT REQUIREMENTS:
- Each step must be visually separated
- Four numbered circles: 1, 2, 3, 4 (in that order, top to bottom)
- Each step has its own distinct section
- Gold arrows between each step
- Even vertical spacing between all 4 steps
- Step 2 and Step 3 are SEPARATE - do not combine them

COLORS:
- Numbers/circles: Forest green #2D5016 with white numbers
- Arrows: Gold #FFD700
- Text: Black #000000
- Tagline: Gold #FFD700

STYLE:
- Clean, instructional process diagram
- Simple friendly icons
- Professional but approachable
- Easy to follow

CRITICAL: There must be exactly FOUR steps numbered 1, 2, 3, 4. Do not skip step 3. Do not combine steps 2 and 3."""


def generate_image(prompt, attempt=1):
    """Generate image using OpenRouter API"""
    print(f"\n{'='*60}")
    print(f"Generating Slide 4 (Attempt {attempt}/3)")
    print(f"{'='*60}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
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

        image_data = data['choices'][0]['message']['images'][0]['image_url']['url']

        response_file = OUTPUT_DIR / f"slide_4_response_attempt_{attempt}_v2.json"
        with open(response_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] Response saved")

        return {"success": True, "image_data": image_data}

    except Exception as e:
        print(f"[-] Error: {e}")
        return {"success": False, "error": str(e)}


def save_image(base64_data, output_path):
    """Save image"""
    print(f"\n[+] Saving image...")

    if base64_data.startswith('data:image'):
        base64_data = base64_data.split(',', 1)[1]

    image_bytes = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_bytes))

    print(f"[*] Size: {image.size[0]}x{image.size[1]}px")

    image.save(output_path, 'PNG')

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[+] Saved! {file_size_mb:.2f} MB")

    return True


def main():
    print("\n" + "="*60)
    print("REGENERATING SLIDE 4 ONLY")
    print("="*60)

    for attempt in range(1, 4):
        result = generate_image(SLIDE_4_PROMPT, attempt)

        if result['success']:
            output_path = OUTPUT_DIR / "post_01_slide_4.png"
            if save_image(result['image_data'], output_path):
                print(f"\n[+] SUCCESS!")
                break
        else:
            print(f"\n[-] Attempt {attempt} failed")
            if attempt < 3:
                time.sleep(5)

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
