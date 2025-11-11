---
title: MCP Gmail Server Setup Guide for Claude Code
date: 2025-11-10
research_query: "Setting up MCP Gmail server with Claude Code - complete implementation guide"
completeness: 95%
performance: "v2.0 wide-then-deep (3 batches, 11 parallel searches)"
execution_time: "3.2 minutes"
---

# Complete MCP Gmail Server Setup Guide for Claude Code

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Google Cloud Console Configuration](#google-cloud-console-configuration)
4. [Gmail MCP Server Installation](#gmail-mcp-server-installation)
5. [Authentication Flow](#authentication-flow)
6. [Available Commands & Capabilities](#available-commands--capabilities)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Overview

The Gmail MCP (Model Context Protocol) server enables Claude Code to interact with Gmail through natural language. This guide covers the complete setup process from Google Cloud configuration to authentication and usage.

**Recommended MCP Server**: `@gongrzhe/server-gmail-autoauth-mcp`
- Auto-authentication with browser launch
- Global credential storage in `~/.gmail-mcp/`
- Full attachment support
- Batch operations for efficiency
- Support for both Desktop and Web OAuth credentials

---

## Prerequisites

### Required Software
- Node.js (v14 or higher)
- npm or npx
- Claude Code installed
- A Google account with Gmail access

### Required Access
- Google Cloud Console access
- Ability to create projects and enable APIs
- Gmail account for testing

---

## Google Cloud Console Configuration

### Step 1: Create Google Cloud Project

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown (top left, next to "Google Cloud")
3. Click "NEW PROJECT"
4. Enter project details:
   - **Project name**: `gmail-mcp-claude` (or your preferred name)
   - **Organization**: (optional, leave default)
   - **Location**: (optional, leave default)
5. Click "CREATE"
6. Wait for project creation (typically 30-60 seconds)
7. Switch to your new project using the project dropdown

### Step 2: Enable Gmail API

1. In the left sidebar, navigate to:
   - **APIs & Services** → **Library**
2. In the search bar, type: `Gmail API`
3. Click on "Gmail API" from the results
4. Click the blue "ENABLE" button
5. Wait for API activation (typically instant)

### Step 3: Configure OAuth Consent Screen

**CRITICAL**: You must complete this step before creating credentials.

1. Navigate to: **APIs & Services** → **OAuth consent screen**
2. Choose **User Type**:
   - Select "External" (for personal Gmail accounts)
   - Select "Internal" (only available for Google Workspace accounts)
3. Click "CREATE"

#### Fill Out App Information

**App Information (Page 1):**
```
App name: Gmail MCP for Claude
User support email: [your email]
App logo: (optional, can skip)
```

**App Domain (Page 1):**
```
Application home page: (optional, can leave blank)
Application privacy policy link: (optional, can leave blank)
Application terms of service link: (optional, can leave blank)
```

**Developer Contact Information (Page 1):**
```
Email addresses: [your email]
```

4. Click "SAVE AND CONTINUE"

#### Configure Scopes (Page 2)

5. Click "ADD OR REMOVE SCOPES"
6. In the filter box, search for and select these scopes:

**Required Scopes:**
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.modify
```

**Scope Explanations:**
- `gmail.readonly` - Read emails, search, download attachments
- `gmail.compose` - Create and update drafts
- `gmail.send` - Send emails
- `gmail.modify` - Manage labels, archive, delete (no permanent deletion)

**Optional (Full Access):**
```
https://mail.google.com/
```
⚠️ **Warning**: Only use this if you need permanent deletion capabilities. All other operations work with the scopes above.

7. Click "UPDATE"
8. Click "SAVE AND CONTINUE"

#### Add Test Users (Page 3)

9. Click "ADD USERS"
10. Enter your Gmail address (the one you'll authenticate with)
11. Click "ADD"
12. Click "SAVE AND CONTINUE"

#### Review and Complete (Page 4)

13. Review all settings
14. Click "BACK TO DASHBOARD"

### Step 4: Create OAuth 2.0 Credentials

1. Navigate to: **APIs & Services** → **Credentials**
2. Click "CREATE CREDENTIALS" (top center)
3. Select "OAuth client ID"

#### Choose Application Type

**Option A: Desktop Application (Recommended for most users)**
```
Application type: Desktop app
Name: Gmail MCP Desktop
```

**Option B: Web Application (For remote/cloud deployments)**
```
Application type: Web application
Name: Gmail MCP Web
Authorized redirect URIs:
  - http://localhost:3000/oauth2callback
  - http://localhost:8080/oauth2callback
```

4. Click "CREATE"

#### Download Credentials

5. A popup will appear showing your Client ID and Client Secret
6. Click "DOWNLOAD JSON"
7. The file will download as something like: `client_secret_123456789.apps.googleusercontent.com.json`

#### Rename Credentials File

8. Rename the downloaded file to: `gcp-oauth.keys.json`

**Important**: The exact filename `gcp-oauth.keys.json` is required for the Gmail MCP server to recognize it.

---

## Gmail MCP Server Installation

### Method 1: Automatic Installation via Smithery (Recommended)

This method automatically handles configuration for Claude Code:

```bash
npx -y @smithery/cli install @gongrzhe/server-gmail-autoauth-mcp --client claude
```

This command will:
- Install the Gmail MCP server
- Configure Claude Code's MCP settings
- Set up global authentication directory

### Method 2: Manual Installation

#### Step 1: Set Up Global Credentials Directory

```bash
# Create the global Gmail MCP directory
mkdir -p ~/.gmail-mcp

# Move your credentials file there
mv ~/Downloads/gcp-oauth.keys.json ~/.gmail-mcp/
```

**Windows Users (Git Bash/PowerShell):**
```bash
# Create directory
mkdir -p $HOME/.gmail-mcp

# Move credentials
mv $HOME/Downloads/gcp-oauth.keys.json $HOME/.gmail-mcp/
```

**Windows Users (Command Prompt):**
```cmd
mkdir %USERPROFILE%\.gmail-mcp
move %USERPROFILE%\Downloads\gcp-oauth.keys.json %USERPROFILE%\.gmail-mcp\
```

#### Step 2: Authenticate with Gmail

Run the authentication command:

```bash
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

**What happens:**
1. The command searches for `gcp-oauth.keys.json` in:
   - `~/.gmail-mcp/` (recommended location)
   - Current directory (fallback)
2. Starts a local OAuth server on port 3000
3. Automatically opens your default browser
4. Prompts you to log in to Google and authorize the app
5. Stores credentials globally at `~/.gmail-mcp/credentials.json`

#### Step 3: Configure Claude Code

**Find Your Configuration File:**

Claude Code uses `~/.claude.json` for MCP server configuration.

**Location by OS:**
- **macOS/Linux**: `~/.claude.json`
- **Windows**: `C:\Users\[YourUsername]\.claude.json`

**Edit the Configuration:**

Open `~/.claude.json` in a text editor and add:

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

**If the file doesn't exist**, create it with the content above.

**If the file already has other MCP servers**, add the gmail section inside the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "other-server": {
      "command": "some-command",
      "args": ["arg1", "arg2"]
    },
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    }
  }
}
```

#### Step 4: Restart Claude Code

For the changes to take effect:
1. Completely quit Claude Code
2. Relaunch the application
3. The Gmail MCP server should now be available

---

## Authentication Flow

### Initial Authentication

When you run the `auth` command, here's the complete flow:

```
1. Command Execution
   └─> npx @gongrzhe/server-gmail-autoauth-mcp auth

2. OAuth Server Starts
   └─> Local server on http://localhost:3000

3. Browser Opens Automatically
   └─> Google OAuth consent page

4. User Actions Required
   ├─> Select Google account
   ├─> Review permissions
   └─> Click "Allow"

5. Callback Handling
   └─> Browser redirects to localhost:3000/oauth2callback

6. Token Exchange
   ├─> OAuth server receives authorization code
   ├─> Exchanges code for access + refresh tokens
   └─> Stores tokens in credentials.json

7. Storage Complete
   └─> Credentials saved to ~/.gmail-mcp/credentials.json

8. Success Message
   └─> "Authentication successful! Credentials saved."
```

### Token Lifecycle

**Access Tokens:**
- Valid for 1 hour
- Automatically refreshed by MCP server
- Used for Gmail API requests

**Refresh Tokens:**
- Valid until revoked
- Used to get new access tokens
- Stored in `credentials.json`

**Credential Files:**
```
~/.gmail-mcp/
├── gcp-oauth.keys.json      (OAuth client credentials)
└── credentials.json          (Access + refresh tokens)
```

### Re-Authentication

You need to re-authenticate when:
- Tokens are revoked
- Scopes are updated (need additional permissions)
- `credentials.json` is deleted
- You want to switch Google accounts

**To re-authenticate:**

```bash
# Delete existing credentials
rm ~/.gmail-mcp/credentials.json

# Run auth again
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

---

## Available Commands & Capabilities

### Email Sending & Drafting

#### send_email
Send emails with full formatting and attachments.

**Parameters:**
```json
{
  "to": ["recipient@example.com"],
  "cc": ["cc@example.com"],           // optional
  "bcc": ["bcc@example.com"],         // optional
  "subject": "Email Subject",
  "body": "Email body text or HTML",
  "attachments": ["/path/to/file.pdf"], // optional
  "html": true                         // optional, default: false
}
```

**Claude Code Example:**
```
"Send an email to john@example.com with subject 'Meeting Tomorrow' and body 'Let's meet at 10am. I've attached the agenda.' Attach /Users/me/agenda.pdf"
```

#### draft_email
Create email drafts without sending.

**Parameters:** Same as `send_email`

**Claude Code Example:**
```
"Create a draft email to team@company.com about the quarterly review. Subject: 'Q4 Review - Draft'. Don't send it yet."
```

### Reading & Searching Emails

#### read_email
Retrieve full email content by message ID.

**Parameters:**
```json
{
  "messageId": "182ab45cd67ef"
}
```

**Returns:**
- Subject, from, to, cc, bcc
- Full body (plain text and HTML)
- Attachment metadata (name, size, mimeType, attachmentId)
- Labels
- Timestamp

**Claude Code Example:**
```
"Read the email with ID 182ab45cd67ef and summarize it for me"
```

#### search_emails
Search emails using Gmail search syntax.

**Parameters:**
```json
{
  "query": "from:sender@example.com subject:urgent",
  "maxResults": 10                    // optional, default: 10
}
```

**Gmail Search Syntax Examples:**
```
from:john@example.com              → Emails from specific sender
to:me                              → Emails sent to you
subject:meeting                    → Emails with "meeting" in subject
has:attachment                     → Emails with attachments
is:unread                          → Unread emails
is:starred                         → Starred emails
after:2024/01/01                   → Emails after date
before:2024/12/31                  → Emails before date
filename:pdf                       → Emails with PDF attachments
larger:5M                          → Emails larger than 5MB
label:important                    → Emails with specific label
in:inbox                           → Emails in inbox
from:john@example.com subject:report → Combined search
```

**Claude Code Example:**
```
"Search for unread emails from sarah@example.com with attachments in the last 7 days"
```

### Attachment Management

#### download_attachment
Download email attachments to local filesystem.

**Parameters:**
```json
{
  "messageId": "182ab45cd67ef",
  "attachmentId": "ANGjdJ9fkTs-i3GCQo5o97f_itG...",
  "savePath": "/path/to/downloads"
}
```

**Claude Code Example:**
```
"Download all attachments from the email with ID 182ab45cd67ef to ~/Downloads"
```

### Label Management

#### list_email_labels
Get all available Gmail labels.

**Returns:** Array of labels with IDs, names, types

**Claude Code Example:**
```
"Show me all my Gmail labels"
```

#### create_label
Create a new Gmail label.

**Parameters:**
```json
{
  "name": "Projects/2025/Marketing"   // Supports nested labels with /
}
```

#### update_label
Modify existing label name.

**Parameters:**
```json
{
  "id": "Label_123",
  "name": "New Name"
}
```

#### delete_label
Remove a label (doesn't delete emails).

**Parameters:**
```json
{
  "id": "Label_123"
}
```

#### get_or_create_label
Get label by name or create if doesn't exist.

**Parameters:**
```json
{
  "name": "Important/Client Work"
}
```

#### modify_email
Add or remove labels from an email.

**Parameters:**
```json
{
  "messageId": "182ab45cd67ef",
  "addLabelIds": ["Label_123", "IMPORTANT"],
  "removeLabelIds": ["INBOX", "UNREAD"]
}
```

**System Labels:**
- `INBOX`, `SENT`, `DRAFT`, `TRASH`, `SPAM`
- `IMPORTANT`, `STARRED`, `UNREAD`
- `CATEGORY_PERSONAL`, `CATEGORY_SOCIAL`, `CATEGORY_PROMOTIONS`

**Claude Code Example:**
```
"Move the email with ID 182ab45cd67ef to the 'Projects' label and mark it as read"
```

### Batch Operations

#### batch_modify_emails
Apply label changes to multiple emails efficiently.

**Parameters:**
```json
{
  "messageIds": ["id1", "id2", "id3", "..."],
  "addLabelIds": ["IMPORTANT"],
  "removeLabelIds": ["INBOX"],
  "batchSize": 50                     // optional, default: 50
}
```

**Claude Code Example:**
```
"Archive all unread emails from newsletters@company.com and mark them as read"
```

#### batch_delete_emails
Delete multiple emails at once.

**Parameters:**
```json
{
  "messageIds": ["id1", "id2", "id3"],
  "batchSize": 50
}
```

**Note**: Uses soft delete (moves to trash), not permanent deletion.

### Filter Management

#### create_filter
Set up automated email rules.

**Parameters:**
```json
{
  "criteria": {
    "from": "notifications@service.com",
    "subject": "Daily Report"
  },
  "action": {
    "addLabelIds": ["Label_Reports"],
    "removeLabelIds": ["INBOX"]
  }
}
```

#### list_filters
Get all configured filters.

#### get_filter
Retrieve specific filter details.

**Parameters:**
```json
{
  "filterId": "ANe1Bmj..."
}
```

#### delete_filter
Remove an email filter.

**Parameters:**
```json
{
  "filterId": "ANe1Bmj..."
}
```

### Advanced Capabilities

**HTML Email Support:**
- Send rich HTML emails with inline styles
- Support for embedded images (base64 or CID)
- Multipart messages (plain text + HTML)

**International Characters:**
- Full Unicode support in subjects and bodies
- Proper encoding for all languages
- RTL (right-to-left) text support

**Attachment Types:**
- Documents (PDF, DOCX, XLSX, etc.)
- Images (JPEG, PNG, GIF, etc.)
- Archives (ZIP, TAR, etc.)
- Size limit: 25MB per email (Gmail limit)

---

## Security Best Practices

### OAuth Token Security

**1. Secure Storage**

```bash
# Set restrictive permissions on credentials
chmod 600 ~/.gmail-mcp/gcp-oauth.keys.json
chmod 600 ~/.gmail-mcp/credentials.json

# Prevent directory listing
chmod 700 ~/.gmail-mcp
```

**2. Never Commit Credentials to Version Control**

Add to `.gitignore`:
```gitignore
# Gmail MCP credentials
gcp-oauth.keys.json
credentials.json
.gmail-mcp/
```

**3. Use Minimal Scopes**

Only request the Gmail scopes you actually need:
- ✅ Use `gmail.readonly` + `gmail.send` + `gmail.compose` + `gmail.modify`
- ❌ Avoid `https://mail.google.com/` unless absolutely necessary

**4. Token Rotation**

Best practices:
- OAuth refresh tokens are long-lived but can be revoked
- Access tokens auto-refresh (1 hour expiration)
- Re-authenticate if suspicious activity detected

**To revoke access:**
1. Visit [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find "Gmail MCP for Claude" (or your app name)
3. Click "Remove Access"

**5. Environment-Specific Credentials**

For teams or multiple environments:

```bash
# Development
~/.gmail-mcp/credentials-dev.json

# Production
~/.gmail-mcp/credentials-prod.json
```

Configure with environment variables:
```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/path/to/specific/credentials.json"
      }
    }
  }
}
```

### MCP Server Security

**According to 2025 MCP Security Specification:**

1. **Token Validation**: MCP servers MUST NOT accept tokens not explicitly issued for them
2. **Resource Indicators**: Use RFC 8707 to specify intended audience
3. **Minimal Access**: Only grant necessary permissions
4. **Audit Logging**: Monitor OAuth usage for suspicious patterns

**Key Security Principle:**
> "MCP servers store OAuth tokens for multiple services. If stolen, attackers can impersonate users across Gmail, Drive, Calendar, etc. Proper token protection is essential."

### Production Deployment Security

**For remote/cloud MCP servers:**

1. **Use HTTPS Only**
   - Configure TLS certificates
   - Force HTTPS redirects

2. **Restrict OAuth Callbacks**
   ```
   Authorized redirect URIs:
   https://gmail.yourdomain.com/oauth2callback
   ```

3. **Implement Rate Limiting**
   - Prevent token theft via brute force
   - Limit API calls per hour

4. **Use Secret Manager**
   - Google Cloud Secret Manager
   - AWS Secrets Manager
   - HashiCorp Vault

5. **Regular Security Scans**
   - Scan for hardcoded secrets
   - Check environment variables
   - Audit token access patterns

---

## Troubleshooting

### Common Installation Issues

#### Issue: "OAuth keys not found"

**Error Message:**
```
Error: Could not find gcp-oauth.keys.json
```

**Solutions:**
1. Verify file location:
   ```bash
   ls ~/.gmail-mcp/gcp-oauth.keys.json
   ```

2. Check filename (must be exact):
   ```bash
   mv client_secret_*.json ~/.gmail-mcp/gcp-oauth.keys.json
   ```

3. Check file permissions:
   ```bash
   chmod 644 ~/.gmail-mcp/gcp-oauth.keys.json
   ```

#### Issue: "Port 3000 already in use"

**Error Message:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solutions:**
1. Find and kill the process:
   ```bash
   # macOS/Linux
   lsof -ti:3000 | xargs kill -9

   # Windows (PowerShell)
   Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
   ```

2. Or use a different port:
   ```bash
   npx @gongrzhe/server-gmail-autoauth-mcp auth --port 8080
   ```
   Update redirect URIs in Google Cloud to match.

### Authentication Issues

#### Issue: "invalid_grant" Error

**Causes:**
- Refresh token expired
- Token was revoked
- System clock is incorrect

**Solutions:**
1. Delete and re-authenticate:
   ```bash
   rm ~/.gmail-mcp/credentials.json
   npx @gongrzhe/server-gmail-autoauth-mcp auth
   ```

2. Check system time:
   ```bash
   date
   ```
   Sync if incorrect.

3. Verify OAuth consent screen is still active in Google Cloud Console

#### Issue: "redirect_uri_mismatch"

**Error Message:**
```
Error 400: redirect_uri_mismatch
```

**Solutions:**
1. Check redirect URIs in Google Cloud Console match exactly:
   - Desktop app: No redirect URI needed
   - Web app: `http://localhost:3000/oauth2callback`

2. Ensure protocol matches (http vs https)

3. For cloud deployments, verify DNS is resolving correctly

#### Issue: "insufficient_permissions" or "access_denied"

**Causes:**
- Missing Gmail API scopes
- User didn't grant all permissions

**Solutions:**
1. Verify scopes in Google Cloud OAuth consent screen

2. Force re-authentication with new scopes:
   ```bash
   rm ~/.gmail-mcp/credentials.json
   npx @gongrzhe/server-gmail-autoauth-mcp auth
   ```

3. Ensure user grants all requested permissions in OAuth flow

### Runtime Issues

#### Issue: MCP server not appearing in Claude Code

**Diagnostics:**
1. Check Claude Code configuration:
   ```bash
   cat ~/.claude.json
   ```

2. Verify JSON syntax (use a validator):
   - No trailing commas
   - Proper quotes
   - Valid structure

3. Restart Claude Code completely:
   - Quit application (not just close window)
   - Relaunch

4. Check Claude Code logs (if available)

#### Issue: "Failed to send email" errors

**Possible Causes:**
- Attachment too large (>25MB)
- Invalid email addresses
- Gmail API quota exceeded
- Network connectivity issues

**Solutions:**
1. Check attachment size:
   ```bash
   ls -lh /path/to/attachment
   ```

2. Validate email addresses

3. Check Gmail API quotas in Google Cloud Console:
   - APIs & Services → Dashboard → Gmail API

4. Test network connectivity:
   ```bash
   ping gmail.googleapis.com
   ```

#### Issue: "Rate limit exceeded"

**Gmail API Quotas (Free Tier):**
- 1 billion quota units per day
- Send email: 100 units per request
- Read email: 5 units per request
- Search: 5 units per request

**Solutions:**
1. Implement exponential backoff in requests

2. Request quota increase in Google Cloud Console if needed

3. Use batch operations to reduce API calls

### Token Issues

#### Issue: Token file corrupted

**Symptoms:**
- Random authentication failures
- JSON parse errors

**Solution:**
```bash
# Delete corrupted token
rm ~/.gmail-mcp/credentials.json

# Re-authenticate
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

#### Issue: Multiple accounts - wrong account authenticated

**Solution:**
1. Clear browser cookies for accounts.google.com

2. Re-run authentication:
   ```bash
   rm ~/.gmail-mcp/credentials.json
   npx @gongrzhe/server-gmail-autoauth-mcp auth
   ```

3. In browser OAuth flow, click "Use another account"

4. Select correct Google account

### Windows-Specific Issues

#### Issue: npx command not found

**Solutions:**
1. Verify Node.js installation:
   ```cmd
   node --version
   npm --version
   ```

2. Add npm to PATH if needed

3. Restart terminal after installing Node.js

#### Issue: Path issues with Windows

**Solution:** Use forward slashes or escape backslashes:
```json
// Good
"GMAIL_CREDENTIALS_PATH": "C:/Users/username/.gmail-mcp/credentials.json"

// Also good
"GMAIL_CREDENTIALS_PATH": "C:\\Users\\username\\.gmail-mcp\\credentials.json"

// Bad
"GMAIL_CREDENTIALS_PATH": "C:\Users\username\.gmail-mcp\credentials.json"
```

---

## Advanced Configuration

### Multiple Gmail Accounts

For managing multiple Gmail accounts with different MCP server instances:

#### Method 1: Multiple MCP Server Entries

```json
{
  "mcpServers": {
    "gmail-personal": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_OAUTH_PATH": "/Users/you/.gmail-mcp/personal-oauth.json",
        "GMAIL_CREDENTIALS_PATH": "/Users/you/.gmail-mcp/personal-credentials.json"
      }
    },
    "gmail-work": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_OAUTH_PATH": "/Users/you/.gmail-mcp/work-oauth.json",
        "GMAIL_CREDENTIALS_PATH": "/Users/you/.gmail-mcp/work-credentials.json"
      }
    }
  }
}
```

#### Method 2: Using mcp-gsuite (Recommended for Multiple Accounts)

Install and configure `mcp-gsuite`:

```bash
# Install
claude mcp add-json "mcp-gsuite" '{"command":"uvx","args":["mcp-gsuite"]}'

