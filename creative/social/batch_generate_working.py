#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KK6 Batch Image Generation - Working Version
Based on proven POST_02 generation method
"""

import requests
import json
import base64
from PIL import Image
from io import BytesIO
import time
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# API Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-image-preview"

def read_prompts_from_specs(specs_file):
    """Extract AI generation prompts from design specs file"""
    with open(specs_file, 'r', encoding='utf-8') as f:
        content = f.read()

    prompts = []
    lines = content.split('\n')
    in_prompt = False
    current_prompt = []

    for line in lines:
        if '## AI IMAGE GENERATION PROMPT' in line.upper():
            in_prompt = True
            current_prompt = []
        elif in_prompt:
            if line.startswith('---') or (line.startswith('##') and 'PROMPT' not in line.upper()):
                if current_prompt:
                    prompt_text = '\n'.join(current_prompt).strip()
                    if prompt_text and len(prompt_text) > 50:
                        prompts.append(prompt_text.strip('"'))
                    current_prompt = []
                if line.startswith('---'):
                    in_prompt = False
            elif line.strip() and not line.startswith('#'):
                current_prompt.append(line.strip())

    return prompts

def generate_image(prompt, output_path):
    """Generate image using OpenRouter API"""

    print(f"\nGenerating: {output_path.name}...")

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
        start_time = time.time()
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        generation_time = time.time() - start_time

        # Extract image from response
        image_data = data['choices'][0]['message']['images'][0]

        # Decode and save
        img_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(img_bytes))

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as PNG
        img.save(output_path, "PNG", optimize=True)

        file_size_kb = output_path.stat().st_size // 1024
        print(f"✓ Saved ({file_size_kb}KB) in {generation_time:.1f}s")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

# Posts to generate
POSTS = [
    ('POST_03', 4),
    ('POST_04', 3),
    ('POST_05', 5),
    ('POST_06', 1),
    ('POST_08', 2),
    ('POST_09', 6),
    ('POST_10', 1),
]

def main():
    print("=" * 60)
    print("KK6 BATCH IMAGE GENERATION")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Posts: {len(POSTS)}")
    print(f"Total images: {sum([n for _, n in POSTS])}")
    print("=" * 60)

    total_generated = 0
    total_failed = 0

    for post_name, num_slides in POSTS:
        print(f"\n[{post_name}] - {num_slides} slides")

        # Read design specs
        specs_file = Path(f"{post_name}_DESIGN_SPECS.md")
        if not specs_file.exists():
            print(f"  [SKIP] Missing {specs_file}")
            total_failed += num_slides
            continue

        # Extract prompts
        prompts = read_prompts_from_specs(specs_file)

        if not prompts:
            print(f"  [SKIP] No prompts found in {specs_file}")
            total_failed += num_slides
            continue

        if len(prompts) < num_slides:
            print(f"  [WARNING] Found {len(prompts)} prompts, expected {num_slides}")

        # Create output directory
        output_dir = Path(f"images/{post_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate each slide
        for i, prompt in enumerate(prompts[:num_slides], 1):
            output_file = output_dir / f"slide_{i}.png"

            if generate_image(prompt, output_file):
                total_generated += 1
            else:
                total_failed += 1

            # Rate limiting: 2-3 seconds between requests
            if i < len(prompts):
                time.sleep(3)

    print("\n" + "=" * 60)
    print(f"COMPLETE!")
    print(f"  Generated: {total_generated} images")
    print(f"  Failed: {total_failed} images")
    if total_generated + total_failed > 0:
        success_rate = (total_generated / (total_generated + total_failed) * 100)
        print(f"  Success: {success_rate:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
