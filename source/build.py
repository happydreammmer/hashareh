import sys, os, unicodedata
import shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

import design as d
from design import Spec, Glyph, R, FORMS
import extras as ex

FAMILY = "Hashareh"
FAMILY_FA = "حشره"
VERSION = "1.000"
DESIGNER = "Hatef Mohammad Ali (Kouzehchi)"
COPYRIGHT = f"Copyright (c) 2026 {DESIGNER}"
LICENSE = ("This font is licensed under the MIT License: free to use, copy, modify, merge, publish, "
           "distribute, sublicense and sell, provided the copyright and permission notices are kept. "
           "The font is provided as is, without warranty of any kind.")
LICENSE_URL = "https://opensource.org/license/mit"

# (codepoint, glyph name, joining type, builder)
def letters():
    L = []
    def add(cp, name, jt, fn):
        L.append((cp, name, jt, fn))
    add(0x0628, "beh", "D", lambda sp, f: d.beh_like(sp, f, 1, False))
    add(0x067E, "peh", "D", lambda sp, f: d.beh_like(sp, f, 3, False))
    add(0x062A, "teh", "D", lambda sp, f: d.beh_like(sp, f, 2, True))
    add(0x062B, "theh", "D", lambda sp, f: d.beh_like(sp, f, 3, True))
    add(0x0646, "noon", "D", lambda sp, f: d.beh_like(sp, f, 1, True, "noon"))
    add(0x06CC, "yehFarsi", "D", lambda sp, f: d.beh_like(sp, f, 2 if f in ("init", "medi") else 0, False, "yeh"))
    add(0x064A, "yeh", "D", lambda sp, f: d.beh_like(sp, f, 2, False, "yeh"))
    add(0x0649, "alefMaksura", "D", lambda sp, f: d.beh_like(sp, f, 0, False, "yeh"))
    add(0x0626, "yehHamza", "D", lambda sp, f: d.beh_like(sp, f, 0, False, "hamza"))
    add(0x062C, "jeem", "D", lambda sp, f: d.jeem_like(sp, f, 1, "below"))
    add(0x0686, "tcheh", "D", lambda sp, f: d.jeem_like(sp, f, 3, "below"))
    add(0x062D, "hah", "D", lambda sp, f: d.jeem_like(sp, f, 0))
    add(0x062E, "khah", "D", lambda sp, f: d.jeem_like(sp, f, 1, "above"))
    add(0x062F, "dal", "R", lambda sp, f: d.dal(sp, f))
    add(0x0630, "thal", "R", lambda sp, f: d.dal(sp, f, 1))
    add(0x0631, "reh", "R", lambda sp, f: d.reh(sp, f))
    add(0x0632, "zain", "R", lambda sp, f: d.reh(sp, f, 1))
    add(0x0698, "jeh", "R", lambda sp, f: d.reh(sp, f, 3))
    add(0x0633, "seen", "D", lambda sp, f: d.seen(sp, f))
    add(0x0634, "sheen", "D", lambda sp, f: d.seen(sp, f, 3))
    add(0x0635, "sad", "D", lambda sp, f: d.sad(sp, f))
    add(0x0636, "dad", "D", lambda sp, f: d.sad(sp, f, 1))
    add(0x0637, "tah", "D", lambda sp, f: d.tah(sp, f))
    add(0x0638, "zah", "D", lambda sp, f: d.tah(sp, f, 1))
    add(0x0639, "ain", "D", lambda sp, f: d.ain(sp, f))
    add(0x063A, "ghain", "D", lambda sp, f: d.ain(sp, f, 1))
    add(0x0641, "feh", "D", lambda sp, f: d.feh_qaf(sp, f, 1))
    add(0x0642, "qaf", "D", lambda sp, f: d.feh_qaf(sp, f, 2, True))
    add(0x06A9, "keheh", "D", lambda sp, f: d.kaf(sp, f))
    add(0x06AF, "gaf", "D", lambda sp, f: d.kaf(sp, f, gaf=True))
    add(0x0643, "kaf", "D", lambda sp, f: d.kaf(sp, f, arabic=True))
    add(0x0644, "lam", "D", lambda sp, f: d.lam(sp, f))
    add(0x0645, "meem", "D", lambda sp, f: d.meem(sp, f))
    add(0x0647, "heh", "D", lambda sp, f: d.heh(sp, f))
    add(0x0629, "tehMarbuta", "R", lambda sp, f: d.heh(sp, f, 2))
    add(0x06C0, "hehYeh", "R", lambda sp, f: d.heh(sp, f, 0, True))
    add(0x0648, "waw", "R", lambda sp, f: d.waw(sp, f))
    add(0x0624, "wawHamza", "R", lambda sp, f: d.waw(sp, f, True))
    add(0x0627, "alef", "R", lambda sp, f: d.alef(sp, f))
    add(0x0622, "alefMadda", "R", lambda sp, f: d.alef(sp, f, "madda"))
    add(0x0623, "alefHamza", "R", lambda sp, f: d.alef(sp, f, "hamza_above"))
    add(0x0625, "alefHamzaBelow", "R", lambda sp, f: d.alef(sp, f, "hamza_below"))
    return L


