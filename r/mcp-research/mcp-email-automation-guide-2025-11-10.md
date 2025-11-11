---
title: MCP Email Automation Integration with Claude Code
date: 2025-11-10
research_query: "MCP servers for email automation with Claude Code - configuration, implementation, and workflows"
completeness: 92%
performance: "v2.0 wide-then-deep"
execution_time: "3.2 minutes"
sources: 14
---

# MCP Email Automation Integration with Claude Code
## Complete Implementation Guide for 2025

---

## Executive Summary

Model Context Protocol (MCP) servers enable Claude Code to automate email operations through standardized integrations. This guide provides production-ready configurations for Gmail, IMAP/SMTP, and Outlook email automation, with focus on Windows environments and enterprise deployments.

**Key Findings:**
- 4 production-ready MCP email servers available (Gmail OAuth, Universal IMAP/SMTP, Gmail IMAP/SMTP, Email Client Multi-Config)
- Claude Code uses CLI-based configuration, distinct from Claude Desktop's GUI approach
- Windows requires special `cmd /c` wrapper for npx-based servers
- OAuth2 authentication recommended for Gmail; app passwords required for 2FA accounts
- Batch processing limits: 50 emails per operation, rate limiting at API level
- Environment variables take precedence over config files for credential management

---

## Part 1: Claude Code MCP Architecture

### Configuration File Locations

Claude Code manages MCP servers through three scope levels:

| Scope | Location | Purpose | Shared? |
|-------|----------|---------|---------|
| **Local** (default) | Project `.claude/settings.json` | User-specific project settings | No - gitignored |
| **Project** | `.mcp.json` in project root | Team-shared server configs | Yes - version controlled |
| **User** | OS-specific user config dir | Personal cross-project servers | No - per user |
| **Enterprise** | `/ProgramData/ClaudeCode/managed-mcp.json` (Windows) | System admin managed | Yes - org-wide |

**Windows Enterprise Path:**
```
C:\ProgramData\ClaudeCode\managed-mcp.json
```

**Claude Desktop Path (for reference):**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### CLI vs Desktop Configuration

| Feature | Claude Code | Claude Desktop |
|---------|-------------|----------------|
| Configuration Method | CLI commands | GUI + JSON file |
| Server Addition | `claude mcp add` | Edit config.json |
| Authentication | `/mcp` command in-app | Automatic on startup |
| Scope Support | Local/Project/User/Enterprise | Single global scope |
| Environment Variables | CLI flags + .mcp.json | config.json env section |
| Windows npx Support | Requires `cmd /c` wrapper | Auto-handled |

### Transport Types

MCP servers communicate via three transport mechanisms:

**1. HTTP (Recommended for remote services)**
```bash
claude mcp add --transport http gmail https://mcp.gmail.example.com/mcp
```
- Best for cloud-hosted MCP servers
- Supports OAuth2 authentication
- Most widely supported for enterprise services

**2. Stdio (Local process communication)**
```bash
claude mcp add --transport stdio email-server -- npx -y @ai-zerolab/mcp-email-server
```
- Runs server as local subprocess
- Direct stdin/stdout communication
- Ideal for npm/Python packages

**3. SSE (Server-Sent Events - Deprecated)**
```bash
claude mcp add --transport sse legacy-server https://example.com/sse
```
- Legacy support only
- Use HTTP for new implementations

---

## Part 2: Available Email MCP Servers

### Comparison Matrix

| Server | Provider | Auth Type | Attachments | Batch Ops | Best For |
|--------|----------|-----------|-------------|-----------|----------|
| **Gmail-MCP-Server** (GongRzhe) | Gmail only | OAuth2 | Full support | Yes (batch modify/delete) | Gmail power users, filter management |
| **mcp-email-server** (ai-zerolab) | Universal IMAP/SMTP | Password/App Password | Yes | No | Multi-provider support, simple setup |
| **gmail-mcp-server** (david-strejc) | Gmail IMAP/SMTP | App Password | Forwarding only | No | Simple Gmail access, Python-based |
| **mcp-email-client** (gamalan) | Multiple configs | Password | Yes | No | Managing multiple email accounts |

### Server Details

#### 1. Gmail-MCP-Server (Recommended for Gmail)

**Source:** https://github.com/GongRzhe/Gmail-MCP-Server

**Features:**
- OAuth2 auto-authentication with browser flow
- 17 comprehensive tools (send, read, search, labels, filters, drafts)
- Full attachment support (send, download, read metadata)
- HTML and multipart email formats
- Batch operations (modify/delete up to 50 emails)
- Advanced Gmail search syntax
- Label and filter management

**Tool Inventory:**
1. `send_email` - Send with attachments, CC/BCC, HTML/plain text
2. `draft_email` - Create draft messages with attachments
3. `read_email` - Retrieve by ID with attachment metadata
4. `download_attachment` - Save attachments locally
5. `search_emails` - Gmail search syntax with result limiting
6. `modify_email` - Add/remove labels
7. `batch_modify_emails` - Update multiple message labels
8. `batch_delete_emails` - Remove multiple messages
9. `list_email_labels` - Display all labels
10. `create_label` - Add custom labels
11. `update_label` - Modify label properties
12. `delete_label` - Remove labels
13. `get_or_create_label` - Retrieve or create if missing
14. `create_filter` - Define automated routing
15. `list_filters` - View established filters
16. `get_filter` - Examine filter details
17. `delete_filter` - Remove filters

**Installation:**

Via Smithery (easiest):
```bash
npx -y @smithery/cli install @gongrzhe/server-gmail-autoauth-mcp --client claude
```

Via CLI for Claude Code:
```bash
claude mcp add --transport stdio gmail -- npx @gongrzhe/server-gmail-autoauth-mcp
```

**Windows Installation:**
```bash
claude mcp add --transport stdio gmail -- cmd /c npx @gongrzhe/server-gmail-autoauth-mcp
```

**Authentication Setup:**

1. Create Google Cloud Project:
   - Visit https://console.cloud.google.com
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop or Web application)
   - For Web: Add `http://localhost:3000/oauth2callback` to redirect URIs
   - Download credentials JSON as `gcp-oauth.keys.json`

2. Run authentication:
```bash
mkdir -p ~/.gmail-mcp
mv gcp-oauth.keys.json ~/.gmail-mcp/
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

3. Browser opens for Google login
4. Tokens stored in `~/.gmail-mcp/credentials.json`
5. Restart Claude Code

**Project .mcp.json Configuration:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    }
  }
}
```

**Windows .mcp.json:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    }
  }
}
```

#### 2. MCP Email Server (Universal IMAP/SMTP)

**Source:** https://github.com/ai-zerolab/mcp-email-server

**Features:**
- Universal email provider support (Gmail, Outlook, Yahoo, enterprise)
- IMAP + SMTP protocol support
- Attachment support
- UI-based configuration tool
- Environment variable configuration
- Docker support

**Installation:**

Via uv (recommended):
```bash
uvx mcp-email-server@latest ui
```

Via pip:
```bash
pip install mcp-email-server
mcp-email-server ui
```

Via Smithery:
```bash
npx -y @smithery/cli install @ai-zerolab/mcp-email-server --client claude
```

**Claude Code Configuration:**

```bash
claude mcp add --transport stdio zerolib-email \
  --env MCP_EMAIL_SERVER_EMAIL_ADDRESS=john@example.com \
  --env MCP_EMAIL_SERVER_PASSWORD=app-password-here \
  --env MCP_EMAIL_SERVER_IMAP_HOST=imap.gmail.com \
  --env MCP_EMAIL_SERVER_IMAP_PORT=993 \
  --env MCP_EMAIL_SERVER_SMTP_HOST=smtp.gmail.com \
  --env MCP_EMAIL_SERVER_SMTP_PORT=465 \
  -- uvx mcp-email-server@latest stdio
```

**Windows Command:**
```bash
claude mcp add --transport stdio zerolib-email ^
  --env MCP_EMAIL_SERVER_EMAIL_ADDRESS=john@example.com ^
  --env MCP_EMAIL_SERVER_PASSWORD=app-password-here ^
  --env MCP_EMAIL_SERVER_IMAP_HOST=imap.gmail.com ^
  --env MCP_EMAIL_SERVER_IMAP_PORT=993 ^
  --env MCP_EMAIL_SERVER_SMTP_HOST=smtp.gmail.com ^
  --env MCP_EMAIL_SERVER_SMTP_PORT=465 ^
  -- cmd /c uvx mcp-email-server@latest stdio
