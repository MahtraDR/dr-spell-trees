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
    ("Heavenly Fires", "Divine Intervention", "Basic", None, "Targeted", None, "Metamagic"),

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
    ("Bitter Feast", "Spirit Manipulation", "Basic", None, "Utility", None, "Metamagic"),
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
    "Intro":        [40, 220],
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

# Manual row overrides: force specific spells to share a row with another spell
ROW_OVERRIDES = {
    "Bitter Feast": "Eylhaar's Feast",
}

# Manual x-position: spell placed 200px right of the named spell
X_ALIGN_OVERRIDES = {
    "Bitter Feast": ("Eylhaar's Feast", 200),
}

# Edges that should always use dashed+arrow style regardless of position
ARROW_EDGES = set()

BOX_W, BOX_H = 160, 40
ROW_SPACING = 60
BAND_PAD_TOP = 15
BAND_PAD_BOTTOM = 15
BAND_GAP = 80
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


def assign_chain_rows(book_name, spells_in_book):
    """Assign y-rows to spells based on prerequisite chains.

    Connected spells share the same row so horizontal edges
    don't cross unrelated cells. Each branch fans out to a new row.
    """
    spell_names = {s[0] for s in spells_in_book}
    spell_tier = {s[0]: s[2] for s in spells_in_book}
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}

    # Build within-book adjacency from EDGES
    children = defaultdict(list)
    parents = defaultdict(list)
    for src, tgt, _ in EDGES:
        if src in spell_names and tgt in spell_names:
            children[src].append(tgt)
            parents[tgt].append(src)

    # Sort children by tier so chains flow left-to-right
    for parent in children:
        children[parent].sort(key=lambda c: tier_rank.get(spell_tier.get(c, "Basic"), 1))

    # Find roots (no within-book parents)
    roots = [s[0] for s in spells_in_book if s[0] not in parents]
    assigned = {}
    row = [0]  # mutable counter

    def assign(name, cur_row):
        if name in assigned:
            return
        assigned[name] = cur_row
        kids = children.get(name, [])
        # First child that is in a LATER tier stays on same row (left-to-right flow)
        # Other children get new rows
        parent_tier = tier_rank.get(spell_tier.get(name, "Basic"), 1)
        same_row_used = False
        for kid in kids:
            kid_tier = tier_rank.get(spell_tier.get(kid, "Basic"), 1)
            if kid_tier >= parent_tier and not same_row_used:
                assign(kid, cur_row)
                same_row_used = True
            else:
                row[0] += 1
                assign(kid, row[0])

    for root in roots:
        assign(root, row[0])
        row[0] += 1

    # Assign any remaining unassigned spells
    for s in spells_in_book:
        if s[0] not in assigned:
            assigned[s[0]] = row[0]
            row[0] += 1

    # Apply row overrides: align spell with another spell's row
    for spell_to_move, align_with in ROW_OVERRIDES.items():
        if spell_to_move in assigned and align_with in assigned:
            assigned[spell_to_move] = assigned[align_with]

    return assigned, row[0]


