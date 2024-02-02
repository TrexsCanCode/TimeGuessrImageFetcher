import shutil
from pathlib import Path

import requests

image_folder = "images"
get_daily_url = "https://timeguessr.com/getdaily"


def sanitise_image_file_name(file_name, image_num):
    # Firstly some of the images file names may contain query strings so trim
    # anything including and after a '?'.
    if '?' in file_name:
        file_name = file_name.split('?')[0]

    print(image_num)
    # Now replace the file name to be the image number.
    return f"{image_num}{Path(file_name).suffix}"


get_daily_response = requests.get(get_daily_url)

if get_daily_response.status_code != 200:
    msg = f"Failed to query page: {get_daily_url}"
    raise (msg)

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

    # Get the file name from the url.
    file_name = Path(image_url).name

    file_name = sanitise_image_file_name(file_name, image_count)

    output_image_path = Path(image_folder, file_name)

    # Increment the image count now incase the image download fails and we restart the loop.
    image_count += 1

    print(f"Downloading image {image_url}...")
    image_response = requests.get(image_url, stream=True)
    if image_response.status_code != 200:
        print(f"Failed to download image from: {image_url}")
        print(f"Received status code: {image_response.status_code}")
        continue

    with Path(output_image_path).open('wb') as out_file:
        shutil.copyfileobj(image_response.raw, out_file)

    del image_response
