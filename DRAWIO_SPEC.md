# DragonRealms Spell Tree Drawio Visual Specification

Reverse-engineered from all 12 guild drawio files in this repository.

---

## 1. Page & Graph Model

| Attribute | Value | Notes |
|-----------|-------|-------|
| `grid` | `1` | Always enabled |
| `gridSize` | `10` | Standard (Necromancer uses `1`, Analogous Patterns uses `5`) |
| `guides` | `1` | |
| `page` | `1` | |
| `pageScale` | `1` | |
| `background` | `none` | |
| `math` | `0` | |
| `shadow` | `0` | |

Page dimensions vary per guild based on spell count. The `dx` and `dy` are viewport offsets (not design-relevant). Representative sizes:

| Guild | pageWidth | pageHeight |
|-------|-----------|------------|
| Ranger | 1630 | 690 |
| Barbarian | 1610 | 670 |
| Trader | 1610 | 670 |
| Bard | 705 | 850 |
| Necromancer | 715 | 1190 |
| Empath | 1600 | 1050 |
| Paladin | 1420 | 760 |
| Cleric | 1800 | 1120 |
| Moon Mage | 1800 | 1120 |
| Warrior Mage | 1800 | 1340 |
| Thief | 1810 | 870 |

---

## 2. Font Families -- Two Eras

There are two font conventions corresponding to different editing eras:

### Era 1: Georgia (older files)
- **Guilds**: Empath, Bard, Ranger, Paladin, Warrior Mage, Analogous Patterns, Thief
- Spell boxes: `fontFamily=Georgia`
- Legend/tier labels: `fontFamily=Helvetica` (tier column labels) or `fontFamily=Georgia` (legend box title, spell type boxes)

### Era 2: Atkinson Hyperlegible (newer files)
- **Guilds**: Necromancer, Barbarian, Trader, Moon Mage
- Spell boxes: `fontFamily=Atkinson Hyperlegible`
- Requires: `fontSource=https%3A%2F%2Ffonts.googleapis.com%2Fcss%3Ffamily%3DAtkinson%2BHyperlegible`
- Tier column labels: `fontFamily=Atkinson Hyperlegible` (with fontSource)

### Hybrid files
- **Cleric**: Mostly Atkinson Hyperlegible for spell boxes, but Georgia for legend and spellbook labels.
- **Bard/Necromancer**: Have a separate "Colors" layer using Georgia, while "Shapes and Lines" layer uses the primary font.

### Common
- Spellbook band cells always use `fontFamily=Helvetica;fontSize=11` (these are the background rectangles, not labeled).
- Tier column labels always use `fontSize=18`.

---

## 3. Spell Box Cells (Primary Element)

### Dimensions
```
width="160" height="40"
```
This is universal across ALL guilds and ALL spells. No exceptions found.

### Common Style String
```
rounded=1;strokeWidth=1;strokeColor=#667788;textShadow=0;labelBackgroundColor=none;
whiteSpace=wrap;fontSize=17;fontFamily=Georgia;fillColor=<TYPE_COLOR>;
fontColor=<TEXT_COLOR>;shadow=1;glass=0;align=center;verticalAlign=middle;
fontStyle=<BOLD_FLAG>;resizable=1;
```

### Font Size Variations
| Font | Typical fontSize | Used when |
|------|-----------------|-----------|
| Georgia | `17` | Standard (Empath) |
| Georgia | `15` | Ranger, Bard, Paladin, Warrior Mage |
| Atkinson Hyperlegible | `18` | Standard (Moon Mage, Necromancer, Barbarian, Trader) |
| Either | `17` or `16` or `14` | Occasionally for long spell names that need to fit |

The `fontSize=11` seen in grep results comes only from the spellbook band background cells, not spell boxes.

### strokeWidth
- **Era 1 (Georgia)**: `strokeWidth=1` on spell box cells (Empath), `strokeWidth=2` on spell box cells (Ranger, Bard, Paladin, WM)
- **Era 2 (Atkinson)**: `strokeWidth=1` on spell box cells (Moon Mage, Cleric), `strokeWidth=2` on spell box cells (Necromancer)

