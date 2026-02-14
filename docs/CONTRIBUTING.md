# Contributing to Tableau Technical Knowledge Base MCP

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community and project
- Show empathy toward other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory language
- Personal attacks or insults
- Publishing others' private information
- Spamming or excessive self-promotion
- Any conduct that could reasonably be considered inappropriate

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
1. Check existing issues to avoid duplicates
2. Try the latest version to see if it's already fixed
3. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- System information (OS, Python version, etc.)
- Error messages or logs
- Screenshots if applicable

**Use this template:**

```markdown
**Description:**
A clear description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: [e.g., Windows 11, macOS 14]
- Python Version: [e.g., 3.11.5]
- ChromaDB Version: [e.g., 0.4.18]

**Additional Context:**
Any other relevant information
```

---

### Suggesting Enhancements

**Before suggesting an enhancement:**
1. Check if it's already suggested in Issues
2. Consider if it fits the project's scope
3. Think about how it benefits other users

**When suggesting an enhancement, include:**
- Clear, descriptive title
- Detailed description of the enhancement
- Why this enhancement would be useful
- Examples of how it would work
- Possible implementation approach (optional)

---

### Contributing Code

Areas where contributions are especially welcome:

**High Priority:**
- Bug fixes
- Performance improvements
- Documentation improvements
- Test coverage expansion

**Medium Priority:**
- New PDF processing features
- Support for other document formats
- Alternative embedding models
- Web UI development

**Nice to Have:**
- Docker support
- Additional BI tool integrations
- Advanced analytics features
- Internationalization

---

### Improving Documentation

Documentation contributions are highly valued:

- Fix typos and grammatical errors
- Improve clarity and readability
- Add examples and use cases
- Translate to other languages
- Create video tutorials
- Write blog posts about the project

---

## Getting Started

### Development Setup

1. **Fork the repository**

   Click "Fork" on GitHub to create your copy

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/tableau-knowledge-mcp.git
   cd tableau-knowledge-mcp
   ```

3. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/tableau-knowledge-mcp.git
   ```

4. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

5. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

6. **Create development branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Workflow

### Branch Naming

Use descriptive branch names:

- `feature/add-epub-support` - New features
- `fix/pdf-encoding-error` - Bug fixes
- `docs/improve-installation-guide` - Documentation
- `test/add-server-tests` - Tests
- `refactor/optimize-chunking` - Code improvements

---

### Making Changes

