# S3 - Prune File Versions

CLI module for checking S3 object versions and deleting versions older than six months.

Commands:

```powershell
poetry run python -m s3.prune_file_versions.main -h
poetry run python -m s3.prune_file_versions.main versioning my-bucket --status
poetry run python -m s3.prune_file_versions.main versioning my-bucket --enable
poetry run python -m s3.prune_file_versions.main versioning my-bucket --disable
poetry run python -m s3.prune_file_versions.main list my-bucket file1.txt folder/file2.png
poetry run python -m s3.prune_file_versions.main cleanup my-bucket file1.txt folder/file2.png --dry-run
poetry run python -m s3.prune_file_versions.main cleanup my-bucket file1.txt folder/file2.png
```