# Create accounts configuration
cat > ~/.accounts.json <<EOF
{
  "accounts": [
    {
      "email": "personal@gmail.com",
      "name": "Personal"
    },
    {
      "email": "work@company.com",
      "name": "Work"
    }
  ]
}
EOF

# Authenticate each account
uv run mcp-gsuite --accounts-file ~/.accounts.json
```

**In Claude Code:**
```
"List emails from my personal Gmail account"
"Send an email from my work account to team@company.com"
```

### Custom Credential Paths

Override default paths with environment variables:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_OAUTH_PATH": "/custom/path/to/oauth-keys.json",
        "GMAIL_CREDENTIALS_PATH": "/custom/path/to/credentials.json"
      }
    }
  }
}
```

### Project-Scoped Configuration

For team projects, use `.mcp.json` in project root:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_OAUTH_PATH": "${PROJECT_ROOT}/.credentials/oauth.json",
        "GMAIL_CREDENTIALS_PATH": "${PROJECT_ROOT}/.credentials/tokens.json"
      }
    }
  }
}
```

**Add to .gitignore:**
```gitignore
.credentials/
```

### Docker Deployment

For containerized environments:

**Dockerfile:**
```dockerfile
FROM node:20-slim

WORKDIR /app

RUN npm install -g @gongrzhe/server-gmail-autoauth-mcp

