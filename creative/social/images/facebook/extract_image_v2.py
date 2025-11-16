#!/usr/bin/env python3
"""
Extract image from API response debug file
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

print(f"Response keys: {data.keys()}")

if "choices" in data and len(data["choices"]) > 0:
    choice = data["choices"][0]
    message = choice.get("message", {})

    print(f"Message keys: {message.keys()}")

    # Check the "images" field
    if "images" in message:
        images = message["images"]
        print(f"\nFound 'images' field!")
        print(f"Type: {type(images)}")

        if isinstance(images, list) and len(images) > 0:
            print(f"Number of images: {len(images)}")

            for i, img_data in enumerate(images):
                print(f"\nImage {i}:")
                print(f"  Type: {type(img_data)}")

                if isinstance(img_data, dict):
                    print(f"  Keys: {img_data.keys()}")

                    # Look for various possible fields
                    base64_data = None

                    if "data" in img_data:
                        base64_data = img_data["data"]
                        print(f"  Found 'data' field (length: {len(base64_data)})")
                    elif "url" in img_data:
                        url = img_data["url"]
                        if url.startswith("data:image"):
                            print(f"  Found data URL")
                            base64_data = url.split("base64,")[1] if "base64," in url else None
                    elif "inline_data" in img_data:
                        base64_data = img_data["inline_data"].get("data")
                        print(f"  Found 'inline_data' field")

                    if base64_data:
                        print(f"  Base64 data length: {len(base64_data)}")

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

                            # Success!
                            break

                        except Exception as e:
                            print(f"[ERROR] Failed to save/process image: {e}")
                            import traceback
                            traceback.print_exc()
                elif isinstance(img_data, str):
                    # Direct base64 string
                    print(f"  Image is direct string (length: {len(img_data)})")
                    base64_data = img_data

                    try:
                        image_bytes = base64.b64decode(base64_data)
                        base_path = OUTPUT_DIR / "kk6_cover_1344x768.png"

                        with open(base_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        print(f"\n[SUCCESS] Image saved to: {base_path}")

                        # Verify
                        img = Image.open(base_path)
                        print(f"[SUCCESS] Image size: {img.size}, format: {img.format}")

                        # Upscale and crop (same as above)
                        print("\n" + "="*60)
                        print("POST-PROCESSING: Upscale and Crop")
                        print("="*60 + "\n")

                        img_upscaled = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                        print(f"Upscaled to: {img_upscaled.size}")

                        top_margin = (1080 - 1005) // 2
                        img_final = img_upscaled.crop((0, top_margin, 1920, 1005 + top_margin))
                        print(f"Cropped to: {img_final.size}")

                        final_path = OUTPUT_DIR / "kk6_event_cover_1920x1005.png"
                        img_final.save(final_path, "PNG", quality=95)

                        file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
                        print(f"Final file size: {file_size_mb:.2f} MB")

                        if file_size_mb <= 8:
                            print("[SUCCESS] File size within Facebook limits")

                        print(f"\n[SUCCESS] Final image: {final_path}")
                        print("\n" + "="*60)
                        print("WORKFLOW COMPLETE")
                        print("="*60)

                        break

                    except Exception as e:
                        print(f"[ERROR] Failed: {e}")
                        import traceback
                        traceback.print_exc()

        elif isinstance(images, str):
            # Single image as string
            print(f"Images is a single string (length: {len(images)})")
            # Handle same as above...

    else:
        print("\n[ERROR] No 'images' field found in message")
        print(f"Available fields: {message.keys()}")
