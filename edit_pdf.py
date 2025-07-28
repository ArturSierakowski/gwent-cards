import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import os

INPUT_PDF = "output/print_sheets/all_sheets.pdf"
OUTPUT_PDF = "output/print_sheets/all_sheets_edited2.pdf"

def process_page(pix):
    # Konwersja do obrazu PIL
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Jasność: +30%
    img = ImageEnhance.Brightness(img).enhance(1.3)
    # Kontrast: -5%
    img = ImageEnhance.Contrast(img).enhance(0.95)

    return img

def increase_shadows(image, strength=0.1):
    # Przetwarza obraz RGB, zmniejszając jasność ciemnych pikseli (cienie)
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            avg = (r + g + b) / 3
            if avg < 80:  # tylko ciemne piksele
                r = int(r * (1 - strength))
                g = int(g * (1 - strength))
                b = int(b * (1 - strength))
                pixels[x, y] = (r, g, b)
    return image

def main():
    doc = fitz.open(INPUT_PDF)
    output_images = []

    for page in doc:
        pix = page.get_pixmap(dpi=200)  # Możesz zmienić DPI
        image = process_page(pix)
        output_images.append(image.convert("RGB"))

    if output_images:
        output_images[0].save(
            OUTPUT_PDF,
            save_all=True,
            append_images=output_images[1:]
        )

    print(f"Zapisano: {OUTPUT_PDF}")

if __name__ == "__main__":
    main()
