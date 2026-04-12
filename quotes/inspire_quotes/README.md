# Quotes - Inspire

CLI module for fetching a random quote from the Quotable API and optionally saving it to S3 as JSON.

Commands:

```powershell
poetry run python -m quotes.inspire_quotes.main --inspire
poetry run python -m quotes.inspire_quotes.main --inspire "Linus Torvalds"
poetry run python -m quotes.inspire_quotes.main my-bucket --inspire "Linus Torvalds" --save
```

The `--inspire` flag without a value returns a random quote. Passing an author name filters the quote request by author.