COPY gcp-oauth.keys.json /app/

EXPOSE 3000

CMD ["npx", "@gongrzhe/server-gmail-autoauth-mcp"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  gmail-mcp:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./credentials:/gmail-server
    environment:
      - GMAIL_OAUTH_PATH=/app/gcp-oauth.keys.json
      - GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json
```

**Authentication:**
```bash
docker run -i --rm \
  -v $(pwd)/gcp-oauth.keys.json:/gcp-oauth.keys.json \
  -v gmail-credentials:/gmail-server \
  -e GMAIL_OAUTH_PATH=/gcp-oauth.keys.json \
  -e GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json \
  -p 3000:3000 \
  gmail-mcp auth
```

### Cloud Server Setup (n8n, Vercel, etc.)

For remote deployments with custom domains:

#### 1. Set Up Reverse Proxy

**nginx example:**
```nginx
server {
    listen 443 ssl;
    server_name gmail.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. Configure DNS

Create A record:
```
gmail.yourdomain.com → [Your Server IP]
```

#### 3. Update Google Cloud Redirect URIs

```
https://gmail.yourdomain.com/oauth2callback
```

#### 4. Authenticate

```bash
npx @gongrzhe/server-gmail-autoauth-mcp auth https://gmail.yourdomain.com/oauth2callback
```

### HTTP Mode (Persistent Server)

For avoiding repeated OAuth popups, run in HTTP mode:

```bash
npx @gongrzhe/server-gmail-autoauth-mcp --http
```

This keeps the server running as a persistent process.

**Configuration for Claude Code:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp",
        "--http"
      ]
    }
  }
}
```

### Custom Batch Sizes

For processing large volumes of emails:

```bash
# Set custom batch size for operations
npx @gongrzhe/server-gmail-autoauth-mcp --batch-size 100
```

**In Claude Code requests:**
```json
{
  "messageIds": ["id1", "id2", "..."],
  "batchSize": 100
}
```

### Logging and Debugging

Enable verbose logging:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp",
        "--verbose"
      ]
    }
  }
}
```

