import logging

import argparse


from s3.upload_files_by_extension.my_args import build_parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    logging.info("Command parser initialized: %s", args.command)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    main()
