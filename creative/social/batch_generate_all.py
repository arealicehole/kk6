#!/usr/bin/env python3
"""
KK6 Batch Image Generation Script
Generates all remaining Instagram posts for KannaKickback 6
"""

import os
import json
import base64
import requests
import time
from pathlib import Path

# Load API config
config_path = Path('C:/Users/figon/zeebot/.claude/agents/visual-creator/config/api-config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

API_KEY = config['openrouter']['api_key']
BASE_URL = config['openrouter']['base_url']
MODEL = config['openrouter']['model']

def generate_image(prompt, output_path):
    """Generate a single image using OpenRouter API"""
    print(f"  Generating: {output_path.name}...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/anthropics/claude-code",
        "X-Title": "KannaKickback 6 Content Generation"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Generate an image: {prompt}"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        result = response.json()

        # Extract image URL from response
        image_url = None
        for choice in result.get('choices', []):
            content = choice.get('message', {}).get('content', '')
            if 'https://' in content and ('media.openrouter.ai' in content or 'generativelanguage.googleapis.com' in content):
                # Extract URL from markdown or plain text
                import re
                urls = re.findall(r'https://[^\s\)]+', content)
                if urls:
                    image_url = urls[0]
                    break

        if not image_url:
            print(f"    [ERROR] No image URL found in response")
            return False

        # Download image
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(img_response.content)

        print(f"    [OK] Saved ({len(img_response.content) // 1024}KB)")
        return True

    except Exception as e:
        print(f"    [ERROR] {str(e)}")
        return False

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
            if line.startswith('---') or line.startswith('##'):
                if current_prompt:
                    prompt_text = '\n'.join(current_prompt).strip()
                    if prompt_text and len(prompt_text) > 50:
                        prompts.append(prompt_text.strip('"'))
                    current_prompt = []
                in_prompt = False if line.startswith('---') else True
            elif line.strip() and not line.startswith('#'):
                current_prompt.append(line.strip())

    return prompts

# Posts to generate
POSTS = [
    ('POST_03', 4),  # Box Locations - 4 slides
    ('POST_04', 3),  # Box Delivery - 3 slides
    ('POST_05', 5),  # Why We Do This - 5 slides
    ('POST_06', 1),  # Green Friday - 1 slide
    ('POST_08', 2),  # Email Blast #2 - 2 slides
    ('POST_09', 6),  # Event Guide - 6 slides
    ('POST_10', 1),  # 24-Hour Warning - 1 slide
]

def main():
    print("KK6 BATCH IMAGE GENERATION")
    print("=" * 60)
    print(f"Using model: {MODEL}")
    print(f"Total posts: {len(POSTS)}")
    print(f"Total images: {sum([n for _, n in POSTS])}")
    print("=" * 60)

    total_generated = 0
    total_failed = 0

    for post_name, num_slides in POSTS:
        print(f"\n[{post_name}] ({num_slides} slides)")

        # Read design specs
        specs_file = Path(f"{post_name}_DESIGN_SPECS.md")
        if not specs_file.exists():
            print(f"  [MISSING] {specs_file}")
            total_failed += num_slides
            continue

        # Extract prompts
        prompts = read_prompts_from_specs(specs_file)

        if len(prompts) < num_slides:
            print(f"  [WARNING] Found {len(prompts)} prompts, expected {num_slides}")
            print(f"  Will generate {len(prompts)} slides")

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

            # Rate limiting: 20 req/min = 3 seconds between requests
            if i < len(prompts):
                time.sleep(3)

    print("\n" + "=" * 60)
    print(f"GENERATION COMPLETE!")
    print(f"   Generated: {total_generated} images")
    print(f"   Failed: {total_failed} images")
    print(f"   Success rate: {(total_generated / (total_generated + total_failed) * 100):.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
