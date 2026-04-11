# S3 - Host Static Site

CLI module for generating a simple static page and hosting any static site on S3.

Commands:

```powershell
poetry run python -m s3.host_static_site.main -h
poetry run python -m s3.host_static_site.main generate --first-name Davit --last-name Example
poetry run python -m s3.host_static_site.main host my-bucket --site-dir ".\s3\host_static_site\site"
```

The `host` command can also upload a React build directory or any other static site output.
