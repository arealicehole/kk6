#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KK6 Event Flyer - Final Regeneration
Fixes: 1) Simplify graphics, 2) Correct participation steps
"""

import sys
import json
import base64
import requests
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-2.5-flash-image-preview"

# Paths
PROMPT_FILE = Path("C:/Users/figon/zeebot/kickback/creative/print/flyer_generation_prompt_v2.txt")
OUTPUT_FILE = Path("C:/Users/figon/zeebot/kickback/creative/print/KK6_EVENT_FLYER.png")
RESPONSE_FILE = Path("C:/Users/figon/zeebot/kickback/creative/print/KK6_EVENT_FLYER_FINAL.json")

print("=" * 70)
print("KK6 EVENT FLYER - FINAL REGENERATION")
print("=" * 70)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Model: {MODEL}")
print(f"Output: {OUTPUT_FILE}")
print()

# Load prompt
print("Loading generation prompt...")
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    prompt = f.read()

print(f"Prompt loaded: {len(prompt)} characters")
print()

# Prepare API request
print("Preparing API request...")
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/kannakrew/kickback",
    "X-Title": "KannaKickback 6 Flyer Generator"
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
                    "text": prompt
                }
            ]
        }
    ]
}

# Call API
print("Calling OpenRouter API...")
print("(This may take 30-60 seconds)")
print()

try:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    response.raise_for_status()

    result = response.json()

    # Save full response
    with open(RESPONSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"✓ API response saved to: {RESPONSE_FILE}")

    # Extract image data (using same logic as working script)
    message = result['choices'][0]['message']
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
        print(f"[DEBUG] Full response: {json.dumps(result, indent=2)}")
        raise ValueError("Could not find image data in API response")

    # Handle different response formats
    if isinstance(image_data, dict):
        print(f"[DEBUG] Image data dict keys: {list(image_data.keys())}")
        if 'image_url' in image_data:
            image_data = image_data['image_url'].get('url')
        else:
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
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_bytes(image_bytes)

    print(f"✓ Image saved to: {OUTPUT_FILE}")
    print(f"  Size: {len(image_bytes):,} bytes")

    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print()
    print("CRITICAL FIXES APPLIED:")
    print("  ✓ Graphics simplified (minimal KannaKlaus)")
    print("  ✓ Participation steps corrected:")
    print("    1. Drop a new, unwrapped toy (Nov 15-Dec 15)")
    print("    2. Get goodies & freebies at the kickback")
    print("    3. Celebrate at the party (Dec 6, 2-6pm)")
    print()
    print(f"Flyer saved to: {OUTPUT_FILE}")
    print()

except requests.exceptions.Timeout:
    print("✗ ERROR: API request timed out")
    print("The image generation service may be overloaded. Try again in a few moments.")
    exit(1)

except requests.exceptions.RequestException as e:
    print(f"✗ ERROR: API request failed")
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
    exit(1)

except Exception as e:
    print(f"✗ ERROR: Unexpected error")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
