#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KannaKickback 6 Facebook Event Cover Generator
CRITICAL: Uses 16:9 aspect ratio to avoid distortion
Output: 1920x1005 Facebook event cover from 1344x768 base
"""

import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os
import sys

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# API Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-image-preview"

# Output paths
OUTPUT_DIR = "C:/Users/figon/zeebot/kickback/creative/social/images/facebook"
BASE_IMAGE_PATH = os.path.join(OUTPUT_DIR, "kk6_cover_16x9_1344x768.png")
FINAL_IMAGE_PATH = os.path.join(OUTPUT_DIR, "kk6_event_cover_1920x1005_v2.png")

# Optimized prompt for KannaKlaus Facebook event cover
PROMPT = """Create a festive holiday event cover photo for KannaKickback 6, a cannabis-friendly charity toy drive party.

LAYOUT (16:9 landscape format):
- KannaKlaus character positioned center-left (leaves horizontal space)
- Festive holiday workshop background with warm lighting
- Cannabis leaf snowflakes falling across the scene
- Wrapped toy presents scattered around KannaKlaus and in foreground
- Soft bokeh glow effects for festive atmosphere

CHARACTER - KannaKlaus:
- Jolly Santa in red suit with white fur trim
- Long beard (possibly with braids/beads)
- Classic Santa hat
- Subtle cannabis leaf patterns on suit (tasteful, small)
- Friendly, welcoming expression
- Holding/surrounded by wrapped toy gifts
- Workshop apron over suit (optional)

TEXT OVERLAYS (all centered for mobile safety):

