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

Quick start:

```powershell
python init.py
```

The `init.py` command creates `.env`, checks Poetry, installs dependencies, and applies platform-specific setup steps.

Manual setup:

```powershell
pip install poetry
poetry install
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

`s3/prune_file_versions`

This module checks object versions for selected S3 keys, deletes versions older than six months, and manages bucket versioning status.

`s3/manage_file_versions`

This module checks whether bucket versioning is enabled, shows file version counts and creation dates, and restores the previous version as the latest version.

`s3/host_static_site`

This module generates a simple `index.html` page and hosts static websites on S3, including directories produced by React builds.

`s3/host_website_source`

This module hosts a local website source folder on S3 in one command by creating the bucket if needed, configuring static website hosting, uploading the source, and returning the website URL.

`quotes/inspire_quotes`

This module fetches a random quote from the Quotable API, supports author filtering, and can save the returned quote to S3 as a JSON file.
