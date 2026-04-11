from os import getenv

import boto3
from dotenv import load_dotenv

load_dotenv()


def init_s3_client():
    client = boto3.client(
        "s3",
        aws_access_key_id=getenv("aws_access_key_id"),
        aws_secret_access_key=getenv("aws_secret_access_key"),
        aws_session_token=getenv("aws_session_token"),
        region_name=getenv("aws_region_name", "us-east-1"),
    )
    client.list_buckets()
    return client
