"""Tiny DSL that emits Excalidraw *skeleton* specs (consumed by render.cjs ->
convertToExcalidrawElements), plus a post-processor that adds arrow bindings
so the resulting .excalidraw files stay editable (move a box, arrows follow)."""
import json, os

FONT = 5   # Excalifont (hand-drawn)
MONO = 3   # Cascadia (code)
INK = '#1e1e1e'
MUTED = '#868e96'
# name: (fill, stroke)
C = {
    'blue': ('#a5d8ff', '#1971c2'), 'green': ('#b2f2bb', '#2f9e44'),
    'yellow': ('#ffec99', '#e67700'), 'red': ('#ffc9c9', '#e03131'),
    'purple': ('#d0bfff', '#6741d9'), 'orange': ('#ffd8a8', '#e8590c'),
    'gray': ('#e9ecef', '#495057'), 'teal': ('#96f2d7', '#0c8599'),
    'white': ('#ffffff', '#343a40'), 'pink': ('#fcc2d7', '#c2255c'),
    'lblue': ('#e7f5ff', '#1971c2'), 'lgreen': ('#ebfbee', '#2f9e44'),
    'lyellow': ('#fff9db', '#e67700'), 'lred': ('#fff5f5', '#e03131'),
    'lpurple': ('#f3f0ff', '#6741d9'), 'lgray': ('#f8f9fa', '#868e96'),
    'lorange': ('#fff4e6', '#e8590c'), 'lteal': ('#e6fcf5', '#0c8599'),
    'none': ('transparent', '#343a40'),
}


def tw(t, fs, mono=False):
    return max(len(l) for l in t.split('\n')) * fs * (0.62 if mono else 0.53)


def th(t, fs):
    return (t.count('\n') + 1) * fs * 1.25


class D:
    def __init__(s, name, title, sub=None, w=None):
        s.name, s.el, s.geo, s.n, s.links = name, [], {}, 0, []
        s.title_h = 0
        s.text(0, 0, title, fs=30, color=INK)
        s.title_h = 44
        if sub:
            s.text(0, 40, sub, fs=16, color=MUTED)
            s.title_h = 76
        s.y0 = s.title_h + 20  # content should start at/below this

    def _id(s, p):
        s.n += 1
        return f'{p}{s.n}'

    # ---------- primitives ----------
    def text(s, x, y, t, fs=18, color=INK, font=FONT, align='left', id=None):
        id = id or s._id('t')
        # NOTE: Excalidraw treats x as the CENTER anchor when textAlign == 'center'
        s.el.append({'type': 'text', 'id': id, 'x': x, 'y': y, 'text': t, 'fontSize': fs,
                     'fontFamily': font, 'strokeColor': color, 'textAlign': align})
        w = tw(t, fs, font == MONO)
        s.geo[id] = ((x - w / 2) if align == 'center' else x, y, w, th(t, fs))
        return id

    def ctext(s, cx, y, t, fs=18, color=INK, font=FONT):
        """text centred horizontally on cx"""
        return s.text(cx, y, t, fs, color, font, 'center')

    def box(s, x, y, w, h, t='', color='white', fs=18, dashed=False, font=FONT, id=None,
            round=True, sw=2, fill=None, stroke=None, tcolor=INK, shape='rectangle',
            valign='middle', opacity=100, fillStyle='solid', talign='center'):
        id = id or s._id('b')
        f, st = C[color]
        if fill: f = fill
        if stroke: st = stroke
        if w is None: w = tw(t, fs, font == MONO) + 44
        if h is None: h = th(t, fs) + 28
        e = {'type': shape, 'id': id, 'x': x, 'y': y, 'width': w, 'height': h,
             'strokeColor': st, 'backgroundColor': f, 'fillStyle': fillStyle, 'strokeWidth': sw,
             'strokeStyle': 'dashed' if dashed else 'solid', 'roughness': 1, 'opacity': opacity,
             'roundness': {'type': 3} if (round and shape == 'rectangle') else None}
        if t:
            e['label'] = {'text': t, 'fontSize': fs, 'fontFamily': font, 'strokeColor': tcolor,
                          'textAlign': talign, 'verticalAlign': valign}
        s.el.append(e)
        s.geo[id] = (x, y, w, h)
        return id

    def zone(s, x, y, w, h, title='', color='lgray', dashed=True, fs=18, tcolor=None, id=None):
        """background grouping rectangle with a title tucked in the top-left"""
        id = s.box(x, y, w, h, '', color, dashed=dashed, id=id, sw=1.5, opacity=60)
        if title:
            s.text(x + 14, y + 8, title, fs=fs, color=tcolor or C[color][1])
        return id

    def anchor(s, id, side, t=0.5):
        x, y, w, h = s.geo[id]
        return {'l': (x, y + h * t), 'r': (x + w, y + h * t),
                't': (x + w * t, y), 'b': (x + w * t, y + h)}[side]

    def arrow(s, pts, color=INK, label=None, dashed=False, heads='->', sw=2, id=None,
              lpos=None, lfs=16, lcolor=None, curve=False, bind=None):
        id = id or s._id('a')
        x0, y0 = pts[0]
        rel = [[round(px - x0, 1), round(py - y0, 1)] for px, py in pts]
        xs = [p[0] for p in rel]; ys = [p[1] for p in rel]
        e = {'type': 'line' if heads == '--' else 'arrow', 'id': id, 'x': x0, 'y': y0,
             'width': max(xs) - min(xs), 'height': max(ys) - min(ys), 'points': rel,
             'strokeColor': color, 'strokeWidth': sw, 'strokeStyle': 'dashed' if dashed else 'solid',
             'roughness': 1, 'roundness': {'type': 2} if curve else None}
        if heads != '--':
            e['endArrowhead'] = 'arrow' if heads in ('->', '<->') else None
            e['startArrowhead'] = 'arrow' if heads in ('<-', '<->') else None
        s.el.append(e)
        if bind: s.links.append((id, bind[0], bind[1]))
        if label:
            if lpos is None:
                # longest segment midpoint
                best = max(range(len(pts) - 1), key=lambda i: abs(pts[i+1][0]-pts[i][0]) + abs(pts[i+1][1]-pts[i][1]))
                (ax, ay), (bx, by) = pts[best], pts[best + 1]
                mx, my = (ax + bx) / 2, (ay + by) / 2
                lines = label.count('\n') + 1
                if abs(bx - ax) >= abs(by - ay):      # horizontal-ish: above the line
                    lpos = (mx - tw(label, lfs) / 2, my - lfs * 1.25 * lines - 6)
                else:                                  # vertical-ish: right of the line
                    lpos = (mx + 10, my - lfs * 0.6 * lines)
            s.text(lpos[0], lpos[1], label, fs=lfs, color=lcolor or color)
        return id

    def link(s, a, b, sa='r', sb='l', ta=0.5, tb=0.5, via=(), **kw):
        p1, p2 = s.anchor(a, sa, ta), s.anchor(b, sb, tb)
        return s.arrow([p1, *via, p2], bind=(a, b), **kw)

    def x(s, cx, cy, size=14, color='#e03131'):
        """a hand-drawn red cross (blocked)"""
        s.arrow([(cx - size, cy - size), (cx + size, cy + size)], color=color, heads='--', sw=4)
        s.arrow([(cx - size, cy + size), (cx + size, cy - size)], color=color, heads='--', sw=4)

    def note(s, x, y, t, color='lyellow', fs=16, w=None, h=None, dashed=False):
        return s.box(x, y, w, h, t, color, fs=fs, dashed=dashed, round=True, sw=1.5)

    def legend(s, x, y, items, fs=15):
        """items: [(color, text)]"""
        for i, (col, t) in enumerate(items):
            s.box(x, y + i * 30, 22, 18, '', col, sw=1.5)
            s.text(x + 32, y + i * 30 - 2, t, fs=fs, color='#495057')

    def spec(s):
        return {'elements': s.el}


