from PIL import Image, ImageDraw, ImageFont
import os
import json
import re

# Wymiary karty
CARD_WIDTH, CARD_HEIGHT = 1024, 1597
FRAME_SIZE = (CARD_WIDTH, CARD_HEIGHT)
MARGIN = 16
MARGIN_SIDE = 70
MARGIN_BOTTOM = 60
LINE_SPACING = 52

ARMOR_SIZE = 256
ORDER_SIZE = 192
STATUS_SIZE = 192

# Foldery
INPUT_JSON = "cards/tokens.json"
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
NAME_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "GWENT-ExtraBold.ttf"), 72)
TAGS_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "Arial.ttf"), 38)
STRENGTH_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "GWENT-ExtraBold.ttf"), 256)
ARMOR_FONT = ImageFont.truetype(os.path.join(FONTS_DIR, "GWENT-ExtraBold.ttf"), 192)
ABILITY_FONT = ImageFont.truetype("arial.ttf", 42)

KEYWORDS = {"order", "spawn", "charges", "armor", "heal", "bleeding", "grace", "shield", "veil", "seize", "lock",
            "symbiosis", "vitality", "melee", "rain", "cooldown", "frost", "zeal", "poison", "discard", "deathwish",
            "doomed", "immunity", "resilience", "deploy", "disloyal", "deathblow", "summon", "purify", "predator",
            "banish", "storm", "timer", "echo", "ranged", "spying", "devotion", "clash", "crew", "thrive", "barricade",
            "bloodthirst", "formation", "veteran", "patience", "inspired", "ambush", "spring", "drain", "duel",
            "bonded", "berserk", "dominance", "exposed", "initiative", "resupply", "resurrect", "reveal", "cataclysm",
            "lineage", "advantage", "conspiracy", "truce", "(melee)", "(ranged)", "dominance", "create"}

ICONS_ABOVE_NAMEBOX = ["shield", "veil", "disloyal", "immunity", "doomed", "resilience"]


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

    if card.get("tags"):
        height_scale = 1.3
    else:
        height_scale = 1

    new_height = int(faction_box.height * scale * height_scale)
    faction_box = faction_box.resize((992, new_height), Image.LANCZOS)

    faction_y = ability_y - new_height
    base.paste(faction_box, (MARGIN, faction_y), faction_box)
    return faction_y


def draw_name_and_tags(draw, card, faction_y):
    name_bbox = draw.textbbox((0, 0), card["name"], font=NAME_FONT)
    name_x = (CARD_WIDTH - (name_bbox[2] - name_bbox[0])) // 2
    name_y = faction_y + MARGIN + 8
    draw.text((name_x, name_y), card["name"], font=NAME_FONT, fill="white")

    tags_bbox = draw.textbbox((0, 0), card["tags"], font=TAGS_FONT)
    tags_x = (CARD_WIDTH - (tags_bbox[2] - tags_bbox[0])) // 2
    tags_y = name_y + (name_bbox[3] - name_bbox[1]) + MARGIN / 2
    draw.text((tags_x, tags_y), card["tags"], font=TAGS_FONT, fill="white")

    return name_y


def draw_ability_text(draw, lines, ability_y, dynamic_height):
    x_start = MARGIN_SIDE
    y_start = ability_y + dynamic_height - MARGIN_BOTTOM - len(lines) * LINE_SPACING
    for line in lines:
        words = line.split()
        x = x_start
        for word in words:
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

    elif card["type"] == "leader":
        icon_name = f"{card['name'].replace(':', '').replace(' ', '_').lower()}.png"
        leader_icon_path = os.path.join("assets", "leader_icons", icon_name)
        if os.path.exists(leader_icon_path):
            leader_icon = Image.open(leader_icon_path).convert("RGBA")
            leader_icon = leader_icon.resize((int(173 * TYPEBOX_SCALE), int(173 * TYPEBOX_SCALE)), Image.LANCZOS)
            icon_x = typebox_x + (typebox.width - leader_icon.width) // 2
            icon_y = typebox_y + (typebox.height - leader_icon.height - int(173 * TYPEBOX_SCALE)) // 2
            base.paste(leader_icon, (icon_x, icon_y), leader_icon)


