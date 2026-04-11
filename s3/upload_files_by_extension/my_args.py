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

    return parser
