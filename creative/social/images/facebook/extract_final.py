#!/usr/bin/env python3
"""
Extract image from API response - FINAL VERSION
"""

import json
import base64
from pathlib import Path
from PIL import Image
import os

OUTPUT_DIR = Path(r"C:\Users\figon\zeebot\kickback\creative\social\images\facebook")

# Load the debug response
debug_file = OUTPUT_DIR / "api_response_debug.json"
print(f"Loading API response from: {debug_file}")

with open(debug_file, "r") as f:
    data = json.load(f)

if "choices" in data and len(data["choices"]) > 0:
    choice = data["choices"][0]
    message = choice.get("message", {})

    if "images" in message and len(message["images"]) > 0:
        img_obj = message["images"][0]
        print(f"Image object keys: {img_obj.keys()}")

        if "image_url" in img_obj:
            image_url_obj = img_obj["image_url"]
            print(f"Image URL object type: {type(image_url_obj)}")

            if isinstance(image_url_obj, dict) and "url" in image_url_obj:
                url = image_url_obj["url"]
            elif isinstance(image_url_obj, str):
                url = image_url_obj
            else:
                print(f"[ERROR] Unexpected image_url format: {image_url_obj}")
                exit(1)

            print(f"URL type: {type(url)}")
            print(f"URL length: {len(url)}")
            print(f"URL preview: {url[:100]}...")

            # Extract base64 data
            if url.startswith("data:image"):
                # Data URI format: data:image/png;base64,XXXXX
                if "base64," in url:
                    base64_data = url.split("base64,", 1)[1]
                    print(f"Base64 data length: {len(base64_data)}")

                    try:
                        # Decode and save
                        image_bytes = base64.b64decode(base64_data)
                        base_path = OUTPUT_DIR / "kk6_cover_1344x768.png"

                        with open(base_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        print(f"\n[SUCCESS] Image saved to: {base_path}")

                        # Verify
                        img = Image.open(base_path)
                        print(f"[SUCCESS] Image size: {img.size}, format: {img.format}")

                        # POST-PROCESSING: Upscale and Crop
                        print("\n" + "="*60)
                        print("POST-PROCESSING: Upscale and Crop")
                        print("="*60 + "\n")

                        # Upscale to 1920x1080 (maintains 16:9)
                        img_upscaled = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                        print(f"Upscaled to: {img_upscaled.size}")

                        # Crop to 1920x1005 for Facebook
                        top_margin = (1080 - 1005) // 2  # 37px top, 38px bottom
                        img_final = img_upscaled.crop((0, top_margin, 1920, 1005 + top_margin))
                        print(f"Cropped to: {img_final.size}")

                        # Save final image
                        final_path = OUTPUT_DIR / "kk6_event_cover_1920x1005.png"
                        img_final.save(final_path, "PNG", quality=95)

                        # Check file size
                        file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
                        print(f"Final file size: {file_size_mb:.2f} MB")

                        if file_size_mb <= 8:
                            print("[SUCCESS] File size within Facebook 8MB limit")
                        else:
                            print("[WARNING] File size exceeds 8MB Facebook limit")

                        print(f"\n[SUCCESS] Final Facebook cover image: {final_path}")

                        print("\n" + "="*60)
                        print("WORKFLOW COMPLETE - IMAGE GENERATION SUCCESS")
                        print("="*60)
                        print(f"\nBase image (16:9, 1344x768): {base_path}")
                        print(f"Final image (Facebook, 1920x1005): {final_path}")
                        print(f"\nReady to upload to Facebook Event page!")

                    except Exception as e:
                        print(f"[ERROR] Failed to process image: {e}")
                        import traceback
                        traceback.print_exc()
                        exit(1)
            else:
                print(f"[ERROR] URL is not a data URI: {url[:200]}")
                exit(1)
