"""Type specimen for Hashareh.

    python specimen.py ../fonts ..

writes, into the second folder:
    Hashareh-specimen.html   self-contained specimen (fonts embedded)
    Hashareh-specimen.png    the same page as an image (needs Microsoft Edge or Google Chrome)
Needs: pillow (for the PNG).
"""
import base64, html, os, shutil, subprocess, sys, tempfile, time

ZWJ = "‍"
WEIGHTS = ("Light", "Medium", "Bold")

# letter, name, joins on the left?, (word with letter at start, in the middle, at the end)
LETTERS = [
    ("ا", "alef", False, ("اسب", "باران", "دریا")),
    ("ب", "be", True, ("باران", "صبح", "کتاب")),
    ("پ", "pe", True, ("پدر", "سپید", "چپ")),
    ("ت", "te", True, ("تابستان", "ستاره", "دوست")),
    ("ث", "se", True, ("ثروت", "مثل", "میراث")),
    ("ج", "jim", True, ("جنگل", "انجمن", "کاج")),
    ("چ", "che", True, ("چراغ", "کوچه", "پیچ")),
    ("ح", "he", True, ("حشره", "محمد", "صبح")),
    ("خ", "khe", True, ("خورشید", "سخن", "کاخ")),
    ("د", "dal", False, ("دریا", "مادر", "سفید")),
    ("ذ", "zal", False, ("ذرت", "گذر", "کاغذ")),
    ("ر", "re", False, ("روز", "مردم", "شهر")),
    ("ز", "ze", False, ("زمین", "سبزه", "سبز")),
    ("ژ", "zhe", False, ("ژاله", "مژده", "دژ")),
    ("س", "sin", True, ("سلام", "آسمان", "درس")),
    ("ش", "shin", True, ("شب", "آشنا", "آتش")),
    ("ص", "sad", True, ("صبح", "قصه", "رقص")),
    ("ض", "zad", True, ("ضرب", "حضور", "حوض")),
    ("ط", "ta", True, ("طبیعت", "قطره", "خط")),
    ("ظ", "za", True, ("ظرف", "نظر", "حافظ")),
    ("ع", "eyn", True, ("عشق", "طبیعت", "شمع")),
    ("غ", "gheyn", True, ("غروب", "مغز", "باغ")),
    ("ف", "fe", True, ("فردا", "سفر", "برف")),
    ("ق", "qaf", True, ("قلم", "عقاب", "عشق")),
    ("ک", "kaf", True, ("کتاب", "مکتب", "بانک")),
    ("گ", "gaf", True, ("گل", "انگور", "سنگ")),
    ("ل", "lam", True, ("لب", "گلستان", "گل")),
    ("م", "mim", True, ("ماه", "انجمن", "مردم")),
    ("ن", "nun", True, ("نان", "پنجره", "ایران")),
    ("و", "vav", False, ("وطن", "روز", "دو")),
    ("ه", "he", True, ("هوا", "شهر", "حشره")),
    ("ی", "ye", True, ("یاد", "ایران", "شادی")),
]
EXTRA = "آ أ إ ء ئ ؤ ة ۀ ك ي ى"

TEXTS = [
    "حشره‌ها بیش از نیمی از گونه‌های جانوری شناخته‌شده‌ی زمین را تشکیل می‌دهند. "
    "از پروانه‌های رنگارنگ تا زنبورهای عسل، دنیای آن‌ها پر از شگفتی است.",
    "صبح زود، ژاله روی گل‌های باغچه نشسته بود و باغبان پیر مثل هر روز، کنار حوض و زیر سایه‌ی درخت، "
    "با ذوق از جلوه‌ی ظریف طبیعت عکس می‌گرفت.",
    "باغ‌های سبز، کوه‌های بلند و دشت‌های گسترده؛ ایران سرزمینی است با طبیعتی گوناگون، "
    "از جنگل‌های شمال تا کویر مرکزی و ساحل‌های گرم جنوب.",
]

