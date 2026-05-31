from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as RLImage,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SCREENSHOTS = DOCS / "screenshots"
ARCHITECTURE = DOCS / "architecture.png"
FINAL_REPORT = DOCS / "final-report.pdf"
SLIDES = DOCS / "slides.pdf"


def find_font():
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


FONT_PATH = find_font()
if FONT_PATH:
    pdfmetrics.registerFont(TTFont("ProjectSans", str(FONT_PATH)))
    BASE_FONT = "ProjectSans"
else:
    BASE_FONT = "Helvetica"


def pil_font(size, bold=False):
    if FONT_PATH:
        return ImageFont.truetype(str(FONT_PATH), size=size)
    return ImageFont.load_default()


def draw_wrapped(draw, text, xy, font, fill, width, line_gap=6):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


def make_architecture():
    DOCS.mkdir(exist_ok=True)
    width, height = 1800, 1100
    img = Image.new("RGB", (width, height), "#f7f8fb")
    draw = ImageDraw.Draw(img)
    title = pil_font(46)
    header = pil_font(30)
    body = pil_font(23)
    small = pil_font(19)

    draw.text(
        (60, 42), "To-Do List Manager - Bulut Test Mimarisi", font=title, fill="#172033"
    )
    draw.text(
        (60, 98),
        "FastAPI mikroservisi, test otomasyonu, container dağıtımı ve gözlemlenebilirlik akışı",
        font=small,
        fill="#586174",
    )

    def box(x, y, w, h, heading, lines, fill="#ffffff", outline="#cfd6e4"):
        draw.rounded_rectangle(
            (x, y, x + w, y + h), radius=22, fill=fill, outline=outline, width=3
        )
        draw.text((x + 28, y + 24), heading, font=header, fill="#172033")
        yy = y + 72
        for line in lines:
            yy = draw_wrapped(draw, line, (x + 28, yy), body, "#354052", w - 56, 4)
            yy += 4

    def arrow(x1, y1, x2, y2, color="#4f6bed"):
        draw.line((x1, y1, x2, y2), fill=color, width=5)
        if x2 >= x1:
            pts = [(x2, y2), (x2 - 18, y2 - 12), (x2 - 18, y2 + 12)]
        else:
            pts = [(x2, y2), (x2 + 18, y2 - 12), (x2 + 18, y2 + 12)]
        draw.polygon(pts, fill=color)

    box(
        70,
        180,
        350,
        210,
        "Kullanıcı / UI",
        ["HTML arayüz", "Playwright E2E", "Postman smoke"],
        "#ffffff",
    )
    box(
        525,
        170,
        420,
        230,
        "FastAPI Servisi",
        ["REST endpointleri", "Prometheus exporter", "OpenTelemetry trace"],
        "#eef5ff",
    )
    box(
        1070,
        150,
        310,
        190,
        "PostgreSQL / SQLite",
        ["Görev ve etiket verisi", "Testcontainers doğrulaması"],
        "#ffffff",
    )
    box(
        1070,
        385,
        310,
        190,
        "LocalStack S3",
        ["Görev eki yükleme", "Newman upload smoke"],
        "#ffffff",
    )
    box(
        1455,
        250,
        280,
        250,
        "Observability",
        ["Prometheus", "Grafana", "Jaeger"],
        "#fff7e8",
    )
    box(
        525,
        520,
        420,
        250,
        "CI/CD",
        ["Black lint", "Pytest coverage >= %70", "Docker build", "Deploy dry-run"],
        "#f2fff4",
    )
    box(
        70,
        570,
        350,
        210,
        "Test Katmanı",
        ["Unit + integration", "E2E senaryolar", "k6 performans"],
        "#ffffff",
    )
    box(
        1070,
        670,
        440,
        250,
        "Kubernetes / Bonus",
        ["Minikube manifestleri", "Helm chart", "ArgoCD GitOps"],
        "#f8f2ff",
    )

    arrow(420, 285, 525, 285)
    arrow(945, 255, 1070, 245)
    arrow(945, 315, 1070, 460)
    arrow(420, 675, 525, 650)
    arrow(735, 520, 735, 400)
    arrow(945, 650, 1070, 790)
    arrow(1380, 455, 1455, 405)
    arrow(1380, 760, 1455, 500)

    draw.text(
        (60, 1018),
        "Not: Bonus akışları temel çalışmayı bozmayacak şekilde opsiyonel ve anlatılabilir tutulmuştur.",
        font=small,
        fill="#586174",
    )
    img.save(ARCHITECTURE)


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName=BASE_FONT,
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "author": ParagraphStyle(
            "Author",
            parent=base["Normal"],
            fontName=BASE_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName=BASE_FONT,
            fontSize=12,
            leading=15,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName=BASE_FONT,
            fontSize=11,
            leading=14,
            spaceBefore=6,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=BASE_FONT,
            fontSize=10.5,
            leading=12.5,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=BASE_FONT,
            fontSize=8.6,
            leading=10.2,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
    }


