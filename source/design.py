"""
Hashareh (حشره) — rebuilt from measurements of the 1968 Societas Entomologica Iranica emblem.

Measured in the emblem (alef = 660 units):
  stems ~120, bars ~105, dots ~118 square, teeth 245, ن cup 640 x 420 with the dot inside,
  ح/ج head 455 x 350 with a drooping lip and a small counter, medial م straddles the baseline
  (−103 … 234) with a small counter at baseline level, ه 302 x 250 with a pin-hole counter,
  ر drops ~165 below the join and runs out in a long foot, digits are full alef height and wide.

Vertical zones, the same in every weight (strokes grow inwards from these lines):
   660  alef, lam, kaf, tah stems, digits
   350  heads: ج ح خ head, ف ق head, ص ض ط ظ loop, م box, ع mouth, ی head, initial ه
   300  د ذ, isolated ر ز ژ, ه ة ۀ, و head
   245  teeth, final ر ز ژ, ن cup, top of medial م, bowl tip of س ص
     0  baseline
  −165  foot of ر ز ژ و, floor of ن
  −230  bowl of س ص, top of the bowl tip of ج ح خ چ ع غ
  −320  bowl of ل ق ی
  −400  bowl of ج ح خ چ ع غ, tail of م

Coordinates: x = 0 is the LEFT edge (the end of the letter, towards the next one),
x = bw is the RIGHT edge (where the letter starts / the previous letter joins).
"""
import math
from shapely.geometry import Polygon, LineString, box
from shapely.affinity import translate, scale as sscale


class Spec:
    def __init__(self, SV, SH):
        self.SV = SV            # vertical stem width
        self.SH = SH            # horizontal bar thickness
        self.AW = round(SV * 1.1)   # alef width
        self.A = 660            # alef / ascender
        self.T = 245            # tooth height
        self.DZ = 300           # dal zone
        self.HH = 350           # head zone
        self.DR = -165          # ر / و drop
        self.DS = -230          # س ص bowls; top of the ج / ع bowl tip
        self.DB = -320          # deep bowls (ل ق ی)
        self.DJ = -400          # ح / ع bowls
        self.DOT = round(SV * 0.55 + 43)   # 108 bold
        self.DG = round(self.DOT * 0.38)   # gap between dots
        self.DA = 85            # body -> dots above
        self.DBL = 60           # baseline -> dots below
        self.G = 190            # join run
        self.SB = 75            # side bearing on free sides
        self.GT = 152           # gap kept above the baseline when a letter tucks in over a ر / و foot
        self.N = self.A         # digit height
        self.t = round(SH * 0.62)  # thin stroke for small marks
        self.OV = 18            # joining stroke reaches this far into the next letter (no seams)


