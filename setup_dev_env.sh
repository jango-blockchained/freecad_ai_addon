#!/bin/bash
# Virtual Environment Setup Script for FreeCAD AI Addon
# This script sets up a development environment for the FreeCAD AI Addon

set -e  # Exit on any error

echo "=== FreeCAD AI Addon Development Setup ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is available
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.8+
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8+ is required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or later."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Remove it? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf venv
            print_status "Removed existing virtual environment"
        else
            print_status "Using existing virtual environment"
            return
        fi
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Requirements installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install development dependencies
    pip install pytest pytest-cov black flake8 mypy sphinx sphinx-rtd-theme
    print_success "Development dependencies installed"
}

# Setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."
    
    pip install pre-commit
    
    # Create pre-commit config if it doesn't exist
    if [ ! -f ".pre-commit-config.yaml" ]; then
        cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
EOF
        print_success "Created pre-commit configuration"
    fi
    
    pre-commit install
    print_success "Pre-commit hooks installed"
}

# Create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Test script
    cat > run_tests.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python -m pytest tests/ -v --cov=freecad_ai_addon --cov-report=html
EOF
    chmod +x run_tests.sh
    
    # Lint script
    cat > run_lint.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo "Running Black..."
black freecad_ai_addon/
echo "Running Flake8..."
flake8 freecad_ai_addon/
echo "Running MyPy..."
mypy freecad_ai_addon/ --ignore-missing-imports
EOF
    chmod +x run_lint.sh
    
    # Format script
    cat > format_code.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
black freecad_ai_addon/
black tests/
EOF
    chmod +x format_code.sh
    
    print_success "Development scripts created"
}

# Main setup function
main() {
    echo
    print_status "Starting FreeCAD AI Addon development environment setup..."
    echo
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    setup_pre_commit
    create_dev_scripts
    
    echo
    print_success "Development environment setup complete!"
    echo
    echo "To get started:"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Run tests: ./run_tests.sh"
    echo "  3. Format code: ./format_code.sh"
    echo "  4. Run linting: ./run_lint.sh"
    echo
    echo "The virtual environment includes:"
    echo "  • All required dependencies from requirements.txt"
    echo "  • Development tools (pytest, black, flake8, mypy)"
    echo "  • Documentation tools (sphinx)"
    echo "  • Pre-commit hooks for code quality"
    echo
}

# Run main function
main