def footer(canv, doc):
    canv.saveState()
    canv.setFont(BASE_FONT, 8)
    canv.setFillColor(colors.HexColor("#5f6674"))
    canv.drawCentredString(LETTER[0] / 2, 0.42 * inch, f"Sayfa {doc.page}")
    canv.restoreState()


def para(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=12) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
    )


def make_final_report():
    s = styles()
    doc = SimpleDocTemplate(
        str(FINAL_REPORT),
        pagesize=LETTER,
        rightMargin=0.78 * inch,
        leftMargin=0.78 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
    )
    story = [
        para(
            "To-Do List Manager Mikroservisi için Uçtan Uca Test ve Dağıtım Altyapısı",
            s["title"],
        ),
        para(
            "MTH2526-B25 Bulut Mimarilerinde Test Mühendisliği Dönem Projesi<br/>Yusuf Eren",
            s["author"],
        ),
        para(
            "<b>Özet</b> - Bu rapor, To-Do List Manager mini servisinin test, container, dağıtım ve gözlemlenebilirlik altyapısını özetler. Çalışmanın amacı karmaşık bir ürün geliştirmek değil, küçük bir servis üzerinde endüstri standardına yakın bir doğrulama hattı kurmaktır. FastAPI uygulaması SQLite/PostgreSQL veri katmanı, LocalStack S3 entegrasyonu, Pytest testleri, Postman/Newman smoke koşumu, Docker, Kubernetes, Prometheus/Grafana, k6 ve Playwright ile desteklenmiştir.",
            s["body"],
        ),
        para(
            "<b>Anahtar Kelimeler</b> - FastAPI, Pytest, Docker, Kubernetes, LocalStack, Prometheus, Grafana, k6, Playwright, Helm, ArgoCD, OpenTelemetry",
            s["small"],
        ),
        para("1. Giriş", s["h1"]),
        para(
            "Seçilen konu, görev oluşturma ve takip etme akışını kapsayan To-Do List Manager servisidir. Alan basit tutulmuştur çünkü proje kapsamının asıl değeri uygulama ekranından çok test piramidi, otomasyon ve dağıtım zincirinin birlikte çalışmasından gelir. Servis; görev ekleme, görev listeleme, görev tamamlama ve göreve dosya eki bağlama gibi temel kullanıcı işlemlerini sunar.",
            s["body"],
        ),
        para(
            "Proje bireysel olarak hazırlanmıştır. Bu nedenle kod, test, container, Kubernetes ve raporlama sorumluluğu tek geliştirici üzerinde toplanmıştır. Repo yapısı şartnamedeki önerilen klasör düzenine uyacak şekilde korunmuştur.",
            s["body"],
        ),
        para("2. Mimari", s["h1"]),
        RLImage(str(ARCHITECTURE), width=6.6 * inch, height=4.0 * inch),
        para(
            "Şekil 1. Uygulama, test, CI/CD ve gözlemlenebilirlik bileşenlerinin genel görünümü.",
            s["small"],
        ),
        PageBreak(),
        para(
            "Mimari üç ana eksene ayrılır: uygulama servisi, doğrulama katmanı ve operasyonel görünürlük. FastAPI servisi HTTP endpointlerini yönetir; SQLAlchemy modelleri görev ve etiket verisini saklar. Varsayılan yerel koşum SQLite kullanabilir, Docker Compose ve integration test akışı PostgreSQL ile doğrulanır. Dosya eki akışı LocalStack üzerinde çalışan S3 uyumlu servise yönlendirilir.",
            s["body"],
        ),
        para(
            "Dockerfile iki aşamalı yapıdadır. İlk aşamada bağımlılıklar izole bir sanal ortama kurulur, runtime aşamasında yalnızca uygulama ve gerekli paketler taşınır. Kubernetes tarafında Deployment, Service ve ConfigMap manifestleri mevcuttur. Helm chart aynı yapılandırmayı paketlenebilir hale getirir; ArgoCD manifesti ise GitOps yaklaşımıyla repo durumunun cluster'a taşınmasını açıklar.",
            s["body"],
        ),
        para("3. Test Stratejisi", s["h1"]),
        para(
            "Test stratejisi katmanlıdır. En alt katmanda hızlı unit testler endpoint davranışlarını ve S3 servis sarmalayıcısını doğrular. Orta katmanda Testcontainers ile PostgreSQL üzerinde create, update ve delete akışları çalıştırılır. Üst katmanda Playwright, kullanıcı arayüzünden görev ekleme ve tamamlama senaryolarını dener.",
            s["body"],
        ),
        bullets(
            [
                "Unit testler: health check, görev oluşturma, listeleme, tamamlama, hata durumu ve S3 yardımcı fonksiyonları.",
                "Integration testler: PostgreSQL container üzerinde görev oluşturma, durum güncelleme ve silme.",
                "E2E testler: sayfa yüklenmesi, görev ekleme ve görevin tamamlanması.",
                "Postman/Newman: health, listeleme, oluşturma, tamamlama ve attachment upload istekleri.",
            ],
            s["body"],
        ),
        para(
            "Coverage eşiği CI içinde `--cov-fail-under=70` ile korunur. Bu yaklaşım, sayısal hedefin manuel takibe bağlı kalmadan pipeline içinde kırmızı/yeşil bir kalite kapısına dönüşmesini sağlar.",
            s["body"],
        ),
        para("4. Pipeline ve Deploy", s["h1"]),
        para(
            "GitHub Actions tek workflow içinde sıralı bir kontrol hattı uygular: kod alınır, Python bağımlılıkları kurulur, Black lint kontrolü yapılır, Playwright browser bağımlılıkları yüklenir, Pytest coverage ile koşar, Newman smoke testleri hazırlanır, Docker image build edilir ve Kubernetes/Helm manifestleri dry-run ile doğrulanır. Son adımda uygulama lokal runner üzerinde ayağa kaldırılır; health check ve Postman koleksiyonu çalıştırılır.",
            s["body"],
        ),
        PageBreak(),
        para(
            "Deploy tarafında Minikube için doğrudan `k8s/` manifestleri, bonus anlatımı için de Helm chart tutulur. Bu ikili yapı sunumda iki seviyeyi net anlatmayı kolaylaştırır: önce temel Kubernetes nesneleri, sonra aynı nesnelerin Helm ile paketlenmesi. ArgoCD manifesti ise cluster tarafında istenen durumun GitHub reposundan okunmasını sağlar.",
            s["body"],
        ),
        para("5. Performans ve Gözlemlenebilirlik", s["h1"]),
        para(
            "Prometheus, FastAPI exporter üzerinden HTTP metriklerini toplar. Grafana dashboard en az üç panel içerir: istek oranı, p95 latency ve status code bazlı trafik. k6 senaryosu `GET /tasks` endpointine 10 sanal kullanıcı ile 30 saniyelik yük gönderir ve p95 değerinin 500 ms altında kalmasını hedefler.",
            s["body"],
        ),
        para(
            "OpenTelemetry bonusu, metriklerden farklı olarak tekil isteklerin servis içinde nasıl ilerlediğini trace olarak gösterir. `OTEL_ENABLED=true` olduğunda FastAPI instrumentation devreye girer ve trace verisi Jaeger arayüzünde izlenebilir. Bu sayede demo sırasında 'kaç istek geldi?' sorusu Grafana ile, 'bir isteğin içinde ne oldu?' sorusu Jaeger ile yanıtlanabilir.",
            s["body"],
        ),
        Table(
            [
                ["Alan", "Hazırlanan çıktı", "Değerlendirme değeri"],
                [
                    "Monitoring",
                    "Prometheus + Grafana",
                    "Latency, throughput ve hata trendi",
                ],
                ["Performans", "k6 senaryosu", "p95 latency eşiği"],
                ["Tracing", "OpenTelemetry + Jaeger", "İstek bazlı iz sürme"],
            ],
            colWidths=[1.45 * inch, 2.15 * inch, 2.55 * inch],
            style=TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9edf5")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#bfc7d5")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        ),
        Spacer(1, 8),
        para("6. Sonuç ve Öğrenilenler", s["h1"]),
        para(
            "Proje, küçük bir servis için uçtan uca kalite hattının nasıl kurulacağını göstermektedir. En önemli kazanım, testlerin tek bir seviyede bırakılmaması ve aynı davranışın unit, integration, E2E, API smoke ve performans perspektiflerinden gözlenmesidir. Container ve Kubernetes çıktıları ise uygulamanın yalnızca geliştirme ortamında değil, paketlenebilir ve dağıtılabilir bir servis olarak ele alındığını gösterir.",
            s["body"],
        ),
        PageBreak(),
        para("Öğrenilen ana noktalar şunlardır:", s["h2"]),
        bullets(
            [
                "Test piramidi, kapsamı artırırken geri bildirim süresini kontrol altında tutar.",
                "LocalStack, harici bulut hesabı gerektirmeden S3 davranışını test etmeyi sağlar.",
                "CI içinde coverage ve smoke kapısı koymak, son teslim öncesi beklenmeyen kırılmaları azaltır.",
                "Grafana metrikleri ve Jaeger trace ekranı birbirini tamamlar; biri sistem davranışını, diğeri istek akışını açıklar.",
                "Helm ve ArgoCD, temel Kubernetes bilgisini daha taşınabilir bir teslim modeline dönüştürür.",
            ],
            s["body"],
        ),
        para("7. İş Paylaşımı", s["h1"]),
        para(
            "Proje bireysel çalışma olduğu için tüm teknik ve dokümantasyon sorumluluğu Yusuf Eren tarafından üstlenilmiştir. Ayrıntılı döküm `docs/work-distribution.md` dosyasında tutulmuştur.",
            s["body"],
        ),
        para("8. Kaynaklar", s["h1"]),
        para(
            "[1] FastAPI Documentation. [2] Pytest Documentation. [3] Docker Documentation. [4] Kubernetes Documentation. [5] LocalStack Documentation. [6] Prometheus and Grafana Documentation. [7] k6 Documentation. [8] OpenTelemetry Documentation. [9] ArgoCD Documentation. [10] Helm Documentation.",
            s["small"],
        ),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def slide_text(c, x, y, text, size=20, color="#172033", leading=25, max_width=900):
    c.setFillColor(colors.HexColor(color))
    text_object = c.beginText(x, y)
    text_object.setFont(BASE_FONT, size)
    text_object.setLeading(leading)
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            trial = f"{line} {word}".strip()
            if c.stringWidth(trial, BASE_FONT, size) <= max_width:
                line = trial
            else:
                text_object.textLine(line)
                line = word
        text_object.textLine(line)
    c.drawText(text_object)