1. **Write code**

   Follow [Coding Standards](#coding-standards)

2. **Test your changes**

   ```bash
   # Run tests
   pytest tests/

   # Run specific test
   pytest tests/test_server.py -v

   # Check code coverage
   pytest --cov=src tests/
   ```

3. **Lint your code**

   ```bash
   # Format code
   black src/ scripts/ tests/

   # Check for style issues
   flake8 src/ scripts/ tests/

   # Type checking
   mypy src/
   ```

4. **Update documentation**

   If you changed functionality, update relevant docs

---

### Commit Messages

**Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(indexing): Add support for EPUB files

- Implemented EPUB parser using ebooklib
- Added EPUB to supported file types
- Updated documentation

Closes #123
```

```
fix(server): Handle missing ChromaDB gracefully

Previously crashed with unclear error. Now shows
helpful message and suggests running indexing script.

Fixes #456
```

---

## Coding Standards

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

**Formatting:**
- Line length: 88 characters (Black default)
- Indentation: 4 spaces
- Quotes: Double quotes for strings
- Imports: Grouped (stdlib, third-party, local)

**Naming:**
```python
# Classes: PascalCase
class PDFIndexer:
    pass

# Functions and variables: snake_case
def index_books():
    chunk_size = 1000

# Constants: UPPER_SNAKE_CASE
MAX_CHUNK_SIZE = 5000

# Private: Leading underscore
def _internal_function():
    pass
```

**Docstrings:**
```python
def search_books(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search the technical book library.

    Args:
        query: Search query text
        max_results: Maximum number of results to return

    Returns:
        List of search results with text, source, and relevance score

    Raises:
        ValueError: If query is empty
        ConnectionError: If ChromaDB is unavailable
    """
    pass
```

---

### Code Quality

**Type Hints:**
```python
# Use type hints for function signatures
def process_pdf(file_path: Path) -> List[str]:
    pass

# Use from __future__ import annotations for complex types
from __future__ import annotations
from typing import List, Dict, Optional
```

**Error Handling:**
```python
# Be specific with exceptions
try:
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
except FileNotFoundError:
    logger.error(f"PDF not found: {file_path}")
    raise
except PyPDF2.errors.PdfReadError:
    logger.error(f"Corrupted PDF: {file_path}")
    return []
```

**Logging:**
```python
# Use appropriate log levels
logger.debug("Processing chunk 42")
logger.info("Indexed 83 books successfully")
logger.warning("Failed to process 3 PDFs")
logger.error("ChromaDB connection failed")
```

---

## Testing Guidelines

### Writing Tests

**Test Structure:**
```python
import pytest
from src.server import search_books

class TestBookSearch:
    """Tests for book search functionality"""

    def test_search_returns_results(self):
        """Search should return relevant results"""
        results = search_books("LOD calculations")
        assert len(results) > 0
        assert all('text' in r for r in results)

    def test_search_empty_query_raises_error(self):
        """Empty query should raise ValueError"""
        with pytest.raises(ValueError):
            search_books("")

    @pytest.mark.slow
    def test_search_large_library(self):
        """Search should handle large libraries"""
        # Test with 10,000+ chunks
        pass
```

**Fixtures:**
```python
@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF for testing"""
    pdf_path = tmp_path / "test.pdf"
    # Create PDF...
    return pdf_path

def test_pdf_processing(sample_pdf):
    """Test PDF text extraction"""
    text = extract_text(sample_pdf)
    assert len(text) > 0
```

---

### Running Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_server.py

# Specific test
pytest tests/test_server.py::test_search_books

# With coverage
pytest --cov=src --cov-report=html

# Skip slow tests
pytest -m "not slow"
```

---

### Test Coverage

**Minimum requirements:**
- New code: 80% coverage
- Critical paths: 100% coverage
- Bug fixes: Include regression test

**Check coverage:**
```bash
pytest --cov=src tests/
```

View detailed report:
```bash
coverage html
open htmlcov/index.html
```

---

## Documentation

### Code Documentation

**Required:**
- Module-level docstrings
- Class docstrings
- Public function docstrings
- Complex logic inline comments

**Example:**
```python
"""
PDF Indexing Module

This module handles PDF processing and ChromaDB indexing for the
technical knowledge base MCP server.
"""

class PDFIndexer:
    """
    Processes PDF files and creates ChromaDB vector index.

    Attributes:
        pdf_dir: Directory containing PDF files
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between consecutive chunks
    """

    def index_pdfs(self) -> None:
        """
        Index all PDFs in the configured directory.

        Process:
        1. Find all PDF files recursively
        2. Extract text from each PDF
        3. Split into chunks
        4. Generate embeddings
        5. Store in ChromaDB

        Raises:
            FileNotFoundError: If PDF directory doesn't exist
            RuntimeError: If ChromaDB is not initialized
        """
        pass
```

---

### User Documentation

When adding features, update:
- README.md (if user-facing)
- INSTALLATION.md (if affects setup)
- Example queries (if adds capabilities)
- TROUBLESHOOTING.md (if adds failure modes)

---

## Submitting Changes

### Pull Request Process

1. **Ensure quality**

   - All tests pass
   - Code is formatted (black)
   - No linting errors (flake8)
   - Documentation updated

2. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create pull request**

   - Go to GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out PR template

4. **PR template:**

   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring

   ## Testing
   - [ ] Tests added/updated
   - [ ] All tests pass
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated

   ## Related Issues
   Closes #123
   Related to #456
   ```

5. **Respond to feedback**

   - Address review comments
   - Push updates to same branch
   - Request re-review when ready

---

### Review Process

**What reviewers look for:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations
- Backwards compatibility

**Timeline:**
- Initial review: Within 3-5 days
- Follow-up reviews: Within 1-2 days
- Merge: After approval from 1+ maintainers

---

## Development Tips

### Local Testing

**Test with your own data:**
```bash
# Use a small test library
export PDF_LIBRARY_PATH="/path/to/test/pdfs"
python scripts/index_books.py --pdf-dir "$PDF_LIBRARY_PATH"
```

**Test MCP server locally:**
```bash
# Run server directly
python src/server.py

# Test with sample queries
# (requires MCP client or manual JSON-RPC)
```

---

### Debugging

**Enable debug logging:**
```env
# In .env
LOG_LEVEL=DEBUG
LOG_FILE=./logs/debug.log
```

**Use Python debugger:**
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

**ChromaDB debugging:**
```python
# List collections
client.list_collections()

# Count documents
collection.count()

# Peek at data
collection.peek()
```

---

### Performance Profiling

**Profile indexing:**
```bash
python -m cProfile -o profile.stats scripts/index_books.py --pdf-dir "/path"
```

**Analyze profile:**
```python
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
```

---

## Questions?

- **General questions:** Use GitHub Discussions
- **Bug reports:** Open an Issue
- **Security issues:** Email maintainers directly
- **Feature ideas:** Open an Issue with "enhancement" label

---

## Recognition

Contributors will be:
- Listed in project README
- Credited in release notes
- Invited to future project decisions

**Thank you for contributing!** 🎉