CSS = """
:root { --bg:#efe9dc; --ink:#151515; --mut:#776f62; --acc:#2a9d97; --card:#f6f2e9; --line:#d8cfbd; }
* { box-sizing:border-box; }
html { background:var(--bg); }
body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }
.wrap { max-width:1300px; margin:0 auto; padding:56px 40px 72px; }
.fa { direction:rtl; font-family:"HasharehBold"; }
.L { font-family:"HasharehLight"; } .M { font-family:"HasharehMedium"; } .B { font-family:"HasharehBold"; }
header { display:flex; justify-content:space-between; align-items:flex-start; gap:24px; flex-wrap:wrap; }
.brand { color:var(--acc); font-weight:800; font-size:26px; letter-spacing:.08em; }
.meta { color:var(--mut); font-weight:600; font-size:14px; margin-top:4px; }
.hero { font-size:190px; line-height:1.25; text-align:right; }
.rule { height:5px; background:var(--acc); margin:22px 0 36px; border-radius:2px; }
h2 { font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--mut); margin:56px 0 18px; display:flex; justify-content:space-between; }
h2 .fa { font-family:"HasharehMedium"; font-size:20px; letter-spacing:0; text-transform:none; color:var(--ink); }
.wline { display:grid; grid-template-columns:110px 1fr; align-items:center; border-top:1px solid var(--line); }
.wline .lab { color:var(--mut); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.wline .fa { font-size:76px; line-height:1.6; text-align:right; white-space:nowrap; overflow:hidden; }
.grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; direction:rtl; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px 12px; direction:ltr; }
.card .top { display:flex; justify-content:space-between; align-items:baseline; color:var(--mut); font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; }
.card .big { font-family:"HasharehBold"; font-size:42px; color:var(--acc); line-height:1; direction:rtl; }
.forms { display:grid; grid-template-columns:repeat(4,1fr); direction:rtl; margin:10px 0 4px; text-align:center; }
.forms div { font-family:"HasharehBold"; font-size:44px; line-height:1.7; }
.forms span { display:block; font:600 9.5px/1 system-ui,sans-serif; color:var(--mut); letter-spacing:.06em; text-transform:uppercase; }
.forms .na { color:#c9bfae; }
.words { display:grid; grid-template-columns:repeat(3,1fr); direction:rtl; text-align:center; border-top:1px solid var(--line); padding-top:6px; }
.words div { font-family:"HasharehMedium"; font-size:23px; line-height:1.9; }
.words span { display:block; font:600 9.5px/1 system-ui,sans-serif; color:var(--mut); letter-spacing:.06em; text-transform:uppercase; }
.row { display:flex; flex-wrap:wrap; gap:10px 34px; direction:rtl; font-size:64px; line-height:1.7; }
.panel { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px 26px; }
.panel + .panel { margin-top:14px; }
.panel .lab { color:var(--mut); font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.wf div { display:grid; grid-template-columns:70px 1fr; align-items:baseline; }
.wf .fa { white-space:nowrap; overflow:hidden; text-align:right; line-height:1.75; }
.cols { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
.cols .panel { margin-top:0; }
.para { font-size:24px; line-height:2.1; text-align:right; margin:8px 0 4px; }
.heads > div { display:grid; grid-template-columns:110px 1fr; align-items:center; }
.heads .fa { font-size:58px; line-height:1.6; text-align:right; }
footer { margin-top:56px; color:var(--mut); font-size:13px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; border-top:1px solid var(--line); padding-top:16px; }
@media (max-width:1000px) { .grid { grid-template-columns:repeat(2,1fr); } .cols { grid-template-columns:1fr; } .hero { font-size:110px; } }
@media (max-width:560px) { .wrap { padding:32px 16px; } .grid { grid-template-columns:1fr; } .hero { font-size:76px; } .wline .fa { font-size:40px; } .row { font-size:44px; } }
"""


def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()


def esc(t):
    return html.escape(t)


