#!/usr/bin/env python3
"""Generate Cleric spell tree drawio from wiki data.

Layout-aware: positions cross-book-connected spells at band edges
and routes edges with appropriate exit/entry points to avoid
crossing cells.
"""

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from collections import defaultdict
import math

# --- Spell data from Elanthipedia ---
# (name, spellbook, tier, slots, primary_type, secondary_type, cast_type)
SPELLS = [
    # Antinomic Sorcery
    ("Aspects of the All-God", "Antinomic Sorcery", "Basic", 2, "Augmentation", "Utility", "Ritual"),

    # Divine Intervention
    ("Glythtide's Gift", "Divine Intervention", "Basic", 1, "Augmentation", None, "Standard"),
    ("Aesrela Everild", "Divine Intervention", "Intermediate", 3, "Targeted", None, "Battle"),
    ("Resurrection", "Divine Intervention", "Intermediate", 1, "Utility", None, "Cyclic"),
    ("Fire of Ushnish", "Divine Intervention", "Advanced", 2, "Targeted", None, "Battle"),
    ("Murrula's Flames", "Divine Intervention", "Advanced", 2, "Utility", None, "Ritual"),
    ("Heavenly Fires", "Divine Intervention", "Basic", 2, "Targeted", None, "Metamagic"),

    # Holy Defense
    ("Visage", "Holy Defense", "Intro", 1, "Warding", None, "Standard"),
    ("Protection from Evil", "Holy Defense", "Basic", 1, "Warding", None, "Standard"),
    ("Soul Shield", "Holy Defense", "Basic", 1, "Warding", None, "Standard"),
    ("Starry Waters", "Holy Defense", "Basic", 3, "Augmentation", None, "Standard"),
    ("Benediction", "Holy Defense", "Intermediate", 3, "Augmentation", None, "Standard"),
    ("Ghost Shroud", "Holy Defense", "Intermediate", 2, "Warding", None, "Cyclic"),
    ("Shield of Light", "Holy Defense", "Intermediate", 3, "Augmentation", "Utility", "Battle"),
    ("Halo", "Holy Defense", "Advanced", 3, "Debilitation", "Warding", "Battle"),
    ("Sanyu Lyba", "Holy Defense", "Advanced", 2, "Warding", None, "Battle"),

    # Holy Evocations
    ("Bless", "Holy Evocations", "Intro", 1, "Utility", None, "Standard"),
    ("Divine Radiance", "Holy Evocations", "Basic", 3, "Targeted", "Utility", "Standard"),
    ("Fists of Faenella", "Holy Evocations", "Basic", 1, "Targeted", None, "Battle"),
    ("Harm Evil", "Holy Evocations", "Basic", 2, "Targeted", None, "Battle"),
    ("Horn of the Black Unicorn", "Holy Evocations", "Basic", 1, "Targeted", None, "Battle"),
    ("Curse of Zachriedek", "Holy Evocations", "Intermediate", 2, "Debilitation", None, "Battle"),
    ("Hand of Tenemlor", "Holy Evocations", "Intermediate", 1, "Targeted", None, "Battle"),
    ("Harm Horde", "Holy Evocations", "Intermediate", 3, "Targeted", None, "Battle"),
    ("Malediction", "Holy Evocations", "Intermediate", 2, "Debilitation", None, "Battle"),
    ("Phelim's Sanction", "Holy Evocations", "Intermediate", 1, "Debilitation", None, "Battle"),
    ("Hydra Hex", "Holy Evocations", "Advanced", 2, "Debilitation", None, "Cyclic"),
    ("Time of the Red Spiral", "Holy Evocations", "Advanced", 2, "Targeted", None, "Metamagic"),

    # Conviction
    ("Uncurse", "Conviction", "Basic", 1, "Utility", None, "Battle"),
    ("Huldah's Pall", "Conviction", "Basic", 2, "Debilitation", None, "Battle"),
    ("Sanctify Pattern", "Conviction", "Basic", 2, "Augmentation", None, "Standard"),
    ("Meraud's Cry", "Conviction", "Intermediate", 2, "Debilitation", None, "Battle"),
    ("Persistence of Mana", "Conviction", "Intermediate", 2, "Augmentation", None, "Ritual"),
    ("Idon's Theft", "Conviction", "Advanced", 3, "Debilitation", "Utility", "Battle"),
    ("Osrel Meraud", "Conviction", "Advanced", 3, "Utility", None, "Standard"),
    ("Spite of Dergati", "Conviction", "Advanced", 4, "Debilitation", "Warding", "Battle"),

    # Spirit Manipulation
    ("Centering", "Spirit Manipulation", "Intro", 1, "Augmentation", None, "Standard"),
    ("Auspice", "Spirit Manipulation", "Basic", 2, "Augmentation", None, "Standard"),
    ("Rejuvenation", "Spirit Manipulation", "Basic", 1, "Utility", None, "Standard"),
    ("Soul Bonding", "Spirit Manipulation", "Basic", 1, "Debilitation", None, "Battle"),
    ("Soul Sickness", "Spirit Manipulation", "Basic", 2, "Debilitation", None, "Battle"),
    ("Vigil", "Spirit Manipulation", "Basic", 1, "Utility", None, "Standard"),
    ("Bitter Feast", "Spirit Manipulation", "Basic", 2, "Utility", None, "Metamagic"),
    ("Chill Spirit", "Spirit Manipulation", "Intermediate", 2, "Targeted", None, "Battle"),
    ("Eylhaar's Feast", "Spirit Manipulation", "Intermediate", 2, "Utility", None, "Battle"),
    ("Mass Rejuvenation", "Spirit Manipulation", "Intermediate", 1, "Utility", None, "Standard"),
    ("Revelation", "Spirit Manipulation", "Intermediate", 3, "Augmentation", "Utility", "Cyclic"),
    ("Soul Attrition", "Spirit Manipulation", "Intermediate", 2, "Targeted", None, "Cyclic"),
]