ALEFS = [("alef", None), ("alefMadda", "madda"), ("alefHamza", "hamza_above"), ("alefHamzaBelow", "hamza_below")]


def build_glyphs(sp):
    G = {}
    cmap = {}
    joining = {}
    for cp, name, jt, fn in letters():
        forms = FORMS if jt == "D" else ("isol", "fina")
        for f in forms:
            G[name if f == "isol" else f"{name}.{f}"] = fn(sp, f)
        cmap[cp] = name
        joining[name] = jt
    # lam-alef ligatures
    for an, var in ALEFS:
        G[f"lam_{an}"] = d.lamalef(sp, "isol", var)
        G[f"lam_{an}.fina"] = d.lamalef(sp, "fina", var)
    # hamza, tatweel
    hz = d.hamza(sp, 0, 0, 1.5)
    G["hamza"] = ex._g(sp, d.shift(hz, -min(s.bounds[0] for s in hz)),
                       max(s.bounds[2] for s in hz) - min(s.bounds[0] for s in hz), 60)
    cmap[0x0621] = "hamza"
    G["tatweel"] = Glyph([R(0, 0, 240, sp.SH)], 240)
    cmap[0x0640] = "tatweel"
    # digits
    for n in range(10):
        G[f"uni{0x06F0 + n:04X}"] = ex.fa_digit(sp, n)
        cmap[0x06F0 + n] = f"uni{0x06F0 + n:04X}"
        ln = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][n]
        G[ln] = ex.la_digit(sp, n)
        cmap[0x30 + n] = ln
        an = f"uni{0x0660 + n:04X}"
        if n in (4, 5, 6):
            G[an] = ex.ar_digit(sp, n)
            cmap[0x0660 + n] = an
        else:
            cmap[0x0660 + n] = f"uni{0x06F0 + n:04X}"
    # punctuation
    P = ex.punct(sp)
    uni = {"period": 0x2E, "colon": 0x3A, "comma": 0x2C, "semicolon": 0x3B, "uni060C": 0x060C, "uni061B": 0x061B,
           "exclam": 0x21, "question": 0x3F, "uni061F": 0x061F, "hyphen": 0x2D, "endash": 0x2013, "emdash": 0x2014,
           "underscore": 0x5F, "slash": 0x2F, "backslash": 0x5C, "parenleft": 0x28, "parenright": 0x29,
           "bracketleft": 0x5B, "bracketright": 0x5D, "plus": 0x2B, "equal": 0x3D, "less": 0x3C, "greater": 0x3E,
           "guillemotleft": 0xAB, "guillemotright": 0xBB, "quotesingle": 0x27, "quotedbl": 0x22, "ellipsis": 0x2026,
           "percent": 0x25, "uni066A": 0x066A, "uni066B": 0x066B, "uni066C": 0x066C, "asterisk": 0x2A, "uni066D": 0x066D}
    for k, v in P.items():
        G[k] = v
        cmap[uni[k]] = k
    cmap[0x066A] = "percent"
    cmap[0x066D] = "asterisk"
    # spaces & controls
    G["space"] = Glyph([], 340)
    cmap[0x20] = "space"; cmap[0xA0] = "space"
    for cp in (0x200C, 0x200D, 0x200E, 0x200F):
        G[f"uni{cp:04X}"] = Glyph([], 0)
        cmap[cp] = f"uni{cp:04X}"
    # marks
    M = ex.marks(sp)
    for k, (sh, pos) in M.items():
        G[k] = Glyph(sh, 0, 0)
        G[k].markpos = pos
        cmap[int(k[3:], 16)] = k
    # presentation forms (for apps without shaping)
    for cp in list(range(0xFB50, 0xFDFF)) + list(range(0xFE70, 0xFEFF)):
        dec = unicodedata.decomposition(chr(cp)).split()
        if not dec or not dec[0].startswith("<"):
            continue
        tag = dec[0][1:-1]
        bases = [int(x, 16) for x in dec[1:]]
        if tag not in ("isolated", "initial", "medial", "final"):
            continue
        sfx = {"isolated": "", "initial": ".init", "medial": ".medi", "final": ".fina"}[tag]
        if len(bases) == 1 and bases[0] in cmap and cmap[bases[0]] in joining:
            g = cmap[bases[0]] + sfx
        elif len(bases) == 2 and bases[0] == 0x0644 and bases[1] in cmap:
            an = cmap[bases[1]]
            g = f"lam_{an}" + (".fina" if tag == "final" else "")
        else:
            continue
        if g in G:
            cmap[cp] = g
    return G, cmap, joining


