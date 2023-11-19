

from helpers import common_helpers

import requests
from html.parser import HTMLParser
from PIL import Image, ImageDraw


class ImageSrcFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.src = None

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            attrs = dict(attrs)
            if attrs.get("id") == "anim_image_anim_anim":
                self.src = attrs.get("src")

def get_image(url, local_filepath):

    # Parse URL of latest image
    response = requests.get(url)
    parser = ImageSrcFinder()
    parser.feed(response.text)
    image_url = parser.src
    print(f"Image url: { image_url }")

    # Fetch image and save to disk
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(local_filepath, 'wb') as file:
            file.write(response.content)
            return True
    
    # Todo: Error handling
    return False


def count_pixels_with_color(image_path, hex_color):
    # Convert hex color to an RGB tuple
    hex_color = hex_color.lstrip('#')
    target_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Load the image
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        width, height = img.size

        # Crop to square
        output_size = 508
        output_size = 200
        left = (width - output_size) / 2
        top = (height - output_size) / 2
        right = (width + output_size) / 2
        bottom = (height + output_size) / 2

        cropped_img = img.crop((left, top, right, bottom))

        # Todo: move to settings
        cropped_img.save('./static/dynamic/latest_rain_cropped_for_calculation.png')

        # Iterate over pixels and count the matches
        count = 0
        for pixel in cropped_img.getdata():
            if pixel == target_color:
                count += 1

    return count


def simiplify_image(image_path, colors_to_keep):
    # Convert hex colors to RGB tuples
    colors_to_keep = [tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for color in colors_to_keep]

    with Image.open(image_path) as img:
        img = img.convert('RGB')
        pixels = img.load()

        for i in range(img.width):
            for j in range(img.height):
                if pixels[i, j] not in colors_to_keep:
                    pixels[i, j] = (0, 0, 0)  # Set to black

        # Create a draw object
        draw = ImageDraw.Draw(img)

        # Position the dot
        left = 288
        top = 246
        right = 296
        bottom = 254

        # Draw the red spot (circle)
        draw.ellipse([left, top, right, bottom], fill='red')

        return img


def main():
    html = dict()

    raw_image_path = "./static/dynamic/latest_rain.png"
    simple_image_path = "/static/dynamic/latest_rain_simple.png"

    # Url where to get the radar image
    url = "https://testbed.fmi.fi/?imgtype=radar&t=5&n=1"
    get_image(url, raw_image_path)

    color_50 = "#FA78FF" # pink
    color_40 = "#FF503C" # red
    color_34 = "#FF9632" # dark orange
    color_30 = "#FFCD14" # light orange
    color_24 = "#F0F014" # yellow
    color_18 = "#8CE614" # green
    color_12 = "#05CDAA" # turquoise
    color_08 = "#0A9BE1" # blue

    pixels_50 = count_pixels_with_color(raw_image_path, color_50)
    pixels_40 = count_pixels_with_color(raw_image_path, color_40)
    pixels_34 = count_pixels_with_color(raw_image_path, color_34)
    pixels_30 = count_pixels_with_color(raw_image_path, color_30)
    pixels_24 = count_pixels_with_color(raw_image_path, color_24)
    pixels_18 = count_pixels_with_color(raw_image_path, color_18)
    pixels_12 = count_pixels_with_color(raw_image_path, color_12)
    pixels_08 = count_pixels_with_color(raw_image_path, color_08)

    rain_value = (pixels_50 * 50) + (pixels_40 * 40) + (pixels_34 * 34) + (pixels_30 * 30) + (pixels_24 * 24) + (pixels_18 * 18) + (pixels_12 * 12) + (pixels_08 * 8)

    print(pixels_50)
    print(pixels_40)
    print(pixels_34)
    print(pixels_30)
    print(pixels_24)
    print(pixels_18)
    print(pixels_12)
    print(pixels_08)

    colors_to_keep = [color_50, color_40, color_34, color_30, color_24, color_18, color_12, color_08]
    
    simple_img = simiplify_image(raw_image_path, colors_to_keep)

    simple_img.save("." + simple_image_path)

    html["rain_value"] = "{:,}".format(rain_value).replace(',', ' ') # Thousand separator
    html["simple_img_path"] = simple_image_path

    return html
