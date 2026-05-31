import os

import boto3
from botocore.exceptions import ClientError

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:4566")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "todo-attachments")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


def ensure_bucket(s3_client):
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
    except ClientError:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)


def upload_file(file_name: str, object_name: str | None = None):
    object_key = object_name or os.path.basename(file_name)
    s3_client = get_s3_client()

    try:
        ensure_bucket(s3_client)
        s3_client.upload_file(file_name, S3_BUCKET_NAME, object_key)
        return f"{S3_ENDPOINT}/{S3_BUCKET_NAME}/{object_key}"
    except Exception as exc:
        print(f"S3 upload error: {exc}")
        return None
