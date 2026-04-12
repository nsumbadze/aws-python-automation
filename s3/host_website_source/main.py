import logging
import mimetypes
from os import getenv
from pathlib import Path

from botocore.exceptions import ClientError

from common.auth import init_s3_client
from s3.host_website_source.my_args import build_parser


WEBSITE_CONFIGURATION = {
    "IndexDocument": {"Suffix": "index.html"},
}

PUBLIC_READ_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::%s/*"
    }
  ]
}"""


def create_bucket_if_missing(aws_s3_client, bucket_name: str) -> None:
    existing_buckets = aws_s3_client.list_buckets().get("Buckets", [])
    if bucket_name in {bucket["Name"] for bucket in existing_buckets}:
        return

    region_name = getenv("aws_region_name", "us-east-1")
    try:
        if region_name == "us-east-1":
            aws_s3_client.create_bucket(Bucket=bucket_name)
        else:
            aws_s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region_name},
            )
    except ClientError as error:
        if (
            region_name == "us-east-1"
            and error.response["Error"].get("Code") == "IllegalLocationConstraintException"
        ):
            aws_s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region_name},
            )
            return
        raise


def configure_static_hosting(aws_s3_client, bucket_name: str, index_document: str) -> None:
    website_configuration = {
        **WEBSITE_CONFIGURATION,
        "IndexDocument": {"Suffix": index_document},
    }
    aws_s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )
    aws_s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=PUBLIC_READ_POLICY % bucket_name,
    )
    aws_s3_client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration=website_configuration,
    )


def upload_source_directory(aws_s3_client, bucket_name: str, source: str) -> list[str]:
    root = Path(source).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Source directory was not found: {root}")

    uploaded_files = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        object_key = file_path.relative_to(root).as_posix()
        content_type, _ = mimetypes.guess_type(str(file_path))
        extra_args = {"ContentType": content_type} if content_type else None

        if extra_args:
            aws_s3_client.upload_file(
                str(file_path),
                bucket_name,
                object_key,
                ExtraArgs=extra_args,
            )
        else:
            aws_s3_client.upload_file(str(file_path), bucket_name, object_key)

        uploaded_files.append(object_key)

    return uploaded_files


def website_url(bucket_name: str) -> str:
    region_name = getenv("aws_region_name", "us-east-1")
    return f"http://{bucket_name}.s3-website-{region_name}.amazonaws.com"


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    s3_client = init_s3_client()

    match args.command:
        case "host":
            create_bucket_if_missing(s3_client, args.bucket_name)
            configure_static_hosting(s3_client, args.bucket_name, args.index_document)
            uploaded_files = upload_source_directory(s3_client, args.bucket_name, args.source)
            print(f"Uploaded files: {len(uploaded_files)}")
            for object_key in uploaded_files:
                print(object_key)
            print(f"Website URL: {website_url(args.bucket_name)}")


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
    except FileNotFoundError as error:
        logging.error(error)