# --- Constants ---
TYPE_COLORS = {
    "Augmentation": ("#AAC8EB", "#000000"),
    "Warding":      ("#147A6D", "#FFFFFF"),
    "Utility":      ("#B3D56A", "#000000"),
    "Targeted":     ("#E80538", "#FFFFFF"),
    "Debilitation":  ("#EBCD00", "#000000"),
    "Metamagic":    ("#D5D0CA", "#000000"),
}

TIER_ORDER = ["Intro", "Basic", "Intermediate", "Advanced", "Esoteric"]
TIER_X = {
    "Intro":        [20, 220],
    "Basic":        [420, 620],
    "Intermediate": [820, 1020],
    "Advanced":     [1220, 1420],
    "Esoteric":     [1620],
}
TIER_DIVIDERS = [400, 800, 1200, 1600]
TIER_LABELS = {
    "Intro": (160, 80),
    "Basic": (560, 80),
    "Intermediate": (940, 120),
    "Advanced": (1340, 120),
    "Esoteric": (1660, 120),
}

# Ordered so adjacent books with cross-connections are neighbors
SPELLBOOK_ORDER = [
    "Holy Defense",
    "Holy Evocations",
    "Conviction",
    "Spirit Manipulation",
    "Divine Intervention",
    "Antinomic Sorcery",
]

