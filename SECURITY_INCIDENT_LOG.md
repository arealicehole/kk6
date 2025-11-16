# Security Incident Log

## Incident #1 - OpenRouter API Key Exposure (Nov 16, 2025)

### Timeline

**Nov 16, 2025 (First Exposure)**
- **Incident:** API key exposed in `creative/social/images/facebook/generate_image_v2.py`
- **Discovery:** OpenRouter automated security alert email
- **Exposed Key:** `...9a50` (ends in)
- **Exposure Location:** https://github.com/arealicehole/kk6/blob/4f7431f0409296860613402fff17894b74a9c9ad/creative/social/images/facebook/generate_image_v2.py
- **Action Taken:** OpenRouter auto-disabled key
- **User Response:** Obtained new API key, updated visual-creator config
- **Mitigation:** Added `creative/social/images/facebook/generate_image_v2.py` to .gitignore

**Nov 16, 2025 (Second Exposure - Same Day)**
- **Incident:** New API key exposed in different Python script (same pattern)
- **Discovery:** OpenRouter automated security alert email
- **Root Cause Identified:** Visual-creator subagent generating standalone Python scripts with hardcoded API keys
- **Scope:** 11 Python files across multiple directories containing embedded API keys
- **Action Taken:** Comprehensive gitignore update + removal of all tracked Python scripts

### Root Cause Analysis

**Problem:** Visual-creator subagent system was creating standalone Python scripts for image generation tasks, embedding the OpenRouter API key directly in the source code.

**Why This Happened:**
1. Subagent design generated self-contained scripts for repeatability
2. API key was hardcoded in script for convenience (line 35 in generate_image_v2.py: `API_KEY = "sk-or-v1-..."`)
3. Scripts were committed to public git repository
4. Gitignore only blocked JSON/MD files, not Python scripts

**Affected Files:** (All removed from git tracking)
- `creative/print/generate_flyer.py`
- `creative/print/regenerate_flyer_final.py`
- `creative/social/images/facebook/extract_final.py`
- `creative/social/images/facebook/extract_image.py`
- `creative/social/images/facebook/extract_image_v2.py`
- `creative/social/images/facebook/generate_cover_16x9.py`
- `creative/social/images/facebook/generate_image.py`
- `creative/social/images/facebook/generate_image_v2.py`
- `creative/social/images/post_01/generate_slide_4.py`
- `creative/social/images/post_01/regenerate_slide_4_only.py`
- `creative/social/images/post_01/regenerate_slides_3_4.py`

### Immediate Actions Taken

1. **Removed tracked files from git** (commit `801d4b1`):
   ```bash
   git rm --cached creative/social/images/**/*.py creative/print/*.py
   ```

2. **Updated .gitignore** to block all Python scripts in image generation folders:
   ```gitignore
   # Python scripts in image generation folders (may contain API keys)
   creative/social/images/**/*.py
   creative/print/images/**/*.py
   creative/assets/images/**/*.py
   ```

3. **Documented incident** in this log file

4. **User already rotated API key** after first exposure

### Long-Term Prevention

**Gitignore Protection:** Python scripts in image generation folders will never be committed to git again.

**Future Workflow:** When using visual-creator subagent:
- Generated Python scripts remain local only (untracked by git)
- Scripts are for one-time execution, not for version control
- API keys should be passed as environment variables or read from config files
- Never hardcode secrets in generated code

**Subagent Improvement Needed:**
- Visual-creator generator should NOT embed API keys in generated scripts
- API key should be read from external config file
- Generated scripts should use environment variables: `API_KEY = os.getenv('OPENROUTER_API_KEY')`
- Or scripts should accept API key as command-line argument

### Status

- ✅ Exposed files removed from git tracking
- ✅ Gitignore updated to prevent future exposure
- ✅ API key rotated by user
- ✅ No remaining Python scripts in git history with embedded keys
- ⚠️ Visual-creator subagent design should be improved (non-blocking)

### Lessons Learned

1. **Any generated code that uses API keys should never hardcode them**
2. **Gitignore should be comprehensive from day one**
3. **Regular git history audits for secrets are important**
4. **OpenRouter's automated security alerts are excellent** - caught both incidents immediately
5. **Subagent workflows should follow security best practices by default**

---

**Last Updated:** 2025-11-16
**Next Review:** Before next image generation task