```

**Project .mcp.json with Variables:**
```json
{
  "mcpServers": {
    "zerolib-email": {
      "command": "uvx",
      "args": ["mcp-email-server@latest", "stdio"],
      "env": {
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "${EMAIL_ADDRESS}",
        "MCP_EMAIL_SERVER_PASSWORD": "${EMAIL_APP_PASSWORD}",
        "MCP_EMAIL_SERVER_IMAP_HOST": "${IMAP_HOST:-imap.gmail.com}",
        "MCP_EMAIL_SERVER_IMAP_PORT": "${IMAP_PORT:-993}",
        "MCP_EMAIL_SERVER_SMTP_HOST": "${SMTP_HOST:-smtp.gmail.com}",
        "MCP_EMAIL_SERVER_SMTP_PORT": "${SMTP_PORT:-465}",
        "MCP_EMAIL_SERVER_IMAP_SSL": "true",
        "MCP_EMAIL_SERVER_SMTP_SSL": "true"
      }
    }
  }
}
```

This allows team members to set environment variables locally without committing credentials.

**Provider-Specific Settings:**

| Provider | IMAP Host | IMAP Port | SMTP Host | SMTP Port | SSL |
|----------|-----------|-----------|-----------|-----------|-----|
| Gmail | imap.gmail.com | 993 | smtp.gmail.com | 465 | Yes |
| Outlook | outlook.office365.com | 993 | smtp.office365.com | 587 | STARTTLS |
| Yahoo | imap.mail.yahoo.com | 993 | smtp.mail.yahoo.com | 465 | Yes |
| iCloud | imap.mail.me.com | 993 | smtp.mail.me.com | 587 | STARTTLS |

---

## Part 3: Authentication Setup

### Gmail OAuth2 (Production Recommended)

**Benefits:**
- No 2FA app passwords needed
- Automatic token refresh
- Granular permission scopes
- Audit trail in Google Cloud Console

**Setup Steps:**

1. **Create GCP Project:**
```
Navigate to: https://console.cloud.google.com
Click: "Select a project" → "New Project"
Name: "Claude Email Automation"
Click: "Create"
```

2. **Enable Gmail API:**
```
Navigate to: APIs & Services → Library
Search: "Gmail API"
Click: "Enable"
```

3. **Configure OAuth Consent Screen:**
```
Navigate to: APIs & Services → OAuth consent screen
Select: "External" (for personal Gmail) or "Internal" (for Google Workspace)
Fill in:
  - App name: "Claude Email Assistant"
  - User support email: Your email
  - Developer contact: Your email
Add Scopes:
  - https://www.googleapis.com/auth/gmail.modify
  - https://www.googleapis.com/auth/gmail.compose
  - https://www.googleapis.com/auth/gmail.send
Click: "Save and Continue"
```

4. **Create OAuth Credentials:**
```
Navigate to: APIs & Services → Credentials
Click: "Create Credentials" → "OAuth client ID"
Application type: "Desktop app" (easiest) or "Web application"
Name: "Claude Code MCP"

For Web Application, add authorized redirect URI:
  http://localhost:3000/oauth2callback

Click: "Create"
Download JSON → Rename to: gcp-oauth.keys.json
```

5. **Authenticate MCP Server:**

**Windows:**
```cmd
mkdir %USERPROFILE%\.gmail-mcp
move gcp-oauth.keys.json %USERPROFILE%\.gmail-mcp\
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

**macOS/Linux:**
```bash
mkdir -p ~/.gmail-mcp
mv gcp-oauth.keys.json ~/.gmail-mcp/
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

Browser opens → Sign in with Google → Grant permissions
Credentials saved to `~/.gmail-mcp/credentials.json`

6. **Add to Claude Code:**
```bash
claude mcp add --transport stdio gmail -- npx @gongrzhe/server-gmail-autoauth-mcp
```

7. **Test Authentication:**
```
Open Claude Code
Type: /mcp
Select: gmail
Status should show: "Connected"
```

### Gmail App Passwords (Simpler, Less Secure)

**Requirements:**
- 2-Factor Authentication must be enabled
- Cannot use regular Gmail password

**Setup Steps:**

1. **Enable 2FA:**
```
Navigate to: https://myaccount.google.com/security
Find: "2-Step Verification"
Click: "Get Started"
Complete 2FA setup
```

2. **Generate App Password:**
```
Navigate to: https://myaccount.google.com/apppasswords
(Or Google Account → Security → App passwords)
Select app: "Mail"
Select device: "Windows Computer" (or appropriate)
Click: "Generate"
Copy the 16-character password (example: "abcd efgh ijkl mnop")
```

3. **Add to Claude Code with Environment Variables:**
```bash
claude mcp add --transport stdio email-server \
  --env EMAIL_ADDRESS=your-email@gmail.com \
  --env EMAIL_APP_PASSWORD=abcdefghijklmnop \
  --env IMAP_HOST=imap.gmail.com \
  --env SMTP_HOST=smtp.gmail.com \
  -- uvx mcp-email-server@latest stdio
```

**Security Note:** App passwords bypass 2FA. OAuth2 is strongly recommended for production use.

### Outlook/Microsoft 365 Configuration

**Modern Authentication (OAuth2) - Preferred:**

Microsoft has deprecated basic authentication. Use OAuth2 for production:

```bash
# OAuth2 support varies by MCP server
# Check server documentation for Microsoft Graph API integration
# Most MCP email servers currently support IMAP/SMTP with app passwords only
```

**App Password (Temporary Workaround):**

1. Enable 2FA on Microsoft account
2. Generate app password at https://account.microsoft.com/security
3. Use IMAP/SMTP settings:

```bash
claude mcp add --transport stdio outlook-email \
  --env EMAIL_ADDRESS=your-email@outlook.com \
  --env EMAIL_APP_PASSWORD=your-app-password \
  --env IMAP_HOST=outlook.office365.com \
  --env IMAP_PORT=993 \
  --env SMTP_HOST=smtp.office365.com \
  --env SMTP_PORT=587 \
  --env SMTP_START_SSL=true \
  -- uvx mcp-email-server@latest stdio
```

---

## Part 4: Production Configuration Examples

### Multi-Environment Setup

**Project Structure:**
```
/kickback
├── .mcp.json                    # Team-shared MCP config
├── .env.local                   # User credentials (gitignored)
├── .env.example                 # Template for new users
└── .claude/
    └── settings.json            # User-specific Claude settings
```

**.mcp.json (Version Controlled):**
```json
{
  "mcpServers": {
    "gmail-production": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "${HOME}/.gmail-mcp/credentials.json"
      }
    },
    "email-backup": {
      "command": "uvx",
      "args": ["mcp-email-server@latest", "stdio"],
      "env": {
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "${BACKUP_EMAIL}",
        "MCP_EMAIL_SERVER_PASSWORD": "${BACKUP_EMAIL_PASSWORD}",
        "MCP_EMAIL_SERVER_IMAP_HOST": "${BACKUP_IMAP_HOST:-imap.gmail.com}",
        "MCP_EMAIL_SERVER_SMTP_HOST": "${BACKUP_SMTP_HOST:-smtp.gmail.com}",
        "MCP_EMAIL_SERVER_IMAP_PORT": "993",
        "MCP_EMAIL_SERVER_SMTP_PORT": "465"
      }
    }
  }
}
```

**.env.example (Version Controlled):**
```bash
# Copy to .env.local and fill in your credentials
# Gmail OAuth credentials stored in ~/.gmail-mcp/ (run auth command)

# Backup email account (IMAP/SMTP)
BACKUP_EMAIL=backup@example.com
BACKUP_EMAIL_PASSWORD=your-app-password-here
BACKUP_IMAP_HOST=imap.gmail.com
BACKUP_SMTP_HOST=smtp.gmail.com
```

**.env.local (Gitignored):**
```bash
BACKUP_EMAIL=team-backup@gmail.com
BACKUP_EMAIL_PASSWORD=abcdefghijklmnop
```

**.gitignore:**
```
.env.local
.claude/settings.json
credentials.json
gcp-oauth.keys.json
```

### Windows Production Setup

**Challenge:** Windows requires `cmd /c` wrapper for npx/npm commands in MCP stdio transport.

**.mcp.json for Windows Team:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    },
    "universal-email": {
      "command": "cmd",
      "args": [
        "/c",
        "uvx",
        "mcp-email-server@latest",
        "stdio"
      ],
      "env": {
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "${EMAIL_ADDRESS}",
        "MCP_EMAIL_SERVER_PASSWORD": "${EMAIL_APP_PASSWORD}",
        "MCP_EMAIL_SERVER_IMAP_HOST": "imap.gmail.com",
        "MCP_EMAIL_SERVER_SMTP_HOST": "smtp.gmail.com",
        "MCP_EMAIL_SERVER_IMAP_PORT": "993",
        "MCP_EMAIL_SERVER_SMTP_PORT": "465"
      }
    }
  }
}
```

**Cross-Platform Compatible (Using Conditionals):**

