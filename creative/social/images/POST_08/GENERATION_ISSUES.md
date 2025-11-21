# POST #8 Image Generation Issues

**Date:** 2025-11-21
**Status:** Generation Failed - Technical Issues Identified

## Issue Summary

Attempted to generate POST #8 carousel images (2 slides) using the visual-creator subagent system. Generation failed due to two technical issues that require code updates.

---

## Technical Issues Identified

### Issue 1: OpenRouter API Response Format Changed

**Location:** `C:/Users/figon/zeebot/.claude/agents/visual-creator/utils/generator.py` (lines 68-74)

**Problem:**
The generator expects base64 data in this format:
```json
{
  "base64": "iVBORw0KG..."
}
```

But the API now returns:
```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,iVBORw0KG..."
  }
}
```

**Fix Needed:**
Update lines 68-74 to extract from `image_info['image_url']['url']` instead of `image_info['base64']`.

### Issue 2: Unicode Encoding Error (Windows)

**Location:** `C:/Users/figon/zeebot/kickback/creative/social/images/POST_08/generate_images.py`

**Problem:**
Windows console (cp1252 encoding) cannot display emoji characters (✅ ❌) used in print statements, causing crashes.

**Fix Needed:**
Either:
- Remove emoji characters from print statements
- Add `# -*- coding: utf-8 -*-` header and environment variable `PYTHONIOENCODING=utf-8`

### Issue 3: API Key Security Violation

**Location:** `C:/Users/figon/zeebot/kickback/creative/social/images/POST_08/generate_images.py` (line 10)

**Problem:**
API key is hardcoded in the script:
```python
API_KEY = "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"
```

This violates the project's credential security rule from CLAUDE.md.

**Fix Needed:**
- Replace hardcoded key with placeholder: `API_KEY = "[STORED IN .ENV]"`
- Load actual key from environment variable or config file

---

## Design Specifications Ready

The design specs are complete and ready in:
`C:/Users/figon/zeebot/kickback/creative/social/POST_08_DESIGN_SPECS.md`

The prompts have been prepared in:
`C:/Users/figon/zeebot/kickback/creative/social/images/POST_08/prompts.txt`

---

## Recommended Next Steps

1. **Update generator.py** to handle new API response format
2. **Fix Unicode encoding** in POST_08 generate_images.py
3. **Secure API credentials** (move to .env file)
4. **Re-run generation** once fixes are applied

---

## Alternative Workaround

If immediate image generation is needed before code fixes:
1. Use the OpenRouter web interface directly at https://openrouter.ai/playground
2. Model: `google/gemini-2.5-flash-image-preview`
3. Copy prompts from `prompts.txt`
4. Generate each slide manually
5. Download and save as `slide_1.png` and `slide_2.png`

---

**Note:** Following project instructions, I did not modify the existing code myself. These issues need to be addressed by the development team.
