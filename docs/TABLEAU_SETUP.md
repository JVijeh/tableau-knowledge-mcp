# Tableau Personal Access Token Setup

Guide for creating and managing Tableau Personal Access Tokens (PATs) for the MCP server.

## What is a Personal Access Token?

A Personal Access Token (PAT) is a secure way to authenticate with Tableau's REST API without using your password. PATs provide:

- **Security:** No password exposure in configuration files
- **Control:** Can be revoked without changing your password
- **Scope:** Limited to API access (cannot login to Tableau UI)
- **Expiration:** Automatically expire after a set time

---

## Prerequisites

- Tableau Cloud or Tableau Server account
- **Creator license** or higher (Explorer cannot create PATs)
- Admin permissions on your site (or permission from your admin)

---

## Creating a Personal Access Token

### Step 1: Sign In to Tableau

1. Go to your Tableau site
2. Sign in with your credentials
3. Example URL: `https://your-company.online.tableau.com`

---

### Step 2: Access Your Account Settings

**Tableau Cloud:**
1. Click your profile picture (top-right corner)
2. Select **"My Account Settings"**

**Tableau Server:**
1. Click your username (top-right corner)
2. Select **"Account Settings"** or **"My Account Settings"**

---

### Step 3: Navigate to Personal Access Tokens

1. In Account Settings, find the **"Personal Access Tokens"** section
2. This is usually near the bottom of the settings page

**If you don't see this section:**
- Your account type doesn't support PATs (need Creator or higher)
- Your administrator has disabled PAT creation
- Contact your Tableau administrator

---

### Step 4: Create New Token

1. Click **"Create New Token"** or **"+ New Personal Access Token"**

2. Fill out the token details:
   - **Token Name:** `tableau-knowledge-mcp` (or descriptive name)
   - **Expiration:** Choose based on your needs (see recommendations below)

3. Click **"Create"**

---

### Step 5: Save Your Token Credentials

**Important:** You'll see two pieces of information:

```
Token Name: tableau-knowledge-mcp
Token Secret: AbCdEf123456789XyZaBcDeF123456789XyZ
```

**CRITICAL:** 
- The **Token Secret** is shown ONLY ONCE
- You cannot view it again
- Copy it immediately
- Store it securely