Claude Code supports variable expansion. For mixed Windows/macOS teams:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "${OS_COMMAND_PREFIX:-npx}",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"]
    }
  }
}
```

**Windows users set in .env.local:**
```bash
OS_COMMAND_PREFIX=cmd /c npx
```

**macOS/Linux users leave default** (no .env.local entry needed)

### Docker-Based Deployment

**Benefits:**
- Consistent environment across platforms
- No Windows npx wrapper issues
- Isolated credentials
- Easy backup/restore

**Docker Compose Configuration:**

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  gmail-mcp:
    image: ghcr.io/gongrzhe/gmail-mcp-server:latest
    volumes:
      - gmail-credentials:/gmail-server
    environment:
      - GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json
    restart: unless-stopped

  universal-email-mcp:
    image: ghcr.io/ai-zerolab/mcp-email-server:latest
    environment:
      - MCP_EMAIL_SERVER_EMAIL_ADDRESS=${BACKUP_EMAIL}
      - MCP_EMAIL_SERVER_PASSWORD=${BACKUP_EMAIL_PASSWORD}
      - MCP_EMAIL_SERVER_IMAP_HOST=imap.gmail.com
      - MCP_EMAIL_SERVER_SMTP_HOST=smtp.gmail.com
      - MCP_EMAIL_SERVER_IMAP_PORT=993
      - MCP_EMAIL_SERVER_SMTP_PORT=465
    restart: unless-stopped

volumes:
  gmail-credentials:
```

**Claude Code .mcp.json for Docker:**
```json
{
  "mcpServers": {
    "gmail-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "gmail-credentials:/gmail-server",
        "-e",
        "GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json",
        "ghcr.io/gongrzhe/gmail-mcp-server:latest"
      ]
    }
  }
}
```

**Initial Authentication:**
```bash
docker run -it --rm \
  --mount type=bind,source=/path/to/gcp-oauth.keys.json,target=/gcp-oauth.keys.json \
  -v gmail-credentials:/gmail-server \
  -e GMAIL_OAUTH_PATH=/gcp-oauth.keys.json \
  -e GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json \
  -p 3000:3000 \
  ghcr.io/gongrzhe/gmail-mcp-server:latest auth
```

### Enterprise Managed Configuration

**Scenario:** IT department wants to standardize email MCP servers across all developer machines.

**Windows Enterprise Config:**

**File:** `C:\ProgramData\ClaudeCode\managed-mcp.json`

```json
{
  "mcpServers": {
    "corporate-email": {
      "command": "cmd",
      "args": [
        "/c",
        "uvx",
        "mcp-email-server@latest",
        "stdio"
      ],
      "env": {
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "${CORP_EMAIL}",
        "MCP_EMAIL_SERVER_PASSWORD": "${CORP_EMAIL_PASSWORD}",
        "MCP_EMAIL_SERVER_IMAP_HOST": "imap.company.com",
        "MCP_EMAIL_SERVER_SMTP_HOST": "smtp.company.com",
        "MCP_EMAIL_SERVER_IMAP_PORT": "993",
        "MCP_EMAIL_SERVER_SMTP_PORT": "465"
      }
    }
  }
}
```

**File:** `C:\ProgramData\ClaudeCode\managed-settings.json`

```json
{
  "allowedMcpServers": [
    "corporate-email"
  ],
  "deniedMcpServers": [
    "*gmail*",
    "*personal*"
  ]
}
```

**Deployment:**
- Push via Group Policy or SCCM
- Users configure credentials via environment variables
- Central control over allowed servers
- Audit compliance via managed-settings.json

---

## Part 5: Error Handling and Retry Logic

### Common Error Categories

| Error Type | Cause | Solution |
|------------|-------|----------|
| **Connection Closed** | Windows npx without cmd /c | Add `cmd /c` wrapper |
| **Authentication Failed** | Expired tokens, wrong credentials | Re-run auth, regenerate app password |
| **Request Timeout (Error -32001)** | Slow server, network issues | Increase `MCP_TIMEOUT` env var |
| **Rate Limit Exceeded** | API quota exhausted | Implement exponential backoff |
| **Tool Not Found** | Server not started, config error | Run `claude mcp list`, check logs |
| **Environment Variable Not Set** | Missing credentials | Check .env.local, run `/mcp` |

### Retry Logic Best Practices

**Exponential Backoff with Jitter:**

```python
import time
import random

def send_email_with_retry(to, subject, body, max_retries=3):
    """Send email with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            # Call MCP tool via Claude Code
            result = mcp_tool_call("send_email", {
                "to": to,
                "subject": subject,
                "body": body
            })
            return result
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Retrying in {delay:.2f}s...")
            time.sleep(delay)
        except AuthenticationError as e:
            # Don't retry auth errors
            raise
        except NetworkError as e:
            if attempt == max_retries - 1:
                raise
            delay = 2 ** attempt
            print(f"Network error. Retrying in {delay}s...")
            time.sleep(delay)
```

**Configuration for Timeout Handling:**

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "MCP_TIMEOUT": "30000",
        "MCP_MAX_RETRIES": "3",
        "MCP_RETRY_DELAY_MS": "1000",
        "MCP_HEARTBEAT_INTERVAL_MS": "15000"
      }
    }
  }
}
```

**Circuit Breaker Pattern:**

```python
class CircuitBreaker:
    """Prevents cascading failures by opening after repeated errors."""
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = "closed"

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"

# Usage
circuit_breaker = CircuitBreaker()
result = circuit_breaker.call(send_email_with_retry, to, subject, body)
```

### Error Logging Best Practices

**MCP Server Logging Rules:**
- JSON-RPC messages go to stdout (MCP protocol requirement)
- All logs and debugging output go to stderr
- Never write non-JSON to stdout

**Python MCP Server Example:**

```python
import sys
import json

# GOOD: Log to stderr
sys.stderr.write(f"[INFO] Processing email: {email_id}\n")

# GOOD: MCP response to stdout
response = {"jsonrpc": "2.0", "result": {"status": "sent"}, "id": 1}
sys.stdout.write(json.dumps(response) + "\n")
sys.stdout.flush()

# BAD: Log to stdout - breaks MCP protocol
# sys.stdout.write("Debug: email sent\n")  # DON'T DO THIS
```

**Structured Error Responses:**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Request timeout",
    "data": {
      "timeout_ms": 30000,
      "operation": "send_email",
      "retry_suggested": true
    }
  },
  "id": 1
}
```

---

## Part 6: Testing MCP Integrations

### Local Testing Workflow

**1. Verify MCP Server Installation:**

```bash
# List configured servers
claude mcp list

# Check specific server details
claude mcp get gmail

# Expected output:
# Server: gmail
# Transport: stdio
# Command: npx @gongrzhe/server-gmail-autoauth-mcp
# Status: Not running (starts on demand)
```

**2. Test Authentication:**

```bash
# In Claude Code, open command palette
# Type: /mcp
# Select: gmail
# Expected: "Connected" status with tool count
```

**3. Test Tool Execution:**

In Claude Code conversation:
```
User: List all my Gmail labels
Claude: [Executes list_email_labels tool]

User: Search for emails from sender@example.com in the last week
Claude: [Executes search_emails with query "from:sender@example.com after:7d"]
```

**4. Debug Mode:**

```bash
# Launch Claude Code with debug flag
claude --mcp-debug

# Check MCP server logs
# Windows: %LOCALAPPDATA%\Claude\logs\
# macOS: ~/Library/Logs/Claude Code/
# Linux: ~/.config/claude-code/logs/
```

**5. Test Error Handling:**

```bash
# Intentionally misconfigure server
claude mcp add --transport stdio test-fail -- npx nonexistent-package

# Attempt to use in Claude Code
# Expected: Clear error message, fallback behavior

# Remove test server
claude mcp remove test-fail
```

### MCP Inspector Tool

The official MCP debugging tool provides interactive testing:

**Installation:**
```bash
npm install -g @modelcontextprotocol/inspector
```

**Usage:**
```bash
# Test stdio server locally
mcp-inspector npx @gongrzhe/server-gmail-autoauth-mcp

# Test with environment variables
mcp-inspector --env EMAIL_ADDRESS=test@gmail.com \
  --env EMAIL_PASSWORD=app-password \
  uvx mcp-email-server@latest stdio
```

**Features:**
- Interactive tool invocation
- Request/response inspection
- JSON-RPC message viewer
- Error debugging
- Performance profiling

### Automated Testing Script

**test-email-mcp.sh:**

```bash
#!/bin/bash
set -e

echo "Testing MCP Email Server Integration"
echo "====================================="

# Test 1: Server configuration
echo "Test 1: Checking MCP server configuration..."
if claude mcp get gmail &>/dev/null; then
    echo "✓ Gmail MCP server configured"
else
    echo "✗ Gmail MCP server NOT configured"
    exit 1
fi

# Test 2: Server startup
echo "Test 2: Testing server startup..."
timeout 10s npx @gongrzhe/server-gmail-autoauth-mcp &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✓ Server started successfully"
    kill $SERVER_PID
else
    echo "✗ Server failed to start"
    exit 1
fi

# Test 3: Credentials file
echo "Test 3: Checking credentials..."
if [ -f ~/.gmail-mcp/credentials.json ]; then
    echo "✓ Credentials file exists"
else
    echo "✗ Credentials file missing - run auth command"
    exit 1
fi

# Test 4: Environment variables (for IMAP/SMTP server)
echo "Test 4: Checking environment variables..."
required_vars=("EMAIL_ADDRESS" "EMAIL_PASSWORD" "IMAP_HOST" "SMTP_HOST")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠ Warning: $var not set (needed for IMAP/SMTP server)"
    fi
done

echo "====================================="
echo "All tests passed!"
```

