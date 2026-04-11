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

Create a local `.env` file based on `.env.example`:

```env
aws_access_key_id=YOUR_ACCESS_KEY_ID
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
aws_session_token=
aws_region_name=us-east-1
```