**Discrepancy note**: `strokeWidth` is inconsistent. Necromancer/Ranger/Bard use `2`, while Empath/Moon Mage/Cleric use `1`. When Necromancer uses `strokeWidth=2`, the shape/line layer has empty-value boxes (colors are on a separate layer).

### Signature vs Non-Signature Spells
- **Signature spells**: `fontStyle=1` (bold)
- **Non-signature spells**: `fontStyle=0` or omitted (normal weight)

### shadow Property
- Normal spells: `shadow=1`
- Metamagic spells: `shadow=0`

---

## 4. Spell Type Color Scheme

These hex values are consistent across ALL guild files:

| Spell Type | fillColor | fontColor | Notes |
|------------|-----------|-----------|-------|
| Augmentation | `#AAC8EB` | `#000000` | Light blue |
| Warding | `#147A6D` | `#FFFFFF` | Teal/dark green (sometimes lowercase `#147a6d`) |
| Utility | `#B3D56A` | `#000000` | Light green |
| Targeted Magic | `#E80538` | `#FFFFFF` | Red |
| Debilitation | `#EBCD00` | `#000000` | Gold/yellow |
| Metamagic | `#D5D0CA` | `#000000` | Warm gray; `shadow=0` (all others `shadow=1`) |

### Multi-type Spells (Gradient)
Some spells belong to two types. These use a horizontal gradient:
```
fillColor=#AAC8EB;gradientColor=#B3D56A;gradientDirection=east
```
Examples:
- Empath: "Aesandry Darlaeth" (Augmentation + Utility), "Tranquility" (Augmentation + Warding)
- Moon Mage: "Tangled Fate" (Debilitation + Utility), "Tezirah's Veil" (Augmentation + Debilitation)
- Ranger: "Bear Strength" (Augmentation + Utility), "Skein of Shadows" (Augmentation + Utility), "Earth Meld" (Augmentation + Utility)

The left color is the `fillColor`, the right color is the `gradientColor`.

---

## 5. Spellbook Band Cells (Background Rectangles)

These are large rounded rectangles behind groups of spells, alternating between two colors.

### Style
```
rounded=1;fontFamily=Helvetica;fontSize=11;fontColor=default;
labelBackgroundColor=none;fillColor=<BAND_COLOR>;strokeColor=#667788;
opacity=30;glass=0;shadow=0;align=center;verticalAlign=middle;
gradientColor=none;strokeWidth=2;
```

### Alternating Colors
| Odd bands | Even bands |
|-----------|------------|
| `fillColor=#FCF4C4` (warm cream) | `fillColor=#667788` (blue-gray) |
| `strokeColor=#667788` | `strokeColor=#667788` |

Both use `opacity=30`.

### Atkinson Hyperlegible variant
Moon Mage and Cleric also add `fontFamily=Atkinson Hyperlegible` and `fontSource=...` to these cells, though the band cells have no visible text.

### Dimensions
Width and height vary per spellbook (depends on number of spells). Bands span from near the left edge to the right edge of the diagram.

---

## 6. Spellbook Label Cells

Text labels positioned below each spellbook band, naming the spellbook.

### Style
```
text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;
fontStyle=1;fontSize=16;fontFamily=Georgia;fontColor=#667788;strokeColor=none;
```

### Dimensions
```
width="140" height="40"
```

### Atkinson Hyperlegible variant (Moon Mage, Cleric)
```
fontFamily=Atkinson Hyperlegible;fontSource=https%3A%2F%2Ffonts.googleapis.com%2Fcss%3Ffamily%3DAtkinson%2BHyperlegible;
```

---

## 7. Tier Column Labels

Labels at the top of the diagram indicating difficulty tiers.

### Standard (4-tier) Guilds
Most guilds use 4 tiers: Intro, Basic, Intermediate, Advanced.

| Tier | x position | Width |
|------|-----------|-------|
| Intro | 60 | 80 |
| Basic | 360 | 80 |
| Intermediate | 740 | 120 |
| Advanced | 1160 | 120 |

### Extended (5-tier) Guilds
Guilds with Esoteric: Barbarian, Cleric, Moon Mage, Trader

For these, positions shift to accommodate the 5th column:

