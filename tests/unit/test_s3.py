from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from src.services.s3 import get_s3_client, upload_file


@patch("src.services.s3.boto3.client")
def test_get_s3_client(mock_boto_client):
    get_s3_client()
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


@patch("src.services.s3.get_s3_client")
def test_upload_file_success(mock_get_s3_client):
    mock_s3_client = MagicMock()
    mock_get_s3_client.return_value = mock_s3_client
    mock_s3_client.head_bucket.return_value = {}

    result = upload_file("test.txt", "test-object.txt")

    assert result == "http://localhost:4566/todo-attachments/test-object.txt"
    mock_s3_client.upload_file.assert_called_once_with(
        "test.txt", "todo-attachments", "test-object.txt"
    )


@patch("src.services.s3.get_s3_client")
def test_upload_file_create_bucket(mock_get_s3_client):
    mock_s3_client = MagicMock()
    mock_get_s3_client.return_value = mock_s3_client
    mock_s3_client.head_bucket.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadBucket"
    )

    result = upload_file("test.txt", "test-object.txt")

    assert result.endswith("/todo-attachments/test-object.txt")
    mock_s3_client.create_bucket.assert_called_once_with(Bucket="todo-attachments")
    mock_s3_client.upload_file.assert_called_once()


@patch("src.services.s3.get_s3_client")
def test_upload_file_failure(mock_get_s3_client):
    mock_s3_client = MagicMock()
    mock_get_s3_client.return_value = mock_s3_client
    mock_s3_client.upload_file.side_effect = Exception("Connection error")

    result = upload_file("test.txt", "test-object.txt")

    assert result is None
