"""Digits, punctuation and combining marks for Hashareh."""
import math
from design import R, P, ring, Glyph, hamza, shift, mirror, mark_loop, mark_tail

AXIS = 250          # centre line of the hyphen, dashes and math signs


def _g(sp, shapes, ink_w, sb=70):
    return Glyph(shift(shapes, sb), ink_w + 2 * sb, sb + ink_w / 2)


def V_shape(sp, W, N, invert=False):
    DS = sp.SV
    w1 = DS * 1.25
    c = W / 2
    fb = DS * 0.55          # half width of the flat at the point
    if not invert:
        return [P((0, N), (w1, N), (c + fb, 0), (c - fb, 0)), P((W - w1, N), (W, N), (c + fb, 0), (c - fb, 0))]
    return [P((0, 0), (w1, 0), (c + fb, N), (c - fb, N)), P((W - w1, 0), (W, 0), (c + fb, N), (c - fb, N))]


# ------------------------------------------------------------------ Persian digits (after ۱۳۴۷ in the emblem)
def fa_digit(sp, n):
    SV, SH, N = sp.SV, sp.SH, sp.N
    DS = SV                      # digit stem
    AB = SH                      # digit arm
    if n == 0:
        d = round(sp.DOT * 1.15)
        c = 290                          # same centre in every weight
        return _g(sp, [R(0, c - d / 2, d, c + d / 2)], d, 110)
    if n == 1:
        return _g(sp, [R(0, 0, DS, N)], DS, 110)
    bar_top = N - round(0.29 * N)          # teeth rise ~190 units above the bar
    bar_bot = bar_top - AB
    if n == 2:
        W = 420
        return _g(sp, [R(0, 0, DS, N), R(0, bar_bot, W, bar_top), R(W - SV, bar_bot, W, N)], W)
    if n == 3:
        W = 590
        p2 = DS + (W - DS - 2 * SV) / 2 - 5
        return _g(sp, [R(0, 0, DS, N), R(0, bar_bot, W, bar_top),
                       R(p2, bar_bot, p2 + SV, N - 40), R(W - SV, bar_bot, W, N)], W)
    if n == 4:
        # emblem ۴: full stem + a ⊏ to its right whose lower arm runs back into the stem
        W = 470
        sx0 = DS + 100                    # spine of the ⊏, separated from the stem
        ta = (N - AB, N)                 # upper arm, flush with the top of the stem
        la = (N - 370, N - 370 + AB)     # lower arm
        return _g(sp, [R(0, 0, DS, N),
                       R(sx0, ta[0], W, ta[1]),
                       R(sx0, la[0], sx0 + SV, ta[1]),
                       R(0, la[0], W, la[1])], W)
    if n == 5:
        # upside-down heart: pointed top, flat bottom, full digit height
        W, H = 460, N
        out = P((0, 0), (W, 0), (W, H * 0.56), (W / 2, H), (0, H * 0.56))
        inner = out.buffer(-DS, join_style=2)
        return _g(sp, [out.difference(inner)], W)
    if n == 6:
        W = 430
        return _g(sp, [R(0, N - AB, W, N), R(W - DS, 0, W, N), R(0, N - AB - 120, DS, N)], W)
    if n == 7:
        return _g(sp, V_shape(sp, 475, N), 475)
    if n == 8:
        return _g(sp, V_shape(sp, 475, N, True), 475)
    if n == 9:
        W, H = 430, 360
        return _g(sp, ring(0, N - H, W, H, DS, AB) + [R(W - DS, 0, W, N)], W)


def ar_digit(sp, n):
    SV, SH, N = sp.SV, sp.SH, sp.N
    DS = SV
    AB = SH
    if n == 4:
        W = 420
        return _g(sp, [R(0, 0, DS, N), R(0, N - AB, W, N), R(0, (N - AB) / 2, W - 60, (N + AB) / 2), R(0, 0, W, AB)], W)
    if n == 5:
        W = 440
        return _g(sp, ring(0, 0, W, N, DS, AB), W)     # full digit height
    if n == 6:
        W = 430
        return _g(sp, [R(0, N - AB, W, N), R(W - DS, 0, W, N)], W)


# ------------------------------------------------------------------ Latin digits (square segment build)
SEG = {0: "abcdef", 2: "abged", 3: "abgcd", 5: "afgcd", 6: "afgedc", 8: "abcdefg", 9: "abcdfg"}


