# EC2 Backup Tool

This project provides a command-line interface for managing AWS EC2 snapshots. It allows users to create and restore snapshots of EC2 instances easily.

## Project Structure

```
ec2_backup_tool/
├── backup.py        # Handles snapshot creation
├── restore.py       # Manages the restore process
├── utils.py         # Contains helper functions
├── cli.py           # Command-line interface using Click
├── requirements.txt  # Lists project dependencies
├── logger.py           # save all logs in backup.log
└── .env             # Stores AWS profile and region
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ec2_backup_tool
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your AWS credentials in the `.env` file:
   ```
   AWS_REGION=your_aws_region
   ```

## Usage

### Backup and Restore

To create a snapshot or restore of an EC2 instance, use the following command:
```
python ./cli.py
```

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
