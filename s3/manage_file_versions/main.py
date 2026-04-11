import logging

from botocore.exceptions import ClientError

from common.auth import init_s3_client
from s3.manage_file_versions.my_args import build_parser


def get_bucket_versioning_status(aws_s3_client, bucket_name: str) -> str:
    response = aws_s3_client.get_bucket_versioning(Bucket=bucket_name)
    return response.get("Status", "Disabled")


def get_object_versions(aws_s3_client, bucket_name: str, object_key: str):
    versions = []
    paginator = aws_s3_client.get_paginator("list_object_versions")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=object_key)

    for page in pages:
        for version in page.get("Versions", []):
            if version["Key"] == object_key:
                versions.append(version)

    return versions


def show_bucket_versioning(aws_s3_client, bucket_name: str) -> None:
    status = get_bucket_versioning_status(aws_s3_client, bucket_name)
    print(f"Bucket versioning status: {status}")


def show_file_versions(aws_s3_client, bucket_name: str, object_key: str) -> None:
    versions = get_object_versions(aws_s3_client, bucket_name, object_key)
    print(f"Object: {object_key}")
    print(f"Version count: {len(versions)}")

    if not versions:
        print("No versions found.")
        return

    print("Version creation dates:")
    for index, version in enumerate(versions, start=1):
        print(
            f"{index}. "
            f"VersionId={version['VersionId']} "
            f"CreatedAt={version['LastModified'].isoformat()} "
            f"IsLatest={version['IsLatest']}"
        )


def restore_previous_version(aws_s3_client, bucket_name: str, object_key: str) -> None:
    versions = get_object_versions(aws_s3_client, bucket_name, object_key)

    if len(versions) < 2:
        raise ValueError("Previous version does not exist for this object.")

    previous_version = versions[1]
    aws_s3_client.copy_object(
        Bucket=bucket_name,
        Key=object_key,
        CopySource={
            "Bucket": bucket_name,
            "Key": object_key,
            "VersionId": previous_version["VersionId"],
        },
    )

    print(
        "Previous version restored as latest: "
        f"VersionId={previous_version['VersionId']} "
        f"CreatedAt={previous_version['LastModified'].isoformat()}"
    )


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    s3_client = init_s3_client()

    match args.command:
        case "bucket":
            if args.versioning:
                show_bucket_versioning(s3_client, args.bucket_name)
            else:
                parser.error("bucket command requires --versioning")
        case "file":
            if args.versions:
                show_file_versions(s3_client, args.bucket_name, args.object_key)
            elif args.restore_previous:
                restore_previous_version(s3_client, args.bucket_name, args.object_key)
            else:
                parser.error("file command requires --versions or --restore-previous")


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
    except ValueError as error:
        logging.error(error)
