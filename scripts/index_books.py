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
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        # Only add if text exists and is a string
                        if page_text and isinstance(page_text, str):
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num} from {pdf_path.name}: {e}")
                        continue
                
                # Ensure we return a valid string
                if not text or not isinstance(text, str) or len(text.strip()) == 0:
                    logger.warning(f"No valid text extracted from {pdf_path.name}")
                    return ""
                
                return text
                
        except Exception as e:
            logger.error(f"Error reading {pdf_path.name}: {e}")
            return ""
    
    def chunk_text(self, text: str, source: str) -> List[Dict]:
        """Split text into overlapping chunks"""
        # Validate input
        if not text or not isinstance(text, str):
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Only add non-empty chunks
            if chunk and len(chunk.strip()) > 0:
                chunks.append({
                    'id': f"{source}_chunk_{chunk_id}",
                    'text': chunk,
                    'source': source
                })
                chunk_id += 1
            
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def index_pdfs(self, reindex: bool = False):
        """Index all PDFs in the directory"""
        if reindex:
            logger.info("Reindexing: clearing existing collection...")
            self.client.delete_collection("technical_books")
            self.collection = self.client.create_collection(name="technical_books")
        
        # Find all PDF files recursively (includes subdirectories)
        pdf_files = list(self.pdf_dir.glob("**/*.pdf"))
        logger.info(f"📚 Found {len(pdf_files)} PDF files")
        
        if len(pdf_files) == 0:
            logger.warning(f"No PDF files found in {self.pdf_dir}")
            logger.warning("Check that the path is correct and contains PDF files")
            return
        
        total_chunks = 0
        successful = 0
        failed = []
        
        for i, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            # Skip if no text extracted
            if not text:
                logger.warning(f"  ⚠️ Skipping {pdf_path.name} - no text extracted")
                failed.append(pdf_path.name)
                continue
            
            # Create chunks
            chunks = self.chunk_text(text, pdf_path.stem)
            
            # Skip if no chunks created
            if not chunks:
                logger.warning(f"  ⚠️ Skipping {pdf_path.name} - no chunks created")
                failed.append(pdf_path.name)
                continue
            
            # Add to ChromaDB in batches
            batch_size = 100
            try:
                for j in range(0, len(chunks), batch_size):
                    batch = chunks[j:j+batch_size]
                    
                    # Validate batch data before adding
                    valid_batch = []
                    for c in batch:
                        if (c.get('text') and 
                            isinstance(c['text'], str) and 
                            len(c['text'].strip()) > 0):
                            valid_batch.append(c)
                    
                    if valid_batch:
                        self.collection.add(
                            ids=[c['id'] for c in valid_batch],
                            documents=[c['text'] for c in valid_batch],
                            metadatas=[{'source': c['source']} for c in valid_batch]
                        )
                
                total_chunks += len(chunks)
                successful += 1
                logger.info(f"  ✓ Indexed {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"  ❌ Error indexing {pdf_path.name}: {e}")
                failed.append(pdf_path.name)
                continue
        
        # Summary
        logger.info(f"\n✅ Indexing complete!")
        logger.info(f"📊 Successfully indexed: {successful}/{len(pdf_files)} books")
        logger.info(f"📊 Total chunks: {total_chunks:,}")
        
        if successful > 0:
            logger.info(f"📊 Average chunks per book: {total_chunks//successful:,}")
        
        if failed:
            logger.info(f"\n⚠️ Failed to index {len(failed)} files:")
            for filename in failed[:10]:  # Show first 10
                logger.info(f"  - {filename}")
            if len(failed) > 10:
                logger.info(f"  ... and {len(failed) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description='Index PDF books for Technical Knowledge Base MCP'
    )
    parser.add_argument(
        '--pdf-dir', 
        required=True, 
        help='Directory containing PDF files (searches recursively)'
    )
    parser.add_argument(
        '--reindex', 
        action='store_true', 
        help='Clear existing index and reindex all files'
    )
    parser.add_argument(
        '--chroma-path', 
        help='Path to ChromaDB storage (default: ./chroma_db)'
    )
    
    args = parser.parse_args()
    
    # Validate PDF directory exists
    if not os.path.exists(args.pdf_dir):
        logger.error(f"PDF directory not found: {args.pdf_dir}")
        sys.exit(1)
    
    # Create indexer and run
    indexer = PDFIndexer(args.pdf_dir, args.chroma_path)
    indexer.index_pdfs(reindex=args.reindex)


if __name__ == "__main__":
    main()
