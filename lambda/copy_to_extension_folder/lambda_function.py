import json
from pprint import pprint
from urllib.parse import unquote_plus

import boto3

s3_client = boto3.client("s3")


def resolve_extension_folder(key: str) -> str:
    if "." not in key:
        return "unknown"
    return key.rsplit(".", maxsplit=1)[-1].lower()


def is_already_in_extension_folder(key: str, extension_folder: str) -> bool:
    return key.startswith(f"{extension_folder}/")


def lambda_handler(event, _):
    pprint(event)

    for record in event.get("Records", []):
        bucket_name = record.get("s3", {}).get("bucket", {}).get("name")
        raw_key = record.get("s3", {}).get("object", {}).get("key")
        object_key = unquote_plus(raw_key)

        print("Bucket", bucket_name)
        print("Key", object_key)

        extension_folder = resolve_extension_folder(object_key)
        if is_already_in_extension_folder(object_key, extension_folder):
            print("Object is already in the target folder, skipping.")
            continue

        target_key = f"{extension_folder}/{object_key.rsplit('/', maxsplit=1)[-1]}"
        print("TargetKey", target_key)

        s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={
                "Bucket": bucket_name,
                "Key": object_key,
            },
            Key=target_key,
        )

    return {"statusCode": 200, "body": json.dumps("Done!")}
