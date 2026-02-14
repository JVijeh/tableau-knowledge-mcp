#!/usr/bin/env python3
"""
PDF Indexing Script for Technical Knowledge Base MCP

Usage:
    python index_books.py --pdf-dir /path/to/pdfs
    python index_books.py --pdf-dir /path/to/pdfs --reindex
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    import PyPDF2
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFIndexer:
    """Handles PDF processing and ChromaDB indexing"""
    
    def __init__(self, pdf_dir: str, chroma_path: str = None):
        self.pdf_dir = Path(pdf_dir)
        self.chroma_path = chroma_path or os.getenv('CHROMA_DB_PATH', './chroma_db')
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1000))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 200))
        
        # Initialize embedding model
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        logger.info(f"Initializing ChromaDB at: {self.chroma_path}")
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(name="technical_books")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error reading {pdf_path.name}: {e}")
            return ""
    
    def chunk_text(self, text: str, source: str) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            chunks.append({
                'id': f"{source}_chunk_{chunk_id}",
                'text': chunk,
                'source': source
            })
            
            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1
        
        return chunks
    
    def index_pdfs(self, reindex: bool = False):
        """Index all PDFs in the directory"""
        if reindex:
            logger.info("Reindexing: clearing existing collection...")
            self.client.delete_collection("technical_books")
            self.collection = self.client.create_collection(name="technical_books")
        
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        logger.info(f"📚 Found {len(pdf_files)} PDF files")
        
        total_chunks = 0
        successful = 0
        
        for i, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
            
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                logger.warning(f"Skipping {pdf_path.name} - no text extracted")
                continue
            
            chunks = self.chunk_text(text, pdf_path.stem)
            
            # Add to ChromaDB in batches
            batch_size = 100
            for j in range(0, len(chunks), batch_size):
                batch = chunks[j:j+batch_size]
                self.collection.add(
                    ids=[c['id'] for c in batch],
                    documents=[c['text'] for c in batch],
                    metadatas=[{'source': c['source']} for c in batch]
                )
            
            total_chunks += len(chunks)
            successful += 1
            logger.info(f"  ✓ Indexed {len(chunks)} chunks")
        
        logger.info(f"\n✅ Indexing complete!")
        logger.info(f"📊 Successfully indexed: {successful}/{len(pdf_files)} books")
        logger.info(f"📊 Total chunks: {total_chunks}")
        logger.info(f"📊 Average chunks per book: {total_chunks//successful if successful > 0 else 0}")


def main():
    parser = argparse.ArgumentParser(description='Index PDF books for Technical Knowledge Base MCP')
    parser.add_argument('--pdf-dir', required=True, help='Directory containing PDF files')
    parser.add_argument('--reindex', action='store_true', help='Clear existing index and reindex')
    parser.add_argument('--chroma-path', help='Path to ChromaDB storage')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_dir):
        logger.error(f"PDF directory not found: {args.pdf_dir}")
        sys.exit(1)
    
    indexer = PDFIndexer(args.pdf_dir, args.chroma_path)
    indexer.index_pdfs(reindex=args.reindex)


if __name__ == "__main__":
    main()
