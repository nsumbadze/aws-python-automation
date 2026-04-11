import logging
from pathlib import Path

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


def list_buckets(aws_s3_client):
    return aws_s3_client.list_buckets()


def sanitize_folder_name(folder_name: str) -> str:
    allowed_characters = []
    for character in folder_name.lower():
        if character.isalnum() or character in {"-", "_"}:
            allowed_characters.append(character)
        else:
            allowed_characters.append("-")
    sanitized = "".join(allowed_characters).strip("-")
    return sanitized or "unknown"


def resolve_folder_name(file_path: Path, mime_type: str) -> str:
    if file_path.suffix:
        return sanitize_folder_name(file_path.suffix[1:])

    if "/" in mime_type:
        return sanitize_folder_name(mime_type.split("/", maxsplit=1)[1])

    return "unknown"


def upload_local_file(aws_s3_client, bucket_name: str, file_name: str, object_name=None):
    try:
        import magic
    except ImportError as error:
        raise ImportError(
            "python-magic is not available. Install project dependencies and, on Windows, also install python-magic-bin."
        ) from error

    file_path = Path(file_name).expanduser().resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"File was not found: {file_path}")

    mime_type = magic.from_file(str(file_path), mime=True)
    folder_name = resolve_folder_name(file_path, mime_type)
    final_name = object_name or file_path.name
    s3_key = f"{folder_name}/{final_name}"

    print(f"Uploading '{file_path.name}' to '{bucket_name}/{s3_key}'...")
    aws_s3_client.upload_file(
        str(file_path),
        bucket_name,
        s3_key,
        ExtraArgs={"ContentType": mime_type},
    )
    print("Upload finished.")

    return {
        "bucket": bucket_name,
        "file_path": str(file_path),
        "mime_type": mime_type,
        "folder_name": folder_name,
        "s3_key": s3_key,
    }


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
        case "list_buckets":
            buckets = list_buckets(s3_client)
            for bucket in buckets.get("Buckets", []):
                print(bucket["Name"])
        case "upload":
            result = upload_local_file(
                s3_client,
                args.bucket_name,
                args.file,
                args.object_name,
            )
            print(f"MIME type: {result['mime_type']}")
            print(f"S3 folder: {result['folder_name']}")
            print(f"S3 key: {result['s3_key']}")


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
    except (FileNotFoundError, ValueError, ImportError) as error:
        logging.error(error)