def la_digit(sp, n):
    SV, SH, N = sp.SV, sp.SH, sp.N
    W = 2 * SV + 190
    m = N / 2
    seg = {"a": R(0, N - SH, W, N), "b": R(W - SV, m, W, N), "c": R(W - SV, 0, W, m),
           "d": R(0, 0, W, SH), "e": R(0, 0, SV, m), "f": R(0, m, SV, N), "g": R(0, m - SH / 2, W, m + SH / 2)}
    if n == 1:
        return _g(sp, [R(W - SV, 0, W, N), R(W - SV - 130, N - SH, W, N)], W)
    if n == 4:
        return _g(sp, [R(0, m - SH / 2, SV, N), R(0, m - SH / 2, W, m + SH / 2), R(W - SV, 0, W, N)], W)
    if n == 7:
        return _g(sp, [seg["a"], R(W - SV, 0, W, N)], W)
    return _g(sp, [seg[k] for k in SEG[n]], W)


# ------------------------------------------------------------------ punctuation
def chevron(x, y0, w, h, t, left):
    """Monoline chevron, stroke t, w x h, flat ends; the point faces left (left=True) or right."""
    k = t / math.cos(math.atan2(h / 2, w))      # vertical thickness of each arm
    n = 2 * w * k / h                           # inner corner, keeps the arms parallel
    yc = y0 + h / 2
    if left:
        return [P((x, yc), (x + w, y0 + h), (x + w, y0 + h - k), (x + n, yc), (x + w, y0 + k), (x + w, y0))]
    return [P((x + w, yc), (x, y0 + h), (x, y0 + h - k), (x + w - n, yc), (x, y0 + k), (x, y0))]


def punct(sp):
    SV, SH, N, T = sp.SV, sp.SH, sp.N, sp.T
    d = sp.DOT
    out = {}
    DZ = sp.DZ                  # upper dot of : ; tops out on the dal line
    out["period"] = _g(sp, [R(0, 0, d, d)], d, 80)
    out["colon"] = _g(sp, [R(0, 0, d, d), R(0, DZ - d, d, DZ)], d, 80)
    out["comma"] = _g(sp, [R(0, 0, d, d), R(d - SV * 0.55, -170, d, d)], d, 80)
    out["semicolon"] = _g(sp, [R(0, DZ - d, d, DZ), R(0, 0, d, d), R(d - SV * 0.55, -170, d, d)], d, 80)
    out["uni060C"] = _g(sp, [R(0, 0, d, d), R(0, 0, SV * 0.55, d + 160)], d, 80)
    out["uni061B"] = _g(sp, [R(0, 0, d, d), R(0, 0, SV * 0.55, d + 160), R(0, T + 140, d, T + 140 + d)], d, 80)
    out["exclam"] = _g(sp, [R(0, 0, d, d), R((d - SV) / 2, d + 80, (d + SV) / 2, N)], d, 80)
    W = 2 * SV + 170
    q = [R(0, N - SH, W, N), R(W - SV, N - 2.8 * SH, W, N), R((W - SV) / 2, N - 2.8 * SH, W, N - 1.8 * SH),
         R((W - SV) / 2, d + 80, (W + SV) / 2, N - 1.8 * SH), R((W - d) / 2, 0, (W + d) / 2, d)]
    out["question"] = _g(sp, q, W)
    out["uni061F"] = _g(sp, mirror(q, W / 2), W)
    out["hyphen"] = _g(sp, [R(0, AXIS - SH / 2, 260, AXIS + SH / 2)], 260, 50)
    out["endash"] = _g(sp, [R(0, AXIS - SH / 2, 480, AXIS + SH / 2)], 480, 50)
    out["emdash"] = _g(sp, [R(0, AXIS - SH / 2, 920, AXIS + SH / 2)], 920, 40)
    out["underscore"] = _g(sp, [R(0, -160, 520, -160 + SH)], 520, 0)
    out["slash"] = _g(sp, [P((0, -110), (1.25 * SV, -110), (360, N + 60), (360 - 1.25 * SV, N + 60))], 360, 30)
    out["backslash"] = _g(sp, [P((360 - 1.25 * SV, -110), (360, -110), (1.25 * SV, N + 60), (0, N + 60))], 360, 30)
    bw = 180
    yb, yt = -170, N + 80
    pk = 70
    reach, bend = 110, 90           # the ends turn out by the same amount in every weight
    pw = pk + SV + reach
    out["parenleft"] = _g(sp, [R(pk, yb + bend, pk + SV, yt - bend),
                               P((pk, yt - bend), (pk + SV, yt - bend), (pw, yt), (pw - SV * 1.2, yt)),
                               P((pk, yb + bend), (pk + SV, yb + bend), (pw, yb), (pw - SV * 1.2, yb))], pw, 60)
    gl = out["parenleft"]
    out["parenright"] = Glyph(mirror(gl.shapes, gl.adv / 2), gl.adv)
    out["bracketleft"] = _g(sp, [R(0, yb, SV, yt), R(0, yb, bw + 50, yb + SH), R(0, yt - SH, bw + 50, yt)], bw + 50, 70)
    out["bracketright"] = _g(sp, [R(bw + 50 - SV, yb, bw + 50, yt), R(0, yb, bw + 50, yb + SH), R(0, yt - SH, bw + 50, yt)], bw + 50, 70)
    out["plus"] = _g(sp, [R(0, AXIS - SH / 2, 440, AXIS + SH / 2), R(220 - SV / 2, 30, 220 + SV / 2, 470)], 440)
    out["equal"] = _g(sp, [R(0, 130, 440, 130 + SH), R(0, 370 - SH, 440, 370)], 440)
    out["less"] = _g(sp, chevron(0, AXIS - 200, 380, 400, 0.8 * SV, True), 380)
    out["greater"] = _g(sp, chevron(0, AXIS - 200, 380, 400, 0.8 * SV, False), 380)

    def chev(x, left):
        return chevron(x, 40, 220, 370, 0.7 * SV, left)
    out["guillemotleft"] = _g(sp, chev(0, True) + chev(240, True), 460, 50)
    out["guillemotright"] = _g(sp, chev(0, False) + chev(240, False), 460, 50)
    out["quotesingle"] = _g(sp, [R(0, N - 250, SV, N)], SV, 70)
    out["quotedbl"] = _g(sp, [R(0, N - 250, SV, N), R(SV + 90, N - 250, 2 * SV + 90, N)], 2 * SV + 90, 70)
    out["ellipsis"] = _g(sp, [R(0, 0, d, d), R(d + 100, 0, 2 * d + 100, d), R(2 * d + 200, 0, 3 * d + 200, d)], 3 * d + 200, 80)
    pr = [R(0, N - d, d, N), R(380 - d, 0, 380, d), P((0, 0), (1.25 * SV, 0), (380, N), (380 - 1.25 * SV, N))]
    out["percent"] = _g(sp, pr, 380)
    out["uni066B"] = _g(sp, [P((0, -130), (SV * 0.95, -130), (SV * 1.7, 120), (SV * 0.75, 120))], SV * 1.7, 70)
    out["uni066C"] = _g(sp, [P((0, 290), (SV * 0.95, 290), (SV * 1.7, 540), (SV * 0.75, 540))], SV * 1.7, 70)
    # the emblem's eight-spoke asterisk
    c, r, w = 205, 205, SV * 0.42
    star = []
    for k in range(4):
        a = math.pi * k / 4
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy * w / 2, dx * w / 2
        star.append(P((c - r * dx + px, 300 - r * dy + py), (c + r * dx + px, 300 + r * dy + py),
                      (c + r * dx - px, 300 + r * dy - py), (c - r * dx - px, 300 - r * dy - py)))
    out["asterisk"] = _g(sp, star, 2 * c, 50)
    return out


