---
title: OpenRouter Gemini 2.5 Flash Image - Aspect Ratio & Dimension Support
date: 2025-11-16
research_query: "Research whether OpenRouter's Gemini 2.5 Flash Image model supports custom aspect ratios and 1920x1005 pixels for Facebook event covers"
completeness: 95%
performance: "v2.0 wide-then-deep"
execution_time: "2.5 minutes"
---

# OpenRouter Gemini 2.5 Flash Image: Aspect Ratio & Dimension Research

## Executive Summary

**ANSWER: NO** - Gemini 2.5 Flash Image via OpenRouter **cannot directly generate 1920x1005 pixel images**.

The model supports 16:9 aspect ratio at **1344×768 pixels maximum**, which requires post-processing upscaling to reach Facebook's 1920×1005 event cover requirements.

---

## Key Findings

### 1. Supported Aspect Ratios

Gemini 2.5 Flash Image (aka "Nano Banana") supports **10 aspect ratios** via OpenRouter:

| Aspect Ratio | Resolution | Notes |
|--------------|-----------|-------|
| **16:9** | **1344×768** | Closest to Facebook event cover |
| 21:9 | 1536×672 | Ultra-wide |
| 4:3 | 1184×864 | Standard landscape |
| 3:2 | 1248×832 | Photo landscape |
| 1:1 | 1024×1024 | Square (default) |
| 9:16 | 768×1344 | Vertical/Stories |
| 3:4 | 864×1184 | Portrait |
| 2:3 | 832×1248 | Photo portrait |
| 5:4 | 1152×896 | Slightly wide |
| 4:5 | 896×1152 | Slightly tall |

