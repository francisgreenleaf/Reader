''' Utils function related to image fetch '''
import base64
import io
from io import BytesIO

from PIL import Image
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as ReportLabImage,
)

# To generate pdf from the content
def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Justify", alignment=TA_JUSTIFY))
    flowables = []

    # Add title
    title = content.split("\n")[0]
    flowables.append(Paragraph(title, styles["Heading1"]))
    flowables.append(Spacer(1, 12))

    # Add content and images
    content_lines = content.split("\n")[1:]
    for i, line in enumerate(content_lines):
        if line.strip():
            p = Paragraph(line, styles["Justify"])
            flowables.append(p)
        else:
            flowables.append(Spacer(1, 6))

    doc.build(flowables)
    buffer.seek(0)
    return buffer