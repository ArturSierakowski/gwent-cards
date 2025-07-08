from PIL import Image, ImageDraw, ImageFont
import os
import json
import re

# Wymiary karty
CARD_WIDTH, CARD_HEIGHT = 1024, 1755
FRAME_SIZE = (CARD_WIDTH, CARD_HEIGHT)
MARGIN = 16
MARGIN_SIDE = 80
MARGIN_BOTTOM = 96
LINE_SPACING = 46

# Foldery
INPUT_JSON = "cards/nilfgaard.json"
TEMPLATES_DIR = "assets/templates/"
ICONS_DIR = "assets/icons/"
ART_DIR = "assets/arts/"
FONTS_DIR = "assets/fonts/"
FACTION_NAME = os.path.splitext(INPUT_JSON)[0]
OUTPUT_DIR = f"output/{FACTION_NAME}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Skalowanie boxa
TYPEBOX_ORIG_SIZE = 197
TYPEBOX_SCALE = 1.7
TYPEBOX_SIZE = int(TYPEBOX_ORIG_SIZE * TYPEBOX_SCALE)

# Czcionki
NAME_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "GWENT-ExtraBold.ttf"), 60)
TYPE_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "Arial.ttf"), 42)
STRENGTH_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "GWENT-ExtraBold.ttf"), 256)
ABILITY_FONT = ImageFont.truetype("arial.ttf", 42)

KEYWORDS = {"order", "spawn", "charges", "armor", "heal", "bleeding", "grace", "shield", "veil", "seize", "lock",
            "symbiosis", "vitality", "melee", "rain", "cooldown", "frost", "zeal", "poison", "discard", "deathwish",
            "doomed", "immunity", "resilience", "deploy", "disloyal", "deathblow", "summon", "harmony", "purify",
            "banish", "storm", "timer", "echo", "ranged", "spying", "devotion", "clash", "crew", "thrive", "barricade",
            "bloodthirst", "formation", "veteran", "patience", "inspired", "ambush", "spring", "drain", "duel",
            "bonded", "berserk", "dominance", "exposed", "initiative", "resupply", "resurrect", "reveal"}


def normalize(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())


def find_image_path(card_name):
    target = normalize(card_name)
    for root, _, files in os.walk(ART_DIR):
        for fname in files:
            if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            base = os.path.splitext(fname)[0]
            if normalize(base).endswith(target):
                return os.path.join(root, fname)
    return None


def wrap_text(draw, text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        line = ""
        for word in paragraph.split():
            test_line = f"{line} {word}".strip()
            w = draw.textlength(test_line, font=font)
            if w <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines

def draw_text_with_outline(draw, position, text, font, fill="white", outline="black", outline_width=2):
    x, y = position
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)

def paste_artwork(base, card):
    art_path = find_image_path(card["name"])
    if not art_path:
        raise FileNotFoundError(f"Brak grafiki do: {card['name']}")
    art = Image.open(art_path).convert("RGBA")
    base.paste(art, (MARGIN, MARGIN))

def draw_ability_box(base, draw, lines):
    dynamic_height = MARGIN + len(lines) * LINE_SPACING + MARGIN_BOTTOM
    ability_box = Image.open(os.path.join(TEMPLATES_DIR, "description_bg.png")).convert("RGBA")
    ability_box = ability_box.resize((992, dynamic_height), Image.LANCZOS)
    ability_y = CARD_HEIGHT - dynamic_height - MARGIN
    base.paste(ability_box, (MARGIN, ability_y), ability_box)
    return ability_y, dynamic_height

def draw_faction_box(base, card, ability_y):
    faction_path = os.path.join(TEMPLATES_DIR, f"{card['faction']}.png")
    faction_box = Image.open(faction_path).convert("RGBA")
    scale = 992 / faction_box.width
    faction_box = faction_box.resize((992, int(faction_box.height * scale * 1.2)), Image.LANCZOS)
    faction_y = ability_y - faction_box.height
    base.paste(faction_box, (MARGIN, faction_y), faction_box)
    return faction_y

def draw_name_and_tags(draw, card, faction_y):
    name_bbox = draw.textbbox((0, 0), card["name"], font=NAME_FONT)
    name_x = (CARD_WIDTH - (name_bbox[2] - name_bbox[0])) // 2
    name_y = faction_y + MARGIN
    draw.text((name_x, name_y), card["name"], font=NAME_FONT, fill="white")

    type_bbox = draw.textbbox((0, 0), card["tags"], font=TYPE_FONT)
    type_x = (CARD_WIDTH - (type_bbox[2] - type_bbox[0])) // 2
    type_y = name_y + (name_bbox[3] - name_bbox[1]) + MARGIN
    draw.text((type_x, type_y), card["tags"], font=TYPE_FONT, fill="white")

