from PIL import Image
import colorsys
import os
import numpy as np

RARITY_COLORS = {
    "red": 0.0,
    "orange": 0.08,
    "yellow": 0.17,
    "green": 0.33,
    "cyan": 0.50,
    "blue": 0.66,
    "purple": 0.83
}

INPUT_PATH = "assets/icons/common.png"
OUTPUT_DIR = "output/rarities"
os.makedirs(OUTPUT_DIR, exist_ok=True)

input_image = Image.open(INPUT_PATH).convert("RGBA")
pixels = input_image.load()
width, height = input_image.size

for name, hue in RARITY_COLORS.items():
    output = Image.new("RGBA", (width, height))
    output_pixels = output.load()

    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]

            if a == 0:
                output_pixels[x, y] = (0, 0, 0, 0)
                continue

            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

            if v == 0:
                output_pixels[x, y] = (0, 0, 0, a)
                continue

            new_r, new_g, new_b = colorsys.hsv_to_rgb((hue + h - 0.58) % 1.0, s ** (1/4), 1/(1+np.exp(-6*(v - 0.5))))
            output_pixels[x, y] = (
                int(new_r * 255),
                int(new_g * 255),
                int(new_b * 255),
                a
            )

    output.save(os.path.join(OUTPUT_DIR, f"{name}.png"))
