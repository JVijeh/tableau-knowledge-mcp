# Troubleshooting Guide

Common issues and solutions for the Tableau Technical Knowledge Base MCP.

## Table of Contents

- [Installation Issues](#installation-issues)
- [MCP Connection Issues](#mcp-connection-issues)
- [PDF Indexing Issues](#pdf-indexing-issues)
- [Tableau Connection Issues](#tableau-connection-issues)
- [Query Issues](#query-issues)
- [Performance Issues](#performance-issues)
- [Environment Issues](#environment-issues)
- [Claude Desktop Issues](#claude-desktop-issues)

---

## Installation Issues

Problems that prevent the project from installing successfully. These issues occur during `pip install` or `setup.bat` execution, before you can run the indexer or start the MCP server.

### `metadata-generation-failed` During pip install (Missing C++ Build Tools)

**Symptom:**

```
ERROR: Failed building wheel for chromadb
ERROR: metadata-generation-failed
WARNING: Failed to activate VS environment: Could not find
C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
```

May appear when installing ChromaDB, `hnswlib`, `onnxruntime`, `tokenizers`, or other packages with native C++ dependencies.

**Cause:**

Windows is missing the Microsoft Visual C++ Build Tools. Several Python packages in this project rely on native C++ extensions that must be compiled from source if no pre-built wheel is available for your Python version. Without a C++ compiler installed, the build step fails.

**Solution:**

1. Download Microsoft C++ Build Tools from:
   <https://visualstudio.microsoft.com/visual-cpp-build-tools/>

2. Run the installer

3. In the workload selector, check **"Desktop development with C++"**

4. Click Install (download is approximately 6GB and takes 10-20 minutes)

5. **Restart your computer** — this is required for environment variables to register

6. Reopen your terminal, activate your virtual environment, and re-run setup:

```
venv\Scripts\activate
setup.bat
```

**Verification:**

After installation, you can confirm `vswhere.exe` exists at:

```
C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
```

**Why this happens:**

A fresh Windows install doesn't include a C++ compiler by default. When pip encounters a package without a pre-built wheel for your specific Python version and Windows architecture, it falls back to compiling from source — which requires the Build Tools. This is especially common on newer Python versions (3.12+) where wheel availability lags behind release.

---

### NumPy 2.0 Compatibility Errors

**Symptom:**

```
AttributeError: module 'numpy' has no attribute 'float_'
```

Or similar errors referencing missing NumPy type aliases. Often appears during PDF indexing or when the embedding model loads.

**Cause:**

NumPy 2.0 (released June 2024) removed several deprecated type aliases (`np.float_`, `np.int_`, `np.bool_`, etc.) that older versions of `sentence-transformers` and ChromaDB still depend on. Everything installs without errors, then fails at runtime.

**Solution:**

Pin NumPy to a version below 2.0 in your `requirements.txt`:

```
numpy<2.0
```

Then reinstall:

```
pip install -r requirements.txt --force-reinstall
```

**Verification:**

```
python -c "import numpy; print(numpy.__version__)"
```

Should report a version below `2.0.0`.

> **Note for Python 3.13+ users:** Pinning `numpy<2.0` will cause pip to compile NumPy from source on Python 3.13+, which often fails on Windows even with C++ Build Tools installed (no pre-built wheels exist for `numpy<2.0` on Python 3.13). If you're on Python 3.13 and hit compilation errors during NumPy install, see [Python Version Wheel Availability](#python-version-wheel-availability) — the recommended fix is to use Python 3.12 instead.

---

### LangChain Import Path Errors

**Symptom:**

```
ModuleNotFoundError: No module named 'langchain.text_splitter'
```

Or similar errors about LangChain submodules not being found.

**Cause:**

LangChain restructured its package layout starting with the 0.1.x release. Several modules that were once part of the main `langchain` package are now distributed in separate sub-packages such as `langchain-text-splitters`, `langchain-community`, and `langchain-core`. Older code referencing the old paths breaks against newer installations.

**Solution:**

Install the relocated sub-packages:

```
pip install langchain-text-splitters langchain-community
```

Then update import statements in any custom scripts:

```python
# Old:
from langchain.text_splitter import RecursiveCharacterTextSplitter

# New:
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

The bundled scripts in this repository already use the updated imports.

---

### Python Version Wheel Availability

**Symptom:**

Multiple packages fail to install with messages like:

```
Could not find a version that satisfies the requirement
ERROR: No matching distribution found
```

Or pip attempts to build from source for many packages simultaneously, even with C++ Build Tools installed. NumPy compilation in particular may fail with errors like:

```
FAILED: numpy/core/libargfunc.dispatch.h_AVX512_SKX.a.p/meson-generated_argfunc.dispatch.c.obj
```

**Cause:**

Pre-built Python wheels for Windows lag behind new Python releases. If you're using a very recent Python version (e.g., 3.13 shortly after release), many packages may not yet have wheels available, forcing pip to compile each from source — which is slow and error-prone even when Build Tools are installed.

**Solution:**

Use a more established Python version for the virtual environment. Python 3.11 or 3.12 typically have the broadest wheel availability:

1. Install Python 3.11 or 3.12 alongside your current version from <https://www.python.org/downloads/>

2. Remove the existing virtual environment and recreate it with the specific version:

```
# Deactivate current venv if active
deactivate

# Remove old venv (Windows)
rmdir /s /q venv

# Remove old venv (Mac/Linux)
rm -rf venv

# Create new venv with Python 3.12 specifically
py -3.12 -m venv venv          # Windows
python3.12 -m venv venv        # Mac/Linux

# Activate it
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**Verification:**

```
python --version
```

Should show the version you targeted (e.g., `Python 3.12.x`).

> **Note:** This issue commonly surfaces when `numpy<2.0` is pinned (per [NumPy 2.0 Compatibility Errors](#numpy-20-compatibility-errors)) and you're using Python 3.13+, since NumPy 1.x has no pre-built wheels for Python 3.13. The two issues compound: the NumPy pin forces a from-source build, which then fails on the newer Python version.

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

```
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Mac:

```
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**2. Validate JSON Syntax**

Copy your configuration and paste into: <https://jsonlint.com/>

Common mistakes:

- Missing commas between sections
- Extra comma after last item
- Unmatched brackets `{` `}`
- Wrong quote types (use `"` not `'`)

**3. Check File Paths**

Paths must be absolute and properly escaped:

**Windows (wrong):**

```
"command": "C:\Users\jvije\venv\Scripts\python.exe"  ❌
```

**Windows (correct):**

```
"command": "C:\\Users\\jvije\\venv\\Scripts\\python.exe"  ✅
```

**Mac (correct):**

```
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

```
# Should be inside your venv folder
which python  # Mac/Linux
where python  # Windows
```

**Check 2: ChromaDB Index Exists**

```
ls chroma_db/  # Mac/Linux
dir chroma_db\  # Windows
```

If empty or missing:

```
python scripts/index_books.py --pdf-dir "/path/to/pdfs"
```

**Check 3: Dependencies Installed**

```
# Activate virtual environment first!
pip list | grep chromadb
pip list | grep sentence-transformers
```

If missing:

```
pip install -r requirements.txt
```

**Check 4: Test Server Manually**

```
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

```
node --version
npm --version
```

If not installed: <https://nodejs.org/>

**Check 2: Credentials in Configuration**

Verify in `claude_desktop_config.json`:

- `--server-url` is correct (include https://)
- `--site-name` matches your site
- `--token-name` and `--token-value` are correct

**Check 3: Test Credentials**

Create a test file `test-tableau.js`:

```
const args = [
  "--server-url", "https://your-site.online.tableau.com",
  "--site-name", "your-site-name",
  "--token-name", "your-token-name",
  "--token-value", "your-token-secret"
];

console.log("Testing Tableau connection with:", args);
```

Run:

```
npx -y @modelcontextprotocol/server-tableau --help
```

Should show help text without errors.

---

## PDF Indexing Issues

### "No module named 'PyPDF2'"

**Symptom:** ImportError when running `index_books.py`

**Solution:**

```
# Make sure virtual environment is activated!
pip install -r requirements.txt
```

Verify installation:

```
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

```
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
   - Solution: Try opening in PDF viewer; if it fails, file is corrupted
   - Re-download or find another copy

3. **Encrypted/Protected PDFs**
   - Solution: Remove encryption using PDF tools
   - Some DRM-protected files cannot be indexed

4. **Non-text content (images, diagrams only)**
   - Solution: These won't have extractable text
   - Skip or add OCR

**View indexing errors:**

```
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
   - Solution: Wait for initial download; subsequent runs are faster

**Speed improvements:**

```
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

```
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

```
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

```
# Must include https:// and correct domain
TABLEAU_SERVER_URL=https://10az.online.tableau.com

# NOT:
TABLEAU_SERVER_URL=10az.online.tableau.com  ❌ (missing https)
TABLEAU_SERVER_URL=https://10az.online.tableau.com/site/mysite  ❌ (has path)
```

**2. Check Internet Connection**

```
ping your-site.online.tableau.com
```

**3. Verify Tableau Server is Running**

Visit your Tableau URL in a browser — should load login page.

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

```
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

   ```
   du -sh chroma_db  # Mac/Linux
   dir chroma_db     # Windows
   ```

   Should be 100MB+ for a decent library.

   Solution: Reindex

   ```
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

   ```
   MAX_SEARCH_RESULTS=10  # Get more results to review
   ```

3. **Check relevance scores**

   Results include relevance scores (0-1). Low scores (<0.3) may not be useful.

4. **Try different embedding model**

   ```
   # More accurate but slower:
   EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
   ```

   Then reindex:

   ```
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

   ```
   MAX_SEARCH_RESULTS=3
   ```

2. **Use faster embedding model**

   ```
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

3. **Optimize chunk size**

   ```
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

   ```
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

```
# Try:
python3 --version
py --version
```

Add Python to PATH:

1. Search "Environment Variables"
2. Edit System PATH
3. Add Python installation directory

**Mac:**

```
# Install Python 3:
brew install python3
```

**Linux:**

```
sudo apt-get install python3
```

---

### Virtual Environment Not Activating

**Symptom:** `(venv)` doesn't appear in prompt

**Windows PowerShell:**

```
# Enable script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate:
venv\Scripts\activate
```

**Windows CMD:**

```
venv\Scripts\activate.bat
```

**Mac/Linux:**

```
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

2. **Check file location**

   Must be in project root, same directory as `src/` and `scripts/`

3. **Create from template**

   ```
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

   Use <https://jsonlint.com/> to check for syntax errors

---

### "Module not found" Errors in Logs

**Symptom:** Server starts but errors about missing modules

**Solution:**

Configuration must point to **virtual environment Python**, not system Python:

**Wrong:**

```
"command": "python"  ❌
"command": "/usr/bin/python3"  ❌
```

**Right:**

```
"command": "C:\\Users\\jvije\\tableau-knowledge-mcp\\venv\\Scripts\\python.exe"  ✅
```

---

## Getting More Help

### Collect Diagnostic Information

When reporting issues, include:

1. **System information:**

   ```
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

- **GitHub Issues:** <https://github.com/JVijeh/tableau-knowledge-mcp/issues>
- **Discussions:** <https://github.com/JVijeh/tableau-knowledge-mcp/discussions>
- **Documentation:** Review [INSTALLATION.md](INSTALLATION.md)
- **Tableau Support:** For Tableau-specific issues

---

**Still stuck?** Open a GitHub issue with:

- Operating system and version
- Python version
- Error messages
- What you've tried
