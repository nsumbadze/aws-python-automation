import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description="Host a source folder as a static website on S3.",
        prog="main.py",
        epilog='Example: python -m s3.host_website_source.main host "my-s3-static-host" --source "project_folder"',
    )

    subparsers = parser.add_subparsers(dest="command")

    host_parser = subparsers.add_parser(
        "host",
        help="Create/configure a bucket and host the provided source folder.",
    )
    host_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    host_parser.add_argument(
        "--source",
        required=True,
        type=str,
        help="Local folder containing the website source.",
    )
    host_parser.add_argument(
        "--index-document",
        default="index.html",
        type=str,
        help="Index document name.",
    )

    return parser
