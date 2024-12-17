import xml.etree.ElementTree as ET
import html
import re
import argparse
import sys

# Case-insensitive
blacklisted_regexes = [
    r"●",
    r"○",
    r"^Circle \d+",
    r"^Legend$",
    r"^Requires:",
    r"^Special requirements",
    r"^Signature spells",
    r"^Metaspell",
    r"^All .+ Spells$",
    r", ",
    r"^Spell Slot",
    r"^(Intro|Basic|Intermediate|Advanced|Esoteric)$"
]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate an image map from draw.io XML file in either HTML or MediaWiki format. Intended to be used on DragonRealms spell trees.",
        epilog="Example:\n"
               "  python spellmap.py --drawio_file Necromancer.drawio --image_file Necromancer.png --output_file necro.txt --format wiki --x_adj -20 --y_adj -17"
    )

    # Required arguments
    parser.add_argument(
        "--drawio_file",
        required=True,
        help="Input draw.io XML file (e.g., 'Necromancer.drawio').",
    )
    parser.add_argument(
        "--image_file",
        required=True,
        help="Pre-generated input image file corresponding to the XML (e.g., 'Necromancer.png').",
    )
    parser.add_argument(
        "--output_file",
        required=True,
        help="Output file for the generated map (e.g., 'necromancer.html' or 'necromancer.txt').",
    )
    parser.add_argument(
        "--format",
        choices=["html", "wiki"],
        required=True,
        help="Output format: 'html' for HTML image map or 'wiki' for MediaWiki imagemap.",
    )

    # Optional arguments
    parser.add_argument(
        "--x_adj", type=int, default=0, help="X-axis adjustment value (default: 0)."
    )
    parser.add_argument(
        "--y_adj", type=int, default=0, help="Y-axis adjustment value (default: 0)."
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()

# Spell names are usually children of at least one parent, each of which has relative position information. So we need to extract the cumulative position of the label and all of its parents/grandparents/etc
def get_cumulative_geometry(cell_id, root):
    x, y = 0, 0
    while cell_id:
        cell = root.find(f".//mxCell[@id='{cell_id}']")
        if cell is None:
            break
        geometry = cell.find(".//mxGeometry")
        if geometry is not None:
            x += float(geometry.get("x", 0))
            y += float(geometry.get("y", 0))
        cell_id = cell.get("parent")
    return x, y

def parse_drawio(file, x_adj, y_adj):
    tree = ET.parse(file)
    root = tree.getroot()

    clickable_boxes = []
    min_x = float("inf")
    min_y = float("inf")

    # First pass: Find minimum x and y values for location normalization
    for cell in root.findall(".//mxCell"):
        geometry = cell.find(".//mxGeometry")
        if geometry is not None:
            parent_id = cell.get("parent")
            parent_x, parent_y = get_cumulative_geometry(parent_id, root)
            x = parent_x + float(geometry.get("x", 0)) + x_adj
            y = parent_y + float(geometry.get("y", 0)) + y_adj
            min_x = min(min_x, x)
            min_y = min(min_y, y)

    # Second pass: Collect labeled areas for clickable boxes
    for cell in root.findall(".//mxCell"):
        value = html.unescape(cell.get("value", ""))
        value = re.sub(r"<.*?>", "", value)

        # Ignore any labels that are blacklisted (unlikely to be actual spells)
        if any(re.search(pattern, value, re.IGNORECASE) for pattern in blacklisted_regexes) or value == "":
            continue

        geometry = cell.find(".//mxGeometry")
        if geometry is not None and value:
            parent_id = cell.get("parent")
            parent_x, parent_y = get_cumulative_geometry(parent_id, root)

            x = parent_x + float(geometry.get("x", 0)) - min_x
            y = parent_y + float(geometry.get("y", 0)) - min_y
            width = float(geometry.get("width", 0))
            height = float(geometry.get("height", 0))

            if output_format == "html":
                link_text = "https://elanthipedia.play.net/" + re.sub(r"\s", "_", value)
            else:
                link_text = re.sub(r"\s", "_", value)

            clickable_boxes.append({
                "label": value,
                "coords": (int(x), int(y), int(x + width), int(y + height)),
                "link": link_text
            })

    return clickable_boxes

def generate_html_map(image_file, areas, output_file):
    html_content = f'<img src="{image_file}" usemap="#flowchart_map">\n'
    html_content += '<map name="flowchart_map">\n'
    for area in areas:
        x1, y1, x2, y2 = area["coords"]
        html_content += f'  <area shape="rect" coords="{x1},{y1},{x2},{y2}" href="{area["link"]}" title="{area["label"]}">\n'
    html_content += '</map>'

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\nHTML image map generated: {output_file}")

def generate_mediawiki_map(image_file, areas, output_file):
    wiki_content = f"<imagemap>\nFile:{image_file}|frameless|upright=4\n"
    for area in areas:
        x1, y1, x2, y2 = area["coords"]
        wiki_content += f"rect {x1} {y1} {x2} {y2} [[{area['link']}]]\n"
    wiki_content += "</imagemap>\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(wiki_content)
    print(f"\nMediaWiki imagemap generated: {output_file}")

if __name__ == "__main__":
    args = parse_args()

    drawio_file = args.drawio_file
    image_file = args.image_file
    output_file = args.output_file
    output_format = args.format
    x_adj = args.x_adj
    y_adj = args.y_adj

    clickable_boxes = parse_drawio(drawio_file, x_adj, y_adj)

    if output_format == "html":
        generate_html_map(image_file, clickable_boxes, output_file)
    elif output_format == "wiki":
        generate_mediawiki_map(image_file, clickable_boxes, output_file)
