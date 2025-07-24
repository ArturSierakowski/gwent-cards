from PIL import Image
import os
from math import ceil

# Stałe
INPUT_DIR = "output/cards"
OUTPUT_DIR = "output/print_sheets"
CARDS_PER_ROW = 2
CARDS_PER_COL = 2
CARDS_PER_PAGE = CARDS_PER_ROW * CARDS_PER_COL
CARD_SIZE = (827, 1417)
A4_SIZE = (2480, 3508)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_sheet(images, sheet_index, faction):
    sheet = Image.new("RGB", A4_SIZE, "white")
    for idx, card in enumerate(images):
        row = idx // CARDS_PER_ROW
        col = idx % CARDS_PER_ROW
        # Oblicz łączny rozmiar siatki kart
        grid_width = CARDS_PER_ROW * CARD_SIZE[0]
        grid_height = CARDS_PER_COL * CARD_SIZE[1]

        # Wyśrodkuj siatkę na arkuszu A4
        offset_x = (A4_SIZE[0] - grid_width) // 2
        offset_y = (A4_SIZE[1] - grid_height) // 2

        x = offset_x + col * CARD_SIZE[0]
        y = offset_y + row * CARD_SIZE[1]

        gray_card = card.convert("L").convert("RGB")
        sheet.paste(gray_card.resize(CARD_SIZE, Image.LANCZOS), (x, y))
    sheet_path = os.path.join(OUTPUT_DIR, f"{faction}_sheet_{sheet_index+1}.png")
    sheet.save(sheet_path)
    print(f"Zapisano: {sheet_path}")

def gather_pngs_by_faction(directory):
    factions = {}
    for root, _, files in os.walk(directory):
        pngs = [os.path.join(root, f) for f in files if f.lower().endswith(".png")]
        if pngs:
            faction = os.path.basename(root)
            factions[faction] = sorted(pngs)
    return factions

def batch_cards_to_sheets():
    faction_pngs = gather_pngs_by_faction(INPUT_DIR)
    for faction, files in faction_pngs.items():
        total_sheets = ceil(len(files) / CARDS_PER_PAGE)
        for i in range(total_sheets):
            batch = files[i * CARDS_PER_PAGE : (i + 1) * CARDS_PER_PAGE]
            images = [Image.open(path).convert("RGB") for path in batch]
            create_sheet(images, i, faction)

if __name__ == "__main__":
    batch_cards_to_sheets()
