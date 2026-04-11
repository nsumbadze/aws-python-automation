# AWS Python Automation

Technical repository for AWS automation scripts built with Python.

Current structure groups scripts by AWS service and keeps shared code in a common package.

## Structure

```text
aws-python-automation/
|- common/
|- s3/
|  `- upload_files_by_extension/
|- .gitattributes
|- .gitignore
|- pyproject.toml
|- poetry.lock
`- README.md
```

## Setup

Install dependencies from the repository root:

```powershell
pip install poetry
poetry install
```

Or run the bootstrap script:

```powershell
python init.py
```

On Windows, install `python-magic-bin` inside the Poetry environment:

```powershell
poetry run pip install python-magic-bin
```

Run modules from the repository root:

```powershell
poetry run python -m s3.upload_files_by_extension.main -h
```

Create a local `.env` file based on `.env.example`:

```env
aws_access_key_id=YOUR_ACCESS_KEY_ID
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
aws_session_token=
aws_region_name=us-east-1
```

## Current module

`s3/upload_files_by_extension`

This module creates S3 buckets and uploads local files into folders derived from file extensions.
