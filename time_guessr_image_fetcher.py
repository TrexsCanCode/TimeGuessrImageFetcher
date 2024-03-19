"""Script which gets and downloads the daily images for timeguessr."""
import shutil
from pathlib import Path

import requests
from requests import Response

image_folder: str = "images"
get_daily_url: str = "https://timeguessr.com/getdaily"


def download_daily_images() -> None:
    """Download the daily timeguessr images."""
    print(f"Getting daily game info from: {get_daily_url}")

    # Get the json for the daily images.
    get_daily_response: Response = requests.get(get_daily_url)
    get_daily_response.raise_for_status()

    # Create the images folder if it doesn't exist.
    Path(image_folder).mkdir(parents=True, exist_ok=True)

    image_count: int = 0
    for value in get_daily_response.json():
        if image_count == 5:
            break

        image_url: str = value["URL"]

        imgur_url: str = "https://i.imgur.com"

        if imgur_url in image_url:
            image_url = f"https://proxy.duckduckgo.com/iu/?u={image_url}"

        # Increment the image count now incase the image download fails and we
        # restart the loop. This will also mean the file names are not 0 indexed
        # matching them up with the game rounds.
        image_count += 1

        print(f"Downloading image {image_url}...")
        image_response: Response = requests.get(image_url, stream=True)
        if image_response.status_code != 200:
            print(f"Failed to download image from: {image_url}")
            print(f"Received status code: {image_response.status_code}")
            continue

        # Get the file name from the url.
        file_name: str = Path(image_url).name

        file_name = _sanitise_image_file_name(file_name, image_count)

        output_image_path: Path = Path(image_folder, file_name)

        with Path(output_image_path).open('wb') as out_file:
            shutil.copyfileobj(image_response.raw, out_file)

        del image_response


def _sanitise_image_file_name(file_name: str, image_num: int) -> str:
    """
    Rename the file to the round number whilst preserving the original file extension.

    :param file_name: The original file name.
    :param round_num: The number of the round the image belongs to.
    :returns: The sanitise image file name.
    """
    # Firstly some of the images file names may contain query strings so trim
    # anything including and after a '?'.
    if '?' in file_name:
        file_name = file_name.split('?')[0]

    # Now replace the file name to be the image number.
    return f"{image_num}{Path(file_name).suffix}"


if __name__ == "__main__":
    download_daily_images()