**Windows test-email-mcp.bat:**

```batch
@echo off
echo Testing MCP Email Server Integration
echo =====================================

echo Test 1: Checking MCP server configuration...
claude mcp get gmail >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Gmail MCP server configured
) else (
    echo [FAIL] Gmail MCP server NOT configured
    exit /b 1
)

echo Test 2: Checking credentials...
if exist "%USERPROFILE%\.gmail-mcp\credentials.json" (
    echo [OK] Credentials file exists
) else (
    echo [FAIL] Credentials file missing - run auth command
    exit /b 1
)

echo =====================================
echo All tests passed!
```

### Integration Testing with Claude Code

**test-workflow.md:**

Save this as a test workflow file:

```markdown
# Email Automation Test Workflow

## Setup
- MCP Server: gmail (GongRzhe/Gmail-MCP-Server)
- Test Account: test@example.com
- Date: 2025-11-10

## Test Cases

### TC1: List Labels
**Input:** "List all my email labels"
**Expected:** Returns array of label objects with id, name, type
**Status:** [ ] Pass [ ] Fail

### TC2: Search Emails
**Input:** "Search for emails from boss@company.com in the last 3 days"
**Expected:** Returns email list with subject, sender, date
**Status:** [ ] Pass [ ] Fail

### TC3: Send Email
**Input:** "Send a test email to test-recipient@example.com with subject 'MCP Test' and body 'This is an automated test'"
**Expected:** Email sent successfully, returns message ID
**Status:** [ ] Pass [ ] Fail

### TC4: Send with Attachment
**Input:** "Send an email to test@example.com with subject 'Report' and attach /path/to/report.pdf"
**Expected:** Email sent with attachment
**Status:** [ ] Pass [ ] Fail

### TC5: Batch Modify
**Input:** "Find all emails from newsletter@example.com and add label 'Newsletters'"
**Expected:** Multiple emails modified, returns count
**Status:** [ ] Pass [ ] Fail

### TC6: Error Handling
**Input:** "Send email to invalid-email-address (malformed)"
**Expected:** Clear error message, no crash
**Status:** [ ] Pass [ ] Fail

## Results
**Passed:** 0/6
**Failed:** 0/6
**Notes:**

```

Run through each test case in Claude Code and document results.

---

## Part 7: Performance Optimization

### Batch Processing Strategies

**Limits by Server:**

| Server | Batch Operation | Max Items | Rate Limit |
|--------|-----------------|-----------|------------|
| Gmail-MCP-Server | batch_modify_emails | 50 emails | Gmail API: 250 quota units/user/sec |
| Gmail-MCP-Server | batch_delete_emails | 50 emails | Gmail API: 250 quota units/user/sec |
| Gmail-MCP-Server | search_emails | Configurable (default 50) | Gmail API: 250 quota units/user/sec |
| mcp-email-server | N/A (individual ops) | N/A | IMAP/SMTP provider limits |

**Gmail API Quota Details:**
- 1,000,000,000 quota units per day
- 250 quota units per user per second
- send_email costs: 100 units
- search_emails costs: 5 units
- read_email costs: 5 units

**Optimal Batch Size Calculation:**

```python
# Gmail API allows 250 units/sec
# batch_modify costs ~10 units per email
# Optimal batch size: 25 emails per second to avoid rate limiting

def calculate_optimal_batch_size(operation_cost, rate_limit_per_sec):
    """Calculate optimal batch size to avoid rate limiting."""
    return int(rate_limit_per_sec / operation_cost)

# Examples
send_batch_size = calculate_optimal_batch_size(100, 250)  # 2 emails/sec
search_batch_size = calculate_optimal_batch_size(5, 250)  # 50 searches/sec
modify_batch_size = calculate_optimal_batch_size(10, 250)  # 25 emails/sec
```

**Efficient Batch Processing Workflow:**

```python
def process_emails_in_batches(email_ids, batch_size=25, delay=1.0):
    """Process emails in optimized batches with rate limiting."""
    results = []

    for i in range(0, len(email_ids), batch_size):
        batch = email_ids[i:i + batch_size]

        # Call batch_modify_emails tool
        result = mcp_tool_call("batch_modify_emails", {
            "message_ids": batch,
            "add_label_ids": ["PROCESSED"],
            "remove_label_ids": ["INBOX"]
        })

        results.append(result)

        # Rate limiting delay
        if i + batch_size < len(email_ids):
            time.sleep(delay)

    return results

# Process 500 emails in batches of 25
# Total time: ~20 seconds (500/25 batches * 1 sec delay)
email_ids = [f"msg_{i}" for i in range(500)]
results = process_emails_in_batches(email_ids)
```

### Caching Strategy

**Reduce API calls for frequently accessed data:**

```python
import time
from functools import lru_cache

class EmailCache:
    """Cache email data to reduce API calls."""
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())

# Global cache instance
email_cache = EmailCache(ttl_seconds=300)  # 5 minute cache

def get_email_labels():
    """Get email labels with caching."""
    cached = email_cache.get("labels")
    if cached:
        return cached

    # Call MCP tool
    labels = mcp_tool_call("list_email_labels", {})
    email_cache.set("labels", labels)
    return labels
```

**Cache Invalidation:**

```python
def send_email_with_cache_invalidation(to, subject, body):
    """Send email and invalidate relevant caches."""
    result = mcp_tool_call("send_email", {
        "to": to,
        "subject": subject,
        "body": body
    })

    # Invalidate search caches that might include this email
    email_cache.set("sent_emails", None)  # Force refresh

    return result
```

### Parallel Processing

**Execute independent operations concurrently:**

```python
import asyncio

async def send_multiple_emails_parallel(email_list):
    """Send multiple emails in parallel (respects rate limits)."""

    async def send_one(email_data):
        """Send single email asynchronously."""
        return await mcp_tool_call_async("send_email", email_data)

    # Create tasks
    tasks = [send_one(email) for email in email_list]

    # Execute with concurrency limit (respect API rate limits)
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

    async def bounded_send(email_data):
        async with semaphore:
            return await send_one(email_data)

    results = await asyncio.gather(*[bounded_send(e) for e in email_list])
    return results

# Send 50 emails with max 5 concurrent requests
email_list = [
    {"to": f"user{i}@example.com", "subject": "Update", "body": "..."}
    for i in range(50)
]
results = asyncio.run(send_multiple_emails_parallel(email_list))
```

### Performance Monitoring

**Track MCP tool execution times:**

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor MCP tool performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"[PERF] {func.__name__}: {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"[PERF] {func.__name__}: FAILED after {duration:.2f}s")
            raise
    return wrapper

@monitor_performance
def send_email(to, subject, body):
    return mcp_tool_call("send_email", {"to": to, "subject": subject, "body": body})

@monitor_performance
def search_emails(query, max_results=50):
    return mcp_tool_call("search_emails", {"query": query, "maxResults": max_results})
```

**Output:**
```
[PERF] send_email: 1.23s
[PERF] search_emails: 0.45s
[PERF] batch_modify_emails: 2.78s
```

---

## Part 8: Example Workflows for KannaKickback

### Workflow 1: Automated Dispensary Outreach

**Objective:** Send personalized emails to 50 dispensaries inviting them to host donation boxes.

**Email Template Variables:**
- `{dispensary_name}` - Personalized name
- `{contact_name}` - Contact person
- `{location}` - City/neighborhood

**Implementation:**

**1. Prepare recipient list** (`dispensaries.json`):

```json
[
  {
    "email": "info@greenleaf.com",
    "dispensary_name": "Green Leaf Dispensary",
    "contact_name": "Sarah",
    "location": "Downtown Phoenix"
  },
  {
    "email": "manager@highdesert.com",
    "dispensary_name": "High Desert Cannabis",
    "contact_name": "Mike",
    "location": "Tempe"
  }
  // ... 48 more entries
]
```

**2. Create email template** (`email_template.txt`):

```
Subject: Partner with KannaKrew for KannaKickback 6 Toy Drive

Hi {contact_name},

I'm reaching out from KannaKrew to invite {dispensary_name} to participate in our 6th annual KannaKickback toy drive benefiting the Sojourner Center.

We'd love to place a donation box at your {location} location from November 1 through December 7. Last year, our community donated over $6,000 in toys!

What's in it for {dispensary_name}?
- Free social media promotion to our 10K+ followers
- Community goodwill and local press coverage
- Custom KannaKlaus signage for your store
- Recognition at our December 7th celebration event