# ---------- post-processing ----------
def add_bindings(path, links):
    """inject arrow<->shape bindings into a generated .excalidraw so arrows follow shapes"""
    if not links: links = []
    d = json.load(open(path))
    d['source'] = 'https://excalidraw.com'
    by = {e['id']: e for e in d['elements']}
    for aid, a, b in links:
        ar = by.get(aid)
        if not ar or a not in by or b not in by: continue
        ar['startBinding'] = {'elementId': a, 'focus': 0, 'gap': 2}
        ar['endBinding'] = {'elementId': b, 'focus': 0, 'gap': 2}
        for sid in (a, b):
            bes = by[sid].get('boundElements') or []
            if not any(x['id'] == aid for x in bes):
                bes.append({'id': aid, 'type': 'arrow'})
            by[sid]['boundElements'] = bes
    json.dump(d, open(path, 'w'), indent=2)


def check_layout(path):
    """report bound-text overflow and overlapping standalone texts"""
    d = json.load(open(path))
    els = {e['id']: e for e in d['elements'] if not e.get('isDeleted')}
    issues = []
    texts = [e for e in els.values() if e['type'] == 'text']
    for t in texts:
        c = els.get(t.get('containerId'))
        if c and c['type'] in ('rectangle', 'ellipse', 'diamond'):
            if t['width'] > c['width'] - 8 or t['height'] > c['height'] - 4:
                issues.append(f"OVERFLOW '{t['text'][:30]!r}' {t['width']:.0f}x{t['height']:.0f} in {c['width']:.0f}x{c['height']:.0f}")
    def bb(t):
        c = els.get(t.get('containerId'))
        return (t['x'], t['y'], t['x'] + t['width'], t['y'] + t['height'])
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = bb(texts[i]), bb(texts[j])
            ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 4 and oy > 4:
                issues.append(f"TEXT-OVERLAP '{texts[i]['text'][:22]!r}' x '{texts[j]['text'][:22]!r}'")
    return issues