# ------------------------------------------------------------------ outlines
def polys(g):
    if not g.shapes:
        return []
    u = unary_union([s.buffer(0) for s in g.shapes])
    u = shapely.set_precision(u, 1.0)
    u = u.buffer(0)
    geoms = list(u.geoms) if hasattr(u, "geoms") else [u]
    return [p for p in geoms if isinstance(p, Polygon) and p.area > 4]


def clean(coords):
    pts = [(int(round(x)), int(round(y))) for x, y in coords[:-1]]
    out = []
    for p in pts:
        if not out or out[-1] != p:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    # drop collinear points
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) == 0:
                out.pop(i); changed = True; break
    return out


def draw(pen, ps, sign):
    rings = []
    for p in ps:
        p = orient(p, sign=sign)
        for ring_ in [p.exterior] + list(p.interiors):
            pts = clean(list(ring_.coords))
            if len(pts) >= 3:
                rings.append(pts)
    if len(rings) == 1 and len(rings[0]) == 4:
        # a glyph that is one plain rectangle (alef, tatweel, ۱, ...): PDF renderers such as
        # pdfium (Chrome, Edge) fill such a path as a pixel-snapped rect without anti-aliasing,
        # so it sticks out by up to a pixel next to its anti-aliased neighbours. A midpoint on
        # one edge keeps it a normal path.
        a, b = rings[0][0], rings[0][1]
        rings[0].insert(1, ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2))
    for pts in rings:
        pen.moveTo(pts[0])
        for q in pts[1:]:
            pen.lineTo(q)
        pen.closePath()


# ------------------------------------------------------------------ kerning
FOOTED = ("reh", "zain", "jeh", "waw", "wawHamza")
CLEAR = 55          # nothing comes closer than this when a letter tucks in over a foot
TUCK_PUNCT = ("period", "comma", "uni060C", "uni061B", "uni061F", "exclam", "question", "colon",
              "ellipsis", "guillemotleft", "guillemotright", "parenleft", "parenright")


def body(ps, sp):
    """The letter without its dots and small marks (hamza, madda)."""
    lim = 2.6 * sp.DOT
    out = [p for p in ps if not (p.bounds[2] - p.bounds[0] <= lim and p.bounds[3] - p.bounds[1] <= lim)]
    return out or ps


def foot_kerning(G, P, joining, sp):
    """For every letter ending in a foot (reh family, waw) and every glyph that can follow it,
    slide the follower right over the foot, as if the foot were not there:
      - above the baseline, the follower's body keeps the regular gap (sp.GT, = 2 x side bearing)
        from the upright of ر / head of و; dots and marks are left out of this measure,
      - nothing comes closer than CLEAR anywhere (dots below, bowls, the follower's own foot),
      - the foot never sticks out past the follower's left edge.
    The feet are drawn so that an alef after ر ends exactly where the foot ends (design.reh) and
    a letter after و begins exactly where its foot ends (design.waw); the same rule gives the
    same picture in every weight."""
    from shapely.geometry import MultiPolygon as MP
    from shapely.geometry import box as bx
    from shapely.affinity import translate as tr
    left = [n + sfx for n in FOOTED for sfx in ("", ".fina")]
    followers = []
    for n, j in joining.items():
        followers.append(n)
        if j == "D":
            followers.append(n + ".init")
    followers += [k for k in G if k.startswith("lam_") and not k.endswith(".fina")]
    followers += [k for k in TUCK_PUNCT if k in G]
    up = bx(-5000, -20, 5000, 5000)
    pairs = []
    for a in left:
        A = MP(P[a]).buffer(0)
        edge = MP(body(P[a], sp)).buffer(0).intersection(up).bounds[0]
        foot_end = A.bounds[0]
        for b in followers:
            if not P.get(b):
                continue
            Bg = MP(P[b]).buffer(0)
            Bup = MP(body(P[b], sp)).buffer(0).intersection(up)
            if Bup.is_empty:
                continue
            adv_b = round(G[b].adv)
            def ok(k):
                Bs = tr(Bg, -adv_b + k, 0)
                return Bs.distance(A) >= CLEAR and Bs.bounds[0] <= foot_end + 0.5
            kmax = k = int(edge - sp.GT - (Bup.bounds[2] - adv_b))
            while k > 0 and not ok(k):
                k -= 4
            while 0 < k < kmax and ok(k + 1):
                k += 1
            if k >= 20:
                pairs.append((a, b, -k))
    return pairs


