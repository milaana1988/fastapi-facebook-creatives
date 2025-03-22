import requests
from google.cloud import vision
from typing import List


def analyze_creative_features(image_url: str) -> List[str]:
    """
    Analyzes the features of the given image URL and returns a list of labels.

    The labels are detected by the Google Cloud Vision API and represent a description of the image content.

    Args:
        image_url (str): The URL of the image to be analyzed.

    Returns:
        List[str]: A list of labels describing the image content.

    Raises:
        Exception: If the image could not be downloaded from the given URL.
    """
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception("Failed to download image from URL")
    content = response.content

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    result = client.label_detection(image=image)
    labels = result.label_annotations

    return [label.description for label in labels]
