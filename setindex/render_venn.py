import html
from .query import Eq, InSet, Between, And, Or, Not, Difference, Xor

PREDICATE_COLORS = ["#2563EB", "#16A34A", "#DC2626", "#7C3AED", "#F59E0B"]
PREDICATE_FILLS = ["rgba(37,99,235,0.18)", "rgba(22,163,74,0.18)", "rgba(220,38,38,0.18)", "rgba(124,58,237,0.18)", "rgba(245,158,11,0.18)"]

def _query_text(query):
    if isinstance(query, Eq):
        return f'{query.field} = {query.value}'
    if isinstance(query, InSet):
        return f'{query.field} IN {{{", ".join(map(str, query.values))}}}'
    if isinstance(query, Between):
        return f'{query.low} <= {query.field} <= {query.high}'
    if isinstance(query, Not):
        return f'NOT ({_query_text(query.operand)})'
    if isinstance(query, And):
        return f'({_query_text(query.left)} AND {_query_text(query.right)})'
    if isinstance(query, Or):
        return f'({_query_text(query.left)} OR {_query_text(query.right)})'
    if isinstance(query, Difference):
        return f'({_query_text(query.left)} DIFF {_query_text(query.right)})'
    if isinstance(query, Xor):
        return f'({_query_text(query.left)} XOR {_query_text(query.right)})'
    return 'query'

def _collect_leaves(query, out):
    if isinstance(query, (Eq, InSet, Between)):
        out.append(query)
    elif isinstance(query, Not):
        _collect_leaves(query.operand, out)
    elif isinstance(query, (And, Or, Difference, Xor)):
        _collect_leaves(query.left, out)
        _collect_leaves(query.right, out)

def _label_query(q):
    if isinstance(q, Eq):
        return f'{q.field} = {q.value}'
    if isinstance(q, InSet):
        return f'{q.field} IN {{{", ".join(map(str, q.values))}}}'
    if isinstance(q, Between):
        return f'{q.low} <= {q.field} <= {q.high}'
    return 'predicate'

def _unique_leaves(query):
    leaves = []
    _collect_leaves(query, leaves)
    out = []
    seen = set()
    for q in leaves:
        label = _label_query(q)
        if label not in seen:
            out.append((label, q))
            seen.add(label)
    return out

def _make_chip(x, y, text, fill, stroke, text_color="#0F172A"):
    safe = html.escape(str(text))
    width = max(70, 12 + 8 * len(safe))
    svg = f'<rect x="{x}" y="{y}" width="{width}" height="30" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/><text x="{x + width/2}" y="{y + 19}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="{text_color}">{safe}</text>'
    return svg, width

def _venn_positions(n):
    if n == 2:
        return [(250, 250, 170), (400, 250, 170)]
    return [(280, 235, 170), (450, 235, 170), (365, 365, 170)]

def _region_anchor_2(mask):
    return {(1,0):(205,250),(0,1):(445,250),(1,1):(325,250)}.get(mask, (40,60))

def _region_anchor_3(mask):
    mapping = {(1,0,0):(220,210),(0,1,0):(510,210),(0,0,1):(365,485),(1,1,0):(365,195),(1,0,1):(285,345),(0,1,1):(445,345),(1,1,1):(365,315)}
    return mapping.get(mask, (40,60))

def _membership_bits(predicates, index, rid):
    return tuple(rid in index.evaluate(q) for _, q in predicates)

def _draw_venn(query, index, output_path, title, label_field):
    predicates = _unique_leaves(query)
    n = len(predicates)
    result = index.evaluate(query)
    width, height = 980, 820
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="28" y="36" font-family="Arial, Helvetica, sans-serif" font-size="20" fill="#0F172A">{html.escape(title)}</text>', '<rect x="24" y="56" width="930" height="64" rx="12" ry="12" fill="#F8FAFC" stroke="#94A3B8"/>', f'<text x="40" y="95" font-family="Courier New, monospace" font-size="14" fill="#0F172A">{html.escape(_query_text(query))}</text>', '<rect x="24" y="145" width="930" height="540" rx="18" ry="18" fill="#F8FAFC" stroke="#CBD5E1"/>', '<text x="48" y="190" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#0F172A">All records</text>']
    for i, (cx, cy, r) in enumerate(_venn_positions(n)):
        label, _ = predicates[i]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PREDICATE_FILLS[i]}" stroke="{PREDICATE_COLORS[i]}" stroke-width="4"/>')
        parts.append(f'<text x="{cx}" y="{cy-r+38}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="bold" fill="{PREDICATE_COLORS[i]}">{html.escape(label)}</text>')
    region_members = {}
    for rid, record in index.items():
        mask = _membership_bits(predicates, index, rid)
        if not any(mask):
            continue
        region_members.setdefault(mask, []).append((rid, record))
    for mask, members in region_members.items():
        anchor = _region_anchor_2(mask) if n == 2 else _region_anchor_3(mask)
        y = anchor[1]
        for rid, record in members:
            fill = '#FEF3C7' if rid in result else 'white'
            stroke = '#F59E0B' if rid in result else '#94A3B8'
            chip, _ = _make_chip(anchor[0] - 45, y, record.get(label_field, rid), fill, stroke)
            parts.append(chip)
            y += 38
    result_names = [index.get(rid).get(label_field, rid) for rid in sorted(result)]
    result_text = '{' + ', '.join(map(str, result_names)) + '}'
    parts.append('<rect x="640" y="170" width="270" height="58" rx="12" ry="12" fill="#FFFBEB" stroke="#F59E0B" stroke-width="2"/>')
    parts.append(f'<text x="775" y="205" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="bold" fill="#111827">result = {html.escape(result_text)}</text>')
    parts.append('<rect x="24" y="705" width="930" height="88" rx="14" ry="14" fill="#FFFFFF" stroke="#CBD5E1"/>')
    parts.append('<rect x="46" y="733" width="72" height="40" rx="8" ry="8" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1.6"/>')
    parts.append('<text x="132" y="758" font-family="Arial, Helvetica, sans-serif" font-size="16" fill="#0F172A">highlighted chips = query result</text>')
    parts.append('<text x="132" y="780" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#64748B">records satisfying the full set expression</text>')
    parts.append('</svg>')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))
    return str(output_path)

