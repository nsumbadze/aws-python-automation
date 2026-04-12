import json
import logging
import random
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional
from urllib.parse import quote
from urllib.request import Request, urlopen

from botocore.exceptions import ClientError

from common.auth import init_s3_client
from quotes.inspire_quotes.my_args import build_parser


HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/111.0.0.0 Safari/537.36"
    ),
}


def get_quote(author: Optional[str] = None):
    base_url = "https://api.quotable.kurokeita.dev/api/quotes/random"
    url = f"{base_url}?author={quote(author)}" if author else base_url

    with urlopen(Request(url, data=None, headers=HEADERS)) as response:
        return json.loads(response.read().decode())


def get_quotes_by_author(author: str):
    url = f"https://api.quotable.kurokeita.dev/api/quotes?author={quote(author)}"

    with urlopen(Request(url, data=None, headers=HEADERS)) as response:
        return json.loads(response.read().decode())


def normalize_quote_payload(api_payload: dict | list) -> dict:
    if isinstance(api_payload, dict):
        if "quote" in api_payload and isinstance(api_payload["quote"], dict):
            return api_payload

        if "quotes" in api_payload and isinstance(api_payload["quotes"], list):
            if not api_payload["quotes"]:
                raise ValueError("No quotes were returned for the requested author.")
            quote_record = api_payload["quotes"][0]
            return {"quote": quote_record}

        if "content" in api_payload and "author" in api_payload:
            return {"quote": api_payload}

    if isinstance(api_payload, list):
        if not api_payload:
            raise ValueError("No quotes were returned for the requested author.")
        if isinstance(api_payload[0], dict):
            return {"quote": api_payload[0]}

    raise ValueError("Unexpected API response format.")


def extract_quote_records(api_payload: dict | list) -> list[dict]:
    if isinstance(api_payload, dict):
        if "quote" in api_payload and isinstance(api_payload["quote"], dict):
            return [api_payload["quote"]]

        if "quotes" in api_payload and isinstance(api_payload["quotes"], list):
            return [quote for quote in api_payload["quotes"] if isinstance(quote, dict)]

        if "data" in api_payload and isinstance(api_payload["data"], list):
            return [quote for quote in api_payload["data"] if isinstance(quote, dict)]

        if "results" in api_payload and isinstance(api_payload["results"], list):
            return [quote for quote in api_payload["results"] if isinstance(quote, dict)]

        if "content" in api_payload and "author" in api_payload:
            return [api_payload]

    if isinstance(api_payload, list):
        return [quote for quote in api_payload if isinstance(quote, dict)]

    return []


def get_quote_for_author(author: str) -> dict:
    try:
        return normalize_quote_payload(get_quote(author))
    except Exception:
        author_quotes_payload = get_quotes_by_author(author)
        author_quotes = extract_quote_records(author_quotes_payload)
        if not author_quotes:
            raise ValueError("No quotes were returned for the requested author.")
        return {"quote": random.choice(author_quotes)}


def quote_author_name(quote_payload: dict) -> str:
    author_value = quote_payload["quote"]["author"]
    if isinstance(author_value, dict):
        return author_value["name"]
    return str(author_value)


def print_quote(quote_payload: dict) -> None:
    print(quote_payload["quote"]["content"])
    print("---")
    print(quote_author_name(quote_payload))


def sanitize_file_part(value: str) -> str:
    sanitized = []
    for character in value.lower():
        if character.isalnum() or character in {"-", "_"}:
            sanitized.append(character)
        else:
            sanitized.append("-")
    return "".join(sanitized).strip("-") or "quote"


def build_object_key(quote_payload: dict) -> str:
    author_name = quote_author_name(quote_payload)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_author = sanitize_file_part(author_name)
    return f"quotes/{safe_author}-{timestamp}.json"


def save_quote_to_s3(bucket_name: str, quote_payload: dict) -> str:
    s3_client = init_s3_client()
    object_key = build_object_key(quote_payload)
    json_bytes = json.dumps(quote_payload, indent=2).encode("utf-8")

    s3_client.upload_fileobj(
        Fileobj=BytesIO(json_bytes),
        Bucket=bucket_name,
        Key=object_key,
        ExtraArgs={"ContentType": "application/json"},
    )

    return object_key


def resolve_author_argument(inspire_argument: Optional[str]) -> Optional[str]:
    if inspire_argument in {None, "__random__"}:
        return None
    return inspire_argument


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.inspire is None:
        parser.print_help()
        return

    if args.save and not args.bucket_name:
        parser.error("bucket_name is required when using --save")

    author = resolve_author_argument(args.inspire)
    if author:
        quote_payload = get_quote_for_author(author)
    else:
        quote_payload = normalize_quote_payload(get_quote())
    print_quote(quote_payload)

    if args.save:
        object_key = save_quote_to_s3(args.bucket_name, quote_payload)
        print(f"Saved to bucket: {args.bucket_name}")
        print(f"S3 key: {object_key}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    try:
        main()
    except ClientError as error:
        logging.error(
            "%s: %s",
            error.response["Error"].get("Code"),
            error.response["Error"].get("Message"),
        )
    except Exception as error:
        logging.error(error)