Or set environment variable:
```bash
export DEBUG=gmail-mcp:*
npx @gongrzhe/server-gmail-autoauth-mcp
```

---

## Quick Reference

### Essential Commands

```bash
# Install via Smithery (automatic)
npx -y @smithery/cli install @gongrzhe/server-gmail-autoauth-mcp --client claude

# Manual authentication
npx @gongrzhe/server-gmail-autoauth-mcp auth

# Re-authenticate
rm ~/.gmail-mcp/credentials.json && npx @gongrzhe/server-gmail-autoauth-mcp auth

# Check installation
ls -la ~/.gmail-mcp/

# Test configuration
cat ~/.claude.json
```

### File Locations

```
~/.gmail-mcp/
├── gcp-oauth.keys.json         OAuth client credentials
└── credentials.json             Access/refresh tokens

~/.claude.json                   Claude Code MCP config
```

### Required Google Cloud APIs

- Gmail API (required)

### Required OAuth Scopes

```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.modify
```

### Common Claude Code Requests

```
"Send an email to john@example.com with subject 'Test'"
"Search for unread emails from sarah@example.com"
"Create a draft email to team@company.com about the meeting"
"Download all attachments from the last email from boss@company.com"
"Archive all emails in the 'Newsletters' label"
"Create a label called 'Projects/2025/Q1'"
"Show me all my Gmail labels"
```

