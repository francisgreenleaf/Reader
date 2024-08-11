''' Utils function related to image fetch '''
import base64

#individual function to fetch images with try except blocks for specific exceptions
def fetch_images(image_urls, requests, logger):
    images = []
    for img in image_urls:
        if img.lower().endswith(".svg"):
            logger.info(f"Skipping SVG image: {img}")
            continue

        try:
            logger.info(f"Attempting to fetch image: {img}")
            response = requests.get(img, timeout=10)
            response.raise_for_status()
            img_data = base64.b64encode(response.content).decode("utf-8")
            images.append({"src": img, "data": img_data})
            logger.info(f"Successfully fetched image: {img}")
        except requests.Timeout:
            logger.warning(f"Timeout fetching image: {img}")
        except requests.HTTPError as http_err:
            logger.warning(f"HTTP error fetching image: {img}: Status code: {http_err}")
        except requests.RequestException as req_err:
            logger.warning(f"Error occurred while fetching image {img}: {req_err}")

    return images