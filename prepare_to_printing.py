from PIL import Image
import os
from math import ceil

# Stałe
INPUT_DIR = "output/cards/monsters"
OUTPUT_DIR = "print_sheets"
CARDS_PER_ROW = 2
CARDS_PER_COL = 2
CARDS_PER_PAGE = CARDS_PER_ROW * CARDS_PER_COL
CARD_SIZE = (827, 1417)  # 80x120 mm at 300 DPI
A4_SIZE = (2480, 3508)   # A4 at 300 DPI
PRINTER_MARGIN = 40      # ok. 5 mm margines

os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_sheet(images, sheet_index):
    sheet = Image.new("RGB", A4_SIZE, "white")

    # Oblicz pole z kartami i offset do wyśrodkowania
    total_width = CARDS_PER_ROW * CARD_SIZE[0]
    total_height = CARDS_PER_COL * CARD_SIZE[1]
    offset_x = (A4_SIZE[0] - total_width) // 2
    offset_y = (A4_SIZE[1] - total_height) // 2

    for idx, card in enumerate(images):
        row = idx // CARDS_PER_ROW
        col = idx % CARDS_PER_ROW
        x = offset_x + col * CARD_SIZE[0]
        y = offset_y + row * CARD_SIZE[1]
        gray_card = card.convert("L").convert("RGB")  # grayscale
        sheet.paste(gray_card.resize(CARD_SIZE, Image.LANCZOS), (x, y))

    path = os.path.join(OUTPUT_DIR, f"sheet_{sheet_index+1}.png")
    sheet.save(path)
    print(f"Zapisano: {path}")

def batch_cards_to_sheets():
    files = sorted([
        os.path.join(INPUT_DIR, f)
        for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".png")
    ])

    total_sheets = ceil(len(files) / CARDS_PER_PAGE)
    for i in range(total_sheets):
        batch = files[i * CARDS_PER_PAGE: (i + 1) * CARDS_PER_PAGE]
        images = [Image.open(path).convert("RGB") for path in batch]
        create_sheet(images, i)

if __name__ == "__main__":
    batch_cards_to_sheets()
