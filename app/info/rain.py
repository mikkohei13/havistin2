

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


def count_pixels_with_color(image_path, color_dict):
    total_rain_value = 0

    # Load the image
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        width, height = img.size

        # Crop to square
        calculation_size = 508
        calculation_size = 300
        left = (width - calculation_size) / 2
        top = (height - calculation_size) / 2
        right = (width + calculation_size) / 2
        bottom = (height + calculation_size) / 2

        cropped_img = img.crop((left, top, right, bottom))

        for color_value, color_hex in color_dict.items():
            # Convert hex color to an RGB tuple
            color_hex = color_hex.lstrip('#')
            target_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))

            # Iterate over pixels and count the matches
            count = 0
            for pixel in cropped_img.getdata():
                if pixel == target_color:
                    count += 1
            
            # Multiply with rain intensity
            count = count * int(color_value)
            total_rain_value = total_rain_value + count

        # Todo: move to settings
        cropped_img.save('./static/dynamic/latest_rain_cropped_for_calculation.png')

    # Calculate rain value relative to area
    area = calculation_size * calculation_size
    total_rain_value = round(total_rain_value / area, 2)

    return total_rain_value, calculation_size


def simiplify_image(image_path, colors_to_keep_dict):
    # Convert hex colors to RGB tuples
#    colors_to_keep = [tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for color in colors_to_keep] # list
    colors_to_keep = [tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for hex_color in colors_to_keep_dict.values()] # dict


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

        # Todo: draw box around where rain intensity is calculated

        return img


def main():
    html = dict()

    raw_image_path = "./static/dynamic/latest_rain.png"
    simple_image_path = "/static/dynamic/latest_rain_simple.png"

    # Url where to get the radar image
    url = "https://testbed.fmi.fi/?imgtype=radar&t=5&n=1"
    get_image(url, raw_image_path)

    rain_colors = dict()
    rain_colors["50"] = "#FA78FF" # pink
    rain_colors["40"] = "#FF503C" # red
    rain_colors["34"] = "#FF9632" # dark orange
    rain_colors["30"] = "#FFCD14" # light orange
    rain_colors["24"] = "#F0F014" # yellow
    rain_colors["18"] = "#8CE614" # green
    rain_colors["12"] = "#05CDAA" # turquoise
    rain_colors["08"] = "#0A9BE1" # blue

    rain_value, calculation_size = count_pixels_with_color(raw_image_path, rain_colors)
    
    simple_img = simiplify_image(raw_image_path, rain_colors)

    simple_img.save("." + simple_image_path)

#    html["rain_value"] = "{:,}".format(rain_value).replace(',', ' ') # Thousand separator, in case the value is absolute (not relative to pixel count)
    html["rain_value"] = rain_value
    html["calculation_size"] = calculation_size
    html["simple_img_path"] = simple_image_path

    return html
