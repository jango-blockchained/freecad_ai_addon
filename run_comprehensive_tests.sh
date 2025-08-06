#!/bin/bash
# Comprehensive Test Runner for FreeCAD AI Addon
# This script runs all tests with different configurations and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not activated"
        if [ -d "venv" ]; then
            print_status "Activating virtual environment..."
            source venv/bin/activate
        else
            print_error "No virtual environment found. Run setup_dev_env.sh first."
            exit 1
        fi
    fi
}

# Run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    # Create test reports directory
    mkdir -p test_reports
    
    # Run tests with coverage
    python -m pytest tests/ \
        --verbose \
        --cov=freecad_ai_addon \
        --cov-report=html:test_reports/coverage_html \
        --cov-report=xml:test_reports/coverage.xml \
        --cov-report=term-missing \
        --junit-xml=test_reports/junit.xml \
        --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed"
    else
        print_error "Unit tests failed"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    # Integration tests (the test_*.py files in root)
    python -m pytest test_*.py \
        --verbose \
        --tb=short \
        --junit-xml=test_reports/integration_junit.xml
    
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed"
    else
        print_warning "Some integration tests failed (this may be expected without FreeCAD)"
    fi
}

# Run agent framework tests
run_agent_tests() {
    print_status "Running agent framework tests..."
    
    python -m pytest test_agent_*.py test_complete_*.py \
        --verbose \
        --tb=short \
        --junit-xml=test_reports/agent_junit.xml
    
    if [ $? -eq 0 ]; then
        print_success "Agent tests passed"
    else
        print_warning "Some agent tests failed (this may be expected without FreeCAD)"
    fi
}

# Run linting
run_linting() {
    print_status "Running code linting..."
    
    # Create lint reports directory
    mkdir -p test_reports/lint
    
    # Run flake8
    print_status "Running flake8..."
    flake8 freecad_ai_addon/ \
        --max-line-length=88 \
        --extend-ignore=E203,W503 \
        --output-file=test_reports/lint/flake8.txt \
        --tee || true
    
    # Run black check
    print_status "Checking code formatting with black..."
    black --check --diff freecad_ai_addon/ > test_reports/lint/black.txt 2>&1 || true
    
    # Run mypy
    print_status "Running type checking with mypy..."
    mypy freecad_ai_addon/ \
        --ignore-missing-imports \
        --show-error-codes \
        --pretty \
        > test_reports/lint/mypy.txt 2>&1 || true
    
    print_success "Linting completed (check reports for details)"
}

# Run security checks
run_security_checks() {
    print_status "Running security checks..."
    
    mkdir -p test_reports/security
    
    # Run bandit security linter
    print_status "Running bandit security analysis..."
    bandit -r freecad_ai_addon/ \
        -f json \
        -o test_reports/security/bandit.json || true
    
    bandit -r freecad_ai_addon/ \
        -f txt \
        -o test_reports/security/bandit.txt || true
    
    # Check dependencies for vulnerabilities
    print_status "Checking dependencies for vulnerabilities..."
    safety check \
        --json \
        --output test_reports/security/safety.json || true
    
    safety check \
        --output test_reports/security/safety.txt || true
    
    print_success "Security checks completed"
}

# Generate test report summary
generate_summary() {
    print_status "Generating test summary..."
    
    cat > test_reports/summary.txt << EOF
FreeCAD AI Addon Test Summary
============================
Generated: $(date)

Test Results:
- Unit Tests: See junit.xml
- Integration Tests: See integration_junit.xml  
- Agent Tests: See agent_junit.xml
- Coverage Report: See coverage_html/index.html

Code Quality:
- Linting: See lint/ directory
- Security: See security/ directory

Files Generated:
EOF
    
    ls -la test_reports/ >> test_reports/summary.txt
    
    print_success "Test summary generated: test_reports/summary.txt"
}

# Show test results
show_results() {
    echo
    echo "=========================================="
    echo "         Test Results Summary"
    echo "=========================================="
    echo
    
    if [ -f "test_reports/coverage.xml" ]; then
        # Extract coverage percentage
        coverage=$(grep -o 'line-rate="[^"]*"' test_reports/coverage.xml | head -1 | cut -d'"' -f2)
        coverage_percent=$(python3 -c "print(f'{float('$coverage') * 100:.1f}%')")
        print_status "Code Coverage: $coverage_percent"
    fi
    
    if [ -f "test_reports/junit.xml" ]; then
        # Extract test counts
        tests=$(grep -o 'tests="[^"]*"' test_reports/junit.xml | head -1 | cut -d'"' -f2)
        failures=$(grep -o 'failures="[^"]*"' test_reports/junit.xml | head -1 | cut -d'"' -f2)
        errors=$(grep -o 'errors="[^"]*"' test_reports/junit.xml | head -1 | cut -d'"' -f2)
        
        print_status "Unit Tests: $tests total, $failures failures, $errors errors"
    fi
    
    echo
    echo "Detailed reports available in test_reports/ directory"
    echo "Open test_reports/coverage_html/index.html in a browser for coverage details"
    echo
}

# Main execution
main() {
    echo "FreeCAD AI Addon - Comprehensive Test Runner"
    echo "==========================================="
    echo
    
    # Parse command line arguments
    RUN_UNIT=true
    RUN_INTEGRATION=true
    RUN_AGENT=true
    RUN_LINT=true
    RUN_SECURITY=true
    
    case "${1:-all}" in
        "unit")
            RUN_INTEGRATION=false
            RUN_AGENT=false
            RUN_LINT=false
            RUN_SECURITY=false
            ;;
        "integration")
            RUN_UNIT=false
            RUN_AGENT=false
            RUN_LINT=false
            RUN_SECURITY=false
            ;;
        "agent")
            RUN_UNIT=false
            RUN_INTEGRATION=false
            RUN_LINT=false
            RUN_SECURITY=false
            ;;
        "lint")
            RUN_UNIT=false
            RUN_INTEGRATION=false
            RUN_AGENT=false
            RUN_SECURITY=false
            ;;
        "security")
            RUN_UNIT=false
            RUN_INTEGRATION=false
            RUN_AGENT=false
            RUN_LINT=false
            ;;
        "all"|"")
            ;;
        *)
            echo "Usage: $0 [unit|integration|agent|lint|security|all]"
            exit 1
            ;;
    esac
    
    check_venv
    
    # Run selected tests
    [ "$RUN_UNIT" = true ] && run_unit_tests
    [ "$RUN_INTEGRATION" = true ] && run_integration_tests
    [ "$RUN_AGENT" = true ] && run_agent_tests
    [ "$RUN_LINT" = true ] && run_linting
    [ "$RUN_SECURITY" = true ] && run_security_checks
    
    generate_summary
    show_results
    
    print_success "All tests completed!"
}

# Run main function with all arguments
main "$@"