# ------------------------------------------------------------------ features
def features(G, joining, marknames, anchors, kerns=()):
    D = [n for n, j in joining.items() if j == "D"]
    Rj = [n for n, j in joining.items() if j == "R"]
    fea = ["languagesystem DFLT dflt;", "languagesystem arab dflt;", "languagesystem arab FAR;", ""]
    def single(tag, names, sfx):
        names = [n for n in names if n + sfx in G]
        fea.append(f"feature {tag} {{")
        fea.append(f"  sub [{' '.join(names)}] by [{' '.join(n + sfx for n in names)}];")
        fea.append(f"}} {tag};")
    single("init", D, ".init")
    single("medi", D, ".medi")
    single("fina", D + Rj, ".fina")
    fea.append("feature rlig {")
    for an, _ in ALEFS:
        fea.append(f"  sub lam.init {an}.fina by lam_{an};")
        fea.append(f"  sub lam.medi {an}.fina by lam_{an}.fina;")
    fea.append("} rlig;")
    top = [m for m in marknames if G[m].markpos == "top"]
    bot = [m for m in marknames if G[m].markpos == "bot"]
    bases = [n for n in G if n not in marknames and n != ".notdef"]
    fea.append(f"markClass [{' '.join(top)}] <anchor 0 0> @TOP;")
    fea.append(f"markClass [{' '.join(bot)}] <anchor 0 0> @BOT;")
    fea.append("feature mark {")
    for n in bases:
        if not G[n].shapes:
            continue
        (tx, ty), (bx, by) = anchors[n]
        fea.append(f"  pos base {n} <anchor {tx} {ty}> mark @TOP <anchor {bx} {by}> mark @BOT;")
    fea.append("} mark;")
    if kerns:
        fea.append("feature kern {")
        fea.append("  lookupflag IgnoreMarks;")
        for a, b, v in kerns:
            # RTL: shift the footed letter (and everything before it) left, so the next letter closes in
            fea.append(f"  pos {a} {b} <{v} 0 {v} 0>;")
        fea.append("} kern;")
    fea.append("feature mkmk {")
    for m in top:
        fea.append(f"  pos mark {m} <anchor 0 {anchors[m][0][1]}> mark @TOP;")
    for m in bot:
        fea.append(f"  pos mark {m} <anchor 0 {anchors[m][1][1]}> mark @BOT;")
    fea.append("} mkmk;")
    fea.append("table GDEF {")
    fea.append(f"  GlyphClassDef [{' '.join(bases)}], , [{' '.join(marknames)}], ;")
    fea.append("} GDEF;")
    return "\n".join(fea)


# ------------------------------------------------------------------ build
STYLE_FA = {"Light": "نازک", "Medium": "متوسط", "Bold": "ضخیم"}


