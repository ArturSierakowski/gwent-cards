from PIL import Image
import os
import json
from math import ceil
import glob

# Stałe
INPUT_DIR = "output/cards"
OUTPUT_DIR = "output/print_sheets"
CARDS_PER_ROW = 3
CARDS_PER_COL = 3
CARDS_PER_PAGE = CARDS_PER_ROW * CARDS_PER_COL
CARD_SIZE = (768, 1157)
A4_SIZE = (2480, 3508)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def gather_pngs_by_faction(directory):
    factions = {}
    cards_json_dir = "cards"  # katalog z jsonami

    for root, _, files in os.walk(directory):
        pngs = [f for f in files if f.lower().endswith(".png")]
        if not pngs:
            continue

        faction = os.path.basename(root)
        json_path = os.path.join(cards_json_dir, f"{faction}.json")
        if os.path.exists(json_path):
            with open(json_path, encoding="utf-8") as f:
                card_data = json.load(f)
            name_to_card = {
                c["name"].replace(":", "").replace(" ", "_").lower(): c for c in card_data
            }
        else:
            name_to_card = {}

        expanded_paths = []
        for fname in pngs:
            name = os.path.splitext(fname)[0]
            full_path = os.path.join(root, fname)

            quantity = 1  # domyślnie jedna kopia
            card_info = name_to_card.get(name)
            if card_info:
                if faction == "token" and "quantity" in card_info:
                    quantity = int(card_info["quantity"])
                elif card_info.get("color") == "bronze":
                    quantity = 2
            expanded_paths.extend([full_path] * quantity)

        factions[faction] = sorted(expanded_paths)

    return factions

def create_sheet(images, sheet_index, faction):
    sheet = Image.new("RGB", A4_SIZE, "white")
    for idx, card in enumerate(images):
        row = idx // CARDS_PER_ROW
        col = idx % CARDS_PER_ROW

        grid_width = CARDS_PER_ROW * CARD_SIZE[0]
        grid_height = CARDS_PER_COL * CARD_SIZE[1]
        offset_x = (A4_SIZE[0] - grid_width) // 2
        offset_y = (A4_SIZE[1] - grid_height) // 2

        x = offset_x + col * CARD_SIZE[0]
        y = offset_y + row * CARD_SIZE[1]

        sheet.paste(card.resize(CARD_SIZE, Image.LANCZOS), (x, y))

    sheet_path = os.path.join(OUTPUT_DIR, f"{faction}_sheet_{sheet_index+1}.png")
    sheet.save(sheet_path)
    print(f"Zapisano: {sheet_path}")

def batch_cards_to_sheets():
    faction_pngs = gather_pngs_by_faction(INPUT_DIR)
    for faction, files in faction_pngs.items():
        total_sheets = ceil(len(files) / CARDS_PER_PAGE)
        for i in range(total_sheets):
            batch = files[i * CARDS_PER_PAGE : (i + 1) * CARDS_PER_PAGE]
            images = [Image.open(path).convert("RGB") for path in batch]
            create_sheet(images, i, faction)

def save_all_sheets_as_pdf(output_dir, output_pdf_path):
    image_paths = sorted(glob.glob(os.path.join(output_dir, "*.png")))
    if not image_paths:
        print("Brak plików PNG do połączenia.")
        return

    images = [Image.open(p).convert("RGB") for p in image_paths]  # ← zostaje RGB
    first_image, rest_images = images[0], images[1:]
    first_image.save(output_pdf_path, save_all=True, append_images=rest_images)
    print(f"Zapisano PDF: {output_pdf_path}")

if __name__ == "__main__":
    batch_cards_to_sheets()
    save_all_sheets_as_pdf(OUTPUT_DIR, os.path.join(OUTPUT_DIR, "all_sheets.pdf"))
