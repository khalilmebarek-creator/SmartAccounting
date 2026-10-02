# يولد شعارات المنصة المتوافقة مع الثيم الداكن البنفسجي
# الخرج: docs/logo_icon.png (أيقونة 512) + docs/logo_full.png (صورة OG 1200x630)

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FONTS = os.path.join(ROOT, "ui", "resources", "fonts")

# ألوان الثيم البنفسجي (مطابقة لتطبيق modern + موقع webild-style)
VIOLET_TOP = (139, 92, 246)     # #8b5cf6
VIOLET_BOTTOM = (109, 40, 217)  # #6d28d9
CYAN = (34, 211, 238)           # #22d3ee
WHITE = (255, 255, 255)
DARK_BG = (10, 10, 20)          # #0a0a14


def _vertical_gradient(size, top, bottom):
    """تدرج رأسي smooth عبر مصفوفة numpy"""
    w, h = size
    rows = np.linspace(0.0, 1.0, h)[:, None]
    grad = (1 - rows) * np.array(top) + rows * np.array(bottom)
    return grad.astype(np.uint8)


def _draw_icon(scale=4, size=512):
    """أيقونة: مربع بزوايا دائرية بتدرج بنفسجي + أعمدة بيانية صاعدة + لمعة سماوية"""
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = int(S * 0.22)
    # خلفية مربع دائري بتدرج رأسي
    grad_col = _vertical_gradient((S, S), VIOLET_TOP, VIOLET_BOTTOM)  # (S, 3)
    grad = np.repeat(grad_col[:, None, :], S, axis=1)                 # (S, S, 3)
    rgba = np.concatenate([grad, np.full((S, S, 1), 255, dtype=np.uint8)], axis=2)
    grad_img = Image.fromarray(rgba.astype(np.uint8))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=255)
    img.paste(grad_img, (0, 0), mask)

    # توهج داخلي علوي خفيف
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-S * 0.3, -S * 0.5, S * 1.0, S * 0.5], fill=(255, 255, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.12))
    img = Image.alpha_composite(img, glow)

    # أعمدة بيانية (4 أعمدة صاعدة)
    bar_w = int(S * 0.10)
    gap = int(S * 0.05)
    base_y = int(S * 0.80)
    top_y = int(S * 0.26)
    heights = [0.42, 0.60, 0.78, 0.96]  # نسب صاعدة
    total = bar_w * 4 + gap * 3
    start_x = (S - total) // 2
    for i, ratio in enumerate(heights):
        x0 = start_x + i * (bar_w + gap)
        x1 = x0 + bar_w
        y0 = base_y - int((base_y - top_y) * ratio)
        color = CYAN if i == 3 else WHITE
        draw.rounded_rectangle([x0, y0, x1, base_y], radius=bar_w // 2, fill=color)

    # لمعة AI صغيرة (نجمة) أعلى اليمين
    cx, cy = int(S * 0.78), int(S * 0.24)
    r = int(S * 0.05)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CYAN)
    r2 = int(S * 0.018)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=WHITE)

    # تصغير ناعم
    return img.resize((size, size), Image.LANCZOS)


def _draw_full():
    """صورة OG: خلفية داكنة بتوهج بنفسجي + الأيقونة + العنوان عربي/إنجليزي"""
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))

    # توهجات aurora
    for cx, cy, rr, col in (
        (180, 0, 620, (124, 58, 237, 90)),
        (1100, 630, 560, (34, 211, 238, 55)),
        (650, 350, 700, (124, 58, 237, 40)),
    ):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
        layer = layer.filter(ImageFilter.GaussianBlur(160))
        img = Image.alpha_composite(img, layer)

    # الأيقونة يساراً
    icon = _draw_icon(scale=2, size=200)
    img.paste(icon, (90, 215), icon)

    draw = ImageDraw.Draw(img)

    # العنوان عربي (أميري)
    title = "المنصة المحاسبية الذكية"
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(title)
        title_rtl = get_display(reshaped)
        font_ar = ImageFont.truetype(os.path.join(FONTS, "Amiri-Bold.ttf"), 78)
        draw.text((350, 250), title_rtl, font=font_ar, fill=WHITE)
    except Exception:
        pass

    # العنوان الإنجليزي + وسم
    font_en = ImageFont.truetype(
        os.path.join(os.path.dirname(__import__("matplotlib").__file__),
                     "mpl-data", "fonts", "ttf", "DejaVuSans-Bold.ttf"), 40)
    draw.text((352, 380), "Smart Accounting Platform", font=font_en, fill=CYAN)
    font_tag = ImageFont.truetype(
        os.path.join(os.path.dirname(__import__("matplotlib").__file__),
                     "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"), 22)
    draw.text((352, 450), "AI-powered Algerian accounting & tax platform", font=font_tag,
              fill=(154, 151, 176, 255))

    return img.convert("RGB")


def main():
    icon = _draw_icon(scale=4, size=512)
    icon.save(os.path.join(DOCS, "logo_icon.png"))
    print("wrote logo_icon.png")

    full = _draw_full()
    full.save(os.path.join(DOCS, "logo_full.png"))
    print("wrote logo_full.png")


if __name__ == "__main__":
    main()