# ------------------------------------------------------------------ primitives
def R(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def P(*pts):
    return Polygon(pts)


def shift(shapes, dx=0, dy=0):
    return [translate(s, dx, dy) for s in shapes]


def mirror(shapes, cx):
    return [sscale(s, -1, 1, origin=(cx, 0)) for s in shapes]


def ring(x, y, w, h, wx, wy=None, wy_top=None):
    wy = wx if wy is None else wy
    wt = wy if wy_top is None else wy_top
    return [R(x, y, x + w, y + wy), R(x, y + h - wt, x + w, y + h),
            R(x, y, x + wx, y + h), R(x + w - wx, y, x + w, y + h)]


def slab(x0top, x1top, ytop, x0bot, x1bot, ybot):
    """Slanted stroke as a parallelogram/trapezoid."""
    return P((x0bot, ybot), (x1bot, ybot), (x1top, ytop), (x0top, ytop))


def pline(pts, w, clip=None):
    """Monoline stroke of width w along a polyline, square (mitred) corners, optionally clipped."""
    g = LineString(pts).buffer(w / 2, cap_style=2, join_style=2, mitre_limit=10)
    return g.intersection(clip) if clip is not None else g


def diag(sp, xtop, ytop, xbot, ybot, weight=1.0):
    """A stroke whose top-left corner starts at (xtop,ytop) and whose bottom-right edge ends
    at (xbot,ybot); horizontal width chosen so perpendicular weight ~= SV*weight."""
    dx, dy = xbot - xtop, ytop - ybot
    ang = math.atan2(abs(dx), dy)
    w = sp.SV * weight / math.cos(ang)
    return P((xbot - w, ybot), (xbot, ybot), (xtop + w, ytop), (xtop, ytop)), w


def dots(sp, n, cx, y, above=True, gap=None, row=False):
    """n square dots centred on cx. above: y = bottom of lowest row; below: y = top of highest row.
    row: three dots in one line instead of a pyramid."""
    d = sp.DOT
    g = sp.DG if gap is None else gap
    out = []
    def sq(x, yy):
        out.append(R(x - d / 2, yy, x + d / 2, yy + d))
    o = (d + g) / 2
    if n == 1:
        sq(cx, y if above else y - d)
    elif n == 2:
        yy = y if above else y - d
        sq(cx - o, yy); sq(cx + o, yy)
    elif n == 3 and row:
        yy = y if above else y - d
        sq(cx - 2 * o, yy); sq(cx, yy); sq(cx + 2 * o, yy)
    elif n == 3:
        if above:   # pyramid
            sq(cx - o, y); sq(cx + o, y); sq(cx, y + d + g * 0.75)
        else:       # inverted pyramid
            sq(cx - o, y - d); sq(cx + o, y - d); sq(cx, y - 2 * d - g * 0.75)
    return out


def dots_h(sp, n, gap=None):
    g = sp.DG if gap is None else gap
    d = sp.DOT
    return d if n == 1 else (2 * d + g * 0.75 if n == 3 else d)


def mark_t(sp, k=1.0):
    """Stroke of the small marks: harakat, hamza, madda."""
    return max(30, round(max(36, sp.t) * k))


def mark_loop(sp, k=1.0):
    """(stroke, outer size) of the square loop shared by damma, sukun and hamza; the counter
    stays open in every weight."""
    t = mark_t(sp, k)
    return t, max(round(120 * k), 2 * t + max(round(34 * k), round(0.6 * t)))


MARK_TAIL, MARK_FOOT = 60, 55


def mark_tail(sp, x0, y, k=1.0):
    """Square tail under a mark loop whose left wall starts at x0: the wall runs down to y and
    turns into a short foot to the left. Returns (shapes, loop bottom)."""
    t = mark_t(sp, k)
    yb = y + round(MARK_TAIL * k)
    return [R(x0, y, x0 + t, yb + t), R(x0 - round(MARK_FOOT * k), y, x0 + t, y + t)], yb


def hamza(sp, x, y, k=1.0):
    """Square hamza, built like the damma: a square 'c' open to the right whose spine runs on
    down into the damma's tail. (x, y) = bottom centre."""
    t, L = mark_loop(sp, k)
    x0 = x - (L - round(MARK_FOOT * k)) / 2
    tail, yb = mark_tail(sp, x0, y, k)
    return tail + [R(x0, yb + L - t, x0 + L, yb + L),          # top arm
                   R(x0, yb, x0 + t, yb + L),                  # spine
                   R(x0, yb, x0 + round(L * 0.85), yb + t)]    # bottom arm


def hamza_h(sp, k=1.0):
    return round(MARK_TAIL * k) + mark_loop(sp, k)[1]


def madda(sp, cx, y):
    """Madda drawn with the fatha's slanted stroke between two flat ends."""
    t = mark_t(sp)
    return [R(cx - 125, y, cx - 45, y + t),
            P((cx - 45, y), (cx + 45, y + 60), (cx + 45, y + 60 + t), (cx - 45, y + t)),
            R(cx + 45, y + 60, cx + 125, y + 60 + t)]


# ------------------------------------------------------------------ glyph + assembly
class Glyph:
    def __init__(self, shapes, adv, cx=None):
        self.shapes = shapes
        self.adv = adv
        self.cx = adv / 2 if cx is None else cx


FORMS = ("isol", "init", "medi", "fina")


def assemble(sp, shapes, bw, form, cx=None, sb_l=None, sb_r=None, run=None):
    SV, SH = sp.SV, sp.SH
    jl = form in ("init", "medi")
    jr = form in ("medi", "fina")
    xo = (sp.G if run is None else run) if jl else (sp.SB if sb_l is None else sb_l)
    out = shift(shapes, xo)
    if jl:
        out.append(R(-sp.OV, 0, xo + SV, SH))
    if jr:
        out.append(R(xo + bw - SV, 0, xo + bw, SH))
    adv = xo + bw + (0 if jr else (sp.SB if sb_r is None else sb_r))
    return Glyph(out, adv, xo + (bw / 2 if cx is None else cx))


def deep_bowl(sp, w, depth, tip, right_drop=True):
    """U hanging below the baseline: bottom bar, left tip rising to y=tip, right side dropping
    from the baseline. Occupies x 0..w."""
    SV, SH = sp.SV, sp.SH
    sh = [R(0, depth, w, depth + SH), R(0, depth, SV, tip)]
    if right_drop:
        sh.append(R(w - SV, depth, w, SH))
    return sh


# ------------------------------------------------------------------ BEH family / NOON / YEH
def beh_like(sp, form, nd=0, above=True, kind="beh"):
    SV, SH, T = sp.SV, sp.SH, sp.T
    if form in ("init", "medi"):
        sh = [R(0, 0, SV, T)]
        cx = SV / 2
        if nd:
            if above:
                sh += dots(sp, nd, cx, T + sp.DA, True)
            else:
                sh += dots(sp, nd, cx - 25, -sp.DBL, False)
        if kind == "hamza":
            sh += hamza(sp, cx + 8, T + 70, 0.9)
        return assemble(sp, sh, SV, form, cx)
    if kind == "noon":
        # the cup hangs across the joining line: the join meets the right wall half-way up,
        # the floor is on the reh / waw foot line and the walls stop on the teeth line
        bw = 600
        yb, yt = sp.DR, T
        sh = [R(0, yb, bw, yb + SH), R(0, yb, SV, yt), R(bw - SV, yb, bw, yt)]
        dy = yt - sp.DOT                         # dot top level with the top of the walls
        sh += [R(bw / 2 - sp.DOT / 2, dy, bw / 2 + sp.DOT / 2, dy + sp.DOT)]
        return assemble(sp, sh, bw, form)
    if kind in ("yeh", "hamza"):
        return yeh_final(sp, form, nd, kind)
    bw = 640
    sh = [R(0, 0, bw, SH), R(0, 0, SV, T)]
    sh.append(R(bw - SV, 0, bw, T))            # right tooth, also in the final form
    if nd:
        if above:
            # the dots hang inside the bowl from the teeth line, like the dot of ن;
            # the third dot of ث sits just above the line
            sh += dots(sp, nd, bw / 2, T - sp.DOT, True)
        else:
            sh += dots(sp, nd, bw / 2, -sp.DBL, False)
    return assemble(sp, sh, bw, form)


def yeh_final(sp, form, nd, kind):
    SV, SH, T = sp.SV, sp.SH, sp.T
    Dd = sp.DB
    if form == "isol":
        bw = 640
        hx = bw - 250            # head (hook open to the right) left edge
        ya = sp.HH - SH          # head arm bottom: the arm's top is on the head line
        sh = [R(hx, ya, bw, ya + SH),          # top arm
              R(hx, 0, hx + SV, ya + SH),      # down
              R(hx, 0, bw, SH),                # back along the baseline
              R(bw - SV, Dd, bw, SH),          # drop into the bowl
              R(0, Dd, bw, Dd + SH),           # bowl floor
              R(0, Dd, SV, 0)]                 # tip rises to the baseline
        htop = ya + SH
        dcx = (SV + hx) / 2 + 10
    else:
        bw = 580
        sh = [R(bw - SV, Dd, bw, SH), R(0, Dd, bw, Dd + SH), R(0, Dd, SV, 0)]
        htop = SH
        dcx = bw / 2
    if nd:
        sh += dots(sp, nd, dcx, Dd + SH + 30, True, gap=34)
    if kind == "hamza":
        hx_ = bw - 130 if form == "isol" else bw - 200
        sh += hamza(sp, hx_, htop + 60, 0.9)
    return assemble(sp, sh, bw, form, bw / 2)

def hah_head(sp, W):
    SV, SH, HH = sp.SV, sp.SH, sp.HH
    HT = SH
    return [R(0, HH - HT, W, HH),                 # top bar
            R(W - SV, 0, W, HH),                  # spine on the right
            R(0, HH - HT - 48, SV, HH)], HT       # drooping lip at the left end


def jeem_like(sp, form, nd=0, where="below"):
    SV, SH, HH, DJ = sp.SV, sp.SH, sp.HH, sp.DJ
    W = 455
    head, HT = hah_head(sp, W)
    sh = head + [R(0, 0, W, SH)]
    if form in ("init", "medi"):
        if nd:
            if where == "above":
                sh += dots(sp, nd, W * 0.5, HH + sp.DA, True)
            else:
                sh += dots(sp, nd, W * 0.45, -sp.DBL, False)
    else:
        # lower bowl opening to the right: spine on the left, floor, upturned tip on the right
        Wb = W + 70                     # final is drawn exactly like the isolated form
        # the tip stops on a fixed line in every weight, low enough to pass under a ر / و foot
        sh += [R(0, DJ, SV, SH), R(0, DJ, Wb, DJ + SH), R(Wb - SV, DJ, Wb, sp.DS)]
        # (fina: the join meets the head's spine; the bowl tip reaches under the join run)
        if nd:
            if where == "above":
                sh += dots(sp, nd, W * 0.5, HH + sp.DA, True)
            # dots in the bowl sit under the centre of the head, in line with the dot of خ
            elif nd == 1:
                inner = (DJ + SH + 0) / 2
                sh += dots(sp, 1, W / 2, inner - sp.DOT / 2, True)
            else:
                # three dots: the same column, unless that would bring them closer than one dot-gap
                # to the spine of the bowl (Bold)
                g = 32
                sh += dots(sp, 3, max(W / 2, SV + g + sp.DOT + g / 2), -30, False, gap=g)
    return assemble(sp, sh, Wb if form == "isol" else W, form, W / 2)


# ------------------------------------------------------------------ DAL / REH
def dal(sp, form, nd=0):
    """Dal: fully square - a right stem with a top arm pointing left over the base."""
    SV, SH = sp.SV, sp.SH
    bw = 380
    H = sp.DZ          # stays below the head line (350)
    arm = 255
    sh = [R(0, 0, bw, SH), R(bw - SV, 0, bw, H), R(bw - arm, H - SH, bw, H)]
    if nd:
        sh += dots(sp, nd, bw - arm / 2 - 10, H + sp.DA, True)
    return assemble(sp, sh, bw, form, bw - 150)


def reh(sp, form, nd=0):
    SV, SH, T, DR = sp.SV, sp.SH, sp.T, sp.DR
    # the foot ends exactly under the left edge of an alef tucked in after it (see build.foot_kerning)
    bw = SV + sp.GT + sp.AW
    top = sp.DZ if form == "isol" else T
    sh = [R(bw - SV, DR, bw, top), R(0, DR, bw, DR + SH)]
    dcx = bw - SV / 2 - 25
    if nd:
        sh += dots(sp, nd, dcx, top + sp.DA, True)
    return assemble(sp, sh, bw, form, dcx)


# ------------------------------------------------------------------ SEEN / SAD / TAH
def teeth3(sp, x0, h=None):
    SV = sp.SV
    gs = 185
    xs = [x0 + k * (SV + gs) for k in range(3)]
    return [R(x, 0, x + SV, sp.T if h is None else h) for x in xs], xs


SEEN_BOWL_W = 520


def seen(sp, form, nd=0):
    SV, SH, T = sp.SV, sp.SH, sp.T
    if form in ("init", "medi"):
        sh, xs = teeth3(sp, 0)
        bw = xs[-1] + SV
    else:
        B = SEEN_BOWL_W
        sh = deep_bowl(sp, B, sp.DS, T)
        t, xs = teeth3(sp, B - SV)
        sh += t
        bw = xs[-1] + SV
    sh.append(R(0 if form in ("init", "medi") else SEEN_BOWL_W - SV, 0, bw, SH))
    cx = xs[1] + SV / 2
    if nd:
        sh += dots(sp, nd, cx, T + sp.DA, True, row=True)     # ش: three dots in one line, as in the emblem
    return assemble(sp, sh, bw, form, cx)


LOOP_W, LOOP_H = 520, 350          # top on the head line


def flat_loop(sp, x, w=LOOP_W, h=LOOP_H):
    return ring(x, 0, w, h, sp.SV, sp.SH)


def sad(sp, form, nd=0):
    SV, SH, T = sp.SV, sp.SH, sp.T
    x = 0
    sh = []
    if form in ("isol", "fina"):
        B = SEEN_BOWL_W
        sh += deep_bowl(sp, B, sp.DS, T)
        x = B - SV
    sh.append(R(x, 0, x + SV, T))          # the tooth that follows the loop
    lx = x + SV + 120
    sh += flat_loop(sp, lx)
    bw = lx + LOOP_W
    sh.append(R(0 if form in ("init", "medi") else x, 0, bw, SH))
    cx = lx + LOOP_W / 2
    if nd:
        sh += dots(sp, nd, cx, LOOP_H + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


def tah(sp, form, nd=0):
    SV, SH, A = sp.SV, sp.SH, sp.A
    W = 480
    sh = flat_loop(sp, 0, W)
    xs = 110                                  # the stem rises out of the loop, left of centre
    sh.append(R(xs, LOOP_H - SH, xs + SV, A))
    cx = (xs + SV + W - SV) / 2 + 10
    if nd:
        sh += dots(sp, nd, cx, LOOP_H + sp.DA, True)
    return assemble(sp, sh, W, form, W / 2)


# ------------------------------------------------------------------ AIN
AIN_W = 400
AIN_ISO_OFF = 170     # isolated / final: the head sits this far right of the bowl's spine


def ain_open(sp, W):
    """Open head of initial / isolated ain: a cup opening to the right with a horn."""
    SV, SH, HH = sp.SV, sp.SH, sp.HH
    return [R(0, HH - SH, W, HH),            # upper arm
            R(W - SV, HH - SH, W, HH + 80),  # horn
            R(0, 0, SV, HH),                 # spine
            R(0, 0, W, SH)]                  # waist on the baseline


def ain_mouth(sp):
    """Head of medial / final ain: a compact closed box with a T-shaped counter (the mouth),
    as in square Kufic. Returns (shapes, width, height)."""
    SV, SH = sp.SV, sp.SH
    W = max(330, 2 * SV + 150)
    H = sp.HH                                  # top on the head line
    inner = H - 2 * SH
    ch, s_w = round(inner * 0.45), 64          # bar of the T, width of its stem
    c = W / 2
    counter = R(SV, H - SH - ch, W - SV, H - SH).union(R(c - s_w / 2, SH, c + s_w / 2, H - SH))
    return [R(0, 0, W, H).difference(counter)], W, H


def ain_bowl(sp, w):
    """Bowl below the baseline: spine on the left, floor, short upturned tip on the right."""
    SV, SH, DJ = sp.SV, sp.SH, sp.DJ
    return [R(0, DJ, SV, SH), R(0, DJ, w, DJ + SH), R(w - SV, DJ, w, sp.DS)]


def ain(sp, form, nd=0):
    """Square ain. Initial: open head (cup + horn). Medial: the T-mouth box on the line.
    Isolated / final: the open head (isolated) or the T-mouth box (final) set to the right of a
    bowl, the waist running left into the bowl's spine."""
    SV, SH, HH = sp.SV, sp.SH, sp.HH
    o = AIN_ISO_OFF
    if form == "init":
        W = AIN_W
        sh, hx, top = ain_open(sp, W), 0, HH + 80
    elif form == "medi":
        sh, W, top = ain_mouth(sp)
        sh = sh + [R(0, 0, W, SH)]
        hx = 0
    else:
        if form == "isol":
            head, W, top = ain_open(sp, AIN_W), AIN_W, HH + 80
        else:
            head, W, top = ain_mouth(sp)
        hx = o
        W = o + W
        sh = shift(head, o) + [R(0, 0, W, SH)] + ain_bowl(sp, W)
    if nd:
        lift = 40 if top == HH + 80 else 0       # the horn leaves room on the left of the dot
        sh += dots(sp, nd, W - (W - hx) / 2, top + sp.DA - lift, True)
    return assemble(sp, sh, W, form, W - (W - hx) / 2)


# ------------------------------------------------------------------ FEH / QAF
HEAD_W, HEAD_H = 330, 350          # top on the head line


def head_box(sp, x, y=0, w=HEAD_W, h=HEAD_H):
    """Loop head sitting on the baseline; small counter in its upper part."""
    SV, SH = sp.SV, sp.SH
    cy0 = y + SH
    cy1 = y + h - SH
    return [R(x, y, x + w, cy0), R(x, cy1, x + w, y + h), R(x, y, x + SV, y + h), R(x + w - SV, y, x + w, y + h)]


def feh_qaf(sp, form, nd=1, qaf=False):
    SV, SH, T = sp.SV, sp.SH, sp.T
    if form in ("init", "medi"):
        sh = head_box(sp, 0)
        bw, lx = HEAD_W, 0
    elif not qaf:
        B = 430
        sh = [R(0, 0, B + HEAD_W, SH), R(0, 0, SV, T)] + head_box(sp, B)
        bw, lx = B + HEAD_W, B
    else:
        B = 300
        bw = B + HEAD_W
        lx = B
        sh = head_box(sp, B) + [R(bw - SV, sp.DB, bw, SH), R(0, sp.DB, bw, sp.DB + SH), R(0, sp.DB, SV, 140)]
    cx = lx + HEAD_W / 2
    sh += dots(sp, nd, cx, HEAD_H + sp.DA, True)
    return assemble(sp, sh, bw, form, cx)


# ------------------------------------------------------------------ KAF / GAF
KAF_ARM = 280      # arm reach right of the stem (also the join run in medial / final)
KAF_FOOT = 560     # baseline run from the tooth to the stem in final / isolated


def kaf(sp, form, gaf=False, arabic=False):
    """Persian keheh / gaf: a tall stem with a flat arm reaching right from its top.
    Final / isolated forms run out to the left on the baseline and end in a tooth.
    Gaf lowers the arm and adds a second, shorter bar above it."""
    SV, SH, A, T = sp.SV, sp.SH, sp.A, sp.T
    gap = 75
    Hk = A if not gaf else A - SH - gap        # top of the arm
    arm = KAF_ARM
    sh = []
    if form in ("init", "medi"):
        sx = 0
    else:
        sx = KAF_FOOT - SV
        sh += [R(0, 0, SV, T)]                  # tooth at the end
    bw = sx + SV + arm
    sh += [R(sx, 0, sx + SV, Hk),               # stem
           R(sx, Hk - SH, bw, Hk)]              # arm
    # baseline: under the arm only when a letter joins from the right
    sh.append(R(0, 0, bw if form in ("medi", "fina") else sx + SV, SH))
    if gaf:
        sh.append(R(sx, A - SH, sx + SV + round(arm * 0.6), A))
    if arabic and form in ("isol", "fina"):
        sh += hamza(sp, sx + SV + arm / 2, SH + 70, 0.8)   # Arabic kaf: small hamza under the arm
    return assemble(sp, sh, bw, form, sx + SV / 2 + arm / 2)


def lam(sp, form):
    SV, SH, A = sp.SV, sp.SH, sp.A
    if form in ("init", "medi"):
        return assemble(sp, [R(0, 0, sp.AW, A)], sp.AW, form)
    bw = 560
    sh = deep_bowl(sp, bw, sp.DB, 140, right_drop=False) + [R(bw - sp.AW, sp.DB, bw, A)]
    return assemble(sp, sh, bw, form, bw - sp.AW / 2)


def lamalef(sp, form, var=None):
    SV, SH, A = sp.SV, sp.SH, sp.A
    bw = 460
    top = A
    if var == "madda":
        top = A - 150
    elif var == "hamza_above":
        top = A - hamza_h(sp, 0.9) - 50
    s, w = diag(sp, 0, top, bw - sp.AW - 70, 0, 1.05)
    sh = [s, R(bw - sp.AW - 70 - w, 0, bw, SH), R(bw - sp.AW, 0, bw, A)]
    cx = w / 2 + 10
    if var == "madda":
        sh += madda(sp, cx + 40, top + 45)
    elif var == "hamza_above":
        sh += hamza(sp, cx + 30, top + 50, 0.9)
    elif var == "hamza_below":
        sh += hamza(sp, bw - sp.AW - 70 - w / 2, -50 - hamza_h(sp, 0.9), 0.9)
    return assemble(sp, sh, bw, form)


# ------------------------------------------------------------------ MEEM
def meem(sp, form):
    """Medial / initial: a box straddling the baseline, its top on the teeth line.
    Final / isolated: the same box sits on the baseline (top on the head line), a short run
    leads left and the tail drops. The box is the same height in every weight and its counter
    is square."""
    SV, SH = sp.SV, sp.SH
    Hm = sp.HH
    W = 2 * SV + (Hm - 2 * SH)
    if form in ("init", "medi"):
        sh = ring(0, sp.T - Hm, W, Hm, SV, SH)
        return assemble(sp, sh, W, form)
    run = 170
    sh = ring(run, 0, W, Hm, SV, SH) + [R(0, 0, run + SV, SH), R(0, sp.DJ, SV, SH)]
    return assemble(sp, sh, run + W, form, run + W / 2)


# ------------------------------------------------------------------ HEH / TEH MARBUTA / WAW
def heh_dims(sp):
    """Box of ه / و: top on the dal line in every weight, square counter."""
    H = sp.DZ
    return 2 * sp.SV + (H - 2 * sp.SH), H


def heh_box(sp, x):
    W, H = heh_dims(sp)
    return ring(x, 0, W, H, sp.SV, sp.SH)


def heh(sp, form, nd=0, hamza_above=False):
    SV, SH = sp.SV, sp.SH
    if form == "init":
        H = sp.HH                       # top on the head line
        cw = round((H - 2 * SH) / 2)    # each counter half as wide as it is tall, in every weight
        W = 3 * SV + 2 * cw
        sh = ring(0, 0, W, H, SV, SH) + [R(SV + cw, 0, 2 * SV + cw, H)]
        top = H
    elif form == "medi":
        W, y1 = heh_dims(sp)            # counters match the isolated heh's counter
        y0 = -(y1 - SH)
        sh = ring(0, y0, W, y1 - y0, SV, SH) + [R(0, 0, W, SH)]
        top = y1
    else:
        W, top = heh_dims(sp)
        sh = heh_box(sp, 0)
    if nd:
        sh += dots(sp, nd, W / 2, top + sp.DA, True)
    if hamza_above:
        sh += hamza(sp, W / 2 + 10, top + 60, 0.9)
    return assemble(sp, sh, W, form)


def waw(sp, form, hamza_above=False):
    """Waw: a square head on the baseline; its right side carries on down below the baseline
    and turns into a foot running left (the same drop and foot as reh) - a square '9'."""
    SV, SH, DR = sp.SV, sp.SH, sp.DR
    W, H = heh_dims(sp)
    run = sp.GT                 # foot reaching left past the head; ends where a tucked-in letter begins
    bw = run + W
    sh = ring(run, 0, W, H, SV, SH) + [R(bw - SV, DR, bw, H), R(0, DR, bw, DR + SH)]
    if hamza_above:
        sh += hamza(sp, run + W / 2 + 10, H + 60, 0.9)
    return assemble(sp, sh, bw, form, run + W / 2)


# ------------------------------------------------------------------ ALEF
def alef(sp, form, var=None):
    A, AW = sp.A, sp.AW
    sh = []
    cx = AW / 2
    top = A
    if var == "madda":
        top = A - 150
        sh += madda(sp, cx, top + 45)
    elif var == "hamza_above":
        top = A - hamza_h(sp, 0.9) - 50
        sh += hamza(sp, cx + 10, top + 50, 0.9)
    if var == "hamza_below":
        sh += hamza(sp, cx + 10, -50 - hamza_h(sp, 0.9), 0.9)
    sh.append(R(0, 0, AW, top))
    sb = 75 if var not in ("madda",) else 120
    return assemble(sp, sh, AW, form, cx, sb_l=sb, sb_r=sb)
