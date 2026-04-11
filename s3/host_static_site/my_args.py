import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate and host static websites on S3.",
        prog="main.py",
        epilog="Example: python -m s3.host_static_site.main host my-bucket --site-dir ./site",
    )

    subparsers = parser.add_subparsers(dest="command")

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a simple static page with first and last name.",
    )
    generate_parser.add_argument(
        "--first-name",
        required=True,
        type=str,
        help="First name to include in index.html.",
    )
    generate_parser.add_argument(
        "--last-name",
        required=True,
        type=str,
        help="Last name to include in index.html.",
    )
    generate_parser.add_argument(
        "--output-dir",
        default="s3/host_static_site/site",
        type=str,
        help="Directory where the generated static site will be written.",
    )

    host_parser = subparsers.add_parser(
        "host",
        help="Upload a static site directory to S3 and enable website hosting.",
    )
    host_parser.add_argument("bucket_name", type=str, help="Target S3 bucket name.")
    host_parser.add_argument(
        "--site-dir",
        required=True,
        type=str,
        help="Local static site directory to upload.",
    )
    host_parser.add_argument(
        "--index-document",
        default="index.html",
        type=str,
        help="Index document name.",
    )

    return parser
