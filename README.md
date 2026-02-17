# Tableau Analytics Assistant with Technical Knowledge Base

> Combine your technical library with live Tableau data analysis using Claude + Model Context Protocol (MCP)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io)

## What This Does

> **Important:** This repository provides the **framework and tools only** - no PDF books or copyrighted materials are included. You will need to provide your own collection of technical PDFs. The stats referenced throughout this README (95 books, 75,003 chunks, etc.) reflect the author's personal library and will vary based on your own collection.

Transform your data analysis workflow by asking questions that combine **theoretical knowledge** from your technical books with **live data** from Tableau:

**Example Questions:**
- *"What are LOD calculation best practices from my Tableau books, then show me examples using my Sample-Superstore data?"*
- *"Search my Python books for pandas merge techniques, then analyze which customers appear in multiple regions"*
- *"According to my data science books, what's the best way to handle outliers, and do I have any in my Profit field?"*

**Powered by Two MCP Servers Working Together:**
1. **Technical Knowledge Base** - Semantic search across your PDF library
2. **Tableau Cloud** - Live queries to your Tableau datasources

## Key Features

- **Semantic Search** - Find relevant content across 90+ technical PDFs instantly
- **Live Data Queries** - Query Tableau datasources, metadata, and analytics
- **Dual-Context Analysis** - Combine theory with practice in a single conversation
- **Secure** - No credentials stored in code (environment variables only)
- **Claude Desktop Integration** - Works seamlessly with Claude's chat interface
- **Fast** - ChromaDB vector search returns results in under 2 seconds

## Prerequisites

