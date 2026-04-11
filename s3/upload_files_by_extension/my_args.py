import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description="S3 automation CLI.",
        prog="main.py",
        epilog="Example: python -m s3.upload_files_by_extension.main -h",
    )

    subparsers = parser.add_subparsers(dest="command")

    return parser