# --- Prerequisites from individual wiki pages ---
# (source_spell, target_spell, is_alternative)
# is_alternative=True means "A OR B required" (dashed arrow)
EDGES = [
    # Holy Defense internal
    ("Visage", "Protection from Evil", False),
    ("Visage", "Starry Waters", False),
    ("Visage", "Sanyu Lyba", False),
    ("Protection from Evil", "Soul Shield", False),
    ("Protection from Evil", "Ghost Shroud", False),
    ("Visage", "Shield of Light", False),
    ("Divine Radiance", "Shield of Light", False),
    ("Divine Radiance", "Halo", False),
    ("Starry Waters", "Halo", False),
    ("Bless", "Benediction", False),
    ("Starry Waters", "Benediction", False),
    # Holy Evocations internal + cross-book
    ("Bless", "Divine Radiance", False),
    ("Bless", "Fists of Faenella", False),
    ("Bless", "Horn of the Black Unicorn", False),
    ("Bless", "Hand of Tenemlor", False),
    ("Divine Radiance", "Phelim's Sanction", False),
    ("Harm Evil", "Harm Horde", False),
    ("Harm Evil", "Time of the Red Spiral", False),
    ("Uncurse", "Curse of Zachriedek", False),
    ("Uncurse", "Malediction", False),
    # OR prereqs
    ("Protection from Evil", "Harm Evil", True),
    ("Divine Radiance", "Harm Evil", True),
    ("Fists of Faenella", "Fire of Ushnish", True),
    ("Horn of the Black Unicorn", "Fire of Ushnish", True),
    ("Malediction", "Hydra Hex", True),
    ("Curse of Zachriedek", "Hydra Hex", True),
    # Conviction
    ("Bless", "Uncurse", False),
    ("Bless", "Sanctify Pattern", False),
    ("Uncurse", "Huldah's Pall", False),
    ("Huldah's Pall", "Meraud's Cry", False),
    ("Huldah's Pall", "Idon's Theft", False),
    ("Huldah's Pall", "Spite of Dergati", False),
    ("Sanctify Pattern", "Persistence of Mana", False),
    ("Sanctify Pattern", "Osrel Meraud", False),
    # Divine Intervention
    ("Auspice", "Aesrela Everild", False),
    ("Soul Bonding", "Resurrection", False),
    ("Vigil", "Resurrection", False),
    ("Resurrection", "Murrula's Flames", False),
    # Spirit Manipulation
    ("Centering", "Auspice", False),
    ("Centering", "Rejuvenation", False),
    ("Centering", "Soul Sickness", False),
    ("Rejuvenation", "Vigil", False),
    ("Rejuvenation", "Mass Rejuvenation", False),
    ("Soul Sickness", "Chill Spirit", False),
    ("Soul Sickness", "Soul Attrition", False),
    ("Vigil", "Soul Attrition", False),
    ("Auspice", "Eylhaar's Feast", False),
    ("Eylhaar's Feast", "Bitter Feast", False),
    # OR prereqs
    ("Vigil", "Soul Bonding", True),
    ("Soul Sickness", "Soul Bonding", True),
    ("Auspice", "Revelation", True),
    ("Divine Radiance", "Revelation", True),
]

CIRCLE_REQS = [
    ("Uncurse", 5),
    ("Glythtide's Gift", 10),
    ("Shield of Light", 10),
    ("Mass Rejuvenation", 10),
    ("Soul Shield", 15),
    ("Eylhaar's Feast", 15),
    ("Aspects of the All-God", 20),
    ("Halo", 20),
    ("Persistence of Mana", 20),
    ("Sanyu Lyba", 25),
    ("Benediction", 30),
    ("Ghost Shroud", 30),
    ("Resurrection", 30),
    ("Osrel Meraud", 30),
    ("Revelation", 30),
    ("Fire of Ushnish", 40),
    ("Harm Horde", 40),
    ("Spite of Dergati", 45),
    ("Hydra Hex", 50),
    ("Murrula's Flames", 50),
    ("Meraud's Cry", 70),
]

BOX_W, BOX_H = 160, 40
ROW_SPACING = 60
BAND_PAD_TOP = 15
BAND_PAD_BOTTOM = 15
BAND_GAP = 50
PAGE_WIDTH = 1800
FONT_SOURCE = "fontSource=https%3A%2F%2Ffonts.googleapis.com%2Fcss%3Ffamily%3DAtkinson%2BHyperlegible;"

cell_id_counter = 0
def next_id():
    global cell_id_counter
    cell_id_counter += 1
    return f"cleric-{cell_id_counter}"


def get_fill_style(primary_type, secondary_type, cast_type):
    if cast_type == "Metamagic":
        fill, font = TYPE_COLORS["Metamagic"]
        shadow = "0"
    else:
        fill, font = TYPE_COLORS.get(primary_type, ("#AAC8EB", "#000000"))
        shadow = "1"
    gradient = ""
    if secondary_type and cast_type != "Metamagic":
        grad_fill, _ = TYPE_COLORS.get(secondary_type, ("#AAC8EB", "#000000"))
        gradient = f"gradientColor={grad_fill};gradientDirection=east;"
    return fill, font, shadow, gradient


def slot_dots(n, max_slots=4):
    if n is None:
        return None
    filled = min(n, max_slots)
    empty = max_slots - filled
    return "\u25CF" * filled + "\u25CB" * empty


def build_cross_book_sets():
    """Find spells involved in cross-book edges."""
    spell_book = {s[0]: s[1] for s in SPELLS}
    connects_up = set()
    connects_down = set()
    book_idx = {b: i for i, b in enumerate(SPELLBOOK_ORDER)}
    for src, tgt, _ in EDGES:
        sb, tb = spell_book.get(src), spell_book.get(tgt)
        if sb and tb and sb != tb:
            si, ti = book_idx.get(sb, 0), book_idx.get(tb, 0)
            if si < ti:
                connects_down.add(src)
                connects_up.add(tgt)
            else:
                connects_up.add(src)
                connects_down.add(tgt)
    return connects_up, connects_down


