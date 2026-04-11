import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description="Check S3 object versions and delete versions older than six months.",
        prog="main.py",
        epilog="Example: python -m s3.prune_file_versions.main cleanup my-bucket file1.txt folder/file2.png",
    )

    subparsers = parser.add_subparsers(dest="command")

    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Delete object versions older than six months.",
    )
    cleanup_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    cleanup_parser.add_argument(
        "object_keys",
        nargs="+",
        type=str,
        help="One or more S3 object keys to inspect.",
    )
    cleanup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which versions would be deleted without deleting them.",
    )

    list_parser = subparsers.add_parser(
        "list",
        help="List all versions for the provided object keys.",
    )
    list_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    list_parser.add_argument(
        "object_keys",
        nargs="+",
        type=str,
        help="One or more S3 object keys to inspect.",
    )

    versioning_parser = subparsers.add_parser(
        "versioning",
        help="Read or change S3 bucket versioning status.",
    )
    versioning_parser.add_argument(
        "bucket_name",
        type=str,
        help="Target S3 bucket name.",
    )
    versioning_parser.add_argument(
        "--status",
        action="store_true",
        help="Show current bucket versioning status.",
    )
    versioning_parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable bucket versioning.",
    )
    versioning_parser.add_argument(
        "--disable",
        action="store_true",
        help="Suspend bucket versioning.",
    )

    return parser