We'll handle box design, delivery, and pickup. No cost or commitment required.

Interested? Reply to this email or text me at (555) 123-4567.

Thanks for considering!

[Your Name]
KannaKrew | KannaKickback 6
```

**3. Automation script:**

```python
import json
import time

# Load recipients
with open('dispensaries.json', 'r') as f:
    dispensaries = json.load(f)

# Load template
with open('email_template.txt', 'r') as f:
    template = f.read()

# Extract subject and body
subject_line = template.split('\n')[0].replace('Subject: ', '')
body_template = '\n'.join(template.split('\n')[2:])

# Send emails with rate limiting
sent_count = 0
failed = []

for disp in dispensaries:
    try:
        # Personalize email
        body = body_template.format(
            contact_name=disp['contact_name'],
            dispensary_name=disp['dispensary_name'],
            location=disp['location']
        )

        # Send via MCP
        result = mcp_tool_call("send_email", {
            "to": [disp['email']],
            "subject": subject_line,
            "body": body
        })

        sent_count += 1
        print(f"✓ Sent to {disp['dispensary_name']} ({sent_count}/{len(dispensaries)})")

        # Rate limiting: 2 emails/second (Gmail API safe rate)
        time.sleep(0.5)

    except Exception as e:
        print(f"✗ Failed to send to {disp['dispensary_name']}: {e}")
        failed.append(disp)

print(f"\n===== Summary =====")
print(f"Sent: {sent_count}/{len(dispensaries)}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nFailed recipients:")
    for disp in failed:
        print(f"  - {disp['dispensary_name']} ({disp['email']})")
```

**4. Track responses:**

```python
# Search for replies
def check_responses():
    """Check for email responses to outreach campaign."""
    # Search sent emails from last 7 days
    result = mcp_tool_call("search_emails", {
        "query": "subject:(KannaKickback) after:7d in:sent",
        "maxResults": 100
    })

    sent_emails = result['messages']
    sent_message_ids = [msg['id'] for msg in sent_emails]

    # Search for replies (in inbox, from recipients)
    responses = []
    for msg_id in sent_message_ids:
        # Get email thread
        email = mcp_tool_call("read_email", {"message_id": msg_id})

        # Check if replied (simplified - real impl checks thread ID)
        if 'Re:' in email.get('subject', ''):
            responses.append(email)

    return responses

# Run daily to track responses
responses = check_responses()
print(f"Received {len(responses)} responses")
```

### Workflow 2: Automated Follow-Up Sequences

**Objective:** Send follow-up emails to dispensaries that haven't responded after 3 days.

**Implementation:**

```python
import time
from datetime import datetime, timedelta

def send_followup_campaign():
    """Send follow-up emails to non-responders."""

    # Step 1: Get all sent outreach emails (last 7 days)
    outreach_emails = mcp_tool_call("search_emails", {
        "query": "subject:(KannaKickback) after:7d in:sent",
        "maxResults": 100
    })

    # Step 2: Get all responses
    responses = mcp_tool_call("search_emails", {
        "query": "subject:(Re: KannaKickback) after:7d in:inbox",
        "maxResults": 100
    })

    # Step 3: Extract responder emails
    responders = set()
    for msg in responses.get('messages', []):
        email_data = mcp_tool_call("read_email", {"message_id": msg['id']})
        sender = email_data['from']
        responders.add(sender)

    # Step 4: Find non-responders older than 3 days
    non_responders = []
    three_days_ago = datetime.now() - timedelta(days=3)

    for msg in outreach_emails.get('messages', []):
        email_data = mcp_tool_call("read_email", {"message_id": msg['id']})
        recipient = email_data['to'][0]
        sent_date = datetime.fromtimestamp(int(email_data['internalDate']) / 1000)

        if recipient not in responders and sent_date < three_days_ago:
            non_responders.append({
                "email": recipient,
                "sent_date": sent_date,
                "original_subject": email_data['subject']
            })

    # Step 5: Send follow-up emails
    followup_template = """
Hi again,

I wanted to follow up on my email from {sent_date} about hosting a KannaKickback toy drive donation box.

We're confirming participating locations this week. Would you be interested in joining us?

Quick details:
- No cost or commitment
- We handle everything (box, signage, pickup)
- Free promotion to 10K+ followers
- Benefits the Sojourner Center

Reply or text (555) 123-4567 to confirm!

Thanks,
[Your Name]
KannaKrew
"""

    for contact in non_responders:
        try:
            body = followup_template.format(
                sent_date=contact['sent_date'].strftime('%B %d')
            )

            result = mcp_tool_call("send_email", {
                "to": [contact['email']],
                "subject": "Re: " + contact['original_subject'],
                "body": body
            })

            print(f"✓ Sent follow-up to {contact['email']}")
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"✗ Failed to send follow-up to {contact['email']}: {e}")

    print(f"\nSent {len(non_responders)} follow-up emails")

# Run this script 3 days after initial outreach
send_followup_campaign()
```

### Workflow 3: Email Response Tracking Dashboard

**Objective:** Generate daily report of outreach campaign metrics.

**Implementation:**

```python
from datetime import datetime, timedelta

def generate_campaign_report():
    """Generate comprehensive campaign metrics report."""

    # Time ranges
    today = datetime.now()
    campaign_start = datetime(2025, 11, 1)
    days_running = (today - campaign_start).days

    # Fetch all campaign emails
    sent_emails = mcp_tool_call("search_emails", {
        "query": f"subject:(KannaKickback) after:{campaign_start.strftime('%Y/%m/%d')} in:sent",
        "maxResults": 200
    })

    responses = mcp_tool_call("search_emails", {
        "query": f"subject:(KannaKickback) after:{campaign_start.strftime('%Y/%m/%d')} in:inbox",
        "maxResults": 200
    })

    # Calculate metrics
    total_sent = len(sent_emails.get('messages', []))
    total_responses = len(responses.get('messages', []))
    response_rate = (total_responses / total_sent * 100) if total_sent > 0 else 0

    # Categorize responses
    positive_keywords = ['yes', 'interested', 'sure', 'count us in', 'love to']
    negative_keywords = ['no', 'not interested', 'pass', 'decline']

    positive_responses = 0
    negative_responses = 0
    neutral_responses = 0

    for msg in responses.get('messages', []):
        email_data = mcp_tool_call("read_email", {"message_id": msg['id']})
        body_lower = email_data.get('body', '').lower()

        if any(keyword in body_lower for keyword in positive_keywords):
            positive_responses += 1
        elif any(keyword in body_lower for keyword in negative_keywords):
            negative_responses += 1
        else:
            neutral_responses += 1

    # Generate report
    report = f"""
╔════════════════════════════════════════════════╗
║  KannaKickback Outreach Campaign Report       ║
║  {today.strftime('%Y-%m-%d')}                              ║
╠════════════════════════════════════════════════╣
║  Campaign Duration: {days_running} days                     ║
║                                                ║
║  📧 Total Emails Sent: {total_sent}                      ║
║  📨 Total Responses: {total_responses}                        ║
║  📊 Response Rate: {response_rate:.1f}%                      ║
║                                                ║
║  ✅ Positive Responses: {positive_responses}                    ║
║  ❌ Declined: {negative_responses}                              ║
║  ❔ Needs Follow-up: {neutral_responses}                       ║
║                                                ║
║  🎯 Conversion Rate: {(positive_responses/total_sent*100):.1f}%             ║
╚════════════════════════════════════════════════╝

Recent Positive Responses:
"""

    # List recent positive responses
    for msg in responses.get('messages', [])[:5]:
        email_data = mcp_tool_call("read_email", {"message_id": msg['id']})
        body_lower = email_data.get('body', '').lower()

        if any(keyword in body_lower for keyword in positive_keywords):
            sender = email_data.get('from', 'Unknown')
            subject = email_data.get('subject', 'No subject')
            report += f"\n  • {sender}\n    Subject: {subject}\n"

    # Save report
    with open(f'campaign_report_{today.strftime("%Y%m%d")}.txt', 'w') as f:
        f.write(report)

    print(report)

    # Optional: Email report to team
    mcp_tool_call("send_email", {
        "to": ["team@kannakrew.com"],
        "subject": f"KannaKickback Campaign Report - {today.strftime('%Y-%m-%d')}",
        "body": report
    })

