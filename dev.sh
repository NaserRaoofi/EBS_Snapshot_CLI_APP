#!/bin/bash

# EBS Snapshot CLI Application - Development Setup Script
# This script sets up the development environment and provides common commands

set -e

echo "🚀 EBS Snapshot CLI Application - Development Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    print_error "Poetry is not installed. Please install Poetry first:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Main setup function
setup() {
    print_status "Installing dependencies..."
    poetry install
    
    print_status "Running tests to verify setup..."
    poetry run pytest tests/unit/ -v
    
    print_success "Setup completed successfully!"
    echo ""
    echo "Available commands:"
    echo "  ./dev.sh run          - Run the CLI application"
    echo "  ./dev.sh test         - Run all tests"
    echo "  ./dev.sh test-unit    - Run unit tests only"
    echo "  ./dev.sh test-integration - Run integration tests only"
    echo "  ./dev.sh lint         - Run code quality checks"
    echo "  ./dev.sh format       - Format code with black"
    echo "  ./dev.sh help         - Show this help message"
}

# Run the CLI application
run() {
    print_status "Running EBS Snapshot CLI..."
    poetry run python -m src.presentation.cli.main
}

# Run tests
test() {
    print_status "Running all tests..."
    poetry run pytest tests/ -v
}

test_unit() {
    print_status "Running unit tests..."
    poetry run pytest tests/unit/ -v
}

test_integration() {
    print_status "Running integration tests..."
    poetry run pytest tests/integration/ -v
}

# Code quality checks
lint() {
    print_status "Running code quality checks..."
    poetry run flake8 src/
    poetry run mypy src/
    poetry run bandit -r src/
    print_success "Code quality checks passed!"
}

# Format code
format() {
    print_status "Formatting code with black..."
    poetry run black src/ tests/
    print_success "Code formatting completed!"
}

# Show help
show_help() {
    echo "EBS Snapshot CLI - Development Script"
    echo ""
    echo "Usage: ./dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup             - Install dependencies and set up environment"
    echo "  run               - Run the CLI application"
    echo "  test              - Run all tests"
    echo "  test-unit         - Run unit tests only"
    echo "  test-integration  - Run integration tests only"
    echo "  lint              - Run code quality checks"
    echo "  format            - Format code with black"
    echo "  help              - Show this help message"
    echo ""
    echo "Example:"
    echo "  ./dev.sh setup    # Set up the development environment"
    echo "  ./dev.sh run      # Run the application"
    echo "  ./dev.sh test     # Run all tests"
}

# Main script logic
case "${1:-help}" in
    setup)
        setup
        ;;
    run)
        run
        ;;
    test)
        test
        ;;
    test-unit)
        test_unit
        ;;
    test-integration)
        test_integration
        ;;
    lint)
        lint
        ;;
    format)
        format
        ;;
    help|*)
        show_help
        ;;
esac
