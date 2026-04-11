# S3 - Upload Files by Extension

CLI module for S3 bucket operations and object uploads.

The implementation creates a bucket and uploads files into folders derived from file extensions.

Examples:

- `img.jpeg` becomes `jpeg/img.jpeg`
- `report.pdf` becomes `pdf/report.pdf`
- `archive.zip` becomes `zip/archive.zip`

Commands:

```powershell
poetry run python -m s3.upload_files_by_extension.main -h
poetry run python -m s3.upload_files_by_extension.main bucket dav3task1 -cb
poetry run python -m s3.upload_files_by_extension.main list_buckets
poetry run python -m s3.upload_files_by_extension.main upload dav3task1 --file ".\s3\upload_files_by_extension\sample_files\img.jpeg"
```
