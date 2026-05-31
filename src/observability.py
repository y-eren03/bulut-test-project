import os


def setup_observability(app):
    """OpenTelemetry paketleri yüklüyse ve aktif edildiyse tracing (izleme) altyapısını başlatır."""
    # Çevresel değişkenden OTEL'in aktif olup olmadığını kontrol et
    if os.getenv("OTEL_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        return False

    # Servis adını belirle ve izleyiciyi (Tracer) oluştur
    resource = Resource.create({"service.name": "todo-list-manager"})
    provider = TracerProvider(resource=resource)
    
    # Trace verilerini iletmek için dışa aktarıcıyı (Exporter) yapılandır
    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    
    # FastAPI uygulamasına otomatik ölçümleme (instrumentation) ekle
    FastAPIInstrumentor.instrument_app(app)
    return True