def parse_ability_keywords(ability_text):
    icons_above_namebox = []
    center_icon = None
    armor_value = None

    ability_text = ability_text.strip()

    match = re.match(r"Armor:\s*(\d+)", ability_text, re.IGNORECASE)
    if match:
        armor_value = int(match.group(1))
        ability_text = ability_text[match.end():].lstrip()

    lowered = ability_text.lower()
    if lowered.startswith("zeal") and "order" in lowered:
        center_icon = "zeal"
    elif lowered.startswith("order"):
        center_icon = "order"

    for kw in ICONS_ABOVE_NAMEBOX:
        pattern = rf"^{kw}[\s.,]*"
        if re.match(pattern, ability_text, re.IGNORECASE):
            icons_above_namebox.append(kw)
            ability_text = re.sub(pattern, "", ability_text, flags=re.IGNORECASE)

    return armor_value, center_icon, icons_above_namebox, ability_text.strip()


def draw_keyword_icons(base, draw, armor_value, center_icon, status_icons, name_y):
    if armor_value is not None:
        armor_icon = Image.open(os.path.join(ICONS_DIR, "armor.png")).convert("RGBA")
        armor_icon = armor_icon.resize((ARMOR_SIZE, ARMOR_SIZE), Image.LANCZOS)
        armor_x = CARD_WIDTH - ARMOR_SIZE - MARGIN
        armor_y = MARGIN
        base.paste(armor_icon, (armor_x, armor_y), armor_icon)

        text = str(armor_value)
        text_w = draw.textlength(text, font=ARMOR_FONT)
        text_h = ARMOR_FONT.getbbox(text)[3] - ARMOR_FONT.getbbox(text)[1]
        text_x = armor_x + (ARMOR_SIZE - text_w) // 2
        text_y = armor_y + (ARMOR_SIZE - text_h) // 2 - 16
        draw_text_with_outline(draw, (text_x, text_y), text, ARMOR_FONT, fill="#CCCCCC", outline="black", outline_width=5)

    if center_icon:
        icon_path = os.path.join(ICONS_DIR, f"{center_icon}.png")
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path).convert("RGBA").resize((ORDER_SIZE, ORDER_SIZE), Image.LANCZOS)
            icon_x = (CARD_WIDTH - ORDER_SIZE) // 2
            icon_y = name_y - ORDER_SIZE - MARGIN
            base.paste(icon_img, (icon_x, icon_y), icon_img)

    for i, kw in enumerate(status_icons):
        icon_path = os.path.join(ICONS_DIR, f"{kw}.png")
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path).convert("RGBA").resize((STATUS_SIZE, STATUS_SIZE), Image.LANCZOS)
            icon_x = 50
            icon_y = name_y - ((i + 1) * (STATUS_SIZE + MARGIN_BOTTOM // 2))
            base.paste(icon_img, (icon_x, icon_y), icon_img)


def save_card_image(base, card):
    filename = f"{card['name'].replace(':', '').replace(' ', '_').lower()}.png"
    base.save(os.path.join(OUTPUT_DIR, filename))


def render_card(card):
    base = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT))
    paste_artwork(base, card)
    draw = ImageDraw.Draw(base)

    lines = wrap_text(draw, card.get("ability", ""), ABILITY_FONT, CARD_WIDTH - 2 * MARGIN_SIDE)
    armor_value, center_icon, icons_above_namebox, cleaned_ability_text = parse_ability_keywords(card.get("ability", ""))
    ability_y, dynamic_height = draw_ability_box(base, draw, wrap_text(draw, cleaned_ability_text, ABILITY_FONT, CARD_WIDTH - 2 * MARGIN_SIDE))
    faction_y = draw_faction_box(base, card, ability_y)
    name_y = draw_name_and_tags(draw, card, faction_y)

    draw_keyword_icons(base, draw, armor_value, center_icon, icons_above_namebox, name_y)

    draw_ability_text(draw, wrap_text(draw, cleaned_ability_text, ABILITY_FONT, CARD_WIDTH - 2 * MARGIN_SIDE), ability_y, dynamic_height)
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