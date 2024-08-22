''' Utils function related to image fetch '''
import io

import requests
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as ReportLabImage
)

from utils.fetch.imageUtils import get_image_display_size

filename = './temp.png'


# To generate pdf from the content
def generate_pdf(content, top_image_url=None):
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

    # Add content and top image
    if top_image_url != '' and top_image_url is not None:
        img = requests.get(top_image_url, stream=True).raw
        width, height = get_image_display_size(top_image_url)
        flowables.append(ReportLabImage(img, width=width, height=height))

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
