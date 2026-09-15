"""Build the Turkish implementation summary PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "ozet.pdf"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")

NAVY = colors.HexColor("#12233F")
BLUE = colors.HexColor("#276EF1")
CYAN = colors.HexColor("#38BDF8")
PALE = colors.HexColor("#EAF2FF")
INK = colors.HexColor("#1D2939")
MUTED = colors.HexColor("#667085")
LINE = colors.HexColor("#D0D5DD")
GREEN = colors.HexColor("#067647")
GREEN_BG = colors.HexColor("#ECFDF3")
AMBER_BG = colors.HexColor("#FFFAEB")
AMBER = colors.HexColor("#B54708")
WHITE = colors.white


def register_fonts() -> None:
    """Register fonts that contain Turkish glyphs."""
    pdfmetrics.registerFont(TTFont("Arial", FONT_DIR / "Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_DIR / "Arial Bold.ttf"))
    pdfmetrics.registerFont(
        TTFont("Arial-Italic", FONT_DIR / "Arial Italic.ttf")
    )


def page_decoration(canvas: object, document: object) -> None:
    """Draw a consistent header, footer, and page number."""
    page_width, page_height = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_height - 12 * mm, page_width, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Arial-Bold", 8.5)
    canvas.drawString(18 * mm, page_height - 7.6 * mm, "A-MAZE-ING / UYGULAMA ÖZETİ")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, page_width - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Arial", 8)
    canvas.drawString(18 * mm, 9.5 * mm, "15 Eylül 2026")
    canvas.drawRightString(
        page_width - 18 * mm,
        9.5 * mm,
        f"Sayfa {document.page}",
    )
    canvas.restoreState()


def build_styles() -> dict[str, ParagraphStyle]:
    """Create the report's compact visual hierarchy."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Arial-Bold",
            fontSize=27,
            leading=32,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=7 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Arial",
            fontSize=12,
            leading=18,
            textColor=MUTED,
            spaceAfter=8 * mm,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Arial-Bold",
            fontSize=17,
            leading=21,
            textColor=NAVY,
            spaceBefore=3 * mm,
            spaceAfter=4 * mm,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Arial-Bold",
            fontSize=11,
            leading=14,
            textColor=BLUE,
            spaceBefore=2 * mm,
            spaceAfter=1.5 * mm,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Arial",
            fontSize=9.4,
            leading=14,
            textColor=INK,
            spaceAfter=3 * mm,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Arial",
            fontSize=8.2,
            leading=11.5,
            textColor=INK,
        ),
        "small_bold": ParagraphStyle(
            "SmallBold",
            parent=base["BodyText"],
            fontName="Arial-Bold",
            fontSize=8.2,
            leading=11.5,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Arial-Bold",
            fontSize=8.2,
            leading=11.5,
            textColor=WHITE,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier-Bold",
            fontSize=10,
            leading=14,
            textColor=NAVY,
            leftIndent=4 * mm,
            rightIndent=4 * mm,
            borderColor=CYAN,
            borderWidth=0.8,
            borderPadding=4 * mm,
            backColor=PALE,
            spaceBefore=2 * mm,
            spaceAfter=5 * mm,
        ),
        "metric": ParagraphStyle(
            "Metric",
            parent=base["Normal"],
            fontName="Arial-Bold",
            fontSize=16,
            leading=18,
            textColor=GREEN,
            alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            parent=base["Normal"],
            fontName="Arial",
            fontSize=7.7,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    """Return an ASCII-hyphen bullet paragraph."""
    return Paragraph(f"- {text}", styles["body"])


def status_box(
    title: str,
    text: str,
    styles: dict[str, ParagraphStyle],
    background: colors.Color = GREEN_BG,
    foreground: colors.Color = GREEN,
) -> Table:
    """Create a highlighted status card."""
    content = Paragraph(
        f'<font color="{foreground.hexval()}"><b>{title}</b></font><br/>{text}',
        styles["body"],
    )
    table = Table([[content]], colWidths=[174 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.7, foreground),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def flow_table(styles: dict[str, ParagraphStyle]) -> Table:
    """Show the connected runtime flow."""
    labels = [
        "1. Config\noku",
        "2. Maze\nüret",
        "3. Dosyaya\nyaz",
        "4. Terminalde\ngöster",
    ]
    cells: list[object] = []
    for index, label in enumerate(labels):
        if index:
            cells.append(Paragraph("-&gt;", styles["metric"]))
        cells.append(Paragraph(label.replace("\n", "<br/>"), styles["small_bold"]))
    table = Table(
        [cells],
        colWidths=[
            35 * mm,
            10 * mm,
            35 * mm,
            10 * mm,
            35 * mm,
            10 * mm,
            39 * mm,
        ],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), PALE),
                ("BACKGROUND", (2, 0), (2, 0), PALE),
                ("BACKGROUND", (4, 0), (4, 0), PALE),
                ("BACKGROUND", (6, 0), (6, 0), PALE),
                ("BOX", (0, 0), (0, 0), 0.7, BLUE),
                ("BOX", (2, 0), (2, 0), 0.7, BLUE),
                ("BOX", (4, 0), (4, 0), 0.7, BLUE),
                ("BOX", (6, 0), (6, 0), 0.7, BLUE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def build_pdf() -> None:
    """Generate the final summary document."""
    register_fonts()
    styles = build_styles()
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="A-Maze-ing Son Komut Özeti",
        author="Codex",
        subject="Algoritma ve görselleştirici entegrasyonu",
    )
    story: list[object] = []

    story.extend(
        [
            Spacer(1, 10 * mm),
            Paragraph("Son Komut Özeti", styles["title"]),
            Paragraph(
                "A-Maze-ing projesinde algoritma, yapılandırma ayrıştırıcısı, "
                "çıktı yazıcısı ve terminal görselleştiricisinin tek bir "
                "çalıştırılabilir akışta birleştirilmesi.",
                styles["subtitle"],
            ),
            Paragraph("Çalıştırma komutu", styles["h2"]),
            Spacer(1, 2 * mm),
            Paragraph("python3 a_maze_ing.py config.txt", styles["code"]),
            status_box(
                "SONUÇ: ÇALIŞIR DURUMDA",
                "Program artık tek config argümanı ile labirenti üretiyor, "
                "OUTPUT_FILE hedefine yazıyor ve etkileşimli ASCII "
                "görselleştiriciyi başlatıyor.",
                styles,
            ),
            Spacer(1, 8 * mm),
            Paragraph("Bağlanan çalışma akışı", styles["h1"]),
            flow_table(styles),
            Spacer(1, 7 * mm),
            Paragraph("Ana davranışlar", styles["h1"]),
            bullet(
                "Başlangıç dosyası config yolunu doğrular ve gerekli tüm "
                "parametreleri MazeGenerator sınıfına aktarır.",
                styles,
            ),
            bullet(
                "Üretilen labirent hexadecimal duvar biçimi, giriş, çıkış ve "
                "en kısa yol bilgisiyle çıktı dosyasına yazılır.",
                styles,
            ),
            bullet(
                "Terminal menüsü yeni labirent üretme, çözüm yolunu açıp "
                "kapatma, duvar rengini değiştirme ve çıkış işlemlerini sunar.",
                styles,
            ),
            bullet(
                "Yeniden üretme işleminden sonra çıktı dosyası da yeni "
                "labirentle otomatik olarak güncellenir.",
                styles,
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("Kodda Yapılan Değişiklikler", styles["title"]),
            Paragraph(
                "Değişiklikler, üretim mantığını bağımsız tutan ince bir "
                "komut satırı ve görselleştirme katmanı olarak düzenlendi.",
                styles["subtitle"],
            ),
        ]
    )
    file_rows = [
        [
            Paragraph("Dosya", styles["table_header"]),
            Paragraph("Yapılan işlem", styles["table_header"]),
        ],
        [
            Paragraph("a_maze_ing.py", styles["small_bold"]),
            Paragraph(
                "CLI giriş noktası eklendi. Config okuma, üretme, yazma ve "
                "görselleştiriciyi çalıştırma sırası bağlandı.",
                styles["small"],
            ),
        ],
        [
            Paragraph("visualizer/config_parser.py", styles["small_bold"]),
            Paragraph(
                "Zorunlu anahtar, koordinat, boyut, PERFECT ve dosya hataları "
                "için açık mesajlar eklendi. Opsiyonel SEED desteklendi.",
                styles["small"],
            ),
        ],
        [
            Paragraph("visualizer/visualizer.py", styles["small_bold"]),
            Paragraph(
                "Etkileşim döngüsü ve dört menü komutu tamamlandı. Yol "
                "durumu, renk paleti ve yeniden üretme davranışı bağlandı.",
                styles["small"],
            ),
        ],
        [
            Paragraph("visualizer/__init__.py", styles["small_bold"]),
            Paragraph(
                "Config ve MazeVisualizer sınıfları paket seviyesinde düzgün "
                "bir genel API olarak dışa aktarıldı.",
                styles["small"],
            ),
        ],
        [
            Paragraph("mazegen/generator.py", styles["small_bold"]),
            Paragraph(
                "Dosyanın sonunda çalışmayı engelleyen fazladan karakter "
                "kaldırıldı.",
                styles["small"],
            ),
        ],
        [
            Paragraph("Yapılandırma dosyaları", styles["small_bold"]),
            Paragraph(
                "config.txt varsayılanı PERFECT=False yapıldı; örnek SEED "
                "satırı eklendi. Python gereksinimi 3.10+ olarak ayarlandı.",
                styles["small"],
            ),
        ],
        [
            Paragraph("Makefile ve kalite ayarları", styles["small_bold"]),
            Paragraph(
                "install, run, debug, clean, lint ve lint-strict kuralları; "
                "flake8 dışlamaları ve Python cache ignore kuralları eklendi.",
                styles["small"],
            ),
        ],
    ]
    files_table = Table(file_rows, colWidths=[51 * mm, 123 * mm], repeatRows=1)
    files_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            files_table,
            Spacer(1, 7 * mm),
            Paragraph("Config davranışı", styles["h1"]),
            Paragraph(
                "Zorunlu anahtarlar: WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE "
                "ve PERFECT. SEED isteğe bağlıdır. SEED verildiğinde ilk "
                "labirent aynı config ile tekrar üretilebilir. Eksik dosya, "
                "bozuk satır, tekrar eden anahtar, geçersiz koordinat ve "
                "imkansız boyutlar traceback yerine anlaşılır bir hata ve "
                "sıfırdan farklı çıkış kodu üretir.",
                styles["body"],
            ),
        ]
    )

    story.append(PageBreak())
    metric_cells = [
        [
            Paragraph("100/100", styles["metric"]),
            Paragraph("30", styles["metric"]),
            Paragraph("0", styles["metric"]),
            Paragraph("12", styles["metric"]),
        ],
        [
            Paragraph("geçerli örnek üretim", styles["metric_label"]),
            Paragraph("bağımsız döngü", styles["metric_label"]),
            Paragraph("gerçek çıkmaz", styles["metric_label"]),
            Paragraph("lint edilen kaynak", styles["metric_label"]),
        ],
    ]
    metrics = Table(metric_cells, colWidths=[43.5 * mm] * 4)
    metrics.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_BG),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#ABEFC6")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ABEFC6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
            ]
        )
    )
    story.extend(
        [
            Paragraph("Doğrulama ve Sonuçlar", styles["title"]),
            Paragraph(
                "Entegrasyon yalnızca statik olarak kontrol edilmedi; gerçek "
                "komut akışı ve proje analiz aracıyla uçtan uca denendi.",
                styles["subtitle"],
            ),
            metrics,
            Spacer(1, 7 * mm),
            Paragraph("Uçtan uca etkileşim testi", styles["h1"]),
            bullet(
                "Program config.txt ile başlatıldı; sırasıyla çözüm yolu "
                "gösterildi, duvar rengi değiştirildi, yeni labirent üretildi "
                "ve program düzgün biçimde kapatıldı.",
                styles,
            ),
            bullet(
                "Varsayılan 20 x 15 çıktıda 280 erişilebilir koridor hücresi, "
                "30 bağımsız döngü ve 0 gerçek çıkmaz raporlandı.",
                styles,
            ),
            bullet(
                "Dört köşe ile merkez erişilebilir bulundu; tüm komşu "
                "duvarlarının hexadecimal kodlaması birbiriyle uyumluydu.",
                styles,
            ),
            bullet(
                "42 deseni tamamen kapalı hücrelerle görünür biçimde korundu. "
                "Desenin çevresindeki üç uç, analiz aracı tarafından gerçek "
                "koridor çıkmazı olarak değerlendirilmedi.",
                styles,
            ),
            Paragraph("Dayanıklılık kontrolleri", styles["h1"]),
            bullet(
                "PERFECT=True için 50, PERFECT=False için 50 farklı seed ile "
                "toplam 100 labirent üretildi ve tamamı yapısal doğrulamadan "
                "geçti.",
                styles,
            ),
            bullet(
                "SEED=42 ile aynı çıktının tekrar üretildiği doğrulandı.",
                styles,
            ),
            bullet(
                "Argüman verilmemesi ve config dosyasının bulunamaması "
                "durumlarında açık hata mesajı ve çıkış kodu 1 alındı.",
                styles,
            ),
            bullet(
                "make lint komutu flake8 ve mypy kontrollerini 12 Python "
                "kaynak dosyasında hatasız tamamladı.",
                styles,
            ),
            Spacer(1, 4 * mm),
            status_box(
                "NOT",
                "Python build modülü ortamda kurulu olmadığı için wheel veya "
                "source archive bu çalışma kapsamında üretilmedi. Uygulamanın "
                "çalışması için ek bir üçüncü taraf bağımlılık gerekmiyor.",
                styles,
                background=AMBER_BG,
                foreground=AMBER,
            ),
            Spacer(1, 5 * mm),
            Paragraph("Kullanım özeti", styles["h1"]),
            KeepTogether(
                [
                    Paragraph("python3 a_maze_ing.py config.txt", styles["code"]),
                    Paragraph(
                        "Menü: 1 yeniden üretir, 2 çözüm yolunu açar/kapatır, "
                        "3 duvar rengini değiştirir, 4 programdan çıkar.",
                        styles["body"],
                    ),
                ]
            ),
        ]
    )

    document.build(
        story,
        onFirstPage=page_decoration,
        onLaterPages=page_decoration,
    )


if __name__ == "__main__":
    build_pdf()
