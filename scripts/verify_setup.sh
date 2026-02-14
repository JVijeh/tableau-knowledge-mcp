#!/bin/bash

# Tableau Knowledge MCP Setup Verification Script
# This script checks that all prerequisites are met

echo "🔍 Verifying Tableau Knowledge MCP Setup..."
echo "==========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ERRORS=0

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check Python version
echo "1. Checking Python version..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        success "Python $PYTHON_VERSION installed"
    else
        error "Python 3.9+ required, found $PYTHON_VERSION"
    fi
else
    error "Python not found in PATH"
fi
echo ""

# 2. Check virtual environment
echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    success "Virtual environment directory exists"
    
    # Check if venv is activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        success "Virtual environment is activated"
    else
        warning "Virtual environment exists but is not activated"
        echo "   Run: source venv/bin/activate (Mac/Linux) or venv\\Scripts\\activate (Windows)"
    fi
else
    error "Virtual environment not found"
    echo "   Run: python -m venv venv"
fi
echo ""

# 3. Check required dependencies
echo "3. Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    success "requirements.txt found"
    
    # Check if key packages are installed
    PACKAGES=("chromadb" "sentence-transformers" "PyPDF2" "python-dotenv")
    for package in "${PACKAGES[@]}"; do
        if python -c "import $package" &> /dev/null; then
            success "$package installed"
        else
            error "$package not installed"
            echo "   Run: pip install -r requirements.txt"
        fi
    done
else
    error "requirements.txt not found"
fi
echo ""

# 4. Check .env file
echo "4. Checking environment configuration..."
if [ -f ".env" ]; then
    success ".env file exists"
    
    # Check for required variables
    source .env 2>/dev/null
    
    REQUIRED_VARS=("TABLEAU_SERVER_URL" "TABLEAU_SITE_NAME" "TABLEAU_PAT_NAME" "TABLEAU_PAT_SECRET" "PDF_LIBRARY_PATH")
    for var in "${REQUIRED_VARS[@]}"; do
        if [ ! -z "${!var}" ]; then
            success "$var is set"
        else
            error "$var is not set in .env"
        fi
    done
else
    error ".env file not found"
    echo "   Run: cp .env.example .env"
    echo "   Then edit .env with your credentials"
fi
echo ""

# 5. Check PDF library path
echo "5. Checking PDF library..."
if [ ! -z "$PDF_LIBRARY_PATH" ] && [ -d "$PDF_LIBRARY_PATH" ]; then
    PDF_COUNT=$(find "$PDF_LIBRARY_PATH" -name "*.pdf" | wc -l)
    success "PDF library directory exists"
    success "Found $PDF_COUNT PDF files"
    
    if [ $PDF_COUNT -eq 0 ]; then
        warning "No PDF files found in $PDF_LIBRARY_PATH"
    fi
else
    error "PDF library path not found or not set"
fi
echo ""

# 6. Check ChromaDB index
echo "6. Checking ChromaDB index..."
CHROMA_PATH="${CHROMA_DB_PATH:-./chroma_db}"
if [ -d "$CHROMA_PATH" ]; then
    success "ChromaDB directory exists"
    
    # Check if it has data
    if [ "$(ls -A $CHROMA_PATH)" ]; then
        success "ChromaDB index contains data"
        
        # Estimate size
        CHROMA_SIZE=$(du -sh "$CHROMA_PATH" 2>/dev/null | cut -f1)
        echo "   Index size: $CHROMA_SIZE"
    else
        warning "ChromaDB directory is empty"
        echo "   Run: python scripts/index_books.py --pdf-dir \"$PDF_LIBRARY_PATH\""
    fi
else
    warning "ChromaDB index not found"
    echo "   Run: python scripts/index_books.py --pdf-dir \"$PDF_LIBRARY_PATH\""
fi
echo ""

# 7. Check Tableau connectivity
echo "7. Checking Tableau connectivity..."
if [ ! -z "$TABLEAU_SERVER_URL" ] && [ ! -z "$TABLEAU_PAT_NAME" ] && [ ! -z "$TABLEAU_PAT_SECRET" ]; then
    # Try to ping the server (basic check)
    if curl -s --head --request GET "$TABLEAU_SERVER_URL" | grep "200\|301\|302" > /dev/null; then
        success "Tableau server is reachable"
    else
        warning "Could not reach Tableau server (might require authentication)"
    fi
else
    error "Tableau credentials not configured"
fi
echo ""

# 8. Check Claude Desktop config
echo "8. Checking Claude Desktop configuration..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
else
    # Linux
    CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
fi

if [ -f "$CLAUDE_CONFIG" ]; then
    success "Claude Desktop config file exists"
    
    # Check if our MCP servers are configured
    if grep -q "technical-knowledge-base" "$CLAUDE_CONFIG"; then
        success "Technical knowledge base MCP configured"
    else
        warning "Technical knowledge base MCP not found in config"
    fi
    
    if grep -q "tableau" "$CLAUDE_CONFIG"; then
        success "Tableau MCP configured"
    else
        warning "Tableau MCP not found in config"
    fi
else
    warning "Claude Desktop config not found at $CLAUDE_CONFIG"
    echo "   See: examples/claude_desktop_config.json"
fi
echo ""

# 9. Check MCP server code
echo "9. Checking MCP server files..."
if [ -f "src/server.py" ]; then
    success "MCP server code exists"
else
    error "src/server.py not found"
fi
echo ""

# Summary
echo "==========================================="
echo "Verification Summary"
echo "==========================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart Claude Desktop"
    echo "2. Check for 🔌 icon in bottom-right"
    echo "3. Verify both MCP servers show as connected"
    echo "4. Try a test query: 'List all books in my technical knowledge base'"
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
    echo ""
    echo "Please fix the errors above before proceeding."
    echo "See docs/INSTALLATION.md for detailed help."
fi

echo ""