def draw_ability_text(draw, lines, ability_y, dynamic_height):
    x_start = MARGIN_SIDE
    y_start = ability_y + dynamic_height - MARGIN_BOTTOM - len(lines) * LINE_SPACING
    for line in lines:
        words = line.split()
        x = x_start
        for word in words:
            # Dodaj spację przed słowem jeśli nie jest to pierwszy wyraz
            prefix = " " if x > x_start else ""
            test_word = prefix + word
            color = "#500000" if word.strip(".,:;!?").lower() in KEYWORDS else "black"
            draw.text((x, y_start), test_word, font=ABILITY_FONT, fill=color)
            x += draw.textlength(test_word, font=ABILITY_FONT)
        y_start += LINE_SPACING

def draw_frame(base, card):
    frame_path = os.path.join(TEMPLATES_DIR, f"{card['color']}_frame.png")
    frame = Image.open(frame_path).convert("RGBA").resize(FRAME_SIZE, Image.LANCZOS)
    base.paste(frame, (0, 0), frame)

def draw_type_box(base, card):
    typebox_path = os.path.join(ICONS_DIR, f"{card['faction']}.png")
    typebox = Image.open(typebox_path).convert("RGBA")
    typebox = typebox.resize((int(typebox.width * TYPEBOX_SCALE), int(typebox.height * TYPEBOX_SCALE)), Image.LANCZOS)
    typebox_x = MARGIN - 10
    typebox_y = MARGIN
    base.paste(typebox, (typebox_x, typebox_y), typebox)
    return typebox, typebox_x, typebox_y

def draw_rarity_icon(base, card, typebox_x, typebox_y):
    rarity_path = os.path.join(ICONS_DIR, f"{card['rarity']}.png")
    if os.path.exists(rarity_path):
        RARITY_SCALE = 0.62
        RARITY_OFFSET_X = 53
        RARITY_OFFSET_Y = 51
        rarity_icon = Image.open(rarity_path).convert("RGBA")
        rarity_icon = rarity_icon.resize(
            (
                int(rarity_icon.width * RARITY_SCALE * TYPEBOX_SCALE),
                int(rarity_icon.height * RARITY_SCALE * TYPEBOX_SCALE),
            ),
            Image.LANCZOS,
        )
        rarity_x = typebox_x + RARITY_OFFSET_X
        rarity_y = typebox_y + RARITY_OFFSET_Y
        base.paste(rarity_icon, (rarity_x, rarity_y), rarity_icon)

def draw_type_or_strength(draw, base, card, typebox, typebox_x, typebox_y):
    if card["type"] == "unit" and "strength" in card:
        strength_text = str(card["strength"])
        strength_w = draw.textlength(strength_text, font=STRENGTH_FONT)
        text_x = typebox_x + (typebox.width - strength_w) // 2
        text_y = typebox_y + (typebox.height - STRENGTH_FONT.size - int(173 * TYPEBOX_SCALE)) // 2
        draw_text_with_outline(draw, (text_x, text_y), strength_text, STRENGTH_FONT, fill="#CCCCCC", outline="black", outline_width=5)
    elif card["type"] in ("special", "artifact", "stratagem"):
        icon_path = os.path.join(ICONS_DIR, f"{card['type']}.png")
        if os.path.exists(icon_path):
            type_icon = Image.open(icon_path).convert("RGBA")
            icon_x = typebox_x + (typebox.width - type_icon.width) // 2
            icon_y = typebox_y + (typebox.height - type_icon.height - int(173 * TYPEBOX_SCALE)) // 2
            if card["type"] == "special":
                icon_x -= 2
            base.paste(type_icon, (icon_x, icon_y), type_icon)

def save_card_image(base, card):
    filename = f"{card['name'].replace(':', '').replace(' ', '_').lower()}.png"
    base.save(os.path.join(OUTPUT_DIR, filename))

def render_card(card):
    base = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT))
    paste_artwork(base, card)
    draw = ImageDraw.Draw(base)

    lines = wrap_text(draw, card.get("ability", ""), ABILITY_FONT, CARD_WIDTH - 2 * MARGIN_SIDE)
    ability_y, dynamic_height = draw_ability_box(base, draw, lines)
    faction_y = draw_faction_box(base, card, ability_y)
    draw_name_and_tags(draw, card, faction_y)
    draw_ability_text(draw, lines, ability_y, dynamic_height)
    draw_frame(base, card)
    typebox, typebox_x, typebox_y = draw_type_box(base, card)
    draw_rarity_icon(base, card, typebox_x, typebox_y)
    draw_type_or_strength(draw, base, card, typebox, typebox_x, typebox_y)
    save_card_image(base, card)

if __name__ == "__main__":
    with open(INPUT_JSON, encoding="utf-8") as f:
        cards = json.load(f)

    for card in cards:
        render_card(card)