| Tier | x position | Width |
|------|-----------|-------|
| Intro | 160 (Empath) or 60 | 80 |
| Basic | 560 (Empath) or 360 | 80 |
| Intermediate | 940 (Empath) or 740 | 120 |
| Advanced | 1240 (Empath) or 1160 | 120 |
| Esoteric | ~1560 | 120 |

### Style
```
text;align=center;verticalAlign=middle;resizable=0;points=[];autosize=0;
strokeColor=none;fillColor=none;fontFamily=Helvetica;fontSize=18;
fontColor=#667788;labelBackgroundColor=none;textShadow=1;
```

Height is always `40`, y is always `0` (top of diagram).

### Atkinson Hyperlegible variant
```
fontFamily=Atkinson Hyperlegible;fontSource=https%3A%2F%2Ffonts.googleapis.com%2Fcss%3Ffamily%3DAtkinson%2BHyperlegible;
```

### Thief exception
Thief uses 5 tiers labeled differently: "Tier 1 - 8 start, 2 pulse" through "Tier 5 - 25 start, 6 pulse".

---

## 8. Tier Divider Lines

Vertical dashed lines separating tier columns. Always on the locked layer (id `1`).

### Style
```
html=1;rounded=0;strokeWidth=2;endArrow=none;endFill=0;dashed=1;
labelBackgroundColor=none;shadow=1;strokeColor=#667788;opacity=70;
dashPattern=1 1;
```

### Positions (x coordinates)
For 4-tier guilds with `x=200/600/1000` pattern:
- Between Intro/Basic: `x=200`
- Between Basic/Intermediate: `x=600`
- Between Intermediate/Advanced: `x=1000`

For 5-tier guilds with `x=400/800/1200/1600` pattern (Empath, Cleric, Moon Mage, WM):
- Between Intro/Basic: `x=400`
- Between Basic/Intermediate: `x=800`
- Between Intermediate/Advanced: `x=1200`
- Between Advanced/Esoteric: `x=1600`

### Horizontal header line
A horizontal dashed line at `y=40` separates the tier labels from the diagram content:
```
sourcePoint: (10, 40)
targetPoint: (<pageWidth-margin>, 40)
```

### dashPattern variants
- Most files: `dashPattern=1 1`
- Bard: `dashPattern=1 2`

### Vertical extent
Lines run from `y=10` to near `pageHeight - margin` (e.g., `y=1030`, `y=1180`, `y=870`).

---

## 9. Circle Prerequisite Labels

Text cells showing circle requirements for spells (e.g., "Circle 30", "Circle 20").

### Style
```
text;align=right;verticalAlign=bottom;resizable=0;points=[];autosize=1;
strokeColor=none;fillColor=none;fontFamily=Georgia;fontSize=13;
fontColor=#667788;labelBackgroundColor=none;fontStyle=3
```

- `fontStyle=3` = bold + italic (bitmask: 1=bold, 2=italic, 3=both)
- Positioned near the spell box they apply to, typically to the right/above
- Width: `80`, Height: `30`
- Layer: "Circle Pre-requisites text" (locked)

---

## 10. Spell Prerequisite Labels

Text cells describing spell prerequisites (e.g., "Requires CD or FP", "Requires Compel or\nAwaken").

### Style
```
text;align=left;verticalAlign=top;resizable=0;points=[];autosize=1;
strokeColor=none;fillColor=none;fontFamily=Georgia;fontSize=13;
fontColor=#667788;labelBackgroundColor=none;spacing=0;spacingBottom=0;
spacingTop=-4;fontStyle=3
```

- `fontStyle=3` = bold + italic
- Layer: "Spell Pre-requisites text" (locked)
- Multiline text uses `&#xa;` for line breaks
- Width varies (130-160), Height: 20-50 depending on line count

---

## 11. Slot Cost Dot Patterns

Unicode filled/empty circle characters showing spell slot costs.

### Symbols
- Filled: `●` (U+25CF BLACK CIRCLE)
- Empty: `○` (U+25CB WHITE CIRCLE)

### 3-slot guilds (most guilds)
```
●○○  (1 slot)
●●○  (2 slots)
●●●  (3 slots)
○○○  (0 slots -- free)
```

