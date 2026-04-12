# S3 - Host Website Source

CLI module for hosting a local website source folder on S3 in one command.

The command creates the bucket if needed, applies website configuration and public read permissions, uploads the source files, and returns the static website URL.

Example:

```powershell
poetry run python -m s3.host_website_source.main host "my-s3-static-host" --source ".\project_folder"
```

Example source repository:

`https://github.com/do-community/html_demo_site`
