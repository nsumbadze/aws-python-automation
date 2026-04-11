# S3 - Manage File Versions

CLI module for checking bucket versioning, listing file versions, and restoring the previous version as the latest version.

Commands:

```powershell
poetry run python -m s3.manage_file_versions.main -h
poetry run python -m s3.manage_file_versions.main bucket my-bucket --versioning
poetry run python -m s3.manage_file_versions.main file my-bucket path/to/file.txt --versions
poetry run python -m s3.manage_file_versions.main file my-bucket path/to/file.txt --restore-previous
```