def _draw_matrix(query, index, output_path, title, label_field):
    predicates = _unique_leaves(query)
    records = index.items()
    result = index.evaluate(query)
    width = 260 + 140 * len(predicates) + 150
    row_h = 34
    height = 180 + row_h * (len(records) + 2)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="28" y="36" font-family="Arial, Helvetica, sans-serif" font-size="20" fill="#0F172A">{html.escape(title)}</text>', f'<rect x="24" y="56" width="{width-48}" height="64" rx="12" ry="12" fill="#F8FAFC" stroke="#94A3B8"/>', f'<text x="40" y="95" font-family="Courier New, monospace" font-size="14" fill="#0F172A">{html.escape(_query_text(query))}</text>', '<text x="28" y="150" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="#0F172A">Predicate membership matrix</text>']
    x0, y0, name_w, pred_w = 30, 200, 210, 130
    parts.append(f'<rect x="{x0}" y="{y0}" width="{name_w}" height="34" fill="#E2E8F0" stroke="#CBD5E1"/>')
    parts.append(f'<text x="{x0+12}" y="{y0+22}" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#0F172A">record</text>')
    for i, (label, _) in enumerate(predicates):
        x = x0 + name_w + i * pred_w
        parts.append(f'<rect x="{x}" y="{y0}" width="{pred_w}" height="34" fill="{PREDICATE_FILLS[i]}" stroke="{PREDICATE_COLORS[i]}"/>')
        parts.append(f'<text x="{x+pred_w/2}" y="{y0+22}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#0F172A">{html.escape(label)}</text>')
    x_result = x0 + name_w + len(predicates) * pred_w
    parts.append(f'<rect x="{x_result}" y="{y0}" width="110" height="34" fill="#FEF3C7" stroke="#F59E0B"/>')
    parts.append(f'<text x="{x_result+55}" y="{y0+22}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#0F172A">result</text>')
    for row, (rid, record) in enumerate(records, start=1):
        y = y0 + row * row_h
        row_fill = '#FFFFFF' if row % 2 else '#F8FAFC'
        parts.append(f'<rect x="{x0}" y="{y}" width="{name_w}" height="{row_h}" fill="{row_fill}" stroke="#E2E8F0"/>')
        label = html.escape(str(record.get(label_field, rid)))
        parts.append(f'<text x="{x0+12}" y="{y+22}" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#0F172A">{label}</text>')
        for i, (_, pred) in enumerate(predicates):
            x = x0 + name_w + i * pred_w
            parts.append(f'<rect x="{x}" y="{y}" width="{pred_w}" height="{row_h}" fill="{row_fill}" stroke="#E2E8F0"/>')
            member = rid in index.evaluate(pred)
            symbol = '●' if member else '–'
            color = PREDICATE_COLORS[i] if member else '#94A3B8'
            parts.append(f'<text x="{x+pred_w/2}" y="{y+22}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="{color}">{symbol}</text>')
        result_fill = '#FFFBEB' if rid in result else row_fill
        result_color = '#D97706' if rid in result else '#94A3B8'
        result_symbol = '✓' if rid in result else '–'
        parts.append(f'<rect x="{x_result}" y="{y}" width="110" height="{row_h}" fill="{result_fill}" stroke="#E2E8F0"/>')
        parts.append(f'<text x="{x_result+55}" y="{y+22}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="{result_color}">{result_symbol}</text>')
    parts.append('</svg>')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))
    return str(output_path)

def write_set_diagram_svg(query, index, output_path, title='Set Diagram', label_field='name'):
    predicates = _unique_leaves(query)
    if len(predicates) < 2:
        raise ValueError('Need at least 2 predicates for a set diagram')
    if len(predicates) <= 3:
        return _draw_venn(query, index, output_path, title, label_field)
    if len(predicates) <= 5:
        return _draw_matrix(query, index, output_path, title, label_field)
    raise ValueError('Set diagrams support up to 5 predicates')

def write_venn_svg(query, index, output_path, title='Set Diagram', label_field='name'):
    return write_set_diagram_svg(query, index, output_path, title=title, label_field=label_field)