def sort_spells_in_tier(tier_spells, connects_up, connects_down):
    """Sort spells within a tier so cross-book connected ones are at edges."""
    def sort_key(spell):
        name = spell[0]
        if name in connects_up and name in connects_down:
            return 1  # middle
        if name in connects_up:
            return 0  # top
        if name in connects_down:
            return 2  # bottom
        return 1  # middle
    return sorted(tier_spells, key=sort_key)


def build_drawio():
    connects_up, connects_down = build_cross_book_sets()
    spell_book = {s[0]: s[1] for s in SPELLS}
    book_idx = {b: i for i, b in enumerate(SPELLBOOK_ORDER)}

    books = defaultdict(list)
    for spell in SPELLS:
        books[spell[1]].append(spell)

    # Calculate band heights with sorted tiers
    band_info = []
    y_cursor = 50
    for book_name in SPELLBOOK_ORDER:
        spells_in_book = books[book_name]
        tiers = defaultdict(list)
        for s in spells_in_book:
            tiers[s[2]].append(s)
        for t in tiers:
            tiers[t] = sort_spells_in_tier(tiers[t], connects_up, connects_down)
        max_rows = 0
        for tier_name, tier_spells in tiers.items():
            cols = len(TIER_X.get(tier_name, [1]))
            rows = math.ceil(len(tier_spells) / cols)
            max_rows = max(max_rows, rows)
        band_h = max(max_rows * ROW_SPACING + BAND_PAD_TOP + BAND_PAD_BOTTOM, 80)
        band_info.append((book_name, y_cursor, band_h, spells_in_book, tiers))
        y_cursor += band_h + BAND_GAP

    page_height = y_cursor + 100
    line_bottom = page_height - 20

    # Spell position lookup: name -> (x, y)
    spell_pos = {}
    for book_name, by, bh, spells_in_book, tiers in band_info:
        for tier_name in TIER_ORDER:
            tier_spells = tiers.get(tier_name, [])
            if not tier_spells:
                continue
            x_positions = TIER_X[tier_name]
            for idx, spell in enumerate(tier_spells):
                col = idx % len(x_positions)
                row = idx // len(x_positions)
                sx = x_positions[col]
                sy = by + BAND_PAD_TOP + row * ROW_SPACING
                spell_pos[spell[0]] = (sx, sy)

    # Build XML
    root = Element("mxfile", host="app.diagrams.net", version="26.0.4")
    diagram = SubElement(root, "diagram", name="Page-1", id="cleric-diagram")
    model = SubElement(diagram, "mxGraphModel",
                       dx="1138", dy="627", grid="1", gridSize="10",
                       guides="1", tooltips="1", connect="1", arrows="1",
                       fold="1", page="1", pageScale="1",
                       pageWidth=str(PAGE_WIDTH), pageHeight=str(page_height),
                       background="none", math="0", shadow="0")
    xml_root = SubElement(model, "root")
    SubElement(xml_root, "mxCell", id="0")
    SubElement(xml_root, "mxCell", id="1", style="locked=1;", parent="0")

    # --- Layer 1: Tier labels, dividers, legend ---
    for tier_name, (lx, lw) in TIER_LABELS.items():
        tid = next_id()
        c = SubElement(xml_root, "mxCell", id=tid, value=tier_name,
                       style=f"text;align=center;verticalAlign=middle;resizable=0;points=[];autosize=0;strokeColor=none;fillColor=none;fontFamily=Atkinson Hyperlegible;fontSize=18;fontColor=#667788;labelBackgroundColor=none;textShadow=1;{FONT_SOURCE}",
                       parent="1", vertex="1")
        SubElement(c, "mxGeometry", x=str(lx), width=str(lw), height="40", **{"as": "geometry"})

    for dx in TIER_DIVIDERS:
        did = next_id()
        c = SubElement(xml_root, "mxCell", id=did, value="",
                       style="html=1;rounded=0;strokeWidth=2;endArrow=none;endFill=0;dashed=1;labelBackgroundColor=none;shadow=1;strokeColor=#667788;opacity=70;dashPattern=1 1;",
                       parent="1", edge="1")
        geo = SubElement(c, "mxGeometry", width="100", relative="1", **{"as": "geometry"})
        SubElement(geo, "mxPoint", x=str(dx), y="10", **{"as": "sourcePoint"})
        SubElement(geo, "mxPoint", x=str(dx), y=str(line_bottom), **{"as": "targetPoint"})

    hid = next_id()
    c = SubElement(xml_root, "mxCell", id=hid, value="",
                   style="html=1;rounded=0;strokeWidth=2;endArrow=none;endFill=0;dashed=1;labelBackgroundColor=none;shadow=1;strokeColor=#667788;opacity=70;dashPattern=1 1;",
                   parent="1", edge="1")
    geo = SubElement(c, "mxGeometry", width="100", relative="1", **{"as": "geometry"})
    SubElement(geo, "mxPoint", x="10", y="40", **{"as": "sourcePoint"})
    SubElement(geo, "mxPoint", x=str(PAGE_WIDTH - 20), y="40", **{"as": "targetPoint"})

    # Legend
    legend_x, legend_y = PAGE_WIDTH - 220, page_height - 520
    lid = next_id()
    c = SubElement(xml_root, "mxCell", id=lid, value="Legend",
                   style="rounded=1;fillColor=none;verticalAlign=top;labelBackgroundColor=none;container=0;fontStyle=1;fontColor=#667788;fontFamily=Georgia;strokeColor=#667788;shadow=1;glass=0;strokeWidth=1;textShadow=0;whiteSpace=wrap;",
                   parent="1", vertex="1")
    SubElement(c, "mxGeometry", x=str(legend_x), y=str(legend_y), width="200", height="500", **{"as": "geometry"})
    legend_items = [
        ("Special requirements in italics", "text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=1;fontFamily=Georgia;fontSize=15;fontColor=#667788;labelBackgroundColor=none;fontStyle=3;strokeColor=none;", None),
        ("Augmentation", None, "#AAC8EB"),
        ("Warding", None, "#147A6D"),
        ("Utility", None, "#B3D56A"),
        ("Targeted Magic", None, "#E80538"),
        ("Debilitation", None, "#EBCD00"),
        ("Metamagic", None, "#D5D0CA"),
        ("Signature spells in bold", "text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=1;fontFamily=Georgia;fontSize=15;fontColor=#667788;labelBackgroundColor=none;fontStyle=1;strokeColor=none;", None),
        ("\u25CF\u25CB\u25CB\u25CB\nSpell slot cost", "text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=1;fontFamily=Georgia;fontSize=15;fontColor=#667788;labelBackgroundColor=none;fontStyle=1;strokeColor=none;", None),
    ]
    ly = legend_y + 40
    for lbl, custom_style, fill in legend_items:
        iid = next_id()
        if fill:
            fc = "#FFFFFF" if fill in ("#147A6D", "#E80538") else "#000000"
            sv = "0" if fill == "#D5D0CA" else "1"
            sty = f"rounded=1;whiteSpace=wrap;fillColor={fill};labelBackgroundColor=none;fontFamily=Georgia;fontSize=18;strokeColor=#667788;shadow={sv};glass=0;strokeWidth=1;align=center;fontStyle=1;verticalAlign=middle;fontColor={fc};textShadow=0;"
        else:
            sty = custom_style
        c = SubElement(xml_root, "mxCell", id=iid, value=lbl, style=sty, parent="1", vertex="1")
        SubElement(c, "mxGeometry", x=str(legend_x + 20), y=str(ly), width="160", height="40", **{"as": "geometry"})
        ly += 50

    # --- Spellbook borders ---
    borders_layer = SubElement(xml_root, "mxCell", id="spellbook-borders", value="Spellbook borders", style="locked=1;", parent="0")
    band_colors = ["#FCF4C4", "#667788"]
    for i, (book_name, by, bh, _, _) in enumerate(band_info):
        fill = band_colors[i % 2]
        bid = next_id()
        c = SubElement(xml_root, "mxCell", id=bid, value="",
                       style=f"rounded=1;fontFamily=Helvetica;fontSize=11;fontColor=default;labelBackgroundColor=none;fillColor={fill};strokeColor=#667788;opacity=30;glass=0;shadow=0;align=center;verticalAlign=middle;gradientColor=none;strokeWidth=2;",
                       parent="spellbook-borders", vertex="1")
        SubElement(c, "mxGeometry", x="10", y=str(by), width=str(PAGE_WIDTH - 240), height=str(bh), **{"as": "geometry"})
        blid = next_id()
        c = SubElement(xml_root, "mxCell", id=blid, value=book_name,
                       style=f"text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=16;fontFamily=Atkinson Hyperlegible;fontColor=#667788;strokeColor=none;{FONT_SOURCE}",
                       parent="spellbook-borders", vertex="1")
        SubElement(c, "mxGeometry", x="10", y=str(by + bh), width="180", height="40", **{"as": "geometry"})

    # --- Shapes and Lines ---
    shapes_layer = SubElement(xml_root, "mxCell", id="shapes-lines", value="Shapes and Lines", style="locked=1;", parent="0")
    spell_cells = {}

    for book_name, by, bh, spells_in_book, tiers in band_info:
        for tier_name in TIER_ORDER:
            tier_spells = tiers.get(tier_name, [])
            if not tier_spells:
                continue
            x_positions = TIER_X[tier_name]
            for idx, spell in enumerate(tier_spells):
                name = spell[0]
                _, _, _, slots, ptype, stype, ctype = spell
                sx, sy = spell_pos[name]
                fill, font_color, shadow, gradient = get_fill_style(ptype, stype, ctype)
                sid = next_id()
                spell_cells[name] = sid
                font_size = "18"
                if len(name) > 20:
                    font_size = "16"
                if len(name) > 25:
                    font_size = "14"
                sty = (f"rounded=1;strokeWidth=1;strokeColor=#667788;textShadow=0;"
                       f"labelBackgroundColor=none;whiteSpace=wrap;fontSize={font_size};"
                       f"fontFamily=Atkinson Hyperlegible;fillColor={fill};"
                       f"fontColor={font_color};shadow={shadow};glass=0;align=center;"
                       f"verticalAlign=middle;fontStyle=1;resizable=1;{gradient}{FONT_SOURCE}")
                c = SubElement(xml_root, "mxCell", id=sid, value=name, style=sty,
                               parent="shapes-lines", vertex="1")
                SubElement(c, "mxGeometry", x=str(sx), y=str(sy),
                           width=str(BOX_W), height=str(BOX_H), **{"as": "geometry"})

    # --- Edges with corridor-based routing ---
    band_bounds = {}
    for book_name, by, bh, _, _ in band_info:
        band_bounds[book_name] = (by, by + bh)

    # Compute gap centers between adjacent bands
    gap_centers = {}
    for i in range(len(SPELLBOOK_ORDER) - 1):
        b1 = SPELLBOOK_ORDER[i]
        b2 = SPELLBOOK_ORDER[i + 1]
        _, b1_bottom = band_bounds[b1]
        b2_top, _ = band_bounds[b2]
        gap_centers[(b1, b2)] = (b1_bottom + b2_top) // 2
        gap_centers[(b2, b1)] = (b1_bottom + b2_top) // 2

    right_margin_counter = 0

    for src_name, tgt_name, is_alt in EDGES:
        src_id = spell_cells.get(src_name)
        tgt_id = spell_cells.get(tgt_name)
        if not src_id or not tgt_id:
            print(f"  WARNING: edge {src_name} -> {tgt_name}: missing cell id")
            continue

        sx, sy = spell_pos[src_name]
        tx, ty = spell_pos[tgt_name]
        src_bk = spell_book[src_name]
        tgt_bk = spell_book[tgt_name]
        same_book = src_bk == tgt_bk
        src_bi = book_idx[src_bk]
        tgt_bi = book_idx[tgt_bk]

        waypoints = None

        if same_book and tx > sx:
            # Same book, target to the right
            exit_style = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
            entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
        elif same_book:
            # Same book, same or leftward column
            if ty > sy:
                exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
            else:
                exit_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                entry_style = "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
        elif abs(src_bi - tgt_bi) == 1:
            # Adjacent bands: exit bottom/top, horizontal in gap, enter top/bottom
            src_cx = sx + BOX_W // 2
            tgt_cx = tx + BOX_W // 2
            gap_y = gap_centers.get((src_bk, tgt_bk))
            if gap_y is None:
                gap_y = (sy + ty) // 2

            if ty > sy:
                exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
            else:
                exit_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                entry_style = "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"

            if src_cx != tgt_cx:
                waypoints = [
                    (src_cx, gap_y),
                    (tgt_cx, gap_y),
                ]
        else:
            # Skip-band: exit right, route through right margin, enter top/bottom
            right_margin_counter += 1
            margin_x = PAGE_WIDTH - 250 + (right_margin_counter * 15)

            exit_style = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
            if ty > sy:
                entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
                tgt_entry_y = ty
            else:
                entry_style = "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
                tgt_entry_y = ty + BOX_H

            src_exit_y = sy + BOX_H // 2
            tgt_cx = tx + BOX_W // 2
            waypoints = [
                (margin_x, src_exit_y),
                (margin_x, tgt_entry_y),
            ]

        eid = next_id()
        if is_alt:
            sty = (f"edgeStyle=orthogonalEdgeStyle;shape=connector;curved=0;rounded=1;"
                   f"orthogonalLoop=1;jettySize=auto;html=1;"
                   f"{exit_style}{entry_style}"
                   f"strokeColor=#667788;strokeWidth=2;"
                   f"endArrow=classic;endFill=1;dashed=1;")
        else:
            sty = (f"edgeStyle=orthogonalEdgeStyle;shape=connector;curved=0;rounded=1;"
                   f"orthogonalLoop=1;jettySize=auto;html=1;"
                   f"{exit_style}{entry_style}"
                   f"strokeColor=#667788;strokeWidth=2;"
                   f"endArrow=none;endFill=0;")

        c = SubElement(xml_root, "mxCell", id=eid, style=sty,
                       parent="shapes-lines", source=src_id, target=tgt_id, edge="1")
        geo = SubElement(c, "mxGeometry", relative="1", **{"as": "geometry"})

        if waypoints:
            arr = SubElement(geo, "Array", **{"as": "points"})
            for wx, wy in waypoints:
                SubElement(arr, "mxPoint", x=str(wx), y=str(wy))

    # --- Slot cost dots ---
    dots_layer = SubElement(xml_root, "mxCell", id="spell-dots", value="Spell cost bubbles text", style="locked=1;", parent="0")
    for spell in SPELLS:
        name, _, _, slots, ptype, stype, ctype = spell
        dots = slot_dots(slots)
        if dots is None:
            continue
        sx, sy = spell_pos[name]
        dot_x = sx + 120
        dot_y = sy + 20
        fc = "default"
        if ptype in ("Warding", "Targeted") and ctype != "Metamagic":
            fc = "#FFFFFF"
        did = next_id()
        c = SubElement(xml_root, "mxCell", id=did, value=dots,
                       style=f"text;align=center;verticalAlign=middle;rounded=0;fontFamily=Georgia;fontSize=13;fontColor={fc};labelBackgroundColor=none;spacing=0;spacingTop=0;spacingBottom=-5;fillColor=none;",
                       parent="spell-dots", vertex="1")
        SubElement(c, "mxGeometry", x=str(dot_x), y=str(dot_y),
                   width="50", height="20", **{"as": "geometry"})

    # --- Circle prereq labels ---
    circle_layer = SubElement(xml_root, "mxCell", id="circle-prereqs",
                              value="Circle Pre-requisites text", style="locked=1;", parent="0")
    for spell_name, circle in CIRCLE_REQS:
        if spell_name not in spell_pos:
            continue
        sx, sy = spell_pos[spell_name]
        cid = next_id()
        c = SubElement(xml_root, "mxCell", id=cid, value=f"Circle {circle}",
                       style="text;align=right;verticalAlign=bottom;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontFamily=Georgia;fontSize=13;fontColor=#667788;labelBackgroundColor=none;fontStyle=3",
                       parent="circle-prereqs", vertex="1")
        SubElement(c, "mxGeometry", x=str(sx + 90), y=str(sy - 30),
                   width="80", height="30", **{"as": "geometry"})

    # --- Transparency ---
    SubElement(xml_root, "mxCell", id="transparency-layer", value="Transparency", style="locked=1;", parent="0")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    return tree


if __name__ == "__main__":
    tree = build_drawio()
    outpath = "/Users/grocha/repos/dr-spell-trees/Cleric/Cleric.drawio"
    tree.write(outpath, encoding="unicode", xml_declaration=True)
    print(f"Generated {outpath}")
    count = len(SPELLS)
    books = set(s[1] for s in SPELLS)
    print(f"{count} spells across {len(books)} spellbooks: {', '.join(sorted(books))}")
