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

## License

This project is licensed under the MIT License.