def slide_title(c, kicker, title):
    c.setFillColor(colors.HexColor("#4f6bed"))
    c.rect(52, 650, 42, 4, stroke=0, fill=1)
    slide_text(c, 108, 642, kicker.upper(), 11, "#4f6bed", 14, 400)
    slide_text(c, 52, 602, title, 28, "#172033", 34, 1080)


def slide_footer(c, n):
    c.setFillColor(colors.HexColor("#7a8394"))
    c.setFont(BASE_FONT, 9)
    c.drawString(52, 32, "To-Do List Manager | Bulut Mimarilerinde Test Mühendisliği")
    c.drawRightString(1228, 32, str(n))


def make_slides():
    w, h = landscape(LETTER)
    c = canvas.Canvas(str(SLIDES), pagesize=(w, h))

    slides = [
        (
            "Kapsam",
            "Küçük bir görev servisi üzerinde uçtan uca kalite hattı kuruldu.",
            [
                "FastAPI mini servis",
                "Unit + integration + E2E + API smoke",
                "Docker, Kubernetes, CI/CD, monitoring ve performans",
            ],
        ),
        (
            "Mimari",
            "Servis, veri, test ve gözlemlenebilirlik bileşenleri tek akışta birleşiyor.",
            [],
        ),
        (
            "Test Stratejisi",
            "Test piramidi hem hızlı geri bildirim hem de gerçekçi doğrulama sağlıyor.",
            [
                "Unit: endpoint ve S3 davranışı",
                "Integration: PostgreSQL Testcontainers",
                "E2E: Playwright UI akışları",
                "Newman: 5 istekli API smoke",
            ],
        ),
        (
            "CI/CD",
            "Tek workflow kalite kapılarını sırayla çalıştırıyor.",
            [
                "Black lint",
                "Pytest coverage >= %70",
                "Docker build",
                "Helm + Kubernetes deploy dry-run",
                "Health check + Newman smoke",
            ],
        ),
        (
            "Gözlemlenebilirlik",
            "Metrik ve trace birlikte sistem davranışını okunur hale getiriyor.",
            [
                "Prometheus exporter",
                "Grafana: RPS, p95 latency, status code",
                "OpenTelemetry + Jaeger trace görünümü",
            ],
        ),
        (
            "Performans",
            "k6 senaryosu p95 latency hedefini görünür bir kabul kriterine çeviriyor.",
            [
                "10 sanal kullanıcı",
                "30 saniyelik listeleme yükü",
                "p95 < 500 ms threshold",
            ],
        ),
        (
            "Bonus",
            "Anlatımı kısa, savunması net üç bonus bileşeni eklendi.",
            [
                "Helm: manifestleri paketler",
                "ArgoCD: repo durumunu cluster'a senkronize eder",
                "OpenTelemetry: tekil istek izini gösterir",
            ],
        ),
        (
            "Sonuç",
            "Proje, küçük bir servis için teslim edilebilir kalite altyapısını tamamlıyor.",
            [
                "Çalışan kod ve testler",
                "Rapor, slayt ve mimari diyagram",
                "Canlı demo için hazır komut seti",
            ],
        ),
    ]

    for i, (kicker, title, points) in enumerate(slides, start=1):
        c.setFillColor(colors.HexColor("#f7f8fb"))
        c.rect(0, 0, w, h, stroke=0, fill=1)
        slide_title(c, kicker, title)
        if i == 1:
            c.setFillColor(colors.HexColor("#172033"))
            c.setFont(BASE_FONT, 44)
            c.drawString(52, 405, "To-Do List Manager")
            slide_text(
                c,
                56,
                352,
                "FastAPI, test otomasyonu, container dağıtımı ve gözlemlenebilirlik.",
                22,
                "#4a5568",
                28,
                760,
            )
        elif i == 2:
            c.drawImage(
                str(ARCHITECTURE),
                78,
                95,
                width=1040,
                height=430,
                preserveAspectRatio=True,
                mask="auto",
            )
        else:
            y = 455
            for point in points:
                c.setFillColor(colors.HexColor("#4f6bed"))
                c.circle(78, y + 6, 5, stroke=0, fill=1)
                slide_text(c, 102, y, point, 23, "#243044", 28, 880)
                y -= 62

        if i in {5, 6}:
            img = SCREENSHOTS / (
                "07-grafana-dashboard.png" if i == 5 else "08-k6-results.png"
            )
            if img.exists():
                c.drawImage(
                    str(img),
                    775,
                    110,
                    width=390,
                    height=250,
                    preserveAspectRatio=True,
                    mask="auto",
                )
        slide_footer(c, i)
        c.showPage()
    c.save()


def main():
    make_architecture()
    make_final_report()
    make_slides()
    print(f"created {ARCHITECTURE}")
    print(f"created {FINAL_REPORT}")
    print(f"created {SLIDES}")


if __name__ == "__main__":
    main()
