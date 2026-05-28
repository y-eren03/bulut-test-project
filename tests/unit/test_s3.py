import pytest
from unittest.mock import MagicMock, patch
from src.services.s3 import get_s3_client, upload_file

@patch("src.services.s3.boto3.client")
def test_get_s3_client(mock_boto_client):
    """S3 client oluşturma fonksiyonunun doğru parametrelerle çağrıldığını test eder."""
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
    """Dosya yükleme işleminin başarılı senaryosunu test eder."""
    mock_s3_client = MagicMock()
    mock_get_s3_client.return_value = mock_s3_client
    
    # Bucket head check'te hata almadığını ve upload'ın başarılı olduğunu varsayıyoruz
    mock_s3_client.head_bucket.return_value = {}
    
    result = upload_file("test.txt", "test-object.txt")
    
    assert "test-object.txt" in result
    mock_s3_client.upload_file.assert_called_once_with("test.txt", "todo-attachments", "test-object.txt")

@patch("src.services.s3.get_s3_client")
def test_upload_file_create_bucket(mock_get_s3_client):
    """Bucket yoksa otomatik oluşturularak dosya yüklendiğini test eder."""
    mock_s3_client = MagicMock()
    mock_get_s3_client.return_value = mock_s3_client
    
    # head_bucket hata dönsün (bucket yok), create_bucket çağrılsın
    mock_s3_client.head_bucket.side_effect = Exception("Bucket not found")
    
    result = upload_file("test.txt", "test-object.txt")
    
    assert "test-object.txt" in result
    mock_s3_client.create_bucket.assert_called_once_with(Bucket="todo-attachments")
    mock_s3_client.upload_file.assert_called_once()

@patch("src.services.s3.get_s3_client")
def test_upload_file_failure(mock_get_s3_client):
    """Yükleme sırasında hata oluşması durumunda None döndüğünü test eder."""
    mock_s3_client = MagicMock()
    mock_get_s3_client.return_value = mock_s3_client
    
    # Yükleme işlemi sırasında exception oluşsun
    mock_s3_client.head_bucket.side_effect = Exception("Connection error")
    
    result = upload_file("test.txt", "test-object.txt")
    
    assert result is None
