# Tableau Analytics Assistant with Technical Knowledge Base

> 🚀 Combine your technical library with live Tableau data analysis using Claude + Model Context Protocol (MCP)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io)

## 🎯 What This Does

Transform your data analysis workflow by asking questions that combine **theoretical knowledge** from your technical books with **live data** from Tableau:

**Example Questions:**
- *"What are LOD calculation best practices from my Tableau books, then show me examples using my Sample-Superstore data?"*
- *"Search my Python books for pandas merge techniques, then analyze which customers appear in multiple regions"*
- *"According to my data science books, what's the best way to handle outliers, and do I have any in my Profit field?"*

**Powered by Two MCP Servers Working Together:**
1. 📚 **Technical Knowledge Base** - Semantic search across your PDF library
2. 📊 **Tableau Cloud** - Live queries to your Tableau datasources

## ✨ Key Features

- 🔍 **Semantic Search** - Find relevant content across 80+ technical PDFs instantly
- 📊 **Live Data Queries** - Query Tableau datasources, metadata, and analytics
- 🧠 **Dual-Context Analysis** - Combine theory with practice in a single conversation
- 🔒 **Secure** - No credentials stored in code (environment variables only)
- 🎨 **Claude Desktop Integration** - Works seamlessly with Claude's chat interface
- ⚡ **Fast** - ChromaDB vector search returns results in <2 seconds

## 📋 Prerequisites

- **Python 3.9+** - Check with `python --version`
- **Tableau Cloud or Server** - With creator license or higher
- **Tableau Personal Access Token (PAT)** - For API authentication
- **Claude Desktop** - Download from [claude.ai](https://claude.ai)
- **PDF Library** - Your collection of technical books (PDF format)
- **4GB RAM minimum** (8GB recommended for larger libraries)
- **2GB disk space** - For ChromaDB index storage

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tableau-knowledge-mcp.git
cd tableau-knowledge-mcp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
# Use your favorite text editor:
nano .env
# or
code .env
```

**Required variables to update:**
- `TABLEAU_SERVER_URL` - Your Tableau Cloud URL
- `TABLEAU_SITE_NAME` - Your site name
- `TABLEAU_PAT_NAME` - Your Personal Access Token name
- `TABLEAU_PAT_SECRET` - Your Personal Access Token secret
- `PDF_LIBRARY_PATH` - Path to your PDF books directory

### 3. Index Your PDF Library

```bash
# Run the indexing script
python scripts/index_books.py --pdf-dir "/path/to/your/pdfs"

# This will:
# - Process all PDFs in the directory
# - Create text chunks with embeddings
# - Build ChromaDB vector index
# - Report indexing statistics

# Expected output:
# 📚 Indexing 83 PDF files...
# ✅ Successfully indexed: 80 books
# 📊 Total chunks: 91,100
# ⚡ Index size: 387MB
# ✅ Indexing complete!
```

### 4. Verify Setup

```bash
# Run verification script
bash scripts/verify_setup.sh

# This checks:
# ✓ Python version
# ✓ Dependencies installed
# ✓ ChromaDB index exists
# ✓ Environment variables set
# ✓ Tableau credentials valid
```

### 5. Configure Claude Desktop

**Edit your Claude Desktop configuration file:**

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this configuration (update paths to match your system):

```json
{
  "mcpServers": {
    "technical-knowledge-base": {
      "command": "C:\\path\\to\\tableau-knowledge-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\tableau-knowledge-mcp\\src\\server.py"
      ]
    },
    "tableau-cloud": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-tableau",
        "--server-url", "https://your-site.online.tableau.com",
        "--site-name", "your-site-name",
        "--token-name", "your-token-name",
        "--token-value", "your-token-secret"
      ]
    }
  }
}
```

### 6. Restart Claude Desktop and Test!

1. **Completely quit** Claude Desktop (File → Quit)
2. **Reopen** Claude Desktop
3. Click the **🔌 plug icon** in the bottom-right corner
4. Verify both servers show as **connected** ✅

**Test with a simple query:**
```
List all books in my technical knowledge base
```

**Then try a dual-MCP query:**
```
Search my Tableau books for LOD calculation examples, 
then show me the fields available in my Sample-Superstore datasource
```

## 📖 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed step-by-step setup
- **[Architecture](docs/ARCHITECTURE.md)** - How the system works
- **[Example Queries](docs/EXAMPLE_QUERIES.md)** - 25+ ready-to-use questions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Tableau Setup](docs/TABLEAU_SETUP.md)** - Creating Personal Access Tokens
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute

## 🎓 Example Use Cases

### 📊 Learning + Application
Ask theoretical questions and immediately see practical examples with your data:
- "What are the different types of joins explained in my SQL book, then show me examples using my Superstore Orders and Returns tables"
- "How should I handle NULL values according to my data cleaning book, and do I have any in my Sales field?"

### 📝 Blog Content Creation
Use the assistant to create educational content:
- "I want to write a blog post about LOD calculations. Pull examples from my Tableau books and create demo queries using my Superstore data"

### 🔍 Data Exploration
Combine domain knowledge with data discovery:
- "What are common customer segmentation techniques from my marketing books, and what segments exist in my customer data?"

### 🐛 Troubleshooting
Get help with specific technical challenges:
- "My RANK() calculation isn't working as expected. What are common mistakes from my Tableau books, and can you review my actual calculation?"

See **[examples/sample_queries.txt](examples/sample_queries.txt)** for 25+ complete examples.

## 🏗️ Architecture

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
│ • 91K chunks     │      │ • Metadata       │
└───┬──────────────┘      └──────────┬───────┘
    │                                 │
┌───▼─────────┐              ┌────────▼─────────┐
│ PDF Library │              │ Tableau Cloud    │
│ (83 books)  │              │ (13 datasources) │
└─────────────┘              └──────────────────┘
```

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for detailed system design.

