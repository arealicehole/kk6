#!/usr/bin/env python3
"""
Extract image from API response debug file
"""

import json
import base64
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path(r"C:\Users\figon\zeebot\kickback\creative\social\images\facebook")

# Load the debug response
debug_file = OUTPUT_DIR / "api_response_debug.json"
print(f"Loading API response from: {debug_file}")

with open(debug_file, "r") as f:
    data = json.load(f)

print(f"Response keys: {data.keys()}")

if "choices" in data:
    print(f"Number of choices: {len(data['choices'])}")

    for i, choice in enumerate(data["choices"]):
        print(f"\nChoice {i}:")
        print(f"  Keys: {choice.keys()}")

        if "message" in choice:
            msg = choice["message"]
            print(f"  Message keys: {msg.keys()}")

            if "content" in msg:
                content = msg["content"]
                print(f"  Content type: {type(content)}")
                print(f"  Content length: {len(str(content))}")

                # Check if it's a list
                if isinstance(content, list):
                    print(f"  Content is list with {len(content)} items")
                    for j, item in enumerate(content):
                        print(f"    Item {j} type: {type(item)}")
                        if isinstance(item, dict):
                            print(f"    Item {j} keys: {item.keys()}")

                            # Check for inline_data (Gemini format)
                            if "inline_data" in item:
                                inline = item["inline_data"]
                                print(f"    Found inline_data!")
                                print(f"    Mime type: {inline.get('mime_type', 'unknown')}")

                                if "data" in inline:
                                    base64_data = inline["data"]
                                    print(f"    Base64 data length: {len(base64_data)}")

                                    # Save image
                                    try:
                                        image_bytes = base64.b64decode(base64_data)
                                        base_path = OUTPUT_DIR / "kk6_cover_1344x768.png"

                                        with open(base_path, "wb") as img_file:
                                            img_file.write(image_bytes)

                                        print(f"\n[SUCCESS] Image saved to: {base_path}")

                                        # Verify
                                        img = Image.open(base_path)
                                        print(f"[SUCCESS] Image size: {img.size}, format: {img.format}")

                                        # Now upscale and crop
                                        print("\n" + "="*60)
                                        print("POST-PROCESSING: Upscale and Crop")
                                        print("="*60 + "\n")

                                        # Upscale to 1920x1080
                                        img_upscaled = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                                        print(f"Upscaled to: {img_upscaled.size}")

                                        # Crop to 1920x1005
                                        top_margin = (1080 - 1005) // 2  # 37px
                                        img_final = img_upscaled.crop((0, top_margin, 1920, 1005 + top_margin))
                                        print(f"Cropped to: {img_final.size}")

                                        # Save final
                                        final_path = OUTPUT_DIR / "kk6_event_cover_1920x1005.png"
                                        img_final.save(final_path, "PNG", quality=95)

                                        import os
                                        file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
                                        print(f"Final file size: {file_size_mb:.2f} MB")

                                        if file_size_mb <= 8:
                                            print("[SUCCESS] File size within Facebook limits")
                                        else:
                                            print("[WARNING] File size exceeds 8MB")

                                        print(f"\n[SUCCESS] Final image: {final_path}")
                                        print("\n" + "="*60)
                                        print("WORKFLOW COMPLETE")
                                        print("="*60)

                                    except Exception as e:
                                        print(f"[ERROR] Failed to save/process image: {e}")
                                        import traceback
                                        traceback.print_exc()
