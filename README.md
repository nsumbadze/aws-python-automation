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
