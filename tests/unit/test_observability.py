import os
from src.observability import setup_observability
from fastapi import FastAPI


def test_setup_observability_disabled():
    """OTEL_ENABLED kapalıyken kurulum yapılmadığını test eder."""
    app = FastAPI()
    os.environ["OTEL_ENABLED"] = "false"
    result = setup_observability(app)
    assert result is False


def test_setup_observability_enabled():
    """OTEL_ENABLED açıkken kurulum yapıldığını test eder."""
    app = FastAPI()
    os.environ["OTEL_ENABLED"] = "true"
    result = setup_observability(app)
    assert result is True