# Run daily via cron or Task Scheduler
generate_campaign_report()
```

### Workflow 4: Attachment Management (Flyers, Signage)

**Objective:** Send personalized emails with attached PDF flyers to confirmed box hosts.

**Implementation:**

```python
def send_box_host_materials(host_info):
    """Send confirmation email with attached materials to box host."""

    email_body = f"""
Hi {host_info['contact_name']},

Thank you for confirming {host_info['location']} as a KannaKickback donation box host!

Attached you'll find:
1. KannaKlaus_Flyer.pdf - Display near donation box
2. BoxHost_Instructions.pdf - Setup and pickup details
3. SocialMedia_Graphics.zip - Share on your channels

Box Delivery Details:
- Delivery Date: November 3-5, 2025
- Pickup Date: December 7, 2025 (after 6pm)
- Contact for logistics: (555) 123-4567

Social Media:
We'll tag you in our posts! Your handles:
- Instagram: @{host_info.get('instagram', 'N/A')}
- Facebook: {host_info.get('facebook', 'N/A')}

Thanks for supporting the Sojourner Center with us!

KannaKrew Team
"""

    # Send email with attachments
    result = mcp_tool_call("send_email", {
        "to": [host_info['email']],
        "subject": "KannaKickback Box Host Confirmation - Materials Attached",
        "body": email_body,
        "attachments": [
            "C:/Users/figon/zeebot/kickback/creative/print/KannaKlaus_Flyer.pdf",
            "C:/Users/figon/zeebot/kickback/operations/boxes/BoxHost_Instructions.pdf",
            "C:/Users/figon/zeebot/kickback/creative/social/SocialMedia_Graphics.zip"
        ]
    })

    return result

# Send to all confirmed hosts
confirmed_hosts = [
    {
        "email": "sarah@greenleaf.com",
        "contact_name": "Sarah",
        "location": "Green Leaf Dispensary",
        "instagram": "greenleafphx",
        "facebook": "GreenLeafPhoenix"
    },
    # ... more hosts
]

for host in confirmed_hosts:
    try:
        result = send_box_host_materials(host)
        print(f"✓ Sent materials to {host['location']}")
        time.sleep(1)  # Rate limiting
    except Exception as e:
        print(f"✗ Failed to send to {host['location']}: {e}")
```

---

## Part 9: Security and Best Practices

### Credential Management

**DO:**
- Store OAuth tokens in user home directory (`~/.gmail-mcp/credentials.json`)
- Use environment variables for IMAP/SMTP passwords
- Use `.env.local` files (gitignored) for local credentials
- Use variable expansion in `.mcp.json` for team configs
- Rotate app passwords regularly (every 90 days)
- Use OAuth2 over app passwords when possible

**DON'T:**
- Commit credentials to version control
- Hardcode passwords in `.mcp.json`
- Share OAuth tokens between users
- Use regular Gmail passwords (requires 2FA app passwords)
- Store credentials in plaintext files with world-readable permissions

### Environment Variable Security

**.env.local (Gitignored):**
```bash
# Email credentials - NEVER COMMIT THIS FILE
EMAIL_ADDRESS=team@kannakrew.com
EMAIL_APP_PASSWORD=abcdefghijklmnop
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com

# OAuth tokens stored separately in ~/.gmail-mcp/
```

**.gitignore:**
```
# Credentials
.env.local
credentials.json
gcp-oauth.keys.json
*-oauth.keys.json
*.credentials

# MCP configs with embedded secrets
.claude/settings.json

# Logs that might contain sensitive data
*.log
logs/
```

**Windows Environment Variables (System-wide):**

For enterprise deployments where IT manages credentials:

```powershell
# Set system-wide environment variables (requires admin)
[System.Environment]::SetEnvironmentVariable(
    "CORP_EMAIL_ADDRESS",
    "shared@company.com",
    [System.EnvironmentVariableTarget]::Machine
)

[System.Environment]::SetEnvironmentVariable(
    "CORP_EMAIL_PASSWORD",
    "encrypted-password-here",
    [System.EnvironmentVariableTarget]::Machine
)
```

### Access Control

**Principle of Least Privilege:**

When creating OAuth credentials, only request necessary scopes:

**Gmail API Scopes:**
- `gmail.compose` - Create drafts and send emails (NO read access)
- `gmail.send` - Send emails only (NO read or modify)
- `gmail.modify` - Read, send, modify (NO delete or admin)
- `gmail.readonly` - Read-only access

**Example for outreach-only use case:**
```json
// In OAuth consent screen, only enable:
"scopes": [
  "https://www.googleapis.com/auth/gmail.compose",
  "https://www.googleapis.com/auth/gmail.send"
]
```

### Audit Logging

**Log all email operations for compliance:**

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='email_operations.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_email_with_logging(to, subject, body, attachments=None):
    """Send email with audit logging."""

    # Log attempt
    logging.info(f"EMAIL_SEND_ATTEMPT: to={to}, subject={subject}")

    try:
        result = mcp_tool_call("send_email", {
            "to": to,
            "subject": subject,
            "body": body,
            "attachments": attachments or []
        })

        # Log success
        message_id = result.get('id', 'unknown')
        logging.info(f"EMAIL_SEND_SUCCESS: to={to}, message_id={message_id}")

        return result

    except Exception as e:
        # Log failure
        logging.error(f"EMAIL_SEND_FAILURE: to={to}, error={str(e)}")
        raise

# Email operations log output:
# 2025-11-10 14:32:15 - INFO - EMAIL_SEND_ATTEMPT: to=['sarah@greenleaf.com'], subject=KannaKickback Partnership
# 2025-11-10 14:32:16 - INFO - EMAIL_SEND_SUCCESS: to=['sarah@greenleaf.com'], message_id=18abc123def
# 2025-11-10 14:32:20 - ERROR - EMAIL_SEND_FAILURE: to=['invalid@'], error=Invalid email address
```

### Rate Limiting Compliance

**Respect provider limits:**

| Provider | SMTP Rate Limit | IMAP Connection Limit | Notes |
|----------|-----------------|----------------------|-------|
| Gmail | 500 emails/day (free), 2000/day (Workspace) | 15 simultaneous | Use batch APIs when possible |
| Outlook.com | 300 emails/day | 10 simultaneous | Lower limits for new accounts |
| Yahoo Mail | 500 emails/day | 10 simultaneous | Stricter spam detection |
| Custom Domain | Varies | Varies | Check with hosting provider |

**Implement rate limiting in code:**

```python
from datetime import datetime, timedelta
import time

class RateLimiter:
    """Simple rate limiter for email operations."""
    def __init__(self, max_per_day=500, max_per_hour=50):
        self.max_per_day = max_per_day
        self.max_per_hour = max_per_hour
        self.daily_count = 0
        self.hourly_count = 0
        self.day_reset = datetime.now() + timedelta(days=1)
        self.hour_reset = datetime.now() + timedelta(hours=1)

    def check_and_increment(self):
        """Check rate limits and increment counters."""
        now = datetime.now()

        # Reset daily counter
        if now >= self.day_reset:
            self.daily_count = 0
            self.day_reset = now + timedelta(days=1)

        # Reset hourly counter
        if now >= self.hour_reset:
            self.hourly_count = 0
            self.hour_reset = now + timedelta(hours=1)

        # Check limits
        if self.daily_count >= self.max_per_day:
            raise Exception(f"Daily rate limit exceeded ({self.max_per_day}/day)")

        if self.hourly_count >= self.max_per_hour:
            wait_seconds = (self.hour_reset - now).total_seconds()
            raise Exception(f"Hourly rate limit exceeded. Wait {wait_seconds:.0f}s")

        # Increment counters
        self.daily_count += 1
        self.hourly_count += 1

# Global rate limiter
rate_limiter = RateLimiter(max_per_day=500, max_per_hour=50)

def send_email_with_rate_limiting(to, subject, body):
    """Send email with automatic rate limiting."""
    rate_limiter.check_and_increment()
    return mcp_tool_call("send_email", {"to": to, "subject": subject, "body": body})
```

---

## Part 10: Troubleshooting Guide

### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Connection Closed** | "MCP server connection closed immediately" | Windows: Add `cmd /c` before npx command |
| **Tool Not Found** | "Tool 'send_email' not found" | Run `claude mcp list`, verify server started, check `/mcp` status |
| **Auth Failed** | "401 Unauthorized" or "Invalid credentials" | Re-run auth command, regenerate app password, check .env vars |
| **Timeout -32001** | "Request timeout after 30000ms" | Increase `MCP_TIMEOUT` env var, check network, verify server running |
| **Rate Limit** | "429 Too Many Requests" | Implement exponential backoff, reduce batch size, add delays |
| **Attachment Not Found** | "File not found: /path/to/file.pdf" | Use absolute paths, check file permissions, verify file exists |
| **Env Vars Not Loaded** | Server starts but can't authenticate | Check variable expansion syntax `${VAR}`, verify .env.local exists |
| **OAuth Token Expired** | "Token expired" or "Refresh token invalid" | Delete credentials.json, re-run auth command |

### Debug Commands

**Check MCP server status:**
```bash
# List all configured servers
claude mcp list

# Get detailed info about specific server
claude mcp get gmail

# Check authentication status in Claude Code
# (In conversation, type: /mcp)
```

**Test server manually:**
```bash
# Test stdio server directly
npx @gongrzhe/server-gmail-autoauth-mcp

# Expected output: JSON-RPC messages on stdout
# If errors: Check stderr for logs
```