- **Python 3.9+** - Use `py --version` on Windows
- **Microsoft C++ Build Tools** - Required for ChromaDB on Windows ([Download here](https://visualstudio.microsoft.com/visual-cpp-build-tools/))
- **Node.js** - Required for Tableau MCP server ([Download here](https://nodejs.org/))
- **Tableau Cloud or Server** - With creator license or higher
- **Tableau Personal Access Token (PAT)** - For API authentication
- **Claude Desktop** - Download from [claude.ai](https://claude.ai)
- **PDF Library** - Your own collection of technical books in PDF format (not included - see note above)
- **4GB RAM minimum** (8GB recommended for larger libraries)
- **2GB disk space** - For ChromaDB index storage

> **Windows Users:** See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for Windows-specific installation steps and solutions to common issues.

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/jvijeh/tableau-knowledge-mcp.git
cd tableau-knowledge-mcp
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
py -m venv venv

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Important:** Always look for `(venv)` in your prompt before running any commands. Without it, packages won't be found.

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Open `.env` and update these required values:

```env
TABLEAU_SERVER_URL=https://your-site.online.tableau.com
TABLEAU_SITE_NAME=your-site-name
TABLEAU_PAT_NAME=your-token-name
TABLEAU_PAT_SECRET=your-token-secret
PDF_LIBRARY_PATH=/path/to/your/pdf/books
```

See [docs/TABLEAU_SETUP.md](docs/TABLEAU_SETUP.md) for help creating a Personal Access Token.

### 3. Index Your PDF Library

```bash
# Windows
python scripts\index_books.py --pdf-dir "C:\path\to\your\books"

# Mac/Linux
python scripts/index_books.py --pdf-dir "/path/to/your/books"
```

**The script searches subfolders automatically** - organize your books in topic folders:

```
books/
├── Tableau/
├── Python/
├── SQL/
└── Data_Science/
```

**Expected output:**
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Initializing ChromaDB at: ./chroma_db
Found 110 PDF files

[1/110] Processing: Learning_Tableau_2025.pdf
  ✓ Indexed 856 chunks
...

✅ Indexing complete!
📊 Successfully indexed: 95/110 books
📊 Total chunks: 75,003
📊 Average chunks per book: 789
```

> **Note:** 85-90% success rate is normal. Scanned PDFs and encrypted files are automatically skipped.

### 4. Configure Claude Desktop

**Config file location:**

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this configuration (replace `{username}` with your Windows username):

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
      "command": "C:\\Users\\{username}\\tableau-knowledge-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\{username}\\tableau-knowledge-mcp\\src\\server.py"
      ],
      "env": {
        "CHROMA_DB_PATH": "C:\\Users\\{username}\\tableau-knowledge-mcp\\chroma_db",
        "PDF_LIBRARY_PATH": "C:\\Users\\{username}\\books",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
        "MAX_SEARCH_RESULTS": "5"
      }
    }
  }
}
```

> **Important:** Use absolute paths with double backslashes `\\` on Windows. The `CHROMA_DB_PATH` env variable is required for Claude Desktop to find your index.

See [examples/claude_desktop_config.json](examples/claude_desktop_config.json) for a complete template.

### 5. Restart Claude Desktop and Test

1. Completely quit Claude Desktop (File → Quit)
2. Reopen Claude Desktop
3. Click the plug icon in the bottom-right corner
4. Verify both servers show as connected

**Test queries:**
```
List all books in my technical knowledge base
```
```
What datasources are available in my Tableau environment?
```
```
Search my Tableau books for LOD calculations, then show me 
the fields available in Sample-Superstore
```

## Documentation

- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Detailed step-by-step setup
- [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) - Windows-specific guide with common issues
- [docs/TABLEAU_SETUP.md](docs/TABLEAU_SETUP.md) - Creating Personal Access Tokens
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - How the system works
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) - How to contribute

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
└────────┬────────┘
         │
    ┌────┴─────────────────────────────┐
    │                                  │
┌───▼──────────────┐      ┌───────────▼──────┐
│ Technical KB MCP │      │ Tableau Cloud MCP│
│                  │      │                  │
│ • ChromaDB       │      │ • REST API       │
│ • Embeddings     │      │ • Live Queries   │
│ • 75K chunks     │      │ • Metadata       │
└───┬──────────────┘      └──────────┬───────┘
    │                                 │
┌───▼─────────┐              ┌────────▼─────────┐
│ PDF Library │              │ Tableau Cloud    │
│ (95 books)  │              │ (your datasets)  │
└─────────────┘              └──────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## Example Use Cases

### Learning + Application
Ask theoretical questions and immediately see practical examples with your data:
- "What are the different types of joins explained in my SQL book, then show me examples using my Superstore data"
- "How should I handle NULL values according to my data cleaning book, and do I have any in my Sales field?"

### Blog Content Creation
Use the assistant to create educational content:
- "I want to write a blog post about LOD calculations. Pull examples from my Tableau books and create demo queries using my Superstore data"

### Data Exploration
Combine domain knowledge with data discovery:
- "What are common customer segmentation techniques from my analytics books, and what segments exist in my customer data?"

### Troubleshooting
Get help with specific technical challenges:
- "My RANK() calculation isn't working as expected. What are common mistakes from my Tableau books, and can you review my actual calculation?"

## Configuration Options

Edit `.env` to customize performance:

```env
CHUNK_SIZE=1000          # Larger = more context per result
CHUNK_OVERLAP=200        # 20% overlap preserves context between chunks
MAX_SEARCH_RESULTS=5     # Number of results returned per query
BATCH_SIZE=10            # PDFs processed simultaneously during indexing
```

## Security Best Practices

**DO:**
- Use `.env` file for all credentials
- Keep `.env` in `.gitignore`
- Rotate Tableau PATs regularly
- Use a dedicated PAT for this project
- Set PAT expiration dates (90-365 days recommended)

**DON'T:**
- Commit `.env` files to Git
- Share credentials in code or documentation
- Use production PATs for testing
- Store credentials directly in claude_desktop_config.json

## Common Issues (Windows)

| Error | Fix |
|-------|-----|
| `python not found` | Use `py` instead of `python` |
| `venv activation fails` | Use `& .\venv\Scripts\Activate.ps1` in PowerShell |
| `pip not recognized` | Activate venv first - look for `(venv)` prefix |
| `chroma-hnswlib build error` | Install Microsoft C++ Build Tools |
| `np.float_ removed` | `pip install "numpy<2.0"` |
| `cached_download missing` | `pip install --upgrade sentence-transformers` |
| `No module named 'mcp'` | `pip install mcp` |
| `Found 0 PDF files` | Check path - script searches subfolders automatically |
| Knowledge base disconnects | Add absolute `CHROMA_DB_PATH` to Claude Desktop config env section |

See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for full details on each issue.

## Project Stats

Tested on fresh Windows installation (February 2026):

- **95 books** successfully indexed
- **75,003 text chunks** searchable
- **86% success rate** across 110 PDF files
- **~23 minutes** indexing time for 110 books
- **~45 minutes** total setup time (includes C++ Build Tools)
- **Under 2 seconds** average query response time

## Roadmap

- [ ] Web UI for setup and configuration
- [ ] Support for Power BI datasets
- [ ] Multi-language PDF support
- [ ] Docker containerization
- [ ] Cloud deployment guide
- [ ] OCR support for scanned PDFs

## Contributing

Contributions are welcome! See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Joshua Vijeh**
- Blog: [DataDevDiary.com](https://datadevdiary.com)
- GitHub: [@jvijeh](https://github.com/jvijeh)

## Acknowledgments

- Built with [Anthropic's Model Context Protocol](https://modelcontextprotocol.io)
- Uses [ChromaDB](https://www.trychroma.com/) for vector search
- Tableau MCP by [@tableau](https://github.com/tableau)
- Sentence Transformers by [UKPLab](https://www.sbert.net/)
- [Claude by Anthropic](https://claude.ai) was used as a development and troubleshooting assistant throughout the build process

## Support

- **Bug reports:** [GitHub Issues](https://github.com/jvijeh/tableau-knowledge-mcp/issues)
- **Questions:** [GitHub Discussions](https://github.com/jvijeh/tableau-knowledge-mcp/discussions)
- **Blog:** [DataDevDiary.com](https://datadevdiary.com)

---

If this project helped you, please star the repository!
