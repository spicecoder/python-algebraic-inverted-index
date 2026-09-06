import html

BOX_W = 180
BOX_H = 44
H_GAP = 36
V_GAP = 74
MARGIN = 24

def _measure(node):
    children = node.get("children", [])
    if not children:
        return BOX_W, BOX_H
    child_sizes = [_measure(child) for child in children]
    total_w = sum(w for w, _ in child_sizes) + H_GAP * (len(child_sizes) - 1)
    total_h = max(h for _, h in child_sizes)
    width = max(BOX_W, total_w)
    height = BOX_H + V_GAP + total_h
    return width, height

def _layout(node, x, y):
    width, _ = _measure(node)
    children = node.get("children", [])
    placed = {"label": node["label"], "type": node["type"], "x": x + (width - BOX_W) / 2, "y": y, "w": BOX_W, "h": BOX_H, "children": []}
    if not children:
        return placed
    child_sizes = [_measure(child) for child in children]
    total_children_w = sum(w for w, _ in child_sizes) + H_GAP * (len(child_sizes) - 1)
    cx = x + (width - total_children_w) / 2
    child_y = y + BOX_H + V_GAP
    for child, (cw, _) in zip(children, child_sizes):
        placed["children"].append(_layout(child, cx, child_y))
        cx += cw + H_GAP
    return placed

def _svg_box(label, x, y, kind):
    rx = 18 if kind == "operator" else 8
    fill = "#EEF3FF" if kind == "operator" else "#F8FAFC"
    stroke = "#3B82F6" if kind == "operator" else "#64748B"
    safe = html.escape(str(label))
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{BOX_W}" height="{BOX_H}" rx="{rx}" ry="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/><text x="{x + BOX_W/2:.1f}" y="{y + BOX_H/2:.1f}" text-anchor="middle" dominant-baseline="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#0F172A">{safe}</text>'

def _svg_edges(node, parts):
    x1 = node["x"] + node["w"] / 2
    y1 = node["y"] + node["h"]
    for child in node["children"]:
        x2 = child["x"] + child["w"] / 2
        y2 = child["y"]
        mid_y = (y1 + y2) / 2
        parts.append(f'<path d="M {x1:.1f} {y1:.1f} C {x1:.1f} {mid_y:.1f}, {x2:.1f} {mid_y:.1f}, {x2:.1f} {y2:.1f}" stroke="#94A3B8" stroke-width="1.5" fill="none"/>')
        _svg_edges(child, parts)

def _svg_nodes(node, parts):
    parts.append(_svg_box(node["label"], node["x"], node["y"], node["type"]))
    for child in node["children"]:
        _svg_nodes(child, parts)

def query_to_svg(query, title="Query Expression"):
    tree = query.to_tree()
    total_w, total_h = _measure(tree)
    width = int(total_w + 2 * MARGIN)
    height = int(total_h + 2 * MARGIN + 40)
    laid_out = _layout(tree, MARGIN, MARGIN + 40)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{MARGIN}" y="{MARGIN+8}" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="#111827">{html.escape(title)}</text>']
    _svg_edges(laid_out, parts)
    _svg_nodes(laid_out, parts)
    parts.append('</svg>')
    return "\n".join(parts)

def write_query_svg(query, output_path, title="Query Expression"):
    svg = query_to_svg(query, title=title)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return str(output_path)
