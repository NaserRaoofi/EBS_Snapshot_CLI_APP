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

# trigger lint workflow
# Workflow test: minor change

## License

This project is licensed under the MIT License.
