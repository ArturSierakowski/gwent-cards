import os
import json
import pandas as pd
from collections import defaultdict

cards_dir = "cards/"
provision_counts = defaultdict(lambda: defaultdict(int))

for filename in os.listdir(cards_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(cards_dir, filename)
        with open(filepath, encoding="utf-8") as f:
            cards = json.load(f)

        for card in cards:
            prov = card.get("provision", 0)
            provision_counts[prov][filename[:-5]] += 1  # usunięcie .json z nazwy

# Konwersja do DataFrame
df = pd.DataFrame(provision_counts).fillna(0).astype(int).T.sort_index()

# Wyświetlenie (lub zapis)
print(df)
# df.to_csv("provision_table.csv")