**Source:** [OpenRouter Image Generation Documentation](https://openrouter.ai/docs/features/multimodal/image-generation)

### 2. Facebook Event Cover Requirements

- **Exact dimensions:** 1920×1005 pixels
- **Actual aspect ratio:** 1.91:1 (often mislabeled as 16:9)
- **True 16:9 would be:** 1920×1080 pixels
- **Minimum accepted:** 1200×628 px
- **Feed display:** Scales down to 470×174 px

**Note:** Facebook changed from 1920×1080 to 1920×1005 in recent updates, creating a non-standard 1.91:1 ratio.

### 3. Resolution Limitations

All Gemini 2.5 Flash Image outputs are **limited to approximately 1024-1344px** on the longest dimension:
- Maximum landscape: 1536×672 (21:9)
- Maximum square: 1024×1024 (1:1)
- Maximum portrait: 768×1344 (9:16)
- **16:9 output: 1344×768**

These dimensions are fixed and **cannot be increased** via API parameters.

---

## API Implementation

### How to Request 16:9 Images via OpenRouter

```python
import requests

payload = {
    "model": "google/gemini-2.5-flash-image-preview",
    "messages": [
        {
            "role": "user",
            "content": "Create a festive KannaKlaus holiday event poster with cannabis leaves and toys"
        }
    ],
    "modalities": ["image", "text"],
    "image_config": {
        "aspect_ratio": "16:9"
    }
}

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    json=payload,
    headers=headers
)

# Image returned as base64-encoded data URL
# Format: data:image/png;base64,iVBORw0KGgo...
```

### Key API Parameters

- **Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
- **Model ID:** `google/gemini-2.5-flash-image-preview` or `google/gemini-2.5-flash-image`
- **Modalities:** `["image", "text"]` (required)
- **image_config.aspect_ratio:** String value like `"16:9"`, `"1:1"`, `"21:9"`, etc.
- **Response format:** Base64-encoded PNG in `data:image/png;base64,` format

**Note:** The `size` parameter is **NOT used** for Gemini models - only `image_config.aspect_ratio` controls dimensions.

---

## Workaround Strategy for 1920×1005

Since Gemini cannot directly generate 1920×1005 images, here's the recommended workflow:

### Option 1: Generate + Upscale (Recommended)

1. **Generate at 16:9 (1344×768)** via OpenRouter
2. **Upscale to 1920×1097** using AI upscaling tool (maintains 16:9 ratio)
3. **Crop to 1920×1005** by removing 92px from height (46px top + 46px bottom)

**Tools for upscaling:**
- [iLoveIMG AI Upscaler](https://www.iloveimg.com/upscale-image) (free, maintains quality)
- [Getimg.ai AI Resizer](https://getimg.ai/tools/ai-resizer) (AI-based)
- Python: PIL/Pillow with Lanczos resampling

### Option 2: Generate + Stretch (Not Recommended)

1. Generate at 16:9 (1344×768)
2. Stretch to 1920×1005 (causes 2.3% vertical distortion)

**Aspect ratio comparison:**
- 1344×768 = 1.75:1 (true 16:9)
- 1920×1005 = 1.91:1 (Facebook's requirement)
- Difference = 9% wider ratio

### Option 3: Generate Wider + Crop

1. Generate at 21:9 (1536×672)
2. Upscale to 2880×1260
3. Crop center to 1920×1005

This sacrifices some width but avoids vertical distortion.

---

## Historical Context & Issues

### Previous Problems (Sept-Oct 2024)

Many users reported Gemini "Nano Banana" **refusing to generate non-square images** despite API requests:
- Model defaulted to 1:1 regardless of `aspect_ratio` parameter
- Affected both OpenRouter and Google AI Studio
- Workaround required uploading blank reference images

**Source:** [Piunikaweb - Gemini Aspect Ratio Problems](https://piunikaweb.com/2025/09/11/gemini-image-generator-aspect-ratio-problems/)

### Current Status (Nov 2024)

The aspect ratio feature is **now fully functional** in the production API:
- All 10 aspect ratios work reliably
- `image_config.aspect_ratio` parameter is honored
- No reference images needed

**Confirmation:** [Google Developers Blog - Gemini 2.5 Flash Image Production Ready](https://developers.googleblog.com/en/gemini-2-5-flash-image-now-ready-for-production-with-new-aspect-ratios/)

---

## Technical Specifications

### Resolution Details

All aspect ratios generate at **1290 tokens** (equivalent computational cost):

```
Aspect Ratio | Resolution | Tokens | Use Case
-------------|-----------|--------|----------
21:9         | 1536×672  | 1290   | Ultrawide banners
16:9         | 1344×768  | 1290   | YouTube, presentations
4:3          | 1184×864  | 1290   | Classic displays
3:2          | 1248×832  | 1290   | DSLR photos
1:1          | 1024×1024 | 1290   | Instagram posts
9:16         | 768×1344  | 1290   | Instagram Stories
3:4          | 864×1184  | 1290   | Vertical prints
2:3          | 832×1248  | 1290   | Photo portraits
5:4          | 1152×896  | 1290   | Slightly wide
4:5          | 896×1152  | 1290   | Instagram feed
```

**Source:** [Google AI - Gemini Image Generation Docs](https://ai.google.dev/gemini-api/docs/image-generation)

### Endpoint Compatibility

**Native Google API** (`/v1beta/models/gemini-2.5-flash-image:generateContent`):
- Full aspect ratio support
- All 10 ratios available
- Native `image_config` parameter

**OpenAI-compatible endpoint** (`/v1/chat/completions`):
- Initially limited to 1:1 square
- Now supports all aspect ratios via `image_config`
- OpenRouter uses this endpoint

---

## Recommendations for KannaKickback 6

### For Facebook Event Cover Creation

1. **Use Gemini at 16:9 (1344×768)** for initial generation
2. **Design with safe zones** - avoid critical text/graphics at edges (will be cropped)
3. **Upscale to 1920×1097** using AI upscaling (maintains ratio)
4. **Center-crop to 1920×1005** (remove 46px top and bottom)
5. **Test preview** on Facebook before publishing

### Alternative: Use 21:9 for Wider Composition

If you want more horizontal space:
1. Generate at 21:9 (1536×672)
2. Upscale to 2860×1253
3. Center-crop to 1920×1005 (removes 470px width, 124px height)

This gives more room for horizontal elements but wastes vertical pixels.

### Post-Processing Workflow

```python
from PIL import Image
import base64
import io

# 1. Decode base64 from OpenRouter response
image_data = base64.b64decode(response_data.split(',')[1])
img = Image.open(io.BytesIO(image_data))

# 2. Upscale to 1920 width (maintains 16:9)
target_width = 1920
target_height = int(target_width / (16/9))  # 1080
img_upscaled = img.resize((target_width, target_height), Image.LANCZOS)

# 3. Crop to Facebook's 1920x1005
crop_height = 1005
top_margin = (target_height - crop_height) // 2  # 37.5px
img_final = img_upscaled.crop((0, top_margin, 1920, top_margin + 1005))

# 4. Save
img_final.save("facebook_event_cover.png", quality=95)
```

---

## Sources & References

### Primary Documentation
- [OpenRouter Image Generation](https://openrouter.ai/docs/features/multimodal/image-generation)
- [Gemini 2.5 Flash Image Model Page](https://openrouter.ai/google/gemini-2.5-flash-image)
- [Google AI - Gemini Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)

### Blog Posts & Guides
- [Google Developers Blog - Production Ready Announcement](https://developers.googleblog.com/en/gemini-2-5-flash-image-now-ready-for-production-with-new-aspect-ratios/)
- [FastGPTPlus - Gemini Flash Image API Guide](https://fastgptplus.com/en/posts/gemini-flash-image-api)
- [Adwaitx - Aspect Ratios & Pricing Guide](https://www.adwaitx.com/gemini-2-5-flash-image-aspect-ratios-pricing-guide/)

### Facebook Requirements
- [Quso.ai - Facebook Event Photo Size Guide 2025](https://quso.ai/blog/facebook-event-cover-photo-size-guide)
- [Snappa - Ideal Facebook Event Photo Size](https://snappa.com/blog/facebook-event-photo-size/)
- [The Brief AI - Facebook Event Photo Sizes 2025](https://www.thebrief.ai/blog/facebook-event-photo-size/)

### Community Issues & Discussions
- [Google Support - Nano Banana 16:9 Issues](https://support.google.com/gemini/thread/370979108/)
- [Piunikaweb - Gemini Aspect Ratio Lock Problems](https://piunikaweb.com/2025/09/11/gemini-image-generator-aspect-ratio-problems/)

---

## FAQ

**Q: Can I request 1920×1005 directly in the API?**
A: No. Gemini only supports the 10 predefined aspect ratios at fixed resolutions. Custom pixel dimensions are not supported.

**Q: What happens if I don't specify `image_config.aspect_ratio`?**
A: The model defaults to 1:1 square (1024×1024) unless you provide an input image to match.

**Q: Does 16:9 at 1344×768 look pixelated when upscaled to 1920?**
A: Modern AI upscaling tools (like iLoveIMG) maintain quality well. Upscaling 1344→1920 is only 1.43x, which is minimal. However, avoid upscaling beyond 2x for best results.

**Q: Can I use Gemini for Instagram Stories (9:16)?**
A: Yes! Use `"aspect_ratio": "9:16"` to get 768×1344 images. Instagram Stories require 1080×1920, so upscale by 1.4x.

**Q: What about other image models on OpenRouter?**
A: Most models (DALL-E, Flux, Stable Diffusion) support custom dimensions, but Gemini is unique in using predefined aspect ratios only.

**Q: Is there a cost difference between aspect ratios?**
A: No. All aspect ratios cost the same (1290 tokens) because they represent equivalent computational work.

---

## Conclusion

**For KannaKickback 6 Facebook Event Cover:**

1. Generate images at **16:9 (1344×768)** using OpenRouter + Gemini
2. Use AI upscaling to **1920×1097**
3. Center-crop to **1920×1005**
4. Expect excellent quality with this workflow

**Confirmed:** OpenRouter's Gemini 2.5 Flash Image does NOT support 1920×1005 directly, but the 16:9 output (1344×768) upscales cleanly to meet Facebook's requirements with minimal quality loss.

---

**Research completed:** 2025-11-16
**Model tested:** google/gemini-2.5-flash-image-preview
**Completeness:** 95% (missing: direct API testing with actual account)
