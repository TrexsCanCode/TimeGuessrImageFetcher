import shutil
from pathlib import Path

import requests

image_folder = "images"
get_daily_url = "https://timeguessr.com/getdaily"


def _sanitise_image_file_name(file_name, image_num):
    # Firstly some of the images file names may contain query strings so trim
    # anything including and after a '?'.
    if '?' in file_name:
        file_name = file_name.split('?')[0]

    # Now replace the file name to be the image number.
    return f"{image_num}{Path(file_name).suffix}"


print(f"Getting daily game info from: {get_daily_url}")

get_daily_response = requests.get(get_daily_url)
get_daily_response.raise_for_status()

# Create the images folder if it doesn't exist.
Path(image_folder).mkdir(parents=True, exist_ok=True)

image_count = 0
for value in get_daily_response.json():
    if image_count == 5:
        break

    image_url = value["URL"]

    imgur_url = "https://i.imgur.com"

    if imgur_url in image_url:
        image_url = f"https://proxy.duckduckgo.com/iu/?u={image_url}"

    # Increment the image count now incase the image download fails and we
    # restart the loop. This will also mean the file names are not 0 indexed
    # matching them up with the game rounds.
    image_count += 1

    print(f"Downloading image {image_url}...")
    image_response = requests.get(image_url, stream=True)
    if image_response.status_code != 200:
        print(f"Failed to download image from: {image_url}")
        print(f"Received status code: {image_response.status_code}")
        continue

    # Get the file name from the url.
    file_name = Path(image_url).name

    file_name = _sanitise_image_file_name(file_name, image_count)

    output_image_path = Path(image_folder, file_name)

    with Path(output_image_path).open('wb') as out_file:
        shutil.copyfileobj(image_response.raw, out_file)

    del image_response
