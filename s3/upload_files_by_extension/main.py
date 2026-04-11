import logging

from botocore.exceptions import ClientError

from common.auth import init_s3_client

from s3.upload_files_by_extension.my_args import build_parser


def create_bucket(aws_s3_client, bucket_name: str, region: str):
    if region == "us-east-1":
        aws_s3_client.create_bucket(Bucket=bucket_name)
    else:
        aws_s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
    return True


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    s3_client = init_s3_client()

    match args.command:
        case "bucket":
            if args.create_bucket == "True":
                print(f"Creating bucket '{args.name}' in region '{args.region}'...")
                if create_bucket(s3_client, args.name, args.region):
                    print(f"Bucket '{args.name}' successfully created.")


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
