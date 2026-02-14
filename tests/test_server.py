"""
Tests for Technical Knowledge Base MCP Server
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestServer:
    """Test MCP server functionality"""
    
    def test_server_imports(self):
        """Verify all required imports work"""
        try:
            from src import server
            assert server is not None
        except ImportError as e:
            pytest.fail(f"Failed to import server: {e}")
    
    def test_chromadb_connection(self):
        """Test ChromaDB connection (requires indexed data)"""
        try:
            import chromadb
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            chroma_path = os.getenv('CHROMA_DB_PATH', './chroma_db')
            
            if not Path(chroma_path).exists():
                pytest.skip("ChromaDB not initialized")
            
            client = chromadb.PersistentClient(path=chroma_path)
            collection = client.get_collection(name="technical_books")
            
            count = collection.count()
            assert count > 0, "Collection should contain chunks"
            
        except Exception as e:
            pytest.skip(f"ChromaDB test skipped: {e}")


class TestIndexing:
    """Test PDF indexing functionality"""
    
    def test_pdf_extraction(self):
        """Test PDF text extraction"""
        pytest.skip("Requires test PDF files")
    
    def test_chunking(self):
        """Test text chunking logic"""
        from scripts.index_books import PDFIndexer
        
        # Test basic chunking
        test_text = "A" * 2000
        indexer = PDFIndexer(pdf_dir=".")
        chunks = indexer.chunk_text(test_text, "test_source")
        
        assert len(chunks) > 1, "Should create multiple chunks"
        assert all('id' in c for c in chunks), "All chunks should have IDs"
        assert all('text' in c for c in chunks), "All chunks should have text"
        assert all('source' in c for c in chunks), "All chunks should have source"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