## 🔧 Configuration

### Technical Knowledge Base Settings

Edit `.env` to customize:

```env
# Chunk size affects granularity of search results
CHUNK_SIZE=1000          # Larger = more context, fewer chunks

# Overlap preserves context between chunks
CHUNK_OVERLAP=200        # 20% overlap recommended

# Number of search results to return
MAX_SEARCH_RESULTS=5     # Balance relevance vs. context size
```

### Performance Tuning

For large PDF libraries (100+ books):
- Increase `BATCH_SIZE` for faster indexing
- Use `sentence-transformers/all-MiniLM-L6-v2` for speed
- Use `sentence-transformers/all-mpnet-base-v2` for accuracy

## 🔒 Security Best Practices

✅ **DO:**
- Use `.env` file for all credentials
- Keep `.env` in `.gitignore`
- Rotate Tableau PATs regularly
- Use dedicated PAT for this project (not your personal PAT)
- Set PAT expiration dates

❌ **DON'T:**
- Commit `.env` files to Git
- Share credentials in code or documentation
- Use production PATs for testing
- Store credentials in claude_desktop_config.json

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_server.py -v
```

## 🤝 Contributing

Contributions are welcome! See **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** for guidelines.

**Areas for contribution:**
- 📚 Additional PDF processing formats
- 🎨 Web UI for configuration
- 📊 Support for other BI tools (Power BI, Looker)
- 🧪 Expanded test coverage
- 📝 Documentation improvements

## 📊 Project Stats

- **83 books** indexed
- **91,100 text chunks** searchable
- **13 Tableau datasources** connected
- **<2 second** average query time
- **387MB** ChromaDB index size
- **80/83** successful PDF indexing rate

## 🗺️ Roadmap

- [ ] Web UI for setup and testing
- [ ] Support for Power BI datasets
- [ ] Multi-language PDF support
- [ ] Custom embedding models
- [ ] Docker containerization
- [ ] Cloud deployment guide

## 📝 License

This project is licensed under the MIT License - see the **[LICENSE](LICENSE)** file for details.

## 👤 Author

**Joshua Vijeh**
- Blog: [DataDevDiary.com](https://datadevdiary.com)
- GitHub: [@JVijeh](https://github.com/JVijeh)
- LinkedIn: [Joshua Vijeh](https://www.linkedin.com/in/joshua-vijeh-0512137/)

## 🙏 Acknowledgments

- **Repo built with the help of Claude.ai by Anthropic**
- Built with [Anthropic's Model Context Protocol](https://modelcontextprotocol.io)
- Uses [ChromaDB](https://www.trychroma.com/) for vector search
- Tableau MCP by [@modelcontextprotocol](https://github.com/modelcontextprotocol)
- Sentence Transformers by [UKPLab](https://www.sbert.net/)

## 📮 Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/yourusername/tableau-knowledge-mcp/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/yourusername/tableau-knowledge-mcp/discussions)
- 📧 **Email:** datadevdiary@gmail.com

---

⭐ **If this project helped you, please star the repository!** ⭐
