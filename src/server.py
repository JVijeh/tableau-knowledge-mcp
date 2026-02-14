#!/usr/bin/env python3
"""
Technical Knowledge Base MCP Server

Provides semantic search across indexed PDF technical books.
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import chromadb
    from chromadb.config import Settings
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error importing dependencies: {e}", file=sys.stderr)
    print("Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize ChromaDB client
chroma_path = os.getenv('CHROMA_DB_PATH', './chroma_db')
logger.info(f"Connecting to ChromaDB at: {chroma_path}")

try:
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(name="technical_books")
    logger.info(f"Connected to collection with {collection.count()} chunks")
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB: {e}")
    logger.error("Run: python scripts/index_books.py --pdf-dir /path/to/pdfs")
    sys.exit(1)

# Initialize MCP Server
app = Server("technical-knowledge-base")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_technical_books",
            description="Search across your technical book library for relevant information. "
                       "Use natural language queries to find content about programming, data science, "
                       "analytics, or any technical topic covered in your books.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (e.g., 'LOD calculations', 'pandas merge', 'SQL joins')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    },
                    "filter_topic": {
                        "type": "string",
                        "description": "Optional filter by topic (e.g., 'tableau', 'python', 'sql')",
                        "default": None
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_available_books",
            description="Get a list of all books in the knowledge base with their metadata",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "search_technical_books":
        query = arguments.get("query")
        max_results = arguments.get("max_results", 5)
        filter_topic = arguments.get("filter_topic")
        
        logger.info(f"Searching for: {query}")
        
        try:
            # Build filter if topic specified
            where_filter = None
            if filter_topic:
                where_filter = {"source": {"$contains": filter_topic.lower()}}
            
            # Query ChromaDB
            results = collection.query(
                query_texts=[query],
                n_results=max_results,
                where=where_filter
            )
            
            if not results['documents'][0]:
                return [TextContent(
                    type="text",
                    text=f"No results found for: '{query}'"
                )]
            
            # Format results
            output = f"Found {len(results['documents'][0])} results for: '{query}'\n\n"
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                source = metadata.get('source', 'Unknown')
                relevance = 1 - distance  # Convert distance to relevance score
                
                output += f"### Result {i} (Relevance: {relevance:.2f})\n"
                output += f"**Source:** {source}\n"
                output += f"**Content:**\n{doc}\n\n---\n\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [TextContent(
                type="text",
                text=f"Error searching books: {str(e)}"
            )]
    
    elif name == "list_available_books":
        try:
            # Get all unique sources from metadata
            all_metadata = collection.get()['metadatas']
            sources = sorted(set(m['source'] for m in all_metadata))
            
            output = f"# Available Books\n\n"
            output += f"Total books indexed: {len(sources)}\n\n"
            
            for i, source in enumerate(sources, 1):
                # Count chunks for this book
                book_results = collection.get(where={"source": source})
                chunk_count = len(book_results['ids'])
                
                output += f"{i}. **{source}** - {chunk_count} indexed chunks\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"List books error: {e}")
            return [TextContent(
                type="text",
                text=f"Error listing books: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


def main():
    """Run the MCP server"""
    logger.info("Starting Technical Knowledge Base MCP Server...")
    
    # Import and run the server
    from mcp.server.stdio import stdio_server
    
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    
    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()
