# Installation Guide

Complete step-by-step instructions for setting up the Tableau Technical Knowledge Base MCP.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Verification](#verification)
- [Next Steps](#next-steps)

## System Requirements

### Required Software

- **Python 3.9 or higher**
  - Check version: `python --version`
  - Download: https://www.python.org/downloads/
  
- **Git**
  - Check version: `git --version`
  - Download: https://git-scm.com/downloads

- **Claude Desktop**
  - Download: https://claude.ai/download

- **Node.js and npm** (for Tableau MCP server)
  - Check version: `node --version` and `npm --version`
  - Download: https://nodejs.org/

### Tableau Requirements

- **Tableau Cloud or Server** access
- **Creator license** (or higher)
- **Admin permissions** to create Personal Access Tokens

### System Specifications

- **Operating System:** Windows 10+, macOS 10.15+, or Linux
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 2GB free (for ChromaDB index)
- **Internet:** Stable connection for Tableau API calls

### PDF Library

- Technical books in PDF format
- Readable text (not scanned images without OCR)
- Recommended: 10-100 books for optimal performance

---

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/yourusername/tableau-knowledge-mcp.git

# Navigate into directory
cd tableau-knowledge-mcp
```

**Alternative: Download ZIP**
1. Go to https://github.com/yourusername/tableau-knowledge-mcp
2. Click "Code" → "Download ZIP"
3. Extract to your desired location
4. Open terminal/command prompt in that directory

---

### Step 2: Create Python Virtual Environment

**Why use a virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Makes the setup reproducible

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify activation:**
Your prompt should now show `(venv)` at the beginning:
```bash
(venv) C:\Users\username\tableau-knowledge-mcp>
```

---

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**This installs:**
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- PyPDF2 (PDF processing)
- python-dotenv (environment variables)
- pytest (testing framework)
- And other dependencies

**Installation time:** 2-5 minutes depending on your internet speed

**Verify installation:**
```bash
pip list
```

You should see all packages listed in `requirements.txt`

---

### Step 4: Configure Environment Variables

**Create your environment file:**

```bash
# Copy the example file
cp .env.example .env
```

**Windows (if cp doesn't work):**
```bash
copy .env.example .env
```

**Edit the `.env` file:**

Open `.env` in your text editor and update these variables:

```env
# Tableau Cloud Configuration
TABLEAU_SERVER_URL=https://your-site.online.tableau.com
TABLEAU_SITE_NAME=your-site-name
TABLEAU_PAT_NAME=your-token-name
TABLEAU_PAT_SECRET=your-token-secret

# Knowledge Base Configuration
PDF_LIBRARY_PATH=/absolute/path/to/your/pdfs
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Performance Settings (optional)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_SEARCH_RESULTS=5
```

**Important notes:**
- Use **absolute paths** for `PDF_LIBRARY_PATH`
- Windows paths use backslashes: `C:\Users\username\Documents\PDFs`
- Mac/Linux paths use forward slashes: `/Users/username/Documents/PDFs`
- See [TABLEAU_SETUP.md](TABLEAU_SETUP.md) for creating Personal Access Tokens

---

### Step 5: Prepare Your PDF Library

**Organize your PDFs:**

1. Create a dedicated folder for your technical books
2. Place all PDF files in this folder
3. PDFs can be in subdirectories (the script will find them)
4. Ensure PDFs are readable (text-based, not scanned images)

**Recommended structure:**
```
/path/to/pdfs/
├── Tableau/
│   ├── Learning Tableau 2025.pdf
│   └── Tableau Cookbook.pdf
├── Python/
│   ├── Python for Data Analysis.pdf
│   └── Learning Pandas.pdf
└── SQL/
    └── SQL Fundamentals.pdf
```

**File naming tips:**
- Use descriptive names
- Avoid special characters
- Keep file names under 100 characters

---

### Step 6: Index Your PDF Library

**Run the indexing script:**

```bash
python scripts/index_books.py --pdf-dir "/path/to/your/pdfs"
```

**Replace `/path/to/your/pdfs`** with your actual path:
- Windows example: `"C:\Users\jvije\Documents\PDFs"`
- Mac example: `"/Users/jvije/Documents/PDFs"`
- Linux example: `"/home/jvije/Documents/PDFs"`

**What happens during indexing:**
1. Script finds all PDF files recursively
2. Extracts text from each PDF
3. Splits text into 1000-character chunks with 200-character overlap
4. Creates embeddings using sentence-transformers
5. Stores in ChromaDB vector database

**Expected output:**
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Initializing ChromaDB at: ./chroma_db
Found 83 PDF files
[1/83] Processing: Learning Tableau 2025.pdf
  ✓ Indexed 234 chunks
[2/83] Processing: Python for Data Analysis.pdf
  ✓ Indexed 312 chunks
...
[83/83] Processing: SQL Fundamentals.pdf
  ✓ Indexed 189 chunks

Indexing complete!
Successfully indexed: 80/83 books
Total chunks: 91,100
Average chunks per book: 1,138
```

**Indexing time estimates:**
- 10 books: ~2 minutes
- 50 books: ~10 minutes
- 100 books: ~20 minutes

**If indexing fails:**
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#pdf-indexing-issues)

---

### Step 7: Install Tableau MCP Server

The Tableau MCP server is installed automatically when Claude Desktop starts (via `npx`), but you can pre-install it:

```bash
npm install -g @modelcontextprotocol/server-tableau
```

**This is optional** - Claude Desktop will install it automatically on first use.

---

### Step 8: Configure Claude Desktop

**Locate your Claude Desktop configuration file:**

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

**Edit the configuration file:**

Add both MCP servers to the configuration:

```json
{
  "mcpServers": {
    "technical-knowledge-base": {
      "command": "C:\\Users\\jvije\\tableau-knowledge-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\jvije\\tableau-knowledge-mcp\\src\\server.py"
      ]
    },
    "tableau-cloud": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-tableau",
        "--server-url",
        "https://your-site.online.tableau.com",
        "--site-name",
        "your-site-name",
        "--token-name",
        "your-token-name",
        "--token-value",
        "your-token-secret"
      ]
    }
  }
}
```

**Important:**
- Update ALL paths to match your system
- Use double backslashes `\\` on Windows
- Use forward slashes `/` on Mac/Linux
- Replace Tableau credentials with your actual values
- Python path should point to your virtual environment's Python

**Finding the correct Python path:**

**Windows:**
```bash
where python
# Use the path inside your venv folder
```

**Mac/Linux:**
```bash
which python
# Use the path inside your venv folder
```

---

### Step 9: Verify Installation

**Run the verification script:**

```bash
bash scripts/verify_setup.sh
```

**Windows (if bash isn't available):**
Run the checks manually:

```bash
# Check Python version
python --version

# Check dependencies
pip list

# Check ChromaDB index
dir chroma_db

# Check environment variables
type .env
```

**Expected output:**
```
Verifying Tableau Knowledge MCP Setup...
===========================================

1. Checking Python version...
✓ Python 3.11.5 installed

2. Checking virtual environment...
✓ Virtual environment is activated

3. Checking Python dependencies...
✓ chromadb installed
✓ sentence-transformers installed
✓ PyPDF2 installed
✓ python-dotenv installed

4. Checking environment configuration...
✓ .env file exists
✓ TABLEAU_SERVER_URL is set
✓ PDF_LIBRARY_PATH is set

5. Checking PDF library...
✓ PDF library directory exists
✓ Found 83 PDF files

6. Checking ChromaDB index...
✓ ChromaDB directory exists
✓ ChromaDB index contains data
  Index size: 387MB

7. Checking Tableau connectivity...
✓ Tableau server is reachable

8. Checking Claude Desktop configuration...
✓ Claude Desktop config file exists
✓ Technical knowledge base MCP configured
✓ Tableau MCP configured

===========================================
✓ All checks passed!
```

---

### Step 10: Test in Claude Desktop

1. **Completely quit** Claude Desktop (File → Quit, not just close window)
2. **Reopen** Claude Desktop
3. Click the **plug icon** (🔌) in the bottom-right corner
4. **Verify both servers** show as connected with green checkmarks

**Test query:**
```
List all books in my technical knowledge base
```

**Expected response:**
```
Available Books

Total books indexed: 83

1. Learning Tableau 2025 - 234 indexed chunks
2. Python for Data Analysis - 312 indexed chunks
...
```

**If servers don't connect:**
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#mcp-connection-issues)

---

## Configuration

### Performance Tuning

**For large PDF libraries (100+ books):**

Edit `.env`:
```env
BATCH_SIZE=50              # Increase for faster indexing
CHUNK_SIZE=1500            # Larger chunks = more context
MAX_SEARCH_RESULTS=10      # More results = better coverage
```

**For better search accuracy:**
```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

**For faster performance:**
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Customizing Chunk Settings

**Chunk size:** Controls granularity of search results
- **Smaller (500-800):** More precise matches, more chunks
- **Larger (1500-2000):** More context, fewer chunks

**Overlap:** Preserves context at chunk boundaries
- **Recommended:** 20-25% of chunk size
- **Example:** CHUNK_SIZE=1000, CHUNK_OVERLAP=200

---

## Verification

### Test Each Component

**1. Test Knowledge Base Search:**
```
Search my technical books for "LOD calculations"
```

**2. Test Tableau Connection:**
```
What datasources are available in my Tableau environment?
```

**3. Test Dual-MCP Query:**
```
Search my Tableau books for ranking best practices, 
then show me the top 5 products by profit
```

**All should work without errors.**

---

## Next Steps

After successful installation:

1. **Explore example queries:** See [EXAMPLE_QUERIES.md](EXAMPLE_QUERIES.md)
2. **Try dual-MCP queries:** Combine theory from books with live data
3. **Create content:** Use the assistant to generate blog posts
4. **Customize:** Adjust settings in `.env` for your needs
5. **Share:** Tell others about your setup

---

## Troubleshooting

For common issues and solutions, see:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [TABLEAU_SETUP.md](TABLEAU_SETUP.md) - For Tableau connection issues

---

## Getting Help

- **GitHub Issues:** https://github.com/yourusername/tableau-knowledge-mcp/issues
- **Discussions:** https://github.com/yourusername/tableau-knowledge-mcp/discussions
- **Email:** your.email@example.com

---

**Installation complete!** You're ready to start using your Tableau Analytics Assistant.
