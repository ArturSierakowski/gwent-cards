import os
import json

CARDS_DIR = "cards"

def sort_cards(cards):
    return sorted(
        cards,
        key=lambda c: (-c.get("provision", 0), c.get("tags", ""))
    )

for filename in os.listdir(CARDS_DIR):
    if filename.endswith(".json"):
        path = os.path.join(CARDS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            try:
                cards = json.load(f)
                if isinstance(cards, list):
                    sorted_cards = sort_cards(cards)
                    with open(path, "w", encoding="utf-8") as out_f:
                        json.dump(sorted_cards, out_f, ensure_ascii=False, indent=4)
                    print(f"✓ Posortowano: {filename}")
                else:
                    print(f"✗ Pominięto (nie lista): {filename}")
            except Exception as e:
                print(f"✗ Błąd przy {filename}: {e}")
