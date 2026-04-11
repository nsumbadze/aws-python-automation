import argparse
from os import getenv

from dotenv import load_dotenv

load_dotenv()


def build_parser():
    parser = argparse.ArgumentParser(
        description="S3 automation CLI.",
        prog="main.py",
        epilog="Example: python -m s3.upload_files_by_extension.main bucket my-bucket -cb",
    )

    subparsers = parser.add_subparsers(dest="command")

    bucket_parser = subparsers.add_parser(
        "bucket",
        help="Create an S3 bucket.",
    )
    bucket_parser.add_argument("name", type=str, help="Target S3 bucket name.")
    bucket_parser.add_argument(
        "-cb",
        "--create_bucket",
        help="Create the bucket.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False",
    )
    bucket_parser.add_argument(
        "-region",
        "--region",
        nargs="?",
        type=str,
        help="AWS region for bucket creation.",
        default=getenv("aws_region_name", "us-east-1"),
    )

    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload one local file into an extension-based folder in S3.",
    )
    upload_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    upload_parser.add_argument(
        "--file",
        required=True,
        type=str,
        help="Path to the local file that will be uploaded.",
    )
    upload_parser.add_argument(
        "--object-name",
        default=None,
        type=str,
        help="Optional custom object name to use in S3.",
    )

    subparsers.add_parser("list_buckets", help="List available S3 buckets.")

    return parser
