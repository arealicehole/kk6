#!/usr/bin/env python3
"""
KannaKickback 6 Facebook Event Cover Generator
Uses OpenRouter API with Gemini 2.5 Flash Image (Nano Banana)
"""

import json
import base64
import os
from pathlib import Path
import time

try:
    import requests
except ImportError:
    print("Installing requests library...")
    os.system("pip install requests")
    import requests

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow library...")
    os.system("pip install Pillow")
    from PIL import Image

# Configuration
API_KEY = "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"
API_BASE = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-2.5-flash-image-preview"
OUTPUT_DIR = Path(r"C:\Users\figon\zeebot\kickback\creative\social\images\facebook")

# Prompt
PROMPT = """A festive holiday event cover photo for KannaKickback 6 - a cannabis-friendly charity toy drive party.

MAIN SUBJECT - KANNAKLAUS CHARACTER:
- Jolly Santa Claus figure positioned center-left of frame
- Red Santa suit with white fur trim and subtle cannabis leaf patterns embroidered on the fabric
- Classic red Santa hat with white fur trim
- Long flowing white beard with small decorative braids and beads for character
- Friendly, warm, welcoming smile - jolly and inviting expression
- Holding wrapped toy presents in arms, surrounded by colorful gift boxes
- Optional: wearing a work apron over the suit (workshop vibe)

BACKGROUND SCENE:
- Cozy festive holiday workshop or decorated indoor space
- Warm lighting with soft bokeh glow effects creating magical atmosphere
- Cannabis leaf shaped snowflakes gently falling throughout the scene
- Multiple wrapped toy presents and gift boxes scattered around (charity toy drive theme)
- Holiday decorations: subtle string lights, garland, ornaments in background
- Warm gradient background blending holiday red, forest green, and gold tones
- Professional, polished, high-quality photography style

COLOR PALETTE (EXACT COLORS):
- Forest Green (#2D5016) - deep rich green in background elements
- Cannabis Green (#4CAF50) - accent highlights and cannabis leaf motifs
- Holiday Red (#C41E3A) - Santa suit, festive accents
- Festive Gold (#FFD700) - premium touches, highlights, ornament accents
- Cream (#FFF8DC) - soft warm lighting
- White (#FFFFFF) - fur trim, snowflakes, bright highlights
- Black (#000000) - shadows, depth, contrast

TEXT OVERLAYS (BOLD, HIGHLY READABLE):

Top center - Extra large bold headline:
"KANNA KICKBACK 6"
- Font style: Bold impact/bebas neue style, extremely thick and prominent
- Color: Pure white (#FFFFFF) with thick black outline stroke (3-4px)
- Size: Very large, dominant, impossible to miss

Below headline - Subheadline:
"Holiday Party & Charity Toy Drive"
- Font: Clean sans-serif medium weight
- Color: Festive gold (#FFD700) with subtle shadow
- Size: Medium complementary

Center middle - Event details:
"SATURDAY, DECEMBER 6TH • 2-6 PM
GINZA, GOLD CANYON, AZ
FREE EVENT"
- Font: Clean readable sans-serif
- Color: White (#FFFFFF) with black outline
- Include simple decorative elements

Bottom center - Tagline:
"Fun first. Charity always."
- Font: Hand-drawn brush script style
- Color: Cannabis green (#4CAF50)
- Size: Medium, memorable

STYLE REQUIREMENTS:
- Composition: Balanced, professional, not cluttered, room to breathe
- Mood: Festive, welcoming, community-focused, cannabis-positive but wholesome
- Quality: High-end social media ready, polished, sharp details
- Text readability: CRITICAL - thick outlines, maximum contrast, bold fonts
- Atmosphere: Warm inviting holiday celebration meets charitable giving
- Cannabis elements: Present but tasteful (family-friendly charity event)

ASPECT RATIO: 16:9 landscape format (1344x768 pixels)

NEGATIVE PROMPTS: Corporate sterile look, too serious, overly childish, cluttered messy composition, low contrast text, off-brand colors, aggressive dark themes, cheap graphics, poor quality, blurry, distorted faces."""


