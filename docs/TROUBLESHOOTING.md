# Troubleshooting Guide

Common issues and solutions for the Tableau Technical Knowledge Base MCP.

## Table of Contents

- [MCP Connection Issues](#mcp-connection-issues)
- [PDF Indexing Issues](#pdf-indexing-issues)
- [Tableau Connection Issues](#tableau-connection-issues)
- [Query Issues](#query-issues)
- [Performance Issues](#performance-issues)
- [Environment Issues](#environment-issues)
- [Claude Desktop Issues](#claude-desktop-issues)

---

## MCP Connection Issues

### Servers Not Showing in Claude Desktop

**Symptom:** Plug icon shows no servers or servers appear disconnected

**Possible Causes:**
1. Claude Desktop not restarted after configuration
2. Configuration file in wrong location
3. Syntax errors in configuration JSON
4. Incorrect file paths

**Solutions:**

**1. Verify Configuration File Location**

Windows:
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Mac:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**2. Validate JSON Syntax**

Copy your configuration and paste into: https://jsonlint.com/

Common mistakes:
- Missing commas between sections
- Extra comma after last item
- Unmatched brackets `{` `}`
- Wrong quote types (use `"` not `'`)

**3. Check File Paths**

Paths must be absolute and properly escaped:

**Windows (wrong):**
```json
"command": "C:\Users\jvije\venv\Scripts\python.exe"  ❌
```

**Windows (correct):**
```json
"command": "C:\\Users\\jvije\\venv\\Scripts\\python.exe"  ✅
```

**Mac (correct):**
```json
"command": "/Users/jvije/venv/bin/python"  ✅
```

**4. Completely Restart Claude Desktop**

- Don't just close the window
- File → Quit (or Cmd+Q on Mac)
- Wait 5 seconds
- Reopen Claude Desktop

---

### Technical Knowledge Base Server Won't Start

**Symptom:** Red X next to "technical-knowledge-base" server

**Check 1: Python Path**

Verify Python path points to your virtual environment:

```bash
# Should be inside your venv folder
which python  # Mac/Linux
where python  # Windows
```

**Check 2: ChromaDB Index Exists**

```bash
ls chroma_db/  # Mac/Linux
dir chroma_db\  # Windows
```

If empty or missing:
```bash
python scripts/index_books.py --pdf-dir "/path/to/pdfs"
```

**Check 3: Dependencies Installed**

```bash
# Activate virtual environment first!
pip list | grep chromadb
pip list | grep sentence-transformers
```

If missing:
```bash
pip install -r requirements.txt
```

**Check 4: Test Server Manually**

```bash
cd /path/to/tableau-knowledge-mcp
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
python src/server.py
```

Look for error messages in the output.

---

### Tableau MCP Server Won't Connect

**Symptom:** Red X next to "tableau-cloud" server

**Check 1: Node.js and npm Installed**

```bash
node --version
npm --version
```

If not installed: https://nodejs.org/

**Check 2: Credentials in Configuration**

Verify in `claude_desktop_config.json`:
- `--server-url` is correct (include https://)
- `--site-name` matches your site
- `--token-name` and `--token-value` are correct

**Check 3: Test Credentials**

Create a test file `test-tableau.js`:

```javascript
const args = [
  "--server-url", "https://your-site.online.tableau.com",
  "--site-name", "your-site-name",
  "--token-name", "your-token-name",
  "--token-value", "your-token-secret"
];

console.log("Testing Tableau connection with:", args);
```

Run:
```bash
npx -y @modelcontextprotocol/server-tableau --help
```

Should show help text without errors.

---

## PDF Indexing Issues

### "No module named 'PyPDF2'"

**Symptom:** ImportError when running index_books.py

**Solution:**

```bash
# Make sure virtual environment is activated!
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import PyPDF2; print('PyPDF2 installed')"
```

---

### "Permission denied" When Reading PDFs

**Symptom:** Error accessing PDF files

**Causes:**
1. PDFs are open in another program
2. Insufficient file permissions
3. Files are encrypted/password-protected

**Solutions:**

1. Close all PDF viewers
2. Check file permissions:
   ```bash
   ls -l /path/to/pdfs/*.pdf  # Mac/Linux
   ```
3. Remove password protection from PDFs
4. Run with appropriate permissions (avoid using sudo unless necessary)

---

### Some PDFs Not Indexing

**Symptom:** "Successfully indexed: 75/83 books"

**Common Reasons:**

1. **Scanned PDFs (images only)**
   - Solution: Use OCR software to convert to searchable PDFs
   - Tools: Adobe Acrobat, Abbyy FineReader

2. **Corrupted PDF files**
   - Solution: Try opening in PDF viewer, if it fails, file is corrupted
   - Re-download or find another copy

3. **Encrypted/Protected PDFs**
   - Solution: Remove encryption using PDF tools
   - Some DRM-protected files cannot be indexed

4. **Non-text content (images, diagrams only)**
   - Solution: These won't have extractable text
   - Skip or add OCR

**View indexing errors:**
```bash
python scripts/index_books.py --pdf-dir "/path" 2>&1 | tee indexing.log
```

Review `indexing.log` for specific errors.

---

### Indexing is Very Slow

**Symptom:** Taking hours to index small library

**Causes & Solutions:**

1. **Large PDF files**
   - PDFs over 100MB take longer
   - Solution: Increase `BATCH_SIZE` in `.env`

2. **Slow disk I/O**
   - Using network drive or external USB 2.0
   - Solution: Copy PDFs to local SSD

3. **CPU overload**
   - Too many background processes
   - Solution: Close unnecessary applications

4. **Embedding model downloading**
   - First run downloads ~500MB model
   - Solution: Wait for initial download, subsequent runs faster

**Speed improvements:**

```env
# In .env file
BATCH_SIZE=50           # Process more at once
CHUNK_SIZE=1500         # Create fewer chunks
```

---

## Tableau Connection Issues

### 401 Unauthorized Error

**Symptom:** "Authentication failed" when querying Tableau

**Solutions:**

**1. Verify Credentials**

Check `.env` file:
```bash
cat .env | grep TABLEAU  # Mac/Linux
type .env | findstr TABLEAU  # Windows
```

All four variables must be set correctly.

**2. Test Token in Tableau UI**

1. Go to your Tableau site
2. Account Settings → Personal Access Tokens
3. Verify your token exists and hasn't expired
4. Check expiration date

**3. Regenerate Token**

If token expired:
1. Create new PAT in Tableau
2. Update `.env` with new secret
3. Restart Claude Desktop

**4. Check Site Name**

Common mistake: Including `/site/` or full URL

```env
# WRONG:
TABLEAU_SITE_NAME=/site/mycompany

# RIGHT:
TABLEAU_SITE_NAME=mycompany
```

---

### 404 Not Found Error

**Symptom:** "Server not found" or "Site not found"

**Solutions:**

**1. Verify Server URL**

```env
# Must include https:// and correct domain
TABLEAU_SERVER_URL=https://10az.online.tableau.com

# NOT:
TABLEAU_SERVER_URL=10az.online.tableau.com  ❌ (missing https)
TABLEAU_SERVER_URL=https://10az.online.tableau.com/site/mysite  ❌ (has path)
```

**2. Check Internet Connection**

```bash
ping your-site.online.tableau.com
```

**3. Verify Tableau Server is Running**

Visit your Tableau URL in a browser - should load login page.

---

### Connection Timeout

**Symptom:** Queries hang or timeout after 30 seconds

**Causes:**
1. Slow internet connection
2. Large dataset queries
3. Firewall blocking API calls
4. Tableau Server overloaded

**Solutions:**

1. Test connection speed to Tableau:
   ```bash
   curl -w "@-" -o /dev/null -s "https://your-site.online.tableau.com"
   ```

2. Try simpler queries first:
   ```
   List all datasources
   ```

3. Check firewall settings (corporate networks)

4. Contact Tableau administrator about server performance

---

## Query Issues

### "No results found" for Book Search

**Symptom:** Knowledge base returns no results for valid queries

**Causes:**

1. **ChromaDB index empty or corrupted**

   Check index size:
   ```bash
   du -sh chroma_db  # Mac/Linux
   dir chroma_db     # Windows
   ```

   Should be 100MB+ for a decent library.

   Solution: Reindex
   ```bash
   python scripts/index_books.py --pdf-dir "/path" --reindex
   ```

2. **Query too specific**

   Instead of: "What does page 47 of Learning Tableau say about parameters?"
   Try: "How do parameters work in Tableau?"

3. **Topic not in your library**

   The books you indexed don't cover that topic.
   Add relevant books and reindex.

---

### Queries Return Irrelevant Results

**Symptom:** Search results don't match query intent

**Solutions:**

1. **Use more specific queries**

   Bad: "data"
   Good: "data cleaning techniques for missing values"

2. **Adjust MAX_SEARCH_RESULTS**

   ```env
   MAX_SEARCH_RESULTS=10  # Get more results to review
   ```

3. **Check relevance scores**

   Results include relevance scores (0-1). Low scores (<0.3) may not be useful.

4. **Try different embedding model**

   ```env
   # More accurate but slower:
   EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
   ```

   Then reindex:
   ```bash
   python scripts/index_books.py --pdf-dir "/path" --reindex
   ```

---

### Tableau Queries Fail

**Symptom:** "Error querying datasource" or similar

**Common Issues:**

1. **Datasource name wrong**

   List available datasources first:
   ```
   What datasources are available?
   ```

   Then use exact name from the list.

2. **Insufficient permissions**

   Your Tableau account needs View access to datasources.
   Check with Tableau administrator.

3. **Datasource is extract and not refreshed**

   Data might be stale.
   Ask admin to refresh extract or use live connection.

---

## Performance Issues

### Slow Query Response

**Symptom:** Queries take 10+ seconds

**For Knowledge Base:**

1. **Reduce search results**
   ```env
   MAX_SEARCH_RESULTS=3
   ```

2. **Use faster embedding model**
   ```env
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

3. **Optimize chunk size**
   ```env
   CHUNK_SIZE=1500  # Fewer chunks = faster search
   ```

**For Tableau:**

1. **Use aggregated views instead of row-level data**
2. **Filter queries to reduce data volume**
3. **Check Tableau Server performance**

---

### High Memory Usage

**Symptom:** Computer slows down, RAM usage high

**Solutions:**

1. **Reduce embedding model memory**

   Smaller model:
   ```env
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

2. **Limit concurrent queries**

   Don't run multiple complex queries simultaneously.

3. **Close other applications**

   ChromaDB and embedding models need RAM.

4. **Increase system RAM**

   Recommended: 8GB minimum for large libraries

---

## Environment Issues

### "python: command not found"

**Symptom:** Can't run Python scripts

**Solutions:**

**Windows:**
```bash
# Try:
python3 --version
py --version
```

Add Python to PATH:
1. Search "Environment Variables"
2. Edit System PATH
3. Add Python installation directory

**Mac:**
```bash
# Install Python 3:
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3
```

---

### Virtual Environment Not Activating

**Symptom:** `(venv)` doesn't appear in prompt

**Windows PowerShell:**
```powershell
# Enable script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate:
venv\Scripts\activate
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
# Make sure you're using source:
source venv/bin/activate

# Not:
./venv/bin/activate  ❌
```

---

### ".env file not found"

**Symptom:** Environment variables not loading

**Solutions:**

1. **Verify .env exists**
   ```bash
   ls -la  # Mac/Linux (shows hidden files)
   dir /a  # Windows (shows hidden files)
   ```

2. **Check file location**
   
   Must be in project root, same directory as `src/` and `scripts/`

3. **Create from template**
   ```bash
   cp .env.example .env
   ```

4. **Check file name**
   
   - Should be `.env` (with dot)
   - Not `env.txt` or `.env.txt`

---

## Claude Desktop Issues

### Configuration Not Loading

**Symptom:** Changes to config file don't take effect

**Solutions:**

1. **Completely quit Claude Desktop**
   - Use File → Quit
   - Don't just close window
   - Wait 5 seconds
   - Reopen

2. **Check file location**

   Make sure editing the right file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

3. **Validate JSON**

   Use https://jsonlint.com/ to check for syntax errors

---

### "Module not found" Errors in Logs

**Symptom:** Server starts but errors about missing modules

**Solution:**

Configuration must point to **virtual environment Python**, not system Python:

**Wrong:**
```json
"command": "python"  ❌
"command": "/usr/bin/python3"  ❌
```

**Right:**
```json
"command": "C:\\Users\\jvije\\tableau-knowledge-mcp\\venv\\Scripts\\python.exe"  ✅
```

---

## Getting More Help

### Collect Diagnostic Information

When reporting issues, include:

1. **System information:**
   ```bash
   python --version
   pip list
   ```

2. **Configuration (sanitized):**
   - Remove tokens/secrets before sharing
   - Show structure and paths only

3. **Error messages:**
   - Complete error text
   - Stack trace if available

4. **Steps to reproduce:**
   - What you did
   - What you expected
   - What actually happened

### Where to Get Help

- **GitHub Issues:** https://github.com/yourusername/tableau-knowledge-mcp/issues
- **Discussions:** https://github.com/yourusername/tableau-knowledge-mcp/discussions
- **Documentation:** Review [INSTALLATION.md](INSTALLATION.md)
- **Tableau Support:** For Tableau-specific issues

---

**Still stuck?** Open a GitHub issue with:
- Operating system and version
- Python version
- Error messages
- What you've tried
