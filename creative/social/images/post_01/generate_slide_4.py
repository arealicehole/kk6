#!/usr/bin/env python3
"""
Generate Slide 4 for KannaKickback 6 Instagram carousel
Using OpenRouter API with Nano Banana (Gemini 2.5 Flash Image)
"""

import os
import json
import base64
import requests
from pathlib import Path

# Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-image-preview"

# Load the prompt
prompt_file = Path(__file__).parent / "slide_4_generation_prompt.txt"
with open(prompt_file, 'r', encoding='utf-8') as f:
    image_prompt = f.read()

print("Generating Slide 4: HOW IT WORKS")
print("=" * 60)
print(f"Using model: {MODEL}")
print(f"Prompt length: {len(image_prompt)} characters")
print("=" * 60)

# Prepare the API request
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/kannakrew/kickback",
    "X-Title": "KannaKickback Visual Creator"
}

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": image_prompt
        }
    ],
    "image_config": {
        "aspect_ratio": "1:1"
    }
}

print("\nCalling OpenRouter API...")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    result = response.json()
    print("[SUCCESS] API call successful!")

    # Extract the image data
    if 'choices' in result and len(result['choices']) > 0:
        message = result['choices'][0]['message']

        # Check if there are images in the message
        image_data = None

        if 'images' in message and len(message['images']) > 0:
            # New format: images array
            first_image = message['images'][0]
            if 'image_url' in first_image:
                url = first_image['image_url']['url']
                if url.startswith('data:image'):
                    image_data = url.split(',')[1]
        elif 'content' in message:
            # Fallback: check content field
            content = message['content']

            # Look for base64 image data in the response
            if isinstance(content, str):
                # Sometimes it's a direct base64 string
                if content.startswith('data:image'):
                    # Extract base64 from data URL
                    image_data = content.split(',')[1]
                elif len(content) > 100:  # Likely base64
                    image_data = content
            elif isinstance(content, list):
                # Sometimes it's an array with image parts
                for part in content:
                    if isinstance(part, dict) and 'image_url' in part:
                        url = part['image_url']['url']
                        if url.startswith('data:image'):
                            image_data = url.split(',')[1]
                        break

        if image_data:
            # Decode and save
            output_path = Path(__file__).parent / "post_01_slide_4.png"

            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(image_data))

            print(f"\n[SUCCESS] Image saved successfully!")
            print(f"Location: {output_path}")
            print(f"Size: {os.path.getsize(output_path) / 1024:.2f} KB")

            # Save metadata
            metadata = {
                "slide_number": 4,
                "slide_name": "HOW IT WORKS",
                "generated_at": response.headers.get('date'),
                "model": MODEL,
                "prompt_length": len(image_prompt),
                "file_size_kb": os.path.getsize(output_path) / 1024,
                "status": "success"
            }

            metadata_path = Path(__file__).parent / "post_01_slide_4_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            print(f"Metadata saved: {metadata_path}")

        else:
            print("\n[WARNING] No image data found in response")
            print("Response structure:")
            print(json.dumps(result, indent=2))
    else:
        print("\n[WARNING] Unexpected response structure")
        print("Full response:")
        print(json.dumps(result, indent=2))

except requests.exceptions.HTTPError as e:
    print(f"\n[ERROR] HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except requests.exceptions.Timeout:
    print("\n[ERROR] Request timed out (>120 seconds)")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Generation complete!")
