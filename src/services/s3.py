import boto3
import os
from botocore.exceptions import NoCredentialsError

# LocalStack S3 Ayarları
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:4566")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "todo-attachments")


def get_s3_client():
    """Boto3 S3 istemcisini döndürür. LocalStack kullanacak şekilde yapılandırılmıştır."""
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


def upload_file(file_name: str, object_name: str = None):
    """Belirtilen dosyayı S3'e yükler."""
    if object_name is None:
        object_name = file_name

    s3_client = get_s3_client()
    try:
        # Bucket yoksa oluşturmayı deneriz (basit senaryo için)
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        except:
            s3_client.create_bucket(Bucket=S3_BUCKET_NAME)

        s3_client.upload_file(file_name, S3_BUCKET_NAME, object_name)
        return f"{S3_ENDPOINT}/{S3_BUCKET_NAME}/{object_name}"
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None