def build_drawio():
    spell_book = {s[0]: s[1] for s in SPELLS}
    book_idx = {b: i for i, b in enumerate(SPELLBOOK_ORDER)}

    books = defaultdict(list)
    for spell in SPELLS:
        books[spell[1]].append(spell)

    # Assign chain-based rows and compute positions
    band_info = []
    y_cursor = 50
    spell_pos = {}

    for book_name in SPELLBOOK_ORDER:
        spells_in_book = books[book_name]
        chain_rows, num_rows = assign_chain_rows(book_name, spells_in_book)
        band_h = max(num_rows * ROW_SPACING + BAND_PAD_TOP + BAND_PAD_BOTTOM + 40, 120)

        # Place spells: x from tier, y from chain row
        spell_tier = {s[0]: s[2] for s in spells_in_book}
        # Track occupied positions to avoid overlaps
        occupied = set()
        for spell in spells_in_book:
            name = spell[0]
            tier = spell[2]
            chain_row = chain_rows[name]
            x_positions = TIER_X[tier]
            sy = y_cursor + BAND_PAD_TOP + chain_row * ROW_SPACING
            # Try each sub-column in this tier, then try ALL tier columns
            sx = None
            for xp in x_positions:
                if (xp, sy) not in occupied:
                    sx = xp
                    break
            if sx is None:
                # All sub-columns occupied at this y; try any available x
                all_x = [x for xs in TIER_X.values() for x in xs]
                for xp in all_x:
                    if (xp, sy) not in occupied:
                        sx = xp
                        break
            if sx is None:
                sx = x_positions[0]  # last resort
            occupied.add((sx, sy))
            spell_pos[name] = (sx, sy)

        band_info.append((book_name, y_cursor, band_h, spells_in_book))
        y_cursor += band_h + BAND_GAP

    # Apply x-alignment overrides
    for spell_name, (align_with, x_offset) in X_ALIGN_OVERRIDES.items():
        if spell_name in spell_pos and align_with in spell_pos:
            _, sy = spell_pos[spell_name]
            ax, _ = spell_pos[align_with]
            spell_pos[spell_name] = (ax + x_offset, sy)

    page_height = y_cursor + 100
    line_bottom = page_height - 20

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
    for i, (book_name, by, bh, _) in enumerate(band_info):
        fill = band_colors[i % 2]
        bid = next_id()
        c = SubElement(xml_root, "mxCell", id=bid, value="",
                       style=f"rounded=1;fontFamily=Helvetica;fontSize=11;fontColor=default;labelBackgroundColor=none;fillColor={fill};strokeColor=#667788;opacity=30;glass=0;shadow=0;align=center;verticalAlign=middle;gradientColor=none;strokeWidth=2;",
                       parent="spellbook-borders", vertex="1")
        SubElement(c, "mxGeometry", x="10", y=str(by), width=str(PAGE_WIDTH - 240), height=str(bh), **{"as": "geometry"})
        # Spellbook label inside the band, at the bottom-left
        blid = next_id()
        c = SubElement(xml_root, "mxCell", id=blid, value=book_name,
                       style=f"text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=16;fontFamily=Atkinson Hyperlegible;fontColor=#667788;strokeColor=none;{FONT_SOURCE}",
                       parent="spellbook-borders", vertex="1")
        SubElement(c, "mxGeometry", x="10", y=str(by + bh - 45), width="180", height="40", **{"as": "geometry"})

    # --- Shapes and Lines ---
    shapes_layer = SubElement(xml_root, "mxCell", id="shapes-lines", value="Shapes and Lines", style="locked=1;", parent="0")
    spell_cells = {}

    for book_name, by, bh, spells_in_book in band_info:
        for spell in spells_in_book:
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
    # Pre-compute per-source and per-target edge counts for staggering
    source_edge_count = defaultdict(int)
    source_edge_idx = {}
    target_edge_count = defaultdict(int)
    target_edge_idx = {}
    for src_name, tgt_name, _ in EDGES:
        source_edge_idx[(src_name, tgt_name)] = source_edge_count[src_name]
        source_edge_count[src_name] += 1
        target_edge_idx[(src_name, tgt_name)] = target_edge_count[tgt_name]
        target_edge_count[tgt_name] += 1

    band_bounds = {}
    for book_name, by, bh, _ in band_info:
        band_bounds[book_name] = (by, by + bh)

    # Compute gap regions between adjacent bands
    gap_regions = {}
    for i in range(len(SPELLBOOK_ORDER) - 1):
        b1 = SPELLBOOK_ORDER[i]
        b2 = SPELLBOOK_ORDER[i + 1]
        _, b1_bottom = band_bounds[b1]
        b2_top, _ = band_bounds[b2]
        gap_regions[(b1, b2)] = (b1_bottom, b2_top)
        gap_regions[(b2, b1)] = (b1_bottom, b2_top)

    # Track gap usage to stagger parallel edges in the same gap
    gap_usage = defaultdict(int)
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

        # Stagger offsets for edges from same source / to same target
        edge_idx = source_edge_idx.get((src_name, tgt_name), 0)
        num_edges = source_edge_count.get(src_name, 1)
        stagger = (edge_idx - num_edges // 2) * 12

        tgt_idx = target_edge_idx.get((src_name, tgt_name), 0)
        tgt_num = target_edge_count.get(tgt_name, 1)
        tgt_stagger = (tgt_idx - tgt_num // 2) * 12

        # Helper: compute staggered exit fraction for right-exiting edges
        exit_frac_r = max(0.15, min(0.85, 0.5 + stagger / BOX_H))

        waypoints = None

        if same_book and tx > sx:
            # Same book, target to the right -- check if horizontal path is blocked
            blocked = False
            edge_y = sy + BOX_H // 2
            for other_name, (ox, oy) in spell_pos.items():
                if other_name == src_name or other_name == tgt_name:
                    continue
                if spell_book.get(other_name) != src_bk:
                    continue
                if (ox > sx and ox <= tx and
                    oy <= edge_y <= oy + BOX_H):
                    blocked = True
                    break

            if blocked:
                entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                tgt_cy = ty + BOX_H // 2
                src_cx = sx + BOX_W // 2

                # Check if vertical drop at src_cx would cross cells
                vert_clear = True
                min_y = min(sy, ty)
                max_y = max(sy + BOX_H, ty + BOX_H)
                for on, (ox, oy) in spell_pos.items():
                    if on == src_name or on == tgt_name:
                        continue
                    if spell_book.get(on) != src_bk:
                        continue
                    if (ox <= src_cx <= ox + BOX_W and
                        oy >= sy + BOX_H and oy <= ty):
                        vert_clear = False
                        break

                stag_x = src_cx + stagger

                if not vert_clear:
                    # Vertical blocked: exit right to corridor, then down, then right
                    exit_style = f"exitX=1;exitY={exit_frac_r:.2f};exitDx=0;exitDy=0;"
                    corridor_x = sx + BOX_W + 20 + abs(stagger)
                    waypoints = [
                        (corridor_x, sy + BOX_H // 2 + stagger),
                        (corridor_x, tgt_cy),
                        (tx - 10, tgt_cy),
                    ]
                elif ty > sy:
                    exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                    adj_y = tgt_cy + tgt_stagger
                    waypoints = [
                        (stag_x, adj_y),
                        (tx - 10, adj_y),
                    ]
                elif ty == sy:
                    exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                    mid_y = sy + BOX_H + 20 + edge_idx * 12
                    waypoints = [
                        (stag_x, mid_y),
                        (tx - 10, mid_y),
                    ]
                else:
                    exit_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                    waypoints = [
                        (stag_x, tgt_cy),
                        (tx - 10, tgt_cy),
                    ]
            else:
                exit_frac = max(0.2, min(0.8, 0.5 + stagger / BOX_H))
                exit_style = f"exitX=1;exitY={exit_frac:.2f};exitDx=0;exitDy=0;"
                entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
        elif same_book and tx <= sx:
            # Same book, same column or leftward
            if ty > sy:
                exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
            else:
                exit_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                entry_style = "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
        elif abs(src_bi - tgt_bi) == 1:
            # Adjacent bands: check if vertical drop from source would cross
            # same-band cells below/above it
            src_cx = sx + BOX_W // 2 + stagger
            tgt_cx = tx + BOX_W // 2
            gap_key = (min(src_bk, tgt_bk), max(src_bk, tgt_bk))
            gap_bottom, gap_top = gap_regions.get((src_bk, tgt_bk), (sy, ty))
            offset = gap_usage[gap_key] * 20
            gap_usage[gap_key] += 1
            gap_y = (gap_bottom + gap_top) // 2 + offset

            # Check if vertical segment from source would cross same-band cells
            vert_blocked = False
            src_band_top, src_band_bottom = band_bounds[src_bk]
            for other_name, (ox, oy) in spell_pos.items():
                if other_name == src_name:
                    continue
                if spell_book.get(other_name) != src_bk:
                    continue
                # Would vertical line at src_cx cross this cell?
                if (ox <= src_cx <= ox + BOX_W and
                    ((ty > sy and oy > sy) or (ty < sy and oy < sy))):
                    vert_blocked = True
                    break

            if vert_blocked:
                # Exit right instead, route to a corridor then down
                exit_style = f"exitX=1;exitY={exit_frac_r:.2f};exitDx=0;exitDy=0;"
                if tx >= sx:
                    entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                else:
                    entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
                # Route right to a clear corridor, then down to gap, then to target
                corridor_x = sx + BOX_W + 30
                entry_offset = gap_usage[gap_key] * 10
                waypoints = [
                    (corridor_x, sy + BOX_H // 2),
                    (corridor_x, gap_y),
                    (tx - 10 - entry_offset if tx >= sx else tgt_cx, gap_y),
                ]
            else:
                if ty > sy:
                    exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                    if tx >= sx:
                        entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                    else:
                        entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
                else:
                    exit_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                    if tx >= sx:
                        entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                    else:
                        entry_style = "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"

                entry_offset = gap_usage[gap_key] * 10
                waypoints = [
                    (src_cx, gap_y),
                    (tx - 10 - entry_offset if tx >= sx else tgt_cx, gap_y),
                ]
        else:
            # Skip-band: route to right margin, enter top/bottom
            right_margin_counter += 1
            margin_x = PAGE_WIDTH - 250 + (right_margin_counter * 15)

            if ty > sy:
                # Stagger entry point for multiple edges to same target
                entry_frac = max(0.15, min(0.85, 0.5 + tgt_stagger / BOX_H))
                entry_style = f"entryX={entry_frac:.2f};entryY=0;entryDx=0;entryDy=0;"
                tgt_entry_y = ty
            else:
                entry_frac = max(0.15, min(0.85, 0.5 + tgt_stagger / BOX_H))
                entry_style = f"entryX={entry_frac:.2f};entryY=1;entryDx=0;entryDy=0;"
                tgt_entry_y = ty + BOX_H

            # Exit right, route through corridor to avoid same-row cells
            exit_style = f"exitX=1;exitY={exit_frac_r:.2f};exitDx=0;exitDy=0;"
            src_band_top, src_band_bottom = band_bounds[src_bk]
            clear_y = src_band_bottom + 15 + right_margin_counter * 15
            corridor_x = sx + BOX_W + 20 + right_margin_counter * 15
            waypoints = [
                (corridor_x, sy + BOX_H // 2),
                (corridor_x, clear_y),
                (margin_x, clear_y),
                (margin_x, tgt_entry_y),
            ]

        eid = next_id()
        force_arrow = (src_name, tgt_name) in ARROW_EDGES
        if is_alt or force_arrow:
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