def build(SV, SH, style, weight, outdir):
    sp = Spec(SV, SH)
    G, cmap, joining = build_glyphs(sp)
    G[".notdef"] = Glyph([R(50, 0, 450, 600), ], 500)
    G[".notdef"].hole = True
    order = [".notdef"] + [n for n in G if n != ".notdef"]
    P = {n: polys(G[n]) for n in order}
    # .notdef box with hole
    P[".notdef"] = [Polygon([(50, 0), (450, 0), (450, 600), (50, 600)], [[(100, 50), (400, 50), (400, 550), (100, 550)]])]
    marknames = [n for n in G if hasattr(G[n], "markpos")]
    anchors = {}
    ymax_all, ymin_all = 0, 0
    for n in order:
        if not P[n]:
            anchors[n] = ((0, 0), (0, 0)); continue
        b = MultiPolygon(P[n]).bounds
        ymin_all, ymax_all = min(ymin_all, b[1]), max(ymax_all, b[3])
        cx = int(round(G[n].cx))
        if n in marknames:
            anchors[n] = ((0, int(b[3] + 45)), (0, int(b[1] - 45)))
        else:
            anchors[n] = ((cx, int(max(b[3], sp.T) + 75)), (cx, int(min(b[1], 0) - 75)))
    asc = int(ymax_all + 230)    # room for marks
    desc = int(ymin_all - 120)
    adv = {n: int(round(G[n].adv)) for n in order}
    kerns = foot_kerning(G, P, joining, sp)
    fea = features(G, joining, marknames, anchors, kerns)
    # Style linking: Medium is the Regular and Bold the Bold of the family "Hashareh" (so Ctrl+B
    # switches between them); Light is the Regular of its own family "Hashareh Light".
    linked = style in ("Medium", "Bold")
    names = {
        "familyName": FAMILY if linked else f"{FAMILY} {style}",
        "styleName": "Bold" if style == "Bold" else "Regular",
        "typographicFamily": FAMILY, "typographicSubfamily": style,
        "uniqueFontIdentifier": f"{FAMILY}-{style};{VERSION}",
        "fullName": f"{FAMILY} {style}", "psName": f"{FAMILY}-{style}",
        "version": f"Version {VERSION}",
        "copyright": COPYRIGHT,
        "designer": DESIGNER,
        "description": ("Hashareh is a geometric square Persian display typeface, rebuilt from the lettering "
                        "of the 1347 / 1968 emblem of the Entomological Society of Iran."),
        "licenseDescription": LICENSE,
        "licenseInfoURL": LICENSE_URL,
        "sampleText": "انجمن حشره‌شناسان ایران ۱۳۴۷",
    }
    outs = []
    for flavor in ("ttf", "otf"):
        fb = FontBuilder(1000, isTTF=(flavor == "ttf"))
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        if flavor == "ttf":
            glyphs = {}
            for n in order:
                pen = TTGlyphPen(None)
                draw(pen, P[n], -1.0)
                glyphs[n] = pen.glyph()
            fb.setupGlyf(glyphs)
        else:
            cs = {}
            for n in order:
                pen = T2CharStringPen(adv[n], None)
                draw(pen, P[n], 1.0)
                cs[n] = pen.getCharString()
            fb.setupCFF(f"{FAMILY}-{style}", {"FullName": f"{FAMILY} {style}", "FamilyName": FAMILY,
                                               "Weight": style, "Notice": COPYRIGHT}, cs, {})
        lsb = {}
        for n in order:
            lsb[n] = int(MultiPolygon(P[n]).bounds[0]) if P[n] else 0
        fb.setupHorizontalMetrics({n: (adv[n], lsb[n]) for n in order})
        fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=0)
        fb.setupNameTable(names)
        nt = fb.font["name"]
        nt.setName(FAMILY_FA if linked else f"{FAMILY_FA} {STYLE_FA[style]}", 1, 3, 1, 0x0429)
        nt.setName(f"{FAMILY_FA} {STYLE_FA[style]}", 4, 3, 1, 0x0429)
        nt.setName(FAMILY_FA, 16, 3, 1, 0x0429)
        nt.setName(STYLE_FA[style], 17, 3, 1, 0x0429)
        fsSel = 0x20 if style == "Bold" else 0x40
        fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
                    usWinAscent=asc, usWinDescent=-desc, usWeightClass=weight,
                    fsType=0,                              # installable: no embedding restrictions
                    fsSelection=fsSel | 0x80, achVendID="NONE",
                    ulUnicodeRange1=(1 << 0) | (1 << 13), ulCodePageRange1=(1 << 0) | (1 << 6),
                    sxHeight=sp.T, sCapHeight=sp.A, version=4)
        fb.setupPost()
        from fontTools.misc.timeTools import timestampNow
        fb.setupHead(unitsPerEm=1000, fontRevision=float(VERSION), macStyle=1 if style == "Bold" else 0, created=timestampNow(), modified=timestampNow())
        addOpenTypeFeaturesFromString(fb.font, fea)
        fb.font["OS/2"].recalcAvgCharWidth(fb.font)
        path = os.path.join(outdir, f"{FAMILY}-{style}.{flavor}")
        fb.save(path)
        outs.append(path)
        if flavor == "ttf":
            f = TTFont(path)
            f.flavor = "woff2"
            wp = os.path.join(outdir, f"{FAMILY}-{style}.woff2")
            f.save(wp)
            outs.append(wp)
    open(os.path.join(outdir, f"features-{style}.fea"), "w").write(fea)
    return outs, len(order)


WEIGHTS = ((60, 56, "Light", 300), (88, 80, "Medium", 500), (118, 106, "Bold", 700))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(out, exist_ok=True)
    for SV, SH, style, w in WEIGHTS:
        o, n = build(SV, SH, style, w, out)
        print(style, n, "glyphs", o)
