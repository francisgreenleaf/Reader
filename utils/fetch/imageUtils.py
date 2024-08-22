''' Utils function related to image fetch '''

from io import BytesIO

import requests
from PIL import Image
from reportlab.lib.units import inch

CDN_PREFIXES = ["https://substackcdn.com/image/fetch/"]
PPI = 96  # 96 px to 1 inch
LETTER_MAX_DISPLAY_WIDTH = 6


# Check if the image is displayed in the html body
def is_image_displayed(top_image_url: str, html: str) -> bool:
    index = max(-1, html.find(f"<a href=\"{top_image_url}\""))
    index = max(index, html.find(f"<image src=\"{top_image_url}\""))
    return index > -1 or _is_url_start_with_cdn_prefixes(top_image_url, CDN_PREFIXES)


def get_image_display_size(url):
    iw, ih = _get_image_size_from_url(url)
    aspect = ih / float(iw)
    display_width = min(iw / PPI, LETTER_MAX_DISPLAY_WIDTH)
    return display_width * inch, display_width * aspect * inch


def _get_image_size_from_url(url):
    data = requests.get(url).content
    im = Image.open(BytesIO(data))
    return im.size


def _is_url_start_with_cdn_prefixes(top_image_url: str, prefixes: []) -> bool:
    for prefix in prefixes:
        if top_image_url.startswith(prefix):
            return True
    return False
