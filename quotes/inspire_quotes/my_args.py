import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description="Fetch a random quote and optionally save it to S3 as JSON.",
        prog="main.py",
        epilog='Example: python -m quotes.inspire_quotes.main my-bucket --inspire "Linus Torvalds" --save',
    )

    parser.add_argument(
        "bucket_name",
        nargs="?",
        type=str,
        help="Target S3 bucket name when using --save.",
    )
    parser.add_argument(
        "--inspire",
        nargs="?",
        const="__random__",
        default=None,
        type=str,
        help="Fetch a random quote, or pass an author name to filter quotes.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the returned quote to the provided bucket as a JSON file.",
    )

    return parser
