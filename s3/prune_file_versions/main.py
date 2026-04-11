import logging
from datetime import datetime, timezone

from botocore.exceptions import ClientError

from common.auth import init_s3_client
from s3.prune_file_versions.my_args import build_parser


def cutoff_datetime():
    current_time = datetime.now(timezone.utc)
    target_year = current_time.year
    target_month = current_time.month - 6

    while target_month <= 0:
        target_month += 12
        target_year -= 1

    month_days = {
        1: 31,
        2: 29 if is_leap_year(target_year) else 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    target_day = min(current_time.day, month_days[target_month])

    return current_time.replace(
        year=target_year,
        month=target_month,
        day=target_day,
    )


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_object_versions(aws_s3_client, bucket_name: str, object_key: str):
    versions = []
    paginator = aws_s3_client.get_paginator("list_object_versions")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=object_key)

    for page in pages:
        for version in page.get("Versions", []):
            if version["Key"] == object_key:
                versions.append(version)

    return versions


def get_bucket_versioning_status(aws_s3_client, bucket_name: str) -> str:
    response = aws_s3_client.get_bucket_versioning(Bucket=bucket_name)
    return response.get("Status", "Disabled")


def set_bucket_versioning(aws_s3_client, bucket_name: str, enabled: bool) -> None:
    status = "Enabled" if enabled else "Suspended"
    aws_s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={"Status": status},
    )


def list_versions(aws_s3_client, bucket_name: str, object_keys: list[str]):
    for object_key in object_keys:
        print(f"Object: {object_key}")
        versions = get_object_versions(aws_s3_client, bucket_name, object_key)

        if not versions:
            print("  No versions found.")
            continue

        for version in versions:
            print(
                "  "
                f"VersionId={version['VersionId']} "
                f"LastModified={version['LastModified'].isoformat()} "
                f"IsLatest={version['IsLatest']}"
            )


def delete_old_versions(
    aws_s3_client,
    bucket_name: str,
    object_keys: list[str],
    dry_run: bool = False,
):
    cutoff = cutoff_datetime()
    deleted_count = 0

    for object_key in object_keys:
        versions = get_object_versions(aws_s3_client, bucket_name, object_key)
        print(f"Object: {object_key}")

        if not versions:
            print("  No versions found.")
            continue

        for version in versions:
            if version["LastModified"] >= cutoff:
                print(
                    "  Keeping "
                    f"VersionId={version['VersionId']} "
                    f"LastModified={version['LastModified'].isoformat()}"
                )
                continue

            print(
                "  Deleting "
                f"VersionId={version['VersionId']} "
                f"LastModified={version['LastModified'].isoformat()}"
            )
            if not dry_run:
                aws_s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    VersionId=version["VersionId"],
                )
            deleted_count += 1

    action = "Marked for deletion" if dry_run else "Deleted"
    print(f"{action} versions: {deleted_count}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    s3_client = init_s3_client()

    match args.command:
        case "list":
            list_versions(s3_client, args.bucket_name, args.object_keys)
        case "cleanup":
            delete_old_versions(
                s3_client,
                args.bucket_name,
                args.object_keys,
                args.dry_run,
            )
        case "versioning":
            if args.enable:
                set_bucket_versioning(s3_client, args.bucket_name, True)
                print(f"Bucket versioning enabled for '{args.bucket_name}'.")
            elif args.disable:
                set_bucket_versioning(s3_client, args.bucket_name, False)
                print(f"Bucket versioning suspended for '{args.bucket_name}'.")
            else:
                status = get_bucket_versioning_status(s3_client, args.bucket_name)
                print(f"Bucket versioning status: {status}")


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