**Recommended:**
1. Copy **Token Name** to a secure note
2. Copy **Token Secret** to the same secure note
3. Click "Copy" button for the secret (don't type it manually)
4. Store in password manager or secure location

---

### Step 6: Add to Your `.env` File

Open your `.env` file and update these variables:

```env
TABLEAU_SERVER_URL=https://your-site.online.tableau.com
TABLEAU_SITE_NAME=your-site-name
TABLEAU_PAT_NAME=tableau-knowledge-mcp
TABLEAU_PAT_SECRET=AbCdEf123456789XyZaBcDeF123456789XyZ
```

**Finding your Site Name:**
- It's in your Tableau URL after `/site/`
- Example: `https://10az.online.tableau.com/#/site/mycompany/home`
- Site name is: `mycompany`
- If no `/site/` in URL, your site name might be blank or "Default"

**Server URL:**
- Include `https://`
- Do NOT include `/site/sitename` or any path
- Just the base domain

---

## Token Expiration Recommendations

### Development/Testing
**Expiration:** 30-90 days
- Good for initial setup
- Easy to regenerate if needed
- Lower security risk during development

### Production Use
**Expiration:** 90-365 days
- Reduces maintenance
- Plan rotation schedule
- Set calendar reminder before expiration

### High-Security Environments
**Expiration:** 30-60 days
- Rotate frequently
- Follow security policies
- Use credential management system

**Best Practice:**
- Set calendar reminder 1 week before expiration
- Create new token before old one expires
- Update `.env` file with new token
- Test to ensure it works
- Delete old token

---

## Token Permissions

Personal Access Tokens inherit your user permissions. For this project, you need:

**Minimum Required:**
- **View workbooks** - To access datasources
- **View datasources** - To query data
- **View site** - To list available content

**Recommended:**
- Same permissions as your user account
- Typically "Creator" or "Explorer (can publish)" role

**Not Needed:**
- Administrative permissions
- User management access
- Content deletion rights

---

## Managing Multiple Tokens

You can create multiple PATs for different purposes:

**Example organization:**
```
Token Name                  Purpose                 Expiration
------------------------------------------------------------------
tableau-mcp-dev            Development/testing     30 days
tableau-mcp-production     Production use          90 days
tableau-api-scripts        Automated scripts       60 days
```

**Benefits:**
- Isolate access by purpose
- Revoke specific tokens without affecting others
- Track usage by token name in Tableau logs

---

## Security Best Practices

### DO:
- ✅ Use descriptive token names
- ✅ Set expiration dates
- ✅ Store tokens in `.env` file (not in code)
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate tokens regularly
- ✅ Revoke unused tokens
- ✅ Use different tokens for dev/prod
- ✅ Document which token is used where

### DON'T:
- ❌ Share tokens between team members
- ❌ Commit tokens to Git
- ❌ Email tokens in plain text
- ❌ Store tokens in cloud sync folders (Dropbox, OneDrive)
- ❌ Set tokens to never expire
- ❌ Reuse tokens across multiple applications
- ❌ Store tokens in screenshots or documentation

---

## Revoking Tokens

**When to revoke:**
- Token is no longer needed
- Token may have been compromised
- Employee leaving or changing roles
- Switching to new token
- Security audit requirement

**How to revoke:**
1. Go to Account Settings
2. Find Personal Access Tokens section
3. Locate the token in the list
4. Click **"Revoke"** or trash icon
5. Confirm revocation

**Effect:**
- Token stops working immediately
- Any application using that token will get authentication errors
- Update applications with new token before revoking old one

---

## Testing Your Token

**Test connection before full setup:**

```bash
# Simple test using curl (Mac/Linux)
curl -X POST "https://your-site.online.tableau.com/api/3.18/auth/signin" \
-H "Content-Type: application/json" \
-d '{
  "credentials": {
    "personalAccessTokenName": "your-token-name",
    "personalAccessTokenSecret": "your-token-secret",
    "site": {
      "contentUrl": "your-site-name"
    }
  }
}'
```

**Expected response:**
- Status code: 200 (success)
- JSON response with authentication token
- If you get 401: Check token name/secret
- If you get 404: Check server URL or site name

---

## Troubleshooting

### "Personal Access Tokens" Section Not Visible

**Possible causes:**
1. **Account type:** You need Creator license or higher
2. **Server version:** Tableau Server older than 2019.4
3. **Admin disabled:** PAT creation disabled by administrator

**Solution:**
- Check your license type in Account Settings
- Contact Tableau administrator
- Request PAT creation permission

### Token Not Working (401 Unauthorized)

**Possible causes:**
1. **Incorrect token secret:** Double-check for typos
2. **Token expired:** Check expiration date
3. **Token revoked:** Verify token still exists in Tableau
4. **Wrong site name:** Verify site name in URL

**Solution:**
- Regenerate token and update `.env`
- Check token list in Tableau
- Verify all credentials match exactly

### Token Works in Testing But Not in MCP

**Possible causes:**
1. **Environment variable not loaded:** `.env` file not in correct location
2. **Cached credentials:** Old credentials cached somewhere
3. **Path issues:** Claude Desktop can't access `.env` file

**Solution:**
- Verify `.env` file location
- Restart Claude Desktop completely
- Check Claude Desktop configuration file has correct credentials

### Site Name Issues

**Common mistakes:**

```env
# WRONG - includes /site/ path:
TABLEAU_SITE_NAME=/site/mycompany

# WRONG - includes full URL:
TABLEAU_SITE_NAME=https://10az.online.tableau.com/#/site/mycompany

# RIGHT - just the site name:
TABLEAU_SITE_NAME=mycompany
```

**Finding your site name:**
Look at your Tableau URL when logged in:
- `https://10az.online.tableau.com/#/site/engineering/home`
- Site name is: `engineering`

If your URL has no `/site/` segment:
- You're on the default site
- Try: empty string `""` or `"Default"`

---

## Alternative: Using Environment Variables

Instead of storing credentials in `.env`, you can use system environment variables:

**Windows (PowerShell):**
```powershell
$env:TABLEAU_PAT_SECRET = "your-token-secret"
```

**Mac/Linux (Bash):**
```bash
export TABLEAU_PAT_SECRET="your-token-secret"
```

**Advantage:**
- Not stored in a file
- More secure for shared environments

**Disadvantage:**
- Must set every session
- Less convenient for development

---

## Token Lifecycle Management

### 1. Creation
- Create with descriptive name
- Set appropriate expiration
- Document purpose and expiration date

### 2. Storage
- Add to `.env` file
- Store backup in password manager
- Never commit to version control

### 3. Usage
- Configure in Claude Desktop
- Test regularly
- Monitor for errors

### 4. Rotation
- Create new token before expiration
- Update configuration
- Test new token
- Revoke old token

### 5. Revocation
- Remove from `.env`
- Revoke in Tableau
- Update password manager records

---

## Getting Help

**Tableau Documentation:**
- [Personal Access Tokens Overview](https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm)
- [REST API Authentication](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_auth.htm)

**Project Support:**
- [GitHub Issues](https://github.com/yourusername/tableau-knowledge-mcp/issues)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**You're now ready to securely authenticate with Tableau!**
