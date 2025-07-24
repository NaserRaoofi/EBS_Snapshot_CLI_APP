# EBS Snapshot Tool - Clean Architecture

This project provides a command-line interface for managing AWS EC2 snapshots using Clean Architecture principles with Domain-Driven Design.

## Architecture Overview

The project follows Clean Architecture with clear separation of concerns:

```
src/
├── domain/                 # Enterprise Business Rules
│   ├── entities/          # Domain entities (dataclasses)
│   ├── repositories/      # Repository interfaces
│   └── services/          # Domain services
├── application/           # Application Business Rules
│   ├── dtos/             # Data Transfer Objects (dataclasses)
│   ├── use_cases/        # Application use cases
│   └── validation.py     # Request validation using Pydantic
├── infrastructure/       # External Interface Adapters
│   ├── aws/              # AWS SDK implementations
│   ├── config/           # Configuration with Pydantic models
│   └── logging/          # Logging infrastructure
└── presentation/         # User Interface
    ├── cli/              # Command-line interface
    └── web/              # Future web interface
```

## Technology Stack

- **Python 3.10+** with Poetry for dependency management
- **Dataclasses** for domain entities and DTOs
- **Pydantic** for configuration validation and request validation
- **Dependency Injector** for IoC container
- **Click** for CLI interface
- **Boto3** for AWS integration

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd EBS_Snapshot_CLI_APP
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up your AWS credentials in the `.env` file:
   ```
   AWS_REGION=your_aws_region
   AWS_PROFILE=your_aws_profile
   LOG_LEVEL=INFO
   LOG_FILE=backup.log
   ```

## Usage

Run the application:
```bash
poetry run python -m src.presentation.cli.main
```

Or use the Poetry script:
```bash
poetry run ebs-snapshot
```

## Features

1. **Take Snapshot** - Create snapshots of EC2 instances with validation
2. **List Snapshots** - View all snapshots for an instance
3. **Delete Snapshot** - Remove snapshots with confirmation
4. **Restore from Snapshot** - Restore instances from snapshots

## Clean Architecture Benefits

- **Testability**: Easy to unit test with mocked dependencies
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy to add new interfaces (web, API, etc.)
- **Validation**: Pydantic ensures data integrity at boundaries
- **Configuration**: Environment-based configuration with validation

## Testing

This project uses `pytest` and `pytest-mock` for unit and CLI tests. To run all tests:

```bash
pytest
```

### Test Structure
- All tests are in the `tests/` directory.
- `pytest-mock` is used for mocking in pytest style.
- No real AWS calls are made during tests; all AWS interactions are mocked.

### Example Test Command

```bash
pytest tests/
```

## Continuous Integration

GitHub Actions will automatically lint and test your code on every push and pull request.

## CI/CD Pipeline Overview

This project uses GitHub Actions for a robust, multi-stage CI/CD pipeline:

- **Lint:** Checks code style and quality using flake8.
- **Test:** Runs all unit and integration tests with pytest.
- **Security & Quality:** Runs SonarCloud analysis, Bandit, and Gitleaks for code quality and security scanning.
- **Build:** Builds the Python package (wheel and sdist) and Docker image after all security checks pass.
- **Deploy:** Pushes the Docker image to AWS ECR only if all previous stages succeed.

### Workflow Chain
- Lint → Test → Security & Quality → Build → Deploy

### Key Workflow Files
- `.github/workflows/python_lint.yml` — Linting
- `.github/workflows/python_test.yml` — Testing
- `.github/workflows/security.yml` — Security & quality checks
- `.github/workflows/build.yml` — Build package and Docker image
- `.github/workflows/deploy.yml` — Deploy Docker image to ECR

### Docker & ECR
- The Docker image is built from the project wheel and pushed to AWS ECR after all checks pass.
- See `Dockerfile` for build details.

## Versioning

This project uses semantic versioning. The current stable release is tagged as `v1.0.0` on GitHub.

## How to Contribute

- Fork the repository
- Create a feature branch
- Submit a pull request

## Changelog

- v1.0.0: Initial stable release with full test coverage, CI, and CLI functionality.

## License

This project is licensed under the MIT License.
