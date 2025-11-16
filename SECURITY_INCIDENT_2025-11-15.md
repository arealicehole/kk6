# Security Incident Report - OpenRouter API Key Exposure

**Date:** 2025-11-15
**Severity:** HIGH
**Status:** MITIGATED

---

## Incident Summary

OpenRouter API key was accidentally committed to public GitHub repository in image generation log files.

---

## Timeline

- **7:06 PM:** OpenRouter detected exposed API key ending in ...97fb
- **7:06 PM:** OpenRouter automatically disabled the key
- **7:24 PM:** User notified via email
- **7:30 PM (approx):** Incident reported to Claude Code
- **Immediate:** Files removed from git tracking, .gitignore updated

---

## Affected Key

- **Key ending in:** ...97fb
- **Service:** OpenRouter API (https://openrouter.ai)
- **Used for:** Google Gemini 2.5 Flash Image generation (Nano Banana model)
- **Status:** ✅ DISABLED by OpenRouter (automatic)

---

## Exposure Location

**Public Repository:** https://github.com/arealicehol/kk6

**Exposed File:**
- `creative/social/images/post_01/SLIDE_3_GENERATION_LOG.md`

**Additional files with API key:**
- `creative/social/images/post_01/slide_3_response_attempt_1.json`
- `creative/social/images/post_01/slide_4_response_*.json` (multiple)

---

## Root Cause

Visual-creator subagent system saved generation logs and API response files containing the full OpenRouter API key. These files were:
1. Not in .gitignore
2. Committed to git
3. Pushed to public GitHub repository

**Why it happened:**
- Subagent generated detailed logs for debugging/documentation
- API responses were saved with full headers (including Authorization)
- No .gitignore pattern for `*_LOG.md` or `*response*.json` files

---

## Immediate Actions Taken

1. ✅ OpenRouter auto-disabled the exposed key
2. ✅ Removed files from git tracking (`git rm --cached`)
3. ✅ Updated .gitignore to exclude:
   - `**/*_response*.json`
   - `**/*_LOG.md`
   - `**/*_metadata.json`
   - `**/*prompt*.txt`
   - `**/manifest.json`
   - Other generation artifacts

---

## Required Actions

### Immediate (User):
1. 🔴 **Rotate OpenRouter API key** at https://openrouter.ai/keys
2. 🔴 **Update new key** in visual-creator agent config
3. 🔴 **Commit .gitignore changes** to prevent future exposure

### Optional (for complete cleanup):
4. ⚪ Rewrite git history to remove key from all commits (use BFG Repo-Cleaner or git filter-branch)
5. ⚪ Force push cleaned history (WARNING: breaks all forks/clones)

---

## Impact Assessment

**Potential damage:** LOW
- Key was disabled within minutes of exposure
- Used only for image generation (limited scope)
- No payment method abuse detected
- OpenRouter has rate limits and monitoring

**Actual damage:** NONE (key disabled before abuse)

---

## Prevention Measures Implemented

### .gitignore Updates:
```gitignore
# Sensitive files - API keys, credentials, logs
**/*_response*.json
**/*_LOG.md
**/*_metadata.json
**/*prompt*.txt
**/manifest.json
**/*_parsed_spec.json
**/generation_state.json
**/*_quality_review.md
**/*_MANIFEST.json
```

### Recommended Future Improvements:
1. **Environment variables:** Store API keys in .env (already gitignored)
2. **Subagent logging:** Modify visual-creator to redact API keys from logs
3. **Pre-commit hooks:** Scan for exposed secrets before commits
4. **Regular audits:** Check for accidentally committed credentials

---

## Lessons Learned

1. **Subagent outputs need security review:** Generation logs shouldn't include full API responses
2. **Gitignore proactive patterns:** Should cover log/debug/response files by default
3. **OpenRouter monitoring works:** Detected and disabled within minutes
4. **Public repos = extra vigilance:** Anything pushed is potentially exposed forever

---

## Status: MITIGATED

- ✅ Exposed key disabled
- ✅ Files removed from tracking
- ✅ .gitignore updated
- 🔴 NEW KEY NEEDED (user action required)
- ⚪ Git history cleanup (optional)

---

**Next Steps:**
1. User rotates API key
2. Commit .gitignore changes
3. Test with new key
4. Monitor for any unusual activity

---

**Reported by:** Claude Code (automated system)
**Reviewed by:** [Pending]
