''' Utils function related to image fetch '''

CDN_PREFIXES = ["https://substackcdn.com/image/fetch/"]

# Check if the image is displayed in the html body
def is_image_displayed(top_image_url: str, html: str) -> bool:
    index = max(-1, html.find(f"<a href=\"{top_image_url}\""))
    index = max(index, html.find(f"<image src=\"{top_image_url}\""))
    return index > -1 or _is_url_start_with_cdn_prefixes(top_image_url, CDN_PREFIXES)

def _is_url_start_with_cdn_prefixes(top_image_url: str, prefixes: []) -> bool:
    for prefix in prefixes:
        if (top_image_url.startswith(prefix)):
            return True
    return False