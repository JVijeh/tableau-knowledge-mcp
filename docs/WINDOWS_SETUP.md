# Windows Setup Guide

This guide addresses Windows-specific setup requirements discovered during real-world testing.

## Prerequisites (Windows)

### 1. Python (using `py` launcher)

Windows 10/11 includes a Python launcher (`py`) that is more reliable than the `python` command:

```powershell
# Use this instead of 'python':
py --version
py -m venv venv
py -m pip install -r requirements.txt
```

If `python` gives "run without arguments to install from Microsoft Store", disable the alias:
1. Search "Manage app execution aliases"
2. Toggle OFF "App Installer - python.exe"
3. Toggle OFF "App Installer - python3.exe"

---

### 2. Microsoft C++ Build Tools (REQUIRED)

ChromaDB requires C++ compilation on Windows. Without this you will see:

```
error: Microsoft Visual C++ 14.0 or greater is required
Building wheel for chroma-hnswlib (pyproject.toml) ... error
```

**Install before running pip install:**

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select **"Desktop development with C++"**
4. Install (~6GB download, 10-15 minutes)
5. **Restart your computer**

---

### 3. Node.js (for Tableau MCP)

Required for the Tableau MCP server:

1. Download: https://nodejs.org/
2. Install LTS version
3. Verify: `node --version` and `npm --version`

---

## Virtual Environment (Windows)

### Creating (First Time Only)

```powershell
py -m venv venv
```

### Activating

**PowerShell (use this):**
```powershell
& .\venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Important:** `.bat` files don't work in PowerShell - use `.ps1` instead!

### Verifying Activation

Look for `(venv)` prefix in your prompt:
```
(venv) C:\Users\username\project>   ← Activated ✅
C:\Users\username\project>          ← NOT activated ❌
```

### Quick Start Scripts

Use the included helper scripts:
```powershell
# First time setup:
setup.bat

# Daily activation:
& .\venv\Scripts\Activate.ps1
```

---

## Installing Dependencies

Always activate venv first, then:

```powershell
# Install all dependencies
py -m pip install -r requirements.txt
```

### Known Windows Issues

**Issue 1: NumPy 2.0 Compatibility**
```
AttributeError: np.float_ was removed in the NumPy 2.0 release
```
Fix:
```powershell
pip install "numpy<2.0"
```

**Issue 2: sentence-transformers version**
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```
Fix:
```powershell
pip install --upgrade sentence-transformers
```

**Issue 3: mcp package missing**
```
Error importing dependencies: No module named 'mcp'
```
Fix:
```powershell
pip install mcp
```

---

## Claude Desktop Configuration (Windows)

Config file location:
```
C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json
```

Open with:
```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

### Important: Use Absolute Paths

Claude Desktop needs absolute paths AND an env section for the knowledge base:

```json
{
  "mcpServers": {
    "tableau": {
      "command": "npx",
      "args": ["-y", "@tableau/mcp-server@latest"],
      "env": {
        "SERVER": "https://your-site.online.tableau.com",
        "SITE_NAME": "your-site-name",
        "PAT_NAME": "your-token-name",
        "PAT_VALUE": "your-token-secret"
      }
    },
    "technical-knowledge-base": {
      "command": "C:\\Users\\{username}\\project\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\{username}\\project\\src\\server.py"
      ],
      "env": {
        "CHROMA_DB_PATH": "C:\\Users\\{username}\\project\\chroma_db",
        "PDF_LIBRARY_PATH": "C:\\Users\\{username}\\books",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
        "MAX_SEARCH_RESULTS": "5"
      }
    }
  }
}
```

**Critical notes:**
- Use double backslashes `\\` throughout
- Use absolute paths (not relative `./`)
- Include `env` section with `CHROMA_DB_PATH` as absolute path
- Replace `{username}` with your actual Windows username

---

## PDF Library Organization

Books can be organized in subfolders - the indexing script searches recursively:

```
books/
├── Tableau/
│   ├── Learning_Tableau_2025.pdf
│   └── Tableau_Cookbook.pdf
├── Python/
│   ├── Python_for_Data_Analysis.pdf
│   └── Learning_Pandas.pdf
└── SQL/
    └── SQL_Fundamentals.pdf
```

Run indexing with the root books folder:
```powershell
python scripts\index_books.py --pdf-dir "C:\path\to\books"
```

---

## Expected Results

**Realistic indexing expectations:**
- Success rate: 85-90% (some PDFs are scanned/encrypted)
- Time: ~15-25 minutes for 100 books
- Chunks: ~750-800 per book average

**Files that fail to index (normal):**
- Scanned PDFs (images only, no text)
- Password-protected PDFs
- Corrupted downloads
- Supplemental materials with minimal text

---

## Troubleshooting Quick Reference

| Error | Fix |
|-------|-----|
| `python not found` | Use `py` instead |
| `venv activation fails` | Use `& .\venv\Scripts\Activate.ps1` |
| `pip not recognized` | Activate venv first |
| `chroma-hnswlib build error` | Install C++ Build Tools |
| `np.float_ removed` | `pip install "numpy<2.0"` |
| `cached_download missing` | `pip install --upgrade sentence-transformers` |
| `No module named 'mcp'` | `pip install mcp` |
| `Found 0 PDF files` | Check path, ensure subfolders are included |
| `TextInputSequence must be str` | Use updated index_books.py with error handling |
| Knowledge base disconnects | Add absolute `CHROMA_DB_PATH` to Claude Desktop config env section |

---

## Real-World Setup Stats (Tested February 2026)

- **Setup time:** ~45 minutes (includes C++ Build Tools installation)
- **Indexing time:** ~23 minutes for 110 PDFs
- **Success rate:** 95/110 books (86%)
- **Total chunks:** 75,003
- **Query response time:** 1-3 seconds

