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
def generate_pdf(content, images):
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

        # Add an image after every 5 paragraphs, if available
        if i % 5 == 0 and images:
            img_data = base64.b64decode(images[0]["data"])
            img = Image.open(BytesIO(img_data))
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            img_width = 6 * inch
            img_height = aspect * img_width
            flowables.append(
                ReportLabImage(BytesIO(img_data), width=img_width, height=img_height)
            )
            flowables.append(Spacer(1, 12))
            images.pop(0)

    doc.build(flowables)
    buffer.seek(0)
    return buffer