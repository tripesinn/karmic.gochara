"""
Génère les assets Google Play Store pour Karmic Gochara :
  - icon_512x512.png    → icône app (512×512)
  - banner_1024x500.png → feature graphic (1024×500)
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

SRC = os.path.join("static", "icons", "icon-512.png")
OUT = "store_assets"
os.makedirs(OUT, exist_ok=True)

GOLD  = (201, 168, 76)
BG    = (10,  10,  8)
WHITE = (232, 228, 216)
DIM   = (138, 134, 120)

# ── 1. ICÔNE 512×512 ─────────────────────────────────────────────────────────

src = Image.open(SRC).convert("RGBA")

icon = Image.new("RGBA", (512, 512), BG + (255,))

# Centrer l'icône source sur fond carré
sw, sh = src.size
scale  = min(512 / sw, 512 / sh)
nw, nh = int(sw * scale), int(sh * scale)
src_r  = src.resize((nw, nh), Image.LANCZOS)
ox, oy = (512 - nw) // 2, (512 - nh) // 2
icon.paste(src_r, (ox, oy), src_r)

# Masque rond (coins arrondis Google Play = cercle complet)
mask = Image.new("L", (512, 512), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 511, 511), fill=255)
icon.putalpha(mask)

icon.save(os.path.join(OUT, "icon_512x512.png"))
print("✓ icon_512x512.png")


# ── 2. BANNER 1024×500 ───────────────────────────────────────────────────────

W, H = 1024, 500
banner = Image.new("RGB", (W, H), BG)
draw   = ImageDraw.Draw(banner)

# --- Fond étoilé ---
import random
random.seed(42)
for _ in range(220):
    x, y = random.randint(0, W), random.randint(0, H)
    r     = random.choice([1, 1, 1, 2])
    alpha = random.randint(60, 200)
    c     = tuple(int(v * alpha / 255) for v in WHITE)
    draw.ellipse((x-r, y-r, x+r, y+r), fill=c)

# --- Icône centrée à gauche ---
ico_size = 280
ico_src  = src.resize((ico_size, ico_size), Image.LANCZOS)
ico_x, ico_y = 80, (H - ico_size) // 2
banner.paste(ico_src, (ico_x, ico_y), ico_src)

# --- Cercle décoratif autour de l'icône ---
cx, cy = ico_x + ico_size // 2, ico_y + ico_size // 2
for radius, width, opacity in [(158, 2, 80), (172, 1, 50)]:
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    d2 = ImageDraw.Draw(overlay)
    c  = GOLD + (opacity,)
    d2.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=c, width=width)
    banner = Image.alpha_composite(banner.convert("RGBA"), overlay).convert("RGB")
    draw   = ImageDraw.Draw(banner)

# --- Texte ---
# Cherche des polices système disponibles
def find_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/Georgia.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    if bold:
        candidates = [
            "C:/Windows/Fonts/Georgiab.ttf",
            "C:/Windows/Fonts/timesbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ] + candidates
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

tx = ico_x + ico_size + 60
ty_start = H // 2 - 90

# Titre principal
font_title = find_font(62, bold=True)
draw.text((tx, ty_start), "KARMIC", font=font_title, fill=GOLD)
draw.text((tx, ty_start + 68), "GOCHARA", font=font_title, fill=WHITE)

# Sous-titre
font_sub = find_font(20)
draw.text((tx, ty_start + 150), "Astrologie védique sidérale", font=font_sub, fill=DIM)

# Tag line
font_tag = find_font(17)
draw.text((tx, ty_start + 184), "✦  Transits karmiques • Gochara • IA", font=font_tag, fill=GOLD)

# Ligne décorative dorée
draw.rectangle((tx, ty_start + 215, tx + 320, ty_start + 217), fill=GOLD)

# URL
font_url = find_font(14)
draw.text((tx, ty_start + 228), "karmic-gochara.netlify.app", font=font_url, fill=DIM)

banner.save(os.path.join(OUT, "banner_1024x500.png"))
print("✓ banner_1024x500.png")
print(f"\nAssets enregistrés dans : {os.path.abspath(OUT)}/")
