import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description="Inspect S3 bucket versioning and manage file versions.",
        prog="main.py",
        epilog="Example: python -m s3.manage_file_versions.main file my-bucket path/to/file.txt --versions",
    )

    subparsers = parser.add_subparsers(dest="command")

    bucket_parser = subparsers.add_parser(
        "bucket",
        help="Inspect bucket-level versioning information.",
    )
    bucket_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    bucket_parser.add_argument(
        "--versioning",
        action="store_true",
        help="Show whether bucket versioning is enabled.",
    )

    file_parser = subparsers.add_parser(
        "file",
        help="Inspect or restore versions for one S3 object key.",
    )
    file_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    file_parser.add_argument("object_key", type=str, help="Target S3 object key.")
    file_parser.add_argument(
        "--versions",
        action="store_true",
        help="Show the number of versions and their creation dates.",
    )
    file_parser.add_argument(
        "--restore-previous",
        action="store_true",
        help="Upload the previous version as the new latest version.",
    )

    return parser