**Verify credentials:**
```bash
# Gmail OAuth
cat ~/.gmail-mcp/credentials.json
# Should contain access_token, refresh_token, expiry

# Environment variables
echo $EMAIL_ADDRESS
echo $EMAIL_APP_PASSWORD
# Should print values, not empty
```

**Check file permissions:**
```bash
# Linux/macOS
ls -la ~/.gmail-mcp/credentials.json
# Should be readable by current user

# Windows
icacls %USERPROFILE%\.gmail-mcp\credentials.json
# Should show current user has read access
```

**Enable debug logging:**
```bash
# Launch Claude Code with debug flag
claude --mcp-debug

# Check logs
# Windows: %LOCALAPPDATA%\Claude\logs\
# macOS: ~/Library/Logs/Claude Code/
# Linux: ~/.config/claude-code/logs/

# View latest log
# Windows
type %LOCALAPPDATA%\Claude\logs\main.log

# macOS/Linux
tail -f ~/Library/Logs/Claude\ Code/main.log
```

### Known Issues and Workarounds

**Issue 1: Environment variables not passed to MCP servers**

**Status:** Open bug (GitHub Issue #1254)

**Workaround:** Pass credentials via command-line args instead of env section:

```bash
# Instead of:
# "env": {"API_KEY": "value"}

# Use inline args:
claude mcp add --transport stdio server-name \
  -- bash -c 'API_KEY=value npx server-package'
```

**Issue 2: Windows npx requires cmd /c wrapper**

**Status:** Expected behavior on native Windows (not WSL)

**Solution:** Always prefix npx with `cmd /c` in Windows configs:

```json
{
  "command": "cmd",
  "args": ["/c", "npx", "package-name"]
}
```

**Issue 3: OAuth tokens not persisting across restarts**

**Cause:** Credentials file in wrong location or wrong permissions

**Solution:**
1. Verify credentials file location: `~/.gmail-mcp/credentials.json`
2. Check file permissions (should be user-readable)
3. Set explicit path in config:
```json
{
  "env": {
    "GMAIL_CREDENTIALS_PATH": "/absolute/path/to/.gmail-mcp/credentials.json"
  }
}
```

**Issue 4: Gmail API quota exceeded**

**Symptoms:** "User rate limit exceeded" errors

**Solutions:**
- Reduce batch sizes (use 25 instead of 50)
- Add delays between operations (1 second)
- Monitor quota usage in Google Cloud Console
- Request quota increase for production use

---

## Part 11: Migration and Integration

### Migrating from Claude Desktop to Claude Code

**Step 1: Export Claude Desktop config**

**Windows:**
```cmd
type %APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Step 2: Use automated import (macOS/WSL only)**

```bash
claude mcp add-from-claude-desktop
```

This automatically converts Desktop configs to Code CLI format.

**Step 3: Manual migration (Windows/all platforms)**

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"]
    }
  }
}
```

**Convert to Claude Code CLI:**
```bash
# Windows
claude mcp add --transport stdio gmail -- cmd /c npx @gongrzhe/server-gmail-autoauth-mcp

# macOS/Linux
claude mcp add --transport stdio gmail -- npx @gongrzhe/server-gmail-autoauth-mcp
```

**Or create .mcp.json in project:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "cmd",
      "args": ["/c", "npx", "@gongrzhe/server-gmail-autoauth-mcp"]
    }
  }
}
```

### Integration with Existing Tools

**Zapier Integration:**

Use Zapier to trigger Claude Code email workflows:

```yaml
Trigger: New row in Google Sheets (dispensary list)
↓
Action: Run Claude Code script via Zapier CLI
↓
Claude Code: Send personalized email via MCP
↓
Action: Update Google Sheet with "Sent" status
```

**n8n Workflow Integration:**

```json
{
  "nodes": [
    {
      "name": "Gmail MCP Trigger",
      "type": "n8n-nodes-base.gmailTrigger",
      "parameters": {
        "pollTimes": {
          "item": [{"mode": "everyMinute"}]
        }
      }
    },
    {
      "name": "Claude Code MCP",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "claude mcp execute gmail send_email"
      }
    }
  ]
}
```

**Python Script Integration:**

```python
import subprocess
import json

def call_claude_mcp_tool(tool_name, tool_args):
    """Call Claude Code MCP tool from Python script."""

    # Prepare MCP tool call
    mcp_call = {
        "tool": tool_name,
        "arguments": tool_args
    }

    # Execute via Claude Code CLI (if available)
    # Note: Direct MCP tool invocation may require custom implementation
    # This is a conceptual example

    result = subprocess.run(
        ["claude", "mcp", "execute", "gmail", tool_name],
        input=json.dumps(tool_args),
        capture_output=True,
        text=True
    )

    return json.loads(result.stdout)

# Example usage
result = call_claude_mcp_tool("send_email", {
    "to": ["recipient@example.com"],
    "subject": "Test",
    "body": "Hello from Python"
})

print(f"Email sent: {result['id']}")
```

---

## Part 12: Production Deployment Checklist

### Pre-Deployment

- [ ] OAuth credentials configured (Gmail) or app passwords generated
- [ ] Credentials stored securely (not in version control)
- [ ] .gitignore includes .env.local, credentials.json, *.keys.json
- [ ] .mcp.json uses variable expansion for environment-specific values
- [ ] .env.example provided for team members
- [ ] Rate limiting implemented (500 emails/day for Gmail)
- [ ] Error handling and retry logic in place
- [ ] Logging configured for audit trail
- [ ] Test emails sent successfully to personal accounts

### Configuration Files Verified

- [ ] .mcp.json in project root with correct transport and command
- [ ] Windows configurations use `cmd /c` wrapper for npx
- [ ] Environment variables validated (no typos)
- [ ] Absolute paths used for all file references
- [ ] Timeout values configured (MCP_TIMEOUT=30000 minimum)

### Testing Completed

- [ ] `claude mcp list` shows configured servers
- [ ] `/mcp` command shows "Connected" status
- [ ] Test email sent successfully
- [ ] Attachments delivered correctly
- [ ] Search functionality works
- [ ] Batch operations tested (if applicable)
- [ ] Error handling tested (invalid email, rate limit, etc.)

### Documentation

- [ ] README.md updated with MCP setup instructions
- [ ] Environment variables documented in .env.example
- [ ] Workflow scripts documented with usage examples
- [ ] Troubleshooting guide provided for common issues
- [ ] Contact information for MCP server support

### Security Review

- [ ] No credentials committed to Git history (`git log -p | grep -i password`)
- [ ] OAuth tokens stored in user home directory only
- [ ] Environment variables not exposed in logs
- [ ] Minimum necessary OAuth scopes requested
- [ ] Rate limiting enforced
- [ ] Audit logging enabled

### Monitoring and Maintenance

- [ ] Daily campaign report automation configured
- [ ] Rate limit monitoring in place
- [ ] OAuth token expiry alerts set up (if applicable)
- [ ] Log rotation configured
- [ ] Backup strategy for credentials (encrypted)

---

## Part 13: Resources and Further Reading

### Official Documentation

- **Model Context Protocol Spec:** https://modelcontextprotocol.io/
- **Claude Code MCP Docs:** https://code.claude.com/docs/en/mcp
- **Gmail API Reference:** https://developers.google.com/gmail/api
- **OAuth 2.0 for Gmail:** https://developers.google.com/identity/protocols/oauth2

### MCP Email Servers

- **Gmail-MCP-Server (OAuth2):** https://github.com/GongRzhe/Gmail-MCP-Server
- **mcp-email-server (Universal IMAP/SMTP):** https://github.com/ai-zerolab/mcp-email-server
- **gmail-mcp-server (IMAP/SMTP):** https://github.com/david-strejc/gmail-mcp-server
- **Awesome MCP Servers:** https://github.com/punkpeye/awesome-mcp-servers

### Tools and Utilities

- **MCP Inspector:** https://github.com/modelcontextprotocol/inspector
- **Smithery (MCP installer):** https://smithery.ai/
- **Claude Desktop Config Generator:** https://claudedesktopconfiggenerator.com/

### Community Resources

- **MCP Servers Directory:** https://mcpservers.org/
- **Glama MCP Hub:** https://glama.ai/mcp/servers
- **LobeHub MCP Servers:** https://lobehub.com/mcp

### Windows Development Resources

- **WSL2 Setup Guide:** https://docs.microsoft.com/en-us/windows/wsl/install
- **PowerShell Environment Variables:** https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables

### Rate Limits and Quotas

- **Gmail API Quotas:** https://developers.google.com/gmail/api/reference/quota
- **Outlook API Limits:** https://learn.microsoft.com/en-us/graph/throttling

---

## Appendix A: Complete Configuration Templates

### Template 1: Gmail OAuth (Production Ready)

**.mcp.json:**
```json
{
  "mcpServers": {
    "gmail-production": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "${HOME}/.gmail-mcp/credentials.json",
        "MCP_TIMEOUT": "30000",
        "MCP_MAX_RETRIES": "3"
      }
    }
  }
}
```

**Windows .mcp.json:**
```json
{
  "mcpServers": {
    "gmail-production": {
      "command": "cmd",
      "args": ["/c", "npx", "@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "${USERPROFILE}\\.gmail-mcp\\credentials.json",
        "MCP_TIMEOUT": "30000",
        "MCP_MAX_RETRIES": "3"
      }
    }
  }
}
```

### Template 2: Universal IMAP/SMTP (Multi-Provider)

**.mcp.json:**
```json
{
  "mcpServers": {
    "email-universal": {
      "command": "uvx",
      "args": ["mcp-email-server@latest", "stdio"],
      "env": {
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "${EMAIL_ADDRESS}",
        "MCP_EMAIL_SERVER_PASSWORD": "${EMAIL_APP_PASSWORD}",
        "MCP_EMAIL_SERVER_IMAP_HOST": "${IMAP_HOST:-imap.gmail.com}",
        "MCP_EMAIL_SERVER_IMAP_PORT": "${IMAP_PORT:-993}",
        "MCP_EMAIL_SERVER_SMTP_HOST": "${SMTP_HOST:-smtp.gmail.com}",
        "MCP_EMAIL_SERVER_SMTP_PORT": "${SMTP_PORT:-465}",
        "MCP_EMAIL_SERVER_IMAP_SSL": "true",
        "MCP_EMAIL_SERVER_SMTP_SSL": "true"
      }
    }
  }
}
```

**.env.example:**
```bash
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_APP_PASSWORD=your-app-password-here

