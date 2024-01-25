import shutil
from pathlib import Path

import requests

get_daily_url = "https://timeguessr.com/getdaily"
get_daily_response = requests.get(get_daily_url)

if get_daily_response.status_code != 200:
    msg = f"Failed to query page: {get_daily_url}"
    raise (msg)

image_count = 1
for value in get_daily_response.json():
    if image_count == 5:
        break

    image_url = value["URL"]

    # Get the file name from the url.
    file_name = Path(image_url).name

    print(f"Downloading image {image_url}...")
    image_response = requests.get(image_url, stream=True)

    with open(file_name, 'wb') as out_file:
        shutil.copyfileobj(image_response.raw, out_file)
    del image_response

    image_count += 1
