# Architecture

System design and technical overview of the Tableau Technical Knowledge Base MCP.

## Table of Contents

- [Overview](#overview)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Technical Stack](#technical-stack)
- [Security Model](#security-model)
- [Design Decisions](#design-decisions)

---

## Overview

The Tableau Technical Knowledge Base MCP combines two independent Model Context Protocol (MCP) servers to enable Claude to access both your PDF library and live Tableau data simultaneously.

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│            Claude Desktop                   │
│  (User Interface + Orchestration)           │
└──────────────┬──────────────────────────────┘
               │
               │ MCP Protocol (JSON-RPC over stdio)
               │
     ┌─────────┴──────────┐
     │                    │
     │                    │
┌────▼────────────┐  ┌────▼──────────────┐
│  Technical KB   │  │  Tableau Cloud    │
│   MCP Server    │  │   MCP Server      │
└────┬────────────┘  └────┬──────────────┘
     │                    │
     │                    │
┌────▼────────────┐  ┌────▼──────────────┐
│   ChromaDB      │  │  Tableau REST     │
│ Vector Database │  │      API          │
└────┬────────────┘  └────┬──────────────┘
     │                    │
┌────▼────────────┐  ┌────▼──────────────┐
│  PDF Library    │  │  Tableau Cloud    │
│  (83 books)     │  │  (Datasources)    │
└─────────────────┘  └───────────────────┘
```

---

## System Components

### 1. Claude Desktop

**Role:** User interface and query orchestration

**Responsibilities:**
- Presents chat interface to user
- Routes queries to appropriate MCP servers
- Combines results from multiple servers
- Manages MCP server lifecycle

**Technology:**
- Electron-based desktop application
- Communicates via JSON-RPC over stdio
- Loads MCP servers from configuration

---

### 2. Technical Knowledge Base MCP Server

**Role:** Semantic search across PDF library

**Location:** `src/server.py`

**Capabilities:**
- `search_technical_books` - Semantic search across indexed PDFs
- `list_available_books` - List all books in the knowledge base

**Implementation Details:**

```python
# Server startup
app = Server("technical-knowledge-base")

# Tool definitions
@app.list_tools()
async def list_tools() -> List[Tool]:
    # Returns available tools

@app.call_tool()
async def call_tool(name: str, arguments: Any):
    # Handles tool execution
```

**Key Features:**
- Asynchronous operation (async/await)
- Error handling for missing dependencies
- Environment variable configuration
- Logging for debugging

---

### 3. ChromaDB Vector Database

**Role:** Storage and retrieval of text embeddings

**Technology:**
- Open-source vector database
- Persistent storage on disk
- Built-in similarity search

**Storage Structure:**

```
chroma_db/
├── chroma.sqlite3          # Metadata database
└── [collection-uuid]/      # Vector data
    ├── data_level0.bin     # Vector storage
    ├── header.bin          # Collection metadata
    └── length.bin          # Dimension info
```

**Collection Schema:**
- **IDs:** `{book_name}_chunk_{number}` (e.g., "learning_tableau_chunk_42")
- **Documents:** Text chunks (1000 chars)
- **Metadata:** `{"source": "book_name"}`
- **Embeddings:** 384-dimensional vectors (MiniLM model)

---

### 4. Sentence Transformers (Embedding Model)

**Role:** Convert text to vector embeddings

**Default Model:** `all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Max sequence length:** 256 tokens
- **Performance:** ~14,000 sentences/sec on CPU
- **Size:** ~80MB

**Alternative Model:** `all-mpnet-base-v2`
- **Dimensions:** 768
- **Performance:** Slower but more accurate
- **Size:** ~420MB

**How it works:**
1. Input text → Tokenization
2. Tokens → Transformer model
3. Output → Mean pooling → 384D vector
4. Vector represents semantic meaning

---

### 5. PDF Processing Pipeline

**Location:** `scripts/index_books.py`

**Process:**

```
PDF File
  ↓
PyPDF2 Reader
  ↓
Text Extraction (page by page)
  ↓
Text Cleaning
  ↓
Chunking (1000 chars, 200 overlap)
  ↓
Embedding Generation
  ↓
ChromaDB Storage
```

**Chunking Strategy:**

```python
# Example chunk boundaries
Text: "...about LOD calculations. FIXED calculations are..."
                                  ↑
                            Chunk boundary
                                  ↓
Chunk 1: "...about LOD calculations. FIXED calc..."
Chunk 2: "...OD calculations. FIXED calculations are..."
         ↑_________________↑
         200-char overlap preserves context
```

**Why overlap?**
- Prevents important info from being split
- Maintains context across chunk boundaries
- Improves search relevance

---

### 6. Tableau Cloud MCP Server

**Role:** Query Tableau datasources and metadata

**Technology:**
- Official Anthropic MCP server
- npm package: `@modelcontextprotocol/server-tableau`
- Runs via `npx` (no installation needed)

**Capabilities:**
- List datasources
- Query datasource metadata (fields, types)
- Execute data queries
- Access workbooks and views

**Authentication:**
- Personal Access Token (PAT)
- REST API v3.x
- Site-specific access

---

### 7. Tableau REST API

**Version:** 3.18+

**Endpoints Used:**
- `/api/3.x/auth/signin` - Authentication
- `/api/3.x/sites/{site}/datasources` - List datasources
- `/api/3.x/sites/{site}/datasources/{id}/data` - Query data

**Response Format:** JSON

---

## Data Flow

### Query: "Search my Tableau books for LOD examples"

```
1. User types query in Claude Desktop
   ↓
2. Claude Desktop sends to Technical KB MCP
   {
     "tool": "search_technical_books",
     "query": "LOD calculations examples"
   }
   ↓
3. MCP Server queries ChromaDB
   - Convert query to embedding
   - Find similar vectors
   - Return top 5 matches
   ↓
4. ChromaDB returns results
   [
     {text: "...FIXED LOD...", source: "learning_tableau", score: 0.87},
     {text: "...INCLUDE example...", source: "tableau_cookbook", score: 0.82}
   ]
   ↓
5. MCP Server formats response
   ↓
6. Claude Desktop receives results
   ↓
7. Claude synthesizes answer for user
```

### Dual-MCP Query: "Search books for LOD, then show Superstore fields"

```
1. User query → Claude Desktop
   ↓
2. Claude Desktop routes to BOTH servers:
   
   → Technical KB MCP
     Query: "LOD calculations"
     Returns: Book excerpts
   
   → Tableau MCP
     Query: "List Superstore fields"
     Returns: Field metadata
   ↓
3. Claude Desktop receives both results
   ↓
4. Claude combines information:
   - Theory from books
   - Practical fields from Tableau
   ↓
5. User sees integrated answer
```

---

## Technical Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| MCP Server | Python 3.9+ | Server implementation |
| Vector DB | ChromaDB 0.4.18 | Embedding storage |
| Embeddings | sentence-transformers | Text → vectors |
| PDF Processing | PyPDF2 3.0.1 | Text extraction |
| Environment | python-dotenv | Config management |
| Testing | pytest | Unit tests |

### Tableau Integration

| Component | Technology | Purpose |
|-----------|------------|---------|
| MCP Server | Node.js (via npx) | Tableau MCP |
| API | Tableau REST API | Data access |
| Auth | Personal Access Token | Secure authentication |

### Communication

| Layer | Protocol | Details |
|-------|----------|---------|
| Claude ↔ MCP | JSON-RPC | Over stdio |
| MCP ↔ ChromaDB | Native API | Python library |
| MCP ↔ Tableau | HTTPS REST | JSON payloads |

---

## Security Model

### Credential Storage

```
Secrets Flow:
  User creates .env
    ↓
  python-dotenv reads .env
    ↓
  os.getenv() in Python code
    ↓
  Used at runtime (never hardcoded)
```

**Security Layers:**

1. **File System Protection**
   - `.env` in `.gitignore`
   - File permissions (600 on Unix)
   - Not committed to version control

2. **Runtime Protection**
   - Credentials only in memory
   - No logging of secrets
   - Cleared after use

3. **Token Management**
   - PAT with expiration
   - Rotation schedule
   - Scope-limited permissions

---

### MCP Protocol Security

**Isolation:**
- Each MCP server runs in separate process
- No direct communication between servers
- Claude Desktop mediates all interactions

**Permissions:**
- Servers have no filesystem access beyond their scope
- Cannot modify system settings
- Limited to defined tool capabilities

---

## Design Decisions

### Why Two Separate MCP Servers?

**Alternative considered:** Single server handling both books and Tableau

**Decision:** Keep separate

**Reasons:**
1. **Modularity** - Each server can be updated independently
2. **Reusability** - Tableau MCP can be used in other projects
3. **Maintainability** - Clearer separation of concerns
4. **Official support** - Tableau MCP is officially maintained

---

### Why ChromaDB?

**Alternatives considered:** Pinecone, Weaviate, Elasticsearch

**Decision:** ChromaDB

**Reasons:**
1. **Local-first** - No cloud dependency
2. **Simple** - Easy setup, no server required
3. **Python-native** - Clean API
4. **Persistent** - Disk-based storage
5. **Open-source** - Free, no usage limits

---

### Why Sentence Transformers?

**Alternatives considered:** OpenAI embeddings, Cohere

**Decision:** Sentence Transformers (MiniLM)

**Reasons:**
1. **Local** - No API calls, works offline
2. **Fast** - CPU-friendly model
3. **Free** - No usage costs
4. **Privacy** - Data never leaves your machine
5. **Quality** - Good enough for technical docs

---

### Why Chunking Strategy (1000 chars, 200 overlap)?

**Chunk Size (1000):**
- Small enough: Relevant results, not too broad
- Large enough: Maintains context
- Typical: 2-4 paragraphs of text

**Overlap (200 = 20%):**
- Prevents split concepts
- Small enough: Not too much duplication
- Large enough: Preserves context

**Tested alternatives:**
- 500/100: Too fragmented
- 2000/400: Too broad, less precise
- 1000/200: Sweet spot ✓

---

### Why Personal Access Tokens (not OAuth)?

**Decision:** PAT-based authentication

**Reasons:**
1. **Simplicity** - No OAuth flow needed
2. **CLI-friendly** - Works in headless environments
3. **User control** - Easy to create/revoke
4. **Tableau standard** - Recommended by Tableau for API access

---

## Performance Characteristics

### Typical Query Times

| Operation | Time | Notes |
|-----------|------|-------|
| Book search | 0.5-2s | Depends on library size |
| Tableau list | 1-3s | Network latency dependent |
| Tableau query | 2-10s | Data volume dependent |
| PDF indexing | 1-2min/book | One-time operation |

### Memory Usage

| Component | RAM | Notes |
|-----------|-----|-------|
| Embedding model | ~200MB | Loaded once |
| ChromaDB | ~100MB | For 100K chunks |
| Python process | ~50MB | Base overhead |
| Total | ~400MB | Per MCP server |

### Disk Usage

| Component | Size | Notes |
|-----------|------|-------|
| ChromaDB index | ~5KB/chunk | 100K chunks = ~500MB |
| Embedding model | 80MB | Cached locally |
| Python venv | ~200MB | Dependencies |

---

## Scalability Considerations

### Current Limits

- **Books:** Tested up to 100 books
- **Chunks:** Up to 200K chunks (200+ books)
- **Query speed:** Acceptable up to 500K chunks

### Scaling Up

**For 500+ books:**
1. Consider cloud vector database (Pinecone)
2. Use batch processing for indexing
3. Implement caching layer
4. Consider distributed ChromaDB

**For enterprise:**
1. Deploy MCP servers on shared infrastructure
2. Use managed Tableau Server
3. Implement rate limiting
4. Add monitoring and alerts

---

## Extension Points

### Adding New Book Sources

Current: Local PDF files

**Could add:**
- EPUB files
- Web scraping (documentation sites)
- Markdown files (GitHub repos)
- Word documents (.docx)

**Implementation:** Create new processor in `scripts/`

---

### Adding New Data Sources

Current: Tableau only

**Could add:**
- Power BI (via REST API)
- Databases (PostgreSQL, MySQL)
- Excel files
- Google Sheets

**Implementation:** Create new MCP server

---

### Custom Embedding Models

Current: sentence-transformers

**Could use:**
- OpenAI embeddings (ada-002)
- Cohere embeddings
- Domain-specific models
- Fine-tuned models

**Implementation:** Modify `src/server.py` embedding logic

---

## Future Architecture Improvements

**Planned:**
1. Web UI for configuration and testing
2. Docker containerization
3. Kubernetes deployment option
4. Multi-user support
5. API endpoint exposure
6. Caching layer (Redis)
7. Monitoring and metrics

---

## References

- [Model Context Protocol Spec](https://modelcontextprotocol.io)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Tableau REST API](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm)

---

**Architecture subject to change as project evolves.**