**Top Center (Extra Large, Bold):**
KANNA KICKBACK 6
(White #FFFFFF text with thick black outline, Bebas Neue/Impact style)

**Below Headline:**
Holiday Party & Charity Toy Drive
(Festive Gold #FFD700 or White, clean sans-serif)

**Center (below subheadline):**
📅 SATURDAY, DECEMBER 6TH • 2-6 PM
📍 GINZA, GOLD CANYON, AZ
🎟️ FREE EVENT
(White text with emoji icons)

**Bottom Center:**
Fun first. Charity always.
(Cannabis Green #4CAF50 or Holiday Red #C41E3A, brush/hand-drawn style)

COLOR PALETTE:
- Background: Warm festive gradient (reds, greens, golds blending)
- Forest Green (#2D5016) for backgrounds
- Cannabis Green (#4CAF50) for accents
- Holiday Red (#C41E3A) for KannaKlaus suit
- Festive Gold (#FFD700) for highlights
- White (#FFFFFF) for text with black outlines
- Cream (#FFF8DC) for soft background tones

DECORATIVE ELEMENTS:
- Cannabis leaf snowflakes falling throughout
- Wrapped presents in various sizes
- Holiday ornaments (subtle background)
- Optional: String lights or garland
- Soft lighting/glow effects

STYLE:
- Professional but playful
- Festive, welcoming, community-focused
- Cannabis-positive but wholesome (family-friendly charity)
- High-end, polished, social media ready
- Balanced composition, not cluttered
- HIGH text readability (thick outlines, high contrast)

AVOID:
- Corporate or sterile look
- Too serious or harsh
- Overly childish
- Cluttered composition
- Low contrast text
- Aggressive or dark themes
- Cheap-looking graphics

This is for the 6th annual KannaKickback benefiting the Sojourner Center (domestic violence support). Past years raised $4,200, $5,500, and $6,500 in toys. Goal: $7,000+ this year.

Branding: All K's, no C's (KannaKrew, KannaKickback, KannaKlaus)"""


def generate_image_16x9():
    """
    Generate image using OpenRouter with 16:9 aspect ratio
    CRITICAL: This ensures 1344x768 output (not 1024x1024)
    """
    print("🎨 Generating KK6 Facebook event cover...")
    print("📐 Aspect ratio: 16:9 (1344x768)")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/yourusername/zeebot",
        "X-Title": "KannaKickback 6 Visual Creator"
    }

    payload = {
        "model": MODEL,
        "modalities": ["text", "image"],
        "image_config": {
            "aspect_ratio": "16:9"  # CRITICAL: This gets us 1344x768 instead of 1024x1024
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
        print("📡 Calling OpenRouter API...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        print("✅ API call successful")

        # Extract image from response
        # The image might be in different formats - check structure
        image_data = data['choices'][0]['message']['images'][0]

        # Debug: check what type of data we got
        print(f"🔍 Image data type: {type(image_data)}")

        # Handle both string and dict formats
        if isinstance(image_data, dict):
            # OpenRouter returns: {'type': 'image_url', 'image_url': {'url': 'data:...'}}
            if 'image_url' in image_data:
                image_data = image_data['image_url']['url']
            elif 'url' in image_data:
                image_data = image_data['url']
            elif 'data' in image_data:
                image_data = image_data['data']
            else:
                print(f"🔍 Image data keys: {image_data.keys()}")
                raise ValueError(f"Unexpected image data format: {image_data}")

        # Now decode base64
        if image_data.startswith('data:image'):
            image_data = image_data.split(',', 1)[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        # VERIFY dimensions (should be 1344x768, not 1024x1024!)
        print(f"📏 Generated image dimensions: {image.size}")

        if image.size == (1024, 1024):
            print("⚠️ WARNING: Got 1024x1024 square! API did not use 16:9 aspect ratio!")
            print("⚠️ This will cause distortion when stretched to Facebook size.")
        elif image.size == (1344, 768):
            print("✅ Perfect! Got 1344x768 (true 16:9 landscape)")
        else:
            print(f"⚠️ Unexpected dimensions: {image.size}")

        # Save base image
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        image.save(BASE_IMAGE_PATH, 'PNG', quality=95)
        print(f"💾 Saved base image: {BASE_IMAGE_PATH}")

        return image

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def upscale_and_crop(base_image):
    """
    Upscale 1344x768 to 1920x1080, then center-crop to 1920x1005
    """
    print("\n📈 Upscaling and cropping for Facebook...")

    # Step 1: Upscale to 1920x1080 (maintains 16:9)
    print("  - Upscaling 1344x768 → 1920x1080 (Lanczos)")
    upscaled = base_image.resize((1920, 1080), Image.Resampling.LANCZOS)

    # Step 2: Center-crop to 1920x1005
    # Remove 37px from top, 38px from bottom
    top_margin = (1080 - 1005) // 2  # = 37px
    bottom_margin = top_margin + 1005  # = 1042px

    print(f"  - Cropping to 1920x1005 (remove {top_margin}px top, {1080 - bottom_margin}px bottom)")
    final_image = upscaled.crop((0, top_margin, 1920, bottom_margin))

    # Verify final dimensions
    print(f"📏 Final image dimensions: {final_image.size}")
    assert final_image.size == (1920, 1005), f"Wrong final size: {final_image.size}"

    # Save final image
    final_image.save(FINAL_IMAGE_PATH, 'PNG', quality=95)
    print(f"💾 Saved final image: {FINAL_IMAGE_PATH}")

    # Check file size
    file_size_mb = os.path.getsize(FINAL_IMAGE_PATH) / (1024 * 1024)
    print(f"📦 File size: {file_size_mb:.2f} MB (Facebook max: 8 MB)")

    if file_size_mb > 8:
        print("⚠️ WARNING: File size exceeds Facebook's 8MB limit!")
    else:
        print("✅ File size OK for Facebook")

    return final_image


def main():
    """
    Full workflow: Generate → Upscale → Crop
    """
    print("=" * 60)
    print("KannaKickback 6 Facebook Event Cover Generator")
    print("=" * 60)
    print()

    # Step 1: Generate base image at 16:9 (1344x768)
    base_image = generate_image_16x9()

    # Step 2: Upscale to 1920x1080 and crop to 1920x1005
    final_image = upscale_and_crop(base_image)

    print()
    print("=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)
    print(f"Base image (16:9):  {BASE_IMAGE_PATH}")
    print(f"Final image:        {FINAL_IMAGE_PATH}")
    print()
    print("Next steps:")
    print("1. Review the image for quality")
    print("2. Check that KannaKlaus is NOT squished/distorted")
    print("3. Verify text is readable on both desktop and mobile")
    print("4. Upload to Facebook event page")
    print()


if __name__ == "__main__":
    main()