---

## Additional Resources

### Official Documentation
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Google APIs](https://developers.google.com/identity/protocols/oauth2)
- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)

### Gmail MCP Server Repositories
- [@gongrzhe/server-gmail-autoauth-mcp](https://github.com/GongRzhe/Gmail-MCP-Server) (Recommended)
- [vinayak-mehta/gmail-mcp](https://github.com/vinayak-mehta/gmail-mcp)
- [mcp-gsuite](https://github.com/markuspfundstein/mcp-gsuite) (Multiple accounts)
- [cafferychen777/gmail-mcp](https://github.com/cafferychen777/gmail-mcp) (Chrome extension, no OAuth)

### Community Resources
- [MCP Servers Directory](https://mcpservers.org/)
- [LobeHub MCP Servers](https://lobehub.com/mcp)
- [MCP Server Finder](https://www.mcpserverfinder.com/)

### Support
- GitHub Issues: Report bugs and request features on respective repositories
- Discord: Anthropic AI Discord (for Claude Code support)
- Stack Overflow: Tag questions with `model-context-protocol` and `gmail-api`

---

## Changelog

**2025-11-10**: Initial comprehensive guide
- Covered full Google Cloud Console setup
- Detailed OAuth consent screen configuration
- Complete authentication flow
- All available commands documented
- Security best practices from 2025 MCP spec
- Advanced multi-account configuration
- Extensive troubleshooting section

---

## License & Disclaimer

This guide is provided for educational purposes. Always follow Google's Terms of Service and API usage policies. OAuth credentials should be kept secure and never shared publicly.

The Gmail MCP servers mentioned are third-party tools. Review their source code and security practices before use in production environments.

---

**Guide Version**: 1.0
**Last Updated**: 2025-11-10
**Completeness**: 95% (minor gaps in n8n-specific deployment)
**Research Sources**: 11 parallel searches across official docs, GitHub repos, and community resources