def specimen_html(fontdir, out):
    css = CSS
    for w in WEIGHTS:
        css += (f'@font-face {{ font-family:"Hashareh{w}"; '
                f'src:url(data:font/woff2;base64,{b64(os.path.join(fontdir, f"Hashareh-{w}.woff2"))}) format("woff2"); }}\n')
    H = [f"<!doctype html><html lang='fa'><head><meta charset='utf-8'>"
         f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>Hashareh Specimen</title><style>{css}</style></head><body><div class='wrap'>"]
    H.append("<header><div><div class='brand'>HASHAREH</div><div class='meta'>Light · Medium · Bold &nbsp;—&nbsp; v1.000 &nbsp;—&nbsp; MIT License</div>"
             "<div class='meta' style='font-weight:400;max-width:520px;margin-top:10px'>A geometric square Persian display face, "
             "rebuilt from the lettering of the 1347 / 1968 emblem of the Entomological Society of Iran.</div></div>"
             "<div class='fa hero'>حشره</div></header><div class='rule'></div>")

    H.append("<h2><span>Weights</span><span class='fa'>وزن‌ها</span></h2>")
    for w in WEIGHTS:
        H.append(f"<div class='wline'><div class='lab'>{w}</div><div class='fa {w[0]}'>انجمن حشره‌شناسان ایران ۱۳۴۷</div></div>")

    H.append("<h2><span>Letters · four forms · in words</span>"
             "<span class='fa'>حروف در جایگاه‌های گوناگون</span></h2><div class='grid'>")
    for ch, name, dual, words in LETTERS:
        cells = [(ch, "isolated"), (ch + ZWJ if dual else None, "initial"),
                 (ZWJ + ch + ZWJ if dual else None, "medial"), (ZWJ + ch, "final")]
        f = "".join(f"<div class='{'na' if t is None else ''}'>{esc(t) if t else '–'}<span>{lab}</span></div>" for t, lab in cells)
        wd = "".join(f"<div>{esc(wd)}<span>{lab}</span></div>" for wd, lab in zip(words, ("start", "middle", "end")))
        H.append(f"<div class='card'><div class='top'><span>{name}</span><span class='big'>{ch}</span></div>"
                 f"<div class='forms'>{f}</div><div class='words'>{wd}</div></div>")
    H.append("</div>")

    H.append("<h2><span>Additional letters · lam-alef · marks</span><span class='fa'>حروف دیگر و نشانه‌ها</span></h2>")
    H.append(f"<div class='panel'><div class='lab'>Arabic and hamza forms</div><div class='row fa'>{esc(EXTRA)}</div></div>")
    H.append("<div class='panel'><div class='lab'>Lam-alef ligatures</div><div class='row fa'>لا  لآ  لأ  لإ  &nbsp; سلام  فلات  کلاس</div></div>")
    H.append("<div class='panel'><div class='lab'>Harakat</div><div class='row fa'>بَ  بِ  بُ  بً  بٍ  بٌ  بّ  بْ  &nbsp; حَتْماً  مُدَرِّس  کِتاب</div></div>")

    H.append("<h2><span>Numerals &amp; punctuation</span><span class='fa'>رقم‌ها و علامت‌ها</span></h2>")
    H.append("<div class='panel'><div class='lab'>Persian digits</div><div class='row fa'>۰ ۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹ &nbsp; ۱۳۴۷ &nbsp; ۱۴۰۵</div></div>")
    H.append("<div class='panel'><div class='lab'>Arabic-Indic &amp; Latin digits</div><div class='row fa' style='font-size:50px'>٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ &nbsp; 0 1 2 3 4 5 6 7 8 9</div></div>")
    H.append("<div class='panel'><div class='lab'>Punctuation</div><div class='row fa'>، ؛ ؟ ! . : « » ( ) [ ] - – — ٪ ٫ ٬ * / + =</div></div>")

    H.append("<h2><span>Sizes</span><span class='fa'>اندازه‌ها</span></h2><div class='panel wf'>")
    for px in (96, 72, 54, 40, 30, 22, 16, 12):
        H.append(f"<div><span class='lab'>{px} px</span><div class='fa M' style='font-size:{px}px'>چگونه پژوهشگران ظرافت طبیعت را در عکس‌ها و یادداشت‌هایشان ثبت کردند</div></div>")
    H.append("</div>")

    H.append("<h2><span>Headlines</span><span class='fa'>تیترها</span></h2><div class='panel heads'>")
    for w, t in (("Bold", "باغ‌های سبز ایران"), ("Medium", "سفر به دل کویر"), ("Light", "شب‌های پرستاره")):
        H.append(f"<div><span class='lab'>{w}</span><div class='fa {w[0]}'>{esc(t)}</div></div>")
    H.append("</div>")

    H.append("<h2><span>Text · 24 px</span><span class='fa'>متن</span></h2><div class='cols'>")
    for w, t in zip(WEIGHTS, TEXTS):
        H.append(f"<div class='panel'><div class='lab'>{w}</div><p class='fa para {w[0]}'>{esc(t)}</p></div>")
    H.append("</div>")

    H.append("<footer><span>Hashareh v1.000 · Light 300 · Medium 500 · Bold 700 · MIT License</span>"
             "<span>Glyphs: Persian & Arabic letters with all contextual forms, lam-alef, harakat, three digit sets, punctuation</span></footer>")
    H.append("</div></body></html>")
    open(out, "w", encoding="utf-8").write("\n".join(H))
    print("wrote", out)


# ------------------------------------------------------------------ PNG of the specimen page
def find_browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(n):
            return shutil.which(n)
    return None


def specimen_png(html_path, out, width=1355):
    """Full-page screenshot of the specimen, the empty page bottom trimmed."""
    from PIL import Image
    browser = find_browser()
    if not browser:
        print("no Edge / Chrome found: skipped", out)
        return
    work = tempfile.mkdtemp()
    tmp = os.path.join(work, "shot.png")
    url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--user-data-dir={os.path.join(work, 'profile')}", f"--window-size={width},12000",
                    "--virtual-time-budget=8000", f"--screenshot={tmp}", url],
                   capture_output=True, timeout=180)
    for _ in range(120):                   # Edge hands the work to a background process: wait for it
        if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            time.sleep(1)
            break
        time.sleep(0.5)
    im = Image.open(tmp).convert("RGB")
    bg = im.getpixel((2, im.height - 2))
    px = im.load()
    y = im.height - 1
    while y > 0 and all(px[x, y] == bg for x in range(0, im.width, 4)):
        y -= 1
    im.crop((0, 0, im.width, min(im.height, y + 40))).save(out, optimize=True)
    print("wrote", out)


def main(fontdir, outdir):
    page = os.path.join(outdir, "Hashareh-specimen.html")
    specimen_html(fontdir, page)
    specimen_png(page, os.path.join(outdir, "Hashareh-specimen.png"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../fonts", sys.argv[2] if len(sys.argv) > 2 else "..")