### 4-slot guilds (Necromancer, Barbarian, Trader)
```
●○○○  (1 slot)
●●○○  (2 slots)
●●●○  (3 slots)
●●●●  (4 slots)
```

### Style
```
text;align=center;verticalAlign=middle;rounded=0;fontFamily=Georgia;
fontSize=13;fontColor=default;labelBackgroundColor=none;spacing=0;
spacingTop=0;spacingBottom=-5;fillColor=none;
```

### Dimensions
```
width="40" height="20"
```

### Position relative to spell box
Positioned to the **right** of the spell box, vertically aligned near the bottom edge:
- x = spell_box_x + 120 to 140 (right of box)
- y = spell_box_y + 20 (bottom half of box)

### fontColor exception
On dark-background spells (Warding `#147A6D`, Targeted `#E80538`), the dot pattern uses `fontColor=#FFFFFF` so dots are visible.

### Layer
"Spell cost bubbles text" layer (some files lock this, some don't).

---

## 12. Legend Box

### Container Style
```
rounded=1;fillColor=none;verticalAlign=top;labelBackgroundColor=none;
container=0;fontStyle=1;fontColor=#667788;fontFamily=Georgia;
strokeColor=#667788;shadow=1;glass=0;strokeWidth=1;textShadow=0;whiteSpace=wrap;
```

### Dimensions
Width: `180` to `200`
Height: Varies by content (`280` for Thief up to `480` for Necromancer)

### Position
Typically placed to the right of the diagram content, outside the tier columns:
- x: usually `1200`-`1630` depending on diagram width
- y: varies

### Contents (in order, top to bottom)

1. **"Special requirements in italics"** -- text cell
   ```
   fontFamily=Georgia;fontSize=15;fontColor=#667788;fontStyle=3
   ```

2. **"Augmentation"** -- colored box `fillColor=#AAC8EB`
3. **"Warding"** -- colored box `fillColor=#147A6D;fontColor=#FFFFFF`
4. **"Utility"** -- colored box `fillColor=#B3D56A`
5. **"Targeted Magic"** -- colored box `fillColor=#E80538;fontColor=#FFFFFF`
6. **"Debilitation"** -- colored box `fillColor=#EBCD00`
7. **"Metamagic"** -- colored box `fillColor=#D5D0CA;shadow=0`
8. **"Signature spells in bold"** -- text cell, `fontStyle=1`
9. **"Spell slot cost"** with dot example -- text cell

Legend spell type boxes are `160x40` with `fontSize=18`, `fontStyle=1`, `strokeColor=#667788`, `strokeWidth=1`.

### Thief exception
Thief has no Metamagic row, no "Targeted Magic" row. Instead has: Utility, Debilitation, Augmentation, Warding, and "Signature spells in bold" + slot cost.

---

## 13. Edge/Connector Styles

### Prerequisite edges (solid line, no arrow -- "leads to")
```
edgeStyle=orthogonalEdgeStyle;shape=connector;curved=0;rounded=1;
orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#667788;strokeWidth=2;
endArrow=none;endFill=0;jumpStyle=none;
```

### Prerequisite edges (dashed line, arrow -- "required by / alternative path")
```
edgeStyle=orthogonalEdgeStyle;shape=connector;curved=0;rounded=1;
orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#667788;strokeWidth=2;
endArrow=classic;endFill=1;dashed=1;jumpStyle=none;
```

### Key properties
| Property | Value | Notes |
|----------|-------|-------|
| `edgeStyle` | `orthogonalEdgeStyle` | Always orthogonal routing |
| `curved` | `0` | Never curved |
| `rounded` | `1` | Rounded corners on bends |
| `strokeColor` | `#667788` | Same blue-gray as everything |
| `strokeWidth` | `2` | Always 2 |
| `endArrow` | `none` or `classic` | `none` = direct prerequisite; `classic` = alternative/additional req |
| `dashed` | `1` or absent | Dashed = alternative requirement path |
| `jumpStyle` | `none` or `arc` | `arc` used in Necromancer/Ranger for line crossings |

### Semantic meaning
- **Solid line, no arrow**: Direct prerequisite chain (A leads to B)
- **Dashed line, with arrow**: Alternative/branching prerequisite (either A or B required for C)

### Font properties on edges (inherited, not displayed)
Edges carry `fontFamily` and `fontSize` matching the file's convention, but these are not rendered.

---

## 14. Layer Structure

All files share a common layer architecture. Layers are identified by their cell id having `parent="0"` and a `value` attribute.

### Standard layers (in order of appearance)

| Layer Name | Locked | Visible | Purpose |
|------------|--------|---------|---------|
| `Spellbook borders` | Sometimes (`locked=1` in most, unlocked in Empath) | Yes | Background band rectangles + spellbook labels |
| `Shapes and Lines` | Usually locked | Yes | Spell box outlines (no fill) + connector edges |
| `Colors` | Locked | Yes | Fill-color-only copies of spell boxes (Necromancer, Bard only) |
| `Spell name text` | Locked (sometimes `visible=0`) | Varies | Text-only copies of spell boxes with spell names |
| `Spell cost bubbles text` | Varies | Yes | Slot cost dot patterns |
| `Circle Pre-requisites text` | Locked | Yes | "Circle N" labels |
| `Spell Pre-requisites text` | Locked | Yes | "Requires X or Y" labels |
| `Spell Skill text` | Locked, `visible=0` | Hidden | Single-letter skill indicators (Bard, Necromancer, Ranger only) |
| `Transparency` | Locked | Yes | Empty layer at bottom (purpose unclear) |

### Layer id=1 (always locked)
The default layer with `id="1"` is always `locked=1`. It contains:
- Tier column labels
- Tier divider lines
- Legend box and its contents

### Architectural variants

**Merged approach** (Empath, Ranger, some older files):
- Spell boxes on "Shapes and Lines" layer contain BOTH the fill color and the text label in one cell.

**Split approach** (Necromancer, Bard, Cleric, Moon Mage):
- "Shapes and Lines" layer has empty-value spell boxes (outlines only, `strokeWidth=2`)
- "Colors" layer has fill-color boxes overlaid
- "Spell name text" layer has text-only labels overlaid
- This split allows independent control of colors, text, and connectors

### Moon Mage / Cleric: "Second spellbook borders"
These have a second spellbook borders layer for special areas (e.g., sorcery spells in Cleric) with different coloring:
```
fillColor=#E80538;strokeColor=#E80538;opacity=30
```

---

## 15. Spacing Patterns

### Tier column widths (x-coordinate ranges)

For 4-tier `200/600/1000` layout:
| Tier | x range | Column width |
|------|---------|-------------|
| Intro | 10-200 | 190px |
| Basic | 200-600 | 400px |
| Intermediate | 600-1000 | 400px |
| Advanced | 1000+ | 400px |

For 5-tier `400/800/1200/1600` layout:
| Tier | x range | Column width |
|------|---------|-------------|
| Intro | 10-400 | 390px |
| Basic | 400-800 | 400px |
| Intermediate | 800-1200 | 400px |
| Advanced | 1200-1600 | 400px |
| Esoteric | 1600+ | 200px |

### Spell box x positions within tiers

Spell boxes snap to consistent x positions aligned with tier boundaries:

For `200/600/1000` layout:
```
Intro:        x=20
Basic:        x=220, x=420
Intermediate: x=620, x=820
Advanced:     x=1020, x=1220
```

For `400/800/1200/1600` layout:
```
Intro:        x=20, x=220
Basic:        x=420, x=620
Intermediate: x=820, x=1020
Advanced:     x=1220, x=1420
Esoteric:     x=1620
```

### Vertical spacing
- Spell boxes within the same spellbook: `60px` vertical gap (y increments of 60)
- Adjacent spells (stacked): `0px` gap, just `height=40` apart (y+40, y+80, etc.)
- Spellbook bands: Separated by the spellbook label height (40px) plus gap

### Standard box positions within a tier column
Two sub-columns per tier, 200px apart:
- Left sub-column: tier_start + 10
- Right sub-column: tier_start + 210

---

## 16. Thief-Specific Conventions

The Thief diagram uses a different tier labeling system:
- "Tier 1 - 8 start, 2 pulse" through "Tier 5 - 25 start, 6 pulse"
- No spellbook bands or spellbook labels (Khri don't have spellbooks)
- Tier divider lines at x = 200, 600, 1000, 1200
- Does NOT have a `Spellbook borders` layer
- Same spell box colors apply (Augmentation, Warding, Utility, Debilitation)
- No Targeted Magic or Metamagic types

---

## 17. Template Generation Checklist

To generate a new drawio file matching this style:

1. **Choose font era**: Georgia (15px) or Atkinson Hyperlegible (18px)
2. **Choose tier count**: 4 (Intro/Basic/Intermediate/Advanced) or 5 (+Esoteric)
3. **Choose slot system**: 3-dot or 4-dot
4. **Set page dimensions** based on spell count (width ~1400-1800, height ~700-1400)
5. **Create layers** in order: Spellbook borders, Shapes and Lines, (Colors), (Spell name text), Spell cost bubbles text, Circle Pre-requisites text, Spell Pre-requisites text, Transparency
6. **Lock layer 1** and place tier labels, dividers, legend
7. **Place spellbook bands** alternating FCF4C4/667788, both at opacity=30
8. **Place spell boxes** at 160x40, using the color table
9. **Place edges** with orthogonal routing, strokeWidth=2, strokeColor=#667788
10. **Place dot patterns** to the right of each spell box
11. **Place prerequisite text** in italics+bold (fontStyle=3)

---

## 18. Raw Style Templates

### Spell box (Georgia, signature, Utility)
```xml
<mxCell value="Spell Name" style="rounded=1;strokeWidth=1;strokeColor=#667788;textShadow=0;labelBackgroundColor=none;whiteSpace=wrap;fontSize=17;fontFamily=Georgia;fillColor=#B3D56A;fontColor=#000000;shadow=1;glass=0;align=center;verticalAlign=middle;fontStyle=1;resizable=1;" vertex="1">
  <mxGeometry x="420" y="110" width="160" height="40" as="geometry" />
</mxCell>
```

### Spell box (Atkinson, non-signature, Targeted)
```xml
<mxCell value="Spell Name" style="rounded=1;strokeWidth=1;strokeColor=#667788;textShadow=0;labelBackgroundColor=none;whiteSpace=wrap;fontSize=18;fontFamily=Atkinson Hyperlegible;fillColor=#E80538;fontColor=#FFFFFF;shadow=1;glass=0;align=center;verticalAlign=middle;fontStyle=0;resizable=1;fontSource=https%3A%2F%2Ffonts.googleapis.com%2Fcss%3Ffamily%3DAtkinson%2BHyperlegible;" vertex="1">
  <mxGeometry x="620" y="240" width="160" height="40" as="geometry" />
</mxCell>
```

### Spell box (Metamagic)
```xml
<mxCell value="Spell Name" style="rounded=1;whiteSpace=wrap;fillColor=#D5D0CA;labelBackgroundColor=none;fontFamily=Georgia;fontSize=18;strokeColor=#667788;shadow=0;glass=0;strokeWidth=1;align=center;fontStyle=1;verticalAlign=middle;fontColor=#000000;textShadow=0;" vertex="1">
  <mxGeometry x="1020" y="460" width="160" height="40" as="geometry" />
</mxCell>
```

### Spellbook band (cream)
```xml
<mxCell value="" style="rounded=1;fontFamily=Helvetica;fontSize=11;fontColor=default;labelBackgroundColor=none;fillColor=#FCF4C4;strokeColor=#667788;opacity=30;glass=0;shadow=0;align=center;verticalAlign=middle;gradientColor=none;strokeWidth=2;" vertex="1">
  <mxGeometry x="10" y="60" width="1380" height="140" as="geometry" />
</mxCell>
```

### Spellbook band (gray)
```xml
<mxCell value="" style="rounded=1;fontFamily=Helvetica;fontSize=11;fontColor=default;labelBackgroundColor=none;fillColor=#667788;strokeColor=#667788;opacity=30;glass=0;shadow=0;align=center;verticalAlign=middle;gradientColor=none;strokeWidth=2;" vertex="1">
  <mxGeometry x="410" y="220" width="780" height="200" as="geometry" />
</mxCell>
```

### Spellbook label
```xml
<mxCell value="Book Name" style="text;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=16;fontFamily=Georgia;fontColor=#667788;strokeColor=none;" vertex="1">
  <mxGeometry x="10" y="160" width="140" height="40" as="geometry" />
</mxCell>
```

### Tier column label
```xml
<mxCell value="Basic" style="text;align=center;verticalAlign=middle;resizable=0;points=[];autosize=0;strokeColor=none;fillColor=none;fontFamily=Helvetica;fontSize=18;fontColor=#667788;labelBackgroundColor=none;textShadow=1;" vertex="1">
  <mxGeometry x="360" width="80" height="40" as="geometry" />
</mxCell>
```

### Tier divider line (vertical)
```xml
<mxCell value="" style="html=1;rounded=0;strokeWidth=2;endArrow=none;endFill=0;dashed=1;labelBackgroundColor=none;shadow=1;strokeColor=#667788;opacity=70;dashPattern=1 1;" edge="1">
  <mxGeometry width="100" relative="1" as="geometry">
    <mxPoint x="600" y="10" as="sourcePoint" />
    <mxPoint x="600" y="1030" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

### Edge (solid, no arrow -- direct prerequisite)
```xml
<mxCell style="edgeStyle=orthogonalEdgeStyle;shape=connector;curved=0;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeColor=#667788;strokeWidth=2;endArrow=none;endFill=0;jumpStyle=none;" edge="1" source="SOURCE_ID" target="TARGET_ID">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Edge (dashed, arrow -- alternative prerequisite)
```xml
<mxCell style="edgeStyle=orthogonalEdgeStyle;shape=connector;curved=0;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeColor=#667788;strokeWidth=2;endArrow=classic;endFill=1;dashed=1;jumpStyle=none;" edge="1" source="SOURCE_ID" target="TARGET_ID">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Slot cost dots
```xml
<mxCell value="●●○" style="text;align=center;verticalAlign=middle;rounded=0;fontFamily=Georgia;fontSize=13;fontColor=default;labelBackgroundColor=none;spacing=0;spacingTop=0;spacingBottom=-5;fillColor=none;" vertex="1">
  <mxGeometry x="540" y="130" width="40" height="20" as="geometry" />
</mxCell>
```

### Circle prerequisite label
```xml
<mxCell value="Circle 30" style="text;align=right;verticalAlign=bottom;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontFamily=Georgia;fontSize=13;fontColor=#667788;labelBackgroundColor=none;fontStyle=3" vertex="1">
  <mxGeometry x="1300" y="50" width="80" height="30" as="geometry" />
</mxCell>
```

### Spell prerequisite label
```xml
<mxCell value="Requires CD or FP" style="text;align=left;verticalAlign=top;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontFamily=Georgia;fontSize=13;fontColor=#667788;labelBackgroundColor=none;spacing=0;spacingBottom=0;spacingTop=-4;fontStyle=3" vertex="1">
  <mxGeometry x="1020" y="280" width="130" height="20" as="geometry" />
</mxCell>
```

### Legend container
```xml
<mxCell value="Legend" style="rounded=1;fillColor=none;verticalAlign=top;labelBackgroundColor=none;container=0;fontStyle=1;fontColor=#667788;fontFamily=Georgia;strokeColor=#667788;shadow=1;glass=0;strokeWidth=1;textShadow=0;whiteSpace=wrap;" vertex="1">
  <mxGeometry x="1410" y="580" width="180" height="460" as="geometry" />
</mxCell>
```

---

## 19. The Universal Color: #667788

The hex color `#667788` (a muted blue-gray) is the single unifying accent color across the entire design system. It is used for:

- All spell box `strokeColor`
- All spellbook band `strokeColor`
- All tier divider lines `strokeColor`
- All edge/connector `strokeColor`
- All text label `fontColor` (tier labels, spellbook labels, prerequisite labels, legend)
- Legend box `strokeColor` and `fontColor`

This creates visual cohesion despite the variety of fill colors for spell types.