def generate_image(attempt=1, max_attempts=3):
    """Generate image using OpenRouter API"""

    print(f"\n{'='*60}")
    print(f"ATTEMPT {attempt} of {max_attempts}")
    print(f"{'='*60}\n")

    print("Calling OpenRouter API with Gemini 2.5 Flash Image (Nano Banana)...")
    print(f"Model: {MODEL}")
    print(f"Aspect Ratio: 16:9 (1344x768)")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/kanna-kickback",
        "X-Title": "KannaKickback 6 Visual Creator"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": PROMPT
            }
        ],
        "image": {
            "aspect_ratio": "16:9"  # This will generate 1344x768
        }
    }

    try:
        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )

        print(f"API Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")

            # Retry on rate limit or server error
            if response.status_code in [429, 500, 503] and attempt < max_attempts:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return generate_image(attempt + 1, max_attempts)

            return None

        data = response.json()

        # Extract base64 image from response
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]

            # Look for base64 image data
            if "data:image/" in content:
                # Extract base64 data
                image_data = content.split("data:image/png;base64,")[1].split('"')[0]
                return image_data
            else:
                print(f"Unexpected response format: {content[:200]}")
                return None
        else:
            print(f"No image in response: {data}")
            return None

    except Exception as e:
        print(f"Exception: {e}")
        if attempt < max_attempts:
            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            return generate_image(attempt + 1, max_attempts)
        return None


def save_base64_image(base64_data, filepath):
    """Save base64 encoded image to file"""
    try:
        image_bytes = base64.b64decode(base64_data)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        print(f"✓ Saved: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Error saving image: {e}")
        return False


def upscale_and_crop(input_path, output_path):
    """Upscale from 1344x768 to 1920x1080, then crop to 1920x1005"""
    try:
        print("\n" + "="*60)
        print("POST-PROCESSING: Upscale and Crop")
        print("="*60 + "\n")

        # Open base image
        img = Image.open(input_path)
        print(f"Base image size: {img.size}")

        # Upscale to 1920x1080 (maintains 16:9)
        img_upscaled = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        print(f"Upscaled to: {img_upscaled.size}")

        # Crop to 1920x1005 (center crop)
        top_margin = (1080 - 1005) // 2  # 37px
        img_final = img_upscaled.crop((0, top_margin, 1920, 1005 + top_margin))
        print(f"Cropped to: {img_final.size}")

        # Save final image
        img_final.save(output_path, "PNG", quality=95)

        # Check file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Final file size: {file_size_mb:.2f} MB")

        if file_size_mb > 8:
            print("⚠ Warning: File size exceeds 8MB Facebook limit")
        else:
            print("✓ File size within Facebook limits")

        print(f"✓ Final image saved: {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error in post-processing: {e}")
        return False


def main():
    """Main execution"""

    print("\n" + "="*60)
    print("KANNAKICKBACK 6 FACEBOOK EVENT COVER GENERATOR")
    print("="*60 + "\n")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate image
    base64_data = generate_image()

    if not base64_data:
        print("\n✗ GENERATION FAILED")
        return 1

    print("\n✓ GENERATION SUCCESSFUL")

    # Save base image (1344x768)
    base_path = OUTPUT_DIR / "kk6_cover_1344x768.png"
    if not save_base64_image(base64_data, base_path):
        return 1

    # Upscale and crop to Facebook specs (1920x1005)
    final_path = OUTPUT_DIR / "kk6_event_cover_1920x1005.png"
    if not upscale_and_crop(base_path, final_path):
        return 1

    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    print(f"\nBase image (16:9): {base_path}")
    print(f"Final image (Facebook): {final_path}")
    print("\n✓ Ready for upload to Facebook Event")

    return 0


if __name__ == "__main__":
    exit(main())
