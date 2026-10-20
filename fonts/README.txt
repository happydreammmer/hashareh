Hashareh (حشره) — Persian display typeface · version 1.000
==========================================================

A geometric square Persian face rebuilt from the lettering of the 1968 (1347)
emblem of the Entomological Society of Iran: monoline strokes, a flat joining
baseline, square teeth and square dots.

Weights: Light (300), Medium (500), Bold (700). Bold matches the emblem's weight.

Free and open source under the MIT License (see ../LICENSE).
Copyright (c) 2026 Hatef Mohammad Ali (Kouzehchi).

Files
  Hashareh-Light / -Medium / -Bold .ttf    install these on Windows, macOS, Linux
  Hashareh-Light / -Medium / -Bold .otf    PostScript (CFF) version, for design apps
  Hashareh-Light / -Medium / -Bold .woff2  for websites
  ../Hashareh-specimen.html / .png         type specimen
  ../font-vs-emblem.png                    the emblem's lettering above the font (Bold)
  ../source/                               Python sources that generate the fonts

Install
  Windows : right-click the .ttf files > Install (or "Install for all users")
  macOS   : double-click the .ttf file > Install Font
  Linux   : copy the .ttf files to ~/.local/share/fonts and run fc-cache -f
  Install either the .ttf or the .otf set, not both.
  In apps the family appears as "Hashareh" (Medium as the regular style, plus Bold,
  so Ctrl+B switches between them) and "Hashareh Light". Apps that understand
  typographic families group all three under "Hashareh". The Persian family name is
  حشره (نازک · متوسط · ضخیم).

Web use
  @font-face { font-family: "Hashareh"; font-weight: 300; src: url(Hashareh-Light.woff2) format("woff2"); }
  @font-face { font-family: "Hashareh"; font-weight: 500; src: url(Hashareh-Medium.woff2) format("woff2"); }
  @font-face { font-family: "Hashareh"; font-weight: 700; src: url(Hashareh-Bold.woff2) format("woff2"); }

Design notes
  Heights: every weight shares one set of lines, so letters line up the same way in Light,
  Medium and Bold (units of 1000)
     660  alef, lam, kaf and tah stems, digits
     350  ج ح خ head, ف ق head, ص ض ط ظ loop, م box, ع غ mouth, ی head, initial ه
     300  د ذ, isolated ر ز ژ, ه ة ۀ, head of و
     245  teeth, final ر ز ژ, ن cup, top of medial م, bowl tip of س ص
       0  baseline (joining line)
    −165  foot of ر ز ژ و, floor of ن
    −230  bowl of س ص, tip of the ج ح ع bowl
    −320  bowl of ل ق ی
    −400  bowl of ج ح خ چ ع غ, tail of م

  Spacing after ر ز ژ و ؤ: the next letter tucks in over the foot. Above the baseline it keeps
  the regular gap (as if the foot were not there), nothing comes closer than 55 units, and the
  foot never sticks out past it. After ر ز ژ an alef ends exactly where the foot ends; after و
  the next letter starts exactly where the foot ends. This looks the same in every weight.

  Dots: one size and gap per weight, 85 units from the body. Dots above sit on three rows
  (teeth letters, د ر ز ه, heads). ش has its three dots in one line, as in the emblem.

Version history
  1.000  First public release.

Character set
  - Full Persian alphabet + Arabic ي ك ى ة ء أ إ آ ؤ ئ ۀ
  - Isolated / initial / medial / final forms (OpenType init, medi, fina)
  - Lam-alef ligatures لا لآ لأ لإ (rlig)
  - Kerning after footed letters ر ز ژ و ؤ (kern)
  - Harakat with mark positioning: ـَ ـِ ـُ ـً ـٍ ـٌ ـّ ـْ ـٰ
  - Persian digits ۰–۹, Arabic-Indic ٠–٩, Latin digits 0–9 (square style)
  - Persian punctuation ، ؛ ؟ « » ٪ ٫ ٬ and basic ASCII punctuation
  - ZWNJ (نیم‌فاصله) and ZWJ, kashida ـ
  - Arabic presentation-form code points for apps without text shaping
  Latin letters are not included; apps fall back to another font for them.

Rebuild from source
  pip install fonttools shapely brotli pillow
  cd source
  python build.py ../fonts
  python specimen.py ../fonts ..
  build.py writes the fonts (and features-*.fea, the OpenType feature code, next to them).
  specimen.py writes Hashareh-specimen.html / .png; the PNG needs Google Chrome or
  Microsoft Edge.

Hashareh is an independent typeface inspired by the emblem's lettering. It is not
affiliated with or endorsed by the Entomological Society of Iran.
