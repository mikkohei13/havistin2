

from helpers import common_helpers

import requests
from html.parser import HTMLParser
from PIL import Image, ImageDraw
from io import BytesIO
import cv2
import numpy as np

def get_image_list(url):
    response = requests.get(url)

    import re

    # Regular expression to extract URLs in anim_images_anim_anim
    pattern = r'var anim_images_anim_anim = new Array\((.*?)\);'

    # Search for the pattern in the script content
    match = re.search(pattern, response.text, re.DOTALL)

    if match:
        # Extract and clean the URLs from the match
        urls_raw = match.group(1)
        urls = re.findall(r'"(https?://[^"]+)"', urls_raw)
        return urls
    
    return None


def count_pixels_with_color(img, color_dict):
    total_rain_value = 0

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


def simiplify_image(img, colors_to_keep_dict):
    # Convert hex colors to RGB tuples
#    colors_to_keep = [tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for color in colors_to_keep] # list
    colors_to_keep = [tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for hex_color in colors_to_keep_dict.values()] # dict

    img = img.convert('RGB')
    pixels = img.load()

    for i in range(img.width):
        for j in range(img.height):
            if pixels[i, j] not in colors_to_keep:
                pixels[i, j] = (0, 0, 0)  # Set to black


    # Draw a dot to our location
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


def calculate_optical_flow_direction(images):
    # Initialize variables for optical flow
    flows = []

    grayscale_images = []

    # Convert images to grayscale
    for img in images:
        gray_image = img.convert("L")
        gray_array = np.array(gray_image)
        grayscale_images.append(gray_array)

    # Calculate optical flow between consecutive frames
    for i in range(len(grayscale_images) - 1):
        flow = cv2.calcOpticalFlowFarneback(
            grayscale_images[i], grayscale_images[i + 1], None,
            pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        flows.append(flow)

    # Aggregate the flow vectors to determine average motion
    average_flows = [np.mean(flow, axis=(0, 1)) for flow in flows]

    # Determine the dominant direction of motion
    average_direction = np.mean(average_flows, axis=0)
    magnitude = np.linalg.norm(average_direction)
    angle = np.arctan2(average_direction[1], average_direction[0]) * 180 / np.pi

#    print(f"Average direction (x, y): {average_direction}")
#    print(f"Magnitude of motion: {magnitude}")
#    print(f"Direction angle: {angle:.2f} degrees")

    return angle, magnitude


def main():
    html = dict()

    image_directory = "./static/dynamic/"

    # Url where to get the radar images
    url = "https://testbed.fmi.fi/?imgtype=radar&t=5&n=3"
    image_urls = get_image_list(url)

    rain_colors = dict()
    rain_colors["50"] = "#FA78FF" # pink
    rain_colors["40"] = "#FF503C" # red
    rain_colors["34"] = "#FF9632" # dark orange
    rain_colors["30"] = "#FFCD14" # light orange
    rain_colors["24"] = "#F0F014" # yellow
    rain_colors["18"] = "#8CE614" # green
    rain_colors["12"] = "#05CDAA" # turquoise
    rain_colors["08"] = "#0A9BE1" # blue

    # Handle each url
    images = []
    image_count = len(image_urls)

    for i, image_url in enumerate(image_urls):

        # Fetch image
        response = requests.get(image_url)

        # Convert response content to image
        image = Image.open(BytesIO(response.content))

        # Simplify the image
        simplified_image = simiplify_image(image, rain_colors)

        # Append to images
        images.append(simplified_image)

        # Save the last image
        if i == image_count - 1:
            simplified_image.save(image_directory + "latest_rain_simple.png")

    # Calculate optical flow
    direction, magnitude = calculate_optical_flow_direction(images)
    html["direction"] = int(direction) - 90 # Convert to compass direction
    html["magnitude"] = round(magnitude, 2)

    # Calculate rain value
    rain_value, calculation_size = count_pixels_with_color(simplified_image, rain_colors)
#    html["rain_value"] = "{:,}".format(rain_value).replace(',', ' ') # Thousand separator, in case the value is absolute (not relative to pixel count)
    html["rain_value"] = rain_value
    html["calculation_size"] = calculation_size

    return html
    



