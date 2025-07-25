# Development Setup Guide

## Quick Start

```bash
# 1. Clone the repository
git clone git@github.com:NaserRaoofi/EBS_Snapshot_CLI_APP.git
cd EBS_Snapshot_CLI_APP

# 2. Set up development environment
./dev.sh setup

# 3. Run the application
./dev.sh run
```

## Development Commands

The project includes a development script (`dev.sh`) that provides common commands:

```bash
./dev.sh setup             # Install dependencies and set up environment
./dev.sh run               # Run the CLI application
./dev.sh test              # Run all tests
./dev.sh test-unit         # Run unit tests only
./dev.sh test-integration  # Run integration tests only
./dev.sh lint              # Run code quality checks
./dev.sh format            # Format code with black
./dev.sh help              # Show help message
```

## Project Structure

```
EBS_Snapshot_CLI_APP/
├── src/                           # Source code
│   ├── domain/                    # Domain layer (entities, repositories, services)
│   ├── application/               # Application layer (use cases, DTOs, validation)
│   ├── infrastructure/            # Infrastructure layer (AWS, config, logging)
│   └── presentation/              # Presentation layer (CLI)
├── tests/                         # Test files (moved from src/)
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── dev.sh                         # Development script
├── pyproject.toml                 # Project configuration
├── pytest.ini                     # Test configuration
└── README.md                      # Project documentation
```

## Recent Fixes Applied

### 🔧 **Issues Resolved:**

1. **✅ Test File Structure Fixed**
   - Moved all test files from `src/` to proper `tests/` directory
   - Fixed import paths in all test files
   - Updated `pytest.ini` configuration

2. **✅ Environment Setup**
   - Configured Python virtual environment
   - Installed Poetry and all dependencies
   - Verified all tests pass

3. **✅ Development Workflow**
   - Created `dev.sh` script for common tasks
   - Added proper project structure documentation
   - Configured code quality tools

### 🧪 **Test Results:**
- ✅ 17 unit tests passing
- ✅ All imports resolved correctly
- ✅ Clean Architecture implementation verified

### 🛠️ **Available Commands:**
```bash
# Run tests
poetry run pytest tests/unit/ -v        # Unit tests
poetry run pytest tests/integration/ -v # Integration tests

# Code quality
poetry run flake8 src/                  # Linting
poetry run mypy src/                    # Type checking
poetry run black src/ tests/            # Code formatting

# Run application
poetry run python -m src.presentation.cli.main
```

## Environment Variables

Configure your AWS credentials in `.env`:

```env
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=your-profile
```

The application is now ready for development! 🚀