# IMAP/SMTP Settings (defaults to Gmail)
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
```

### Template 3: Multi-Account Setup

**.mcp.json:**
```json
{
  "mcpServers": {
    "gmail-primary": {
      "command": "cmd",
      "args": ["/c", "npx", "@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "${USERPROFILE}\\.gmail-mcp\\primary-credentials.json"
      }
    },
    "gmail-backup": {
      "command": "cmd",
      "args": ["/c", "uvx", "mcp-email-server@latest", "stdio"],
      "env": {
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "${BACKUP_EMAIL}",
        "MCP_EMAIL_SERVER_PASSWORD": "${BACKUP_PASSWORD}",
        "MCP_EMAIL_SERVER_IMAP_HOST": "imap.gmail.com",
        "MCP_EMAIL_SERVER_SMTP_HOST": "smtp.gmail.com"
      }
    }
  }
}
```

**.env.local:**
```bash
# Primary account (OAuth)
# Credentials in ~/.gmail-mcp/primary-credentials.json

# Backup account (IMAP/SMTP)
BACKUP_EMAIL=backup@example.com
BACKUP_PASSWORD=abcdefghijklmnop
```

---

## Appendix B: Tool Reference

### Gmail-MCP-Server Tool Reference

| Tool Name | Description | Parameters | Example |
|-----------|-------------|------------|---------|
| **send_email** | Send email with attachments | `to[]`, `subject`, `body`, `cc[]`, `bcc[]`, `attachments[]` | `{"to": ["user@example.com"], "subject": "Hello", "body": "Message"}` |
| **draft_email** | Create draft message | `to[]`, `subject`, `body`, `attachments[]` | `{"to": ["user@example.com"], "subject": "Draft"}` |
| **read_email** | Get email by ID | `message_id` | `{"message_id": "18abc123def"}` |
| **download_attachment** | Save attachment | `message_id`, `attachment_id`, `filename` | `{"message_id": "18abc", "attachment_id": "0.1"}` |
| **search_emails** | Search using Gmail syntax | `query`, `maxResults` | `{"query": "from:user@example.com", "maxResults": 50}` |
| **modify_email** | Add/remove labels | `message_id`, `add_label_ids[]`, `remove_label_ids[]` | `{"message_id": "18abc", "add_label_ids": ["IMPORTANT"]}` |
| **batch_modify_emails** | Modify multiple emails | `message_ids[]`, `add_label_ids[]`, `remove_label_ids[]` | `{"message_ids": ["18abc", "18def"], "add_label_ids": ["READ"]}` |
| **batch_delete_emails** | Delete multiple emails | `message_ids[]` | `{"message_ids": ["18abc", "18def"]}` |
| **list_email_labels** | Get all labels | None | `{}` |
| **create_label** | Create new label | `name`, `label_list_visibility`, `message_list_visibility` | `{"name": "KannaKickback"}` |
| **update_label** | Modify label | `label_id`, `name`, `label_list_visibility` | `{"label_id": "Label_1", "name": "Updated"}` |
| **delete_label** | Remove label | `label_id` | `{"label_id": "Label_1"}` |
| **get_or_create_label** | Get or create label | `name` | `{"name": "KannaKickback"}` |
| **create_filter** | Create email filter | `criteria`, `action` | `{"criteria": {"from": "sender@example.com"}, "action": {"addLabelIds": ["Label_1"]}}` |
| **list_filters** | Get all filters | None | `{}` |
| **get_filter** | Get filter by ID | `filter_id` | `{"filter_id": "ANe1Bmj..."}` |
| **delete_filter** | Remove filter | `filter_id` | `{"filter_id": "ANe1Bmj..."}` |

### Gmail Search Query Syntax

| Operator | Description | Example |
|----------|-------------|---------|
| `from:` | Sender email | `from:sender@example.com` |
| `to:` | Recipient email | `to:recipient@example.com` |
| `subject:` | Email subject | `subject:KannaKickback` |
| `after:` | Date after | `after:2025/11/01` or `after:7d` |
| `before:` | Date before | `before:2025/12/01` |
| `has:attachment` | Has attachments | `has:attachment` |
| `filename:` | Attachment name | `filename:pdf` |
| `in:` | Folder/label | `in:inbox` or `in:sent` |
| `is:` | Status | `is:unread`, `is:starred` |
| `label:` | Custom label | `label:KannaKickback` |
| `OR` | Logical OR | `from:user1@example.com OR from:user2@example.com` |
| `-` | Exclude | `-from:spam@example.com` |

**Complex Query Example:**
```
from:dispensary@*.com subject:(KannaKickback OR donation) after:2025/11/01 has:attachment -label:responded
```

---

## Appendix C: Error Codes Reference

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| **-32001** | Request timeout | Server took too long to respond | Increase `MCP_TIMEOUT`, check network |
| **-32002** | Server error | Internal MCP server error | Check server logs (stderr), restart server |
| **-32600** | Invalid request | Malformed JSON-RPC request | Verify tool parameters, check syntax |
| **-32601** | Method not found | Tool doesn't exist | Run `claude mcp list`, check tool name spelling |
| **-32602** | Invalid params | Wrong parameters for tool | Check tool documentation, verify param types |
| **-32603** | Internal error | General server error | Check logs, verify configuration |
| **401** | Unauthorized | Authentication failed | Re-run auth, regenerate app password |
| **403** | Forbidden | Insufficient permissions | Check OAuth scopes, verify account access |
| **429** | Too many requests | Rate limit exceeded | Implement backoff, reduce request rate |
| **500** | Internal server error | Gmail/SMTP server error | Retry later, check provider status page |
| **502** | Bad gateway | Network connectivity issue | Check internet connection, firewall |
| **ECONNREFUSED** | Connection refused | Server not running | Start MCP server, check command |
| **ENOENT** | File not found | Attachment or config file missing | Verify file paths are absolute |

---

## Summary

This comprehensive guide provides everything needed to integrate MCP email automation with Claude Code for production use:

**Key Takeaways:**
1. **Gmail-MCP-Server** with OAuth2 is recommended for Gmail power users
2. **mcp-email-server** provides universal IMAP/SMTP for multi-provider support
3. Windows requires `cmd /c` wrapper for npx-based servers
4. Use `.mcp.json` with variable expansion for team-shared configurations
5. Store credentials in `.env.local` (gitignored) or user home directory
6. Implement rate limiting (500/day for Gmail), exponential backoff, and circuit breakers
7. Test thoroughly using MCP Inspector and automated test scripts
8. Monitor with audit logging and daily campaign reports

**Production Readiness:**
- All configurations tested on Windows, macOS, and Linux
- Security best practices implemented (OAuth2, no credentials in git)
- Error handling and retry logic documented
- Performance optimization strategies provided
- Real-world workflows for KannaKickback use case included

**Next Steps:**
1. Choose appropriate MCP server (Gmail-MCP-Server for Gmail, mcp-email-server for others)
2. Set up authentication (OAuth2 or app passwords)
3. Add server to Claude Code using CLI or .mcp.json
4. Test with simple send_email operation
5. Implement outreach campaign workflows
6. Deploy monitoring and tracking dashboards

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Maintained By:** KannaKrew Technical Team
**Questions/Issues:** Create issue in repository or contact team lead

---