# ------------------------------------------------------------------ combining marks (zero width, anchor at 0,0)
def marks(sp):
    t = max(36, sp.t)
    m = {}
    def fat(y):
        return P((-95, y), (95, y + 60), (95, y + 60 + t), (-95, y + t))
    m["uni064E"] = ([fat(0)], "top")
    m["uni0650"] = ([fat(-60 - t)], "bot")
    m["uni064B"] = ([fat(0), fat(t + 50)], "top")
    m["uni064D"] = ([fat(-60 - t), fat(-60 - 2 * t - 50)], "bot")
    _, L = mark_loop(sp)

    def damma(x):
        x0 = x - L / 2
        tail, yb = mark_tail(sp, x0, 0)
        return ring(x0, yb, L, L, t) + tail
    m["uni064F"] = (damma(10), "top")
    m["uni064C"] = (damma(-L / 2 - 25) + damma(L / 2 + 50), "top")
    m["uni0652"] = (ring(-L / 2, 0, L, L, t), "top")
    g = max(50, round(t * 0.8))          # open gaps between the three teeth of the shadda
    sw = 3 * t + 2 * g
    m["uni0651"] = ([R(-sw / 2, 0, sw / 2, t)] + [R(-sw / 2 + k * (t + g), 0, -sw / 2 + k * (t + g) + t, 115) for k in range(3)], "top")
    m["uni0670"] = ([R(-t / 2, 0, t / 2, 160)], "top")
    m["uni0654"] = (hamza(sp, 0, 0, 0.9), "top")
    m["uni0655"] = (shift(hamza(sp, 0, 0, 0.9), 0, -170), "bot")
    return m
