# -*- coding: utf-8 -*-
"""
Smart Accounting Platform — Video Tutorial Slide Generator
Generates 11 high-quality PNG slides (1920×1080) for video recording.
Run: python generate_slides.py
Output: thesis/video_slides/slide_01.png ... slide_11.png
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──────────────────────────────────────────────────────
OUT = os.path.join("thesis", "video_slides")
os.makedirs(OUT, exist_ok=True)

AMIRI = "ui/resources/fonts/Amiri-Regular.ttf"
AMIRI_B = "ui/resources/fonts/Amiri-Bold.ttf"
ARIAL = "C:/Windows/Fonts/arial.ttf"
ARIAL_B = "C:/Windows/Fonts/arialbd.ttf"

# ── Colors ─────────────────────────────────────────────────────
BG      = (13, 17, 23)       # #0D1117
BG2     = (22, 27, 34)       # #161B22
BLUE    = (31, 78, 121)      # #1F4E79
BLUE_L  = (44, 120, 180)
GOLD    = (255, 215, 0)
WHITE   = (255, 255, 255)
GRAY    = (139, 148, 158)
GREEN   = (63, 185, 80)
RED     = (248, 81, 73)
ORANGE  = (210, 153, 34)
CYAN    = (56, 189, 248)
PURPLE  = (163, 113, 247)

W, H = 1920, 1080


# ── Helpers ────────────────────────────────────────────────────
def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_size(draw, txt, f):
    bb = draw.textbbox((0, 0), txt, font=f)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_text(draw, x, y, txt, f, color=WHITE, anchor="lt", max_w=0):
    if max_w:
        words = txt.split()
        lines, line = [], ""
        for w in words:
            test = f"{line} {w}".strip()
            tw = draw.textbbox((0, 0), test, font=f)[2]
            if tw > max_w and line:
                lines.append(line)
                line = w
            else:
                line = test
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            draw.text((x, y + i * (f.size + 8)), ln, font=f, fill=color, anchor=anchor)
        return len(lines) * (f.size + 8)
    draw.text((x, y), txt, font=f, fill=color, anchor=anchor)
    return f.size


def draw_rounded_rect(draw, xy, fill, radius=20):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_gradient_bar(draw, x, y, w, h, color):
    for i in range(w):
        r = int(color[0] * (1 - i / w * 0.3))
        g = int(color[1] * (1 - i / w * 0.3))
        b = int(color[2] * (1 - i / w * 0.3))
        draw.line([(x + i, y), (x + i, y + h)], fill=(r, g, b))


def draw_circle(draw, cx, cy, r, fill):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


def draw_icon(draw, cx, cy, icon, size=48, color=GOLD):
    f = font(ARIAL_B, size)
    draw.text((cx, cy), icon, font=f, fill=color, anchor="mm")


def slide_bg():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # top gradient bar
    draw_gradient_bar(draw, 0, 0, W, 6, BLUE)
    return img, draw


def section_number(draw, num, x=100, y=100):
    draw_circle(draw, x, y, 36, BLUE)
    f = font(ARIAL_B, 32)
    draw.text((x, y), str(num), font=f, fill=WHITE, anchor="mm")


def bottom_bar(draw, text="Smart Accounting Platform v3.1.7"):
    draw.rectangle([(0, H - 50), (W, H)], fill=BLUE)
    f = font(ARIAL, 20)
    draw.text((W // 2, H - 25), text, font=f, fill=WHITE, anchor="mm")


# ── SLIDES ─────────────────────────────────────────────────────

def slide_01():
    """Opening — Logo Reveal"""
    img, draw = slide_bg()
    # large centered logo text
    f1 = font(ARIAL_B, 72)
    f2 = font(AMIRI_B, 42)
    f3 = font(ARIAL, 28)
    f4 = font(ARIAL_B, 36)
    # icon circle
    draw_circle(draw, W // 2, 280, 90, BLUE)
    draw.text((W // 2, 280), "SAP", font=font(ARIAL_B, 48), fill=GOLD, anchor="mm")
    # title
    draw.text((W // 2, 420), "Smart Accounting Platform", font=f1, fill=WHITE, anchor="mm")
    draw.text((W // 2, 480), "المنصة المحاسبية الذكية", font=f2, fill=GOLD, anchor="mm")
    draw.text((W // 2, 540), "v3.1.7", font=f4, fill=GRAY, anchor="mm")
    # stats row
    stats = [
        ("35", "Screens", "شاشات"),
        ("20", "Ratios", "نسب مالية"),
        ("1800", "Tests", "اختبارات"),
        ("3", "Languages", "لغات"),
        ("44ms", "Startup", "إقلاع"),
    ]
    sx = 180
    for val, en, ar in stats:
        draw_rounded_rect(draw, (sx, 640, sx + 260, 760), BG2)
        draw.text((sx + 130, 670), val, font=font(ARIAL_B, 44), fill=GOLD, anchor="mt")
        draw.text((sx + 130, 720), en, font=font(ARIAL, 20), fill=GRAY, anchor="mt")
        draw.text((sx + 130, 750), ar, font=font(AMIRI, 18), fill=GRAY, anchor="mt")
        sx += 310
    # tagline
    draw.text((W // 2, 860), "Built for Algerian SMEs  |  مصمم للمؤسسات الصغيرة والمتوسطة الجزائرية",
              font=font(ARIAL, 24), fill=GRAY, anchor="mm")
    # tax compliance badge
    draw_rounded_rect(draw, (W // 2 - 200, 920, W // 2 + 200, 970), BLUE)
    draw.text((W // 2, 945), "100% Algerian Tax Compliance", font=font(ARIAL_B, 22), fill=WHITE, anchor="mm")
    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_01_opening.png"))
    print("  slide_01_opening.png")


def slide_02():
    """Getting Started — Login"""
    img, draw = slide_bg()
    section_number(draw, 1)
    f_h = font(ARIAL_B, 48)
    f_sub = font(AMIRI, 30)
    draw.text((180, 70), "Getting Started", font=f_h, fill=WHITE, anchor="lt")
    draw.text((180, 125), "البدء — تسجيل الدخول", font=f_sub, fill=GOLD, anchor="lt")

    # login box mockup
    bx, by = 300, 220
    draw_rounded_rect(draw, (bx, by, bx + 500, by + 420), BG2)
    draw.text((bx + 250, by + 30), "🔐 Login", font=font(ARIAL_B, 32), fill=WHITE, anchor="mt")
    # email field
    draw_rounded_rect(draw, (bx + 40, by + 90, bx + 460, by + 140), (30, 35, 44))
    draw.text((bx + 50, by + 100), "Email: admin@example.com", font=font(ARIAL, 20), fill=GRAY, anchor="lt")
    # password field
    draw_rounded_rect(draw, (bx + 40, by + 160, bx + 460, by + 210), (30, 35, 44))
    draw.text((bx + 50, by + 170), "Password: ••••••••", font=font(ARIAL, 20), fill=GRAY, anchor="lt")
    # login button
    draw_rounded_rect(draw, (bx + 40, by + 240, bx + 460, by + 290), BLUE)
    draw.text((bx + 250, by + 265), "تسجيل الدخول / Login", font=font(ARIAL_B, 22), fill=WHITE, anchor="mm")

    # right side — key points
    rx = 900
    points = [
        ("⚡", "44ms cold start", "إقلاع فوري — أقل من ثانية"),
        ("🔑", "Admin: admin / Admin@1234", "كلمة المرور الافتراضية"),
        ("🔄", "Password change on first login", "تغيير كلمة المرور عند أول دخول"),
        ("🌐", "RTL Arabic + LTR English/French", "واجهة عربية يمين-يسار"),
    ]
    py = 240
    for icon, en, ar in points:
        draw.text((rx, py), icon, font=font(ARIAL, 36), fill=GOLD, anchor="lt")
        draw.text((rx + 60, py), en, font=font(ARIAL_B, 22), fill=WHITE, anchor="lt")
        draw.text((rx + 60, py + 30), ar, font=font(AMIRI, 18), fill=GRAY, anchor="lt")
        py += 90

    # theme toggle
    draw_rounded_rect(draw, (rx, py + 20, rx + 280, py + 70), (40, 44, 52))
    draw.text((rx + 10, py + 30), "🌙 Dark / ☀️ Light", font=font(ARIAL, 18), fill=WHITE, anchor="lt")
    draw.text((rx + 200, py + 38), "Ctrl+T", font=font(ARIAL_B, 16), fill=GOLD, anchor="lt")

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_02_login.png"))
    print("  slide_02_login.png")


def slide_03():
    """Sidebar Tour + Shortcuts"""
    img, draw = slide_bg()
    section_number(draw, 2)
    draw.text((180, 70), "Navigation & Shortcuts", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "التنقل والاختصارات — 35 شاشة", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # sidebar mockup
    sx, sy = 80, 200
    draw_rounded_rect(draw, (sx, sy, sx + 300, sy + 720), BG2)
    draw.text((sx + 150, sy + 20), "📋 القائمة الجانبية", font=font(AMIRI_B, 22), fill=GOLD, anchor="mt")
    items = [
        ("Ctrl+1", "📋 Data Entry / إدخال البيانات"),
        ("Ctrl+2", "📊 Dashboard / لوحة التحكم"),
        ("Ctrl+3", "📈 Financial Ratios / النسب المالية"),
        ("Ctrl+4", "🔄 DuPont Analysis / تحليل DuPont"),
        ("Ctrl+0", "💰 Tax System / النظام الجبائي"),
        ("F3", "📈 Scenario Analysis / السيناريوهات"),
        ("F5", "🤖 AI Insights / الرؤى الذكية"),
        ("F9", "🏢 Demo Companies / شركات تجريبية"),
    ]
    iy = sy + 60
    for key, label in items:
        draw_rounded_rect(draw, (sx + 10, iy, sx + 290, iy + 48), (30, 35, 44))
        draw.text((sx + 20, iy + 8), key, font=font(ARIAL_B, 14), fill=GOLD, anchor="lt")
        draw.text((sx + 90, iy + 8), label, font=font(ARIAL, 13), fill=WHITE, anchor="lt")
        iy += 58

    # shortcut table
    rx = 450
    draw.text((rx, 200), "Keyboard Shortcuts", font=font(ARIAL_B, 28), fill=WHITE, anchor="lt")
    shortcuts = [
        ("Ctrl+1..0", "Screens 1–10"),
        ("Ctrl+Shift+1..0", "Screens 11–20"),
        ("F2..F12", "Screens 21–35"),
        ("Ctrl+R", "Calculate Ratios"),
        ("Ctrl+S", "Save to Database"),
        ("Ctrl+E", "Export PDF"),
        ("Ctrl+P", "Print"),
        ("Ctrl+T", "Toggle Theme"),
        ("Ctrl+L", "Logout"),
        ("F1", "Shortcuts Dialog"),
    ]
    ky = 250
    for key, desc in shortcuts:
        draw_rounded_rect(draw, (rx, ky, rx + 500, ky + 38), (30, 35, 44))
        draw.text((rx + 10, ky + 5), key, font=font(ARIAL_B, 16), fill=GOLD, anchor="lt")
        draw.text((rx + 200, ky + 5), desc, font=font(ARIAL, 16), fill=WHITE, anchor="lt")
        ky += 44

    # right side — 35 screens count
    draw_rounded_rect(draw, (rx + 540, 250, rx + 860, 750), BG2)
    draw.text((rx + 700, 280), "35", font=font(ARIAL_B, 120), fill=GOLD, anchor="mt")
    draw.text((rx + 700, 430), "Interactive", font=font(ARIAL_B, 32), fill=WHITE, anchor="mt")
    draw.text((rx + 700, 470), "Screens", font=font(ARIAL_B, 32), fill=WHITE, anchor="mt")
    draw.text((rx + 700, 530), "شاشات تفاعلية", font=font(AMIRI_B, 28), fill=GOLD, anchor="mt")
    draw.text((rx + 700, 580), "Lazy-loaded", font=font(ARIAL, 20), fill=GRAY, anchor="mt")
    draw.text((rx + 700, 610), "loads in <100ms", font=font(ARIAL, 20), fill=GRAY, anchor="mt")

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_03_navigation.png"))
    print("  slide_03_navigation.png")


def slide_04():
    """Data Entry"""
    img, draw = slide_bg()
    section_number(draw, 3)
    draw.text((180, 70), "Data Entry", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "إدخال البيانات — مركز التحكم", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # mockup form
    bx, by = 80, 220
    draw_rounded_rect(draw, (bx, by, bx + 700, by + 680), BG2)
    draw.text((bx + 350, by + 15), "📋 Data Entry — Ctrl+1", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    fields = [
        ("Revenue (إيرادات)", "5,000,000", "DZD"),
        ("COGS (تكلفة البضاعة)", "3,000,000", "DZD"),
        ("Operating Expenses (مصاريف)", "800,000", "DZD"),
        ("Cash (صندوق)", "500,000", "DZD"),
        ("Avg Payables (الذمم المدينة)", "200,000", "DZD"),
        ("Total Assets (إجمالي الأصول)", "4,000,000", "DZD"),
        ("Total Equity (رأس المال)", "2,500,000", "DZD"),
        ("Total Liabilities (الخصوم)", "1,500,000", "DZD"),
    ]
    fy = by + 60
    for label, val, unit in fields:
        draw.text((bx + 20, fy), label, font=font(AMIRI, 16), fill=GRAY, anchor="lt")
        draw_rounded_rect(draw, (bx + 320, fy - 5, bx + 580, fy + 35), (30, 35, 44))
        draw.text((bx + 560, fy + 2), unit, font=font(ARIAL, 12), fill=GRAY, anchor="rt")
        draw.text((bx + 330, fy + 2), val, font=font(ARIAL_B, 18), fill=GREEN, anchor="lt")
        fy += 55

    # action buttons
    draw_rounded_rect(draw, (bx + 20, fy + 20, bx + 180, fy + 60), BLUE)
    draw.text((bx + 100, fy + 40), "Ctrl+R Calculate", font=font(ARIAL_B, 14), fill=WHITE, anchor="mm")
    draw_rounded_rect(draw, (bx + 200, fy + 20, bx + 350, fy + 60), GREEN)
    draw.text((bx + 275, fy + 40), "Ctrl+S Save", font=font(ARIAL_B, 14), fill=WHITE, anchor="mm")

    # right side — features
    rx = 850
    features = [
        ("🔢", "Placeholder not zeros", "أدخل المبلغ بدل 0.00"),
        ("📊", "20 ratios calculated", "حساب 20 نسبة فوراً"),
        ("📅", "Multi-year comparison", "مقارنة سنوات متعددة"),
        ("💾", "SQLite persistence", "حفظ دائم في قاعدة بيانات"),
        ("📄", "PDF / Excel export", "تصدير PDF و Excel"),
        ("🖨️", "Direct printing", "طباعة مباشرة"),
    ]
    py = 240
    for icon, en, ar in features:
        draw.text((rx, py), icon, font=font(ARIAL, 32), fill=GOLD, anchor="lt")
        draw.text((rx + 55, py), en, font=font(ARIAL_B, 20), fill=WHITE, anchor="lt")
        draw.text((rx + 55, py + 28), ar, font=font(AMIRI, 16), fill=GRAY, anchor="lt")
        py += 80

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_04_data_entry.png"))
    print("  slide_04_data_entry.png")


def slide_05():
    """Dashboard + Ratios"""
    img, draw = slide_bg()
    section_number(draw, 4)
    draw.text((180, 70), "Financial Dashboard & Ratios", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "لوحة التحكم + النسب المالية — 20 نسبة", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # ratio table mockup
    bx, by = 80, 220
    draw_rounded_rect(draw, (bx, by, bx + 850, by + 500), BG2)
    draw.text((bx + 425, by + 15), "📈 Financial Ratios — Ctrl+3", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")

    ratios = [
        ("LIQUIDITY", [("Current Ratio", "1.67", GREEN), ("Quick Ratio", "1.20", GREEN), ("Cash Ratio", "0.50", ORANGE)]),
        ("PROFITABILITY", [("ROE", "28.0%", GREEN), ("ROA", "15.0%", GREEN), ("Net Margin", "24.0%", GREEN), ("Gross Margin", "40.0%", GREEN)]),
        ("SOLVENCY", [("Debt-to-Equity", "0.60", GREEN), ("Interest Coverage", "8.5x", GREEN)]),
        ("EFFICIENCY", [("Asset Turnover", "0.63x", ORANGE), ("Inv. Turnover", "5.0x", GREEN)]),
    ]
    ty = by + 55
    for family, items in ratios:
        draw.text((bx + 15, ty), family, font=font(ARIAL_B, 14), fill=GOLD, anchor="lt")
        tx = bx + 180
        for name, val, clr in items:
            draw.text((tx, ty), name, font=font(ARIAL, 14), fill=GRAY, anchor="lt")
            draw.text((tx + 140, ty), val, font=font(ARIAL_B, 14), fill=clr, anchor="lt")
            tx += 220
        ty += 50

    # right side — dashboard charts mockup
    rx = 1000
    draw_rounded_rect(draw, (rx, by, rx + 800, by + 500), BG2)
    draw.text((rx + 400, by + 15), "📊 Dashboard — Ctrl+2", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    # bar chart mockup
    bars = [(120, 300), (180, 400), (250, 500), (200, 350), (300, 550), (280, 480)]
    for i, (h1, h2) in enumerate(bars):
        x = rx + 60 + i * 110
        draw.rectangle([(x, by + 450 - h1), (x + 40, by + 450)], fill=BLUE_L)
        draw.rectangle([(x + 45, by + 450 - h2), (x + 85, by + 450)], fill=GOLD)
    # KPI cards
    kpis = [("Net Profit", "1,200,000", GREEN), ("ROE", "28%", GREEN), ("Current", "1.67", GREEN)]
    kx = rx + 50
    for name, val, clr in kpis:
        draw_rounded_rect(draw, (kx, by + 60, kx + 220, by + 130), (30, 35, 44))
        draw.text((kx + 110, by + 70), val, font=font(ARIAL_B, 28), fill=clr, anchor="mt")
        draw.text((kx + 110, by + 105), name, font=font(ARIAL, 16), fill=GRAY, anchor="mt")
        kx += 240

    # legend
    draw.rectangle([(rx + 50, by + 470), (rx + 70, by + 485)], fill=BLUE_L)
    draw.text((rx + 80, by + 470), "Year 1", font=font(ARIAL, 14), fill=GRAY, anchor="lt")
    draw.rectangle([(rx + 170, by + 470), (rx + 190, by + 485)], fill=GOLD)
    draw.text((rx + 200, by + 470), "Year 2", font=font(ARIAL, 14), fill=GRAY, anchor="lt")

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_05_ratios.png"))
    print("  slide_05_ratios.png")


def slide_06():
    """DuPont + Z-Score"""
    img, draw = slide_bg()
    section_number(draw, 5)
    draw.text((180, 70), "Advanced Analysis", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "التحليل المتقدم — DuPont + Z-Score + السيناريوهات", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # DuPont waterfall mockup
    bx, by = 80, 220
    draw_rounded_rect(draw, (bx, by, bx + 550, by + 400), BG2)
    draw.text((bx + 275, by + 15), "🔄 DuPont — Ctrl+4", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    # waterfall bars
    wf = [("ROE", 300, GOLD), ("Net Margin", -60, GREEN), ("× Asset Turnover", -40, BLUE_L), ("× Equity Mult.", -80, CYAN)]
    wx = bx + 40
    for label, h, clr in wf:
        draw.rectangle([(wx, by + 350 - abs(h)), (wx + 100, by + 350)], fill=clr)
        draw.text((wx + 50, by + 360), label, font=font(ARIAL, 12), fill=GRAY, anchor="mt")
        draw.text((wx + 50, by + 340 - abs(h)), label.split()[-1], font=font(ARIAL_B, 14), fill=WHITE, anchor="mb")
        wx += 120

    # Z-Score gauge mockup
    rx = 700
    draw_rounded_rect(draw, (rx, by, rx + 550, by + 400), BG2)
    draw.text((rx + 275, by + 15), "📊 Z-Score — Ctrl+Shift+3", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    # gauge
    cx, cy = rx + 275, by + 220
    for angle in range(180):
        rad = math.radians(angle)
        x = cx + int(120 * math.cos(rad))
        y = cy - int(120 * math.sin(rad))
        if angle < 60:
            c = RED
        elif angle < 120:
            c = ORANGE
        else:
            c = GREEN
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=c)
    # needle
    draw.text((cx, cy + 20), "2.7", font=font(ARIAL_B, 48), fill=GOLD, anchor="mt")
    draw.text((cx, cy + 80), "Grey Zone — Caution", font=font(ARIAL, 20), fill=ORANGE, anchor="mt")

    # Scenario mockup
    sy = 660
    draw_rounded_rect(draw, (80, sy, 1250, sy + 300), BG2)
    draw.text((665, sy + 15), "📈 Scenario Analysis — F3", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    scenarios = [("Optimistic 📈", GREEN, "+15%"), ("Normal ➡️", BLUE_L, "+5%"), ("Pessimistic 📉", RED, "-8%")]
    sx = 150
    for name, clr, pct in scenarios:
        draw_rounded_rect(draw, (sx, sy + 60, sx + 340, sy + 260), (30, 35, 44))
        draw.text((sx + 170, sy + 80), name, font=font(ARIAL_B, 20), fill=WHITE, anchor="mt")
        draw.text((sx + 170, sy + 120), pct, font=font(ARIAL_B, 36), fill=clr, anchor="mt")
        # mini line chart
        pts = [(sx + 30, sy + 220), (sx + 100, sy + 200), (sx + 170, sy + 180), (sx + 240, sy + 160), (sx + 310, sy + 140)]
        draw.line(pts, fill=clr, width=3)
        sx += 370

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_06_advanced.png"))
    print("  slide_06_advanced.png")


def slide_07():
    """Tax Compliance"""
    img, draw = slide_bg()
    section_number(draw, 6)
    draw.text((180, 70), "Algerian Tax Compliance", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "النظام الجبائي الجزائري — 6 حاسبات + تقويم + إقرارات", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # Tax calculators grid
    taxes = [
        ("IBS", "19/23/26%", "ضريبة أرباح الشركات", BLUE),
        ("TVA", "19/9/6/0%", "ضريبة القيمة المضافة", GREEN),
        ("IRG", "0–35%", "ضريبة الدخل", ORANGE),
        ("CNAS", "33.5%", "التأمينات الاجتماعية", CYAN),
        ("CNAC", "2%", "تأمين البطالة", PURPLE),
        ("VF", "2%", "الدفعات المقدمة", RED),
    ]
    gx, gy = 80, 220
    for name, rate, ar, clr in taxes:
        draw_rounded_rect(draw, (gx, gy, gx + 350, gy + 180), BG2)
        draw.text((gx + 20, gy + 15), name, font=font(ARIAL_B, 32), fill=clr, anchor="lt")
        draw.text((gx + 330, gy + 15), rate, font=font(ARIAL_B, 24), fill=WHITE, anchor="rt")
        draw.text((gx + 20, gy + 60), ar, font=font(AMIRI, 20), fill=GRAY, anchor="lt")
        # mini detail
        draw.text((gx + 20, gy + 100), "Monthly by day 20", font=font(ARIAL, 14), fill=GRAY, anchor="lt")
        draw.text((gx + 20, gy + 125), "Penalty: 10% + 3%/mo", font=font(ARIAL, 14), fill=RED, anchor="lt")
        gx += 380
        if gx > 1200:
            gx = 80
            gy += 210

    # Tax Calendar
    cy = 660
    draw_rounded_rect(draw, (80, cy, 1840, cy + 320), BG2)
    draw.text((960, cy + 15), "📅 Tax Calendar — Ctrl+Shift+9", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    obligations = [
        (2, "DAS", RED), (2, "IBS₁", ORANGE), (3, "IBS₁", ORANGE),
        (4, "IBS Bal", RED), (5, "IBS₂", ORANGE), (10, "IBS₃", ORANGE),
    ]
    mx = 130
    for i, m in enumerate(months):
        draw_rounded_rect(draw, (mx, cy + 60, mx + 130, cy + 100), (30, 35, 44))
        draw.text((mx + 65, cy + 72), m, font=font(ARIAL_B, 16), fill=WHITE, anchor="mm")
        # check obligations
        for month_idx, label, clr in obligations:
            if month_idx == i + 1:
                draw_rounded_rect(draw, (mx, cy + 110, mx + 130, cy + 140), clr)
                draw.text((mx + 65, cy + 118), label, font=font(ARIAL_B, 12), fill=WHITE, anchor="mm")
        # monthly markers
        draw_rounded_rect(draw, (mx + 20, cy + 155, mx + 110, cy + 180), (50, 55, 64))
        draw.text((mx + 65, cy + 162), "TVA/IRG/CNAS day 20", font=font(ARIAL, 10), fill=GRAY, anchor="mm")
        mx += 140

    # Declarations
    draw.text((130, cy + 210), "📄 G50 (Monthly TVA)  |  📄 G57 (Annual TVA)  |  📄 DAS (Annual Salary)",
              font=font(ARIAL, 20), fill=WHITE, anchor="lt")
    draw.text((130, cy + 250), "Export to PDF/Excel — ready to file",
              font=font(ARIAL, 18), fill=GRAY, anchor="lt")

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_07_tax.png"))
    print("  slide_07_tax.png")


def slide_08():
    """AI Insights + Forecasting"""
    img, draw = slide_bg()
    section_number(draw, 7)
    draw.text((180, 70), "AI-Powered Insights", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "الرؤى الذكية — تنبؤ + كشف شذوذ + توصيات", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # Forecast chart mockup
    bx, by = 80, 220
    draw_rounded_rect(draw, (bx, by, bx + 750, by + 450), BG2)
    draw.text((bx + 375, by + 15), "📈 Forecasting — 3 Methods", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    # line chart
    pts_hist = [(bx + 60, by + 380), (bx + 130, by + 350), (bx + 200, by + 320),
                (bx + 270, by + 340), (bx + 340, by + 300), (bx + 410, by + 280)]
    pts_fc = [(bx + 410, by + 280), (bx + 480, by + 250), (bx + 550, by + 220),
              (bx + 620, by + 200), (bx + 690, by + 180)]
    # confidence band
    band_top = [(bx + 410, by + 260), (bx + 480, by + 220), (bx + 550, by + 180),
                (bx + 620, by + 150), (bx + 690, by + 130)]
    band_bot = [(bx + 410, by + 300), (bx + 480, by + 280), (bx + 550, by + 260),
                (bx + 620, by + 250), (bx + 690, by + 230)]
    # draw band
    for i in range(len(band_top) - 1):
        poly = [band_top[i], band_top[i + 1], band_bot[i + 1], band_bot[i]]
        draw.polygon(poly, fill=(44, 120, 180, 40))
    draw.line(pts_hist, fill=WHITE, width=3)
    draw.line(pts_fc, fill=GOLD, width=3)
    # methods
    methods = [("Linear Regression", GREEN), ("Moving Average", CYAN), ("Exp. Smoothing", GOLD)]
    mx = bx + 60
    for name, clr in methods:
        draw.rectangle([(mx, by + 420), (mx + 20, by + 435)], fill=clr)
        draw.text((mx + 25, by + 420), name, font=font(ARIAL, 14), fill=GRAY, anchor="lt")
        mx += 230

    # Anomaly detection
    rx = 900
    draw_rounded_rect(draw, (rx, by, rx + 900, by + 450), BG2)
    draw.text((rx + 450, by + 15), "🔍 Anomaly Detection", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    anomalies = [
        ("⚠️ Transaction #47", "Amount: 850,000 DZD", "Expected: 120,000", "Z-score: 3.2", "CRITICAL", RED),
        ("⚠️ Profit Feb", "Value: -50,000", "Expected: +200,000", "Z-score: 2.8", "WARNING", ORANGE),
        ("ℹ️ Expense spike", "Value: 450,000", "Expected: 200,000", "IQR: 2.1", "INFO", CYAN),
    ]
    ay = by + 60
    for title, amt, exp, score, sev, clr in anomalies:
        draw_rounded_rect(draw, (rx + 20, ay, rx + 880, ay + 110), (30, 35, 44))
        draw.text((rx + 40, ay + 10), title, font=font(ARIAL_B, 18), fill=WHITE, anchor="lt")
        draw.text((rx + 40, ay + 38), amt, font=font(ARIAL, 14), fill=GRAY, anchor="lt")
        draw.text((rx + 40, ay + 58), exp, font=font(ARIAL, 14), fill=GRAY, anchor="lt")
        draw.text((rx + 40, ay + 78), score, font=font(ARIAL, 14), fill=GRAY, anchor="lt")
        draw_rounded_rect(draw, (rx + 750, ay + 10, rx + 870, ay + 40), clr)
        draw.text((rx + 810, ay + 18), sev, font=font(ARIAL_B, 14), fill=WHITE, anchor="mm")
        ay += 125

    # Recommendations
    ry = 700
    draw_rounded_rect(draw, (80, ry, 1840, ry + 280), BG2)
    draw.text((960, ry + 15), "💡 Smart Recommendations", font=font(ARIAL_B, 22), fill=WHITE, anchor="mt")
    recs = [
        ("HIGH", "Reduce operating expenses by 10%", "تقليل المصاريف التشغيلية بنسبة 10%", RED),
        ("MEDIUM", "Increase cash reserves to 800K DZD", "زيادة الاحتياطي النقدي", ORANGE),
        ("LOW", "Review pricing strategy for Q4", "مراجعة استراتيجية التسعير", GREEN),
    ]
    rx2 = 150
    for pri, en, ar, clr in recs:
        draw_rounded_rect(draw, (rx2, ry + 60, rx2 + 520, ry + 250), (30, 35, 44))
        draw_rounded_rect(draw, (rx2 + 10, ry + 70, rx2 + 90, ry + 100), clr)
        draw.text((rx2 + 50, ry + 78), pri, font=font(ARIAL_B, 14), fill=WHITE, anchor="mm")
        draw.text((rx2 + 110, ry + 75), en, font=font(ARIAL_B, 18), fill=WHITE, anchor="lt")
        draw.text((rx2 + 110, ry + 105), ar, font=font(AMIRI, 16), fill=GRAY, anchor="lt")
        rx2 += 560

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_08_ai.png"))
    print("  slide_08_ai.png")


def slide_09():
    """Cloud + Import + Export"""
    img, draw = slide_bg()
    section_number(draw, 8)
    draw.text((180, 70), "Productivity & Data Management", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "إدارة البيانات — سحابي + استيراد + تصدير + شركات تجريبية", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # Cloud Sync
    bx, by = 80, 220
    draw_rounded_rect(draw, (bx, by, bx + 550, by + 350), BG2)
    draw.text((bx + 275, by + 15), "☁️ Cloud Sync", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    clouds = [("Dropbox", CYAN), ("OneDrive", BLUE_L), ("Google Drive", GREEN)]
    cx = bx + 60
    for name, clr in clouds:
        draw_rounded_rect(draw, (cx, by + 60, cx + 140, by + 100), clr)
        draw.text((cx + 70, by + 72), name, font=font(ARIAL_B, 14), fill=WHITE, anchor="mm")
        cx += 160
    draw.text((bx + 30, by + 130), "🔒 AES-256 encryption", font=font(ARIAL, 18), fill=GREEN, anchor="lt")
    draw.text((bx + 30, by + 160), "📋 Checksum verification", font=font(ARIAL, 18), fill=WHITE, anchor="lt")
    draw.text((bx + 30, by + 190), "🔄 Auto-backup daily/weekly", font=font(ARIAL, 18), fill=WHITE, anchor="lt")
    draw.text((bx + 30, by + 220), "📝 Sync log (every operation)", font=font(ARIAL, 18), fill=WHITE, anchor="lt")

    # Data Import
    rx = 700
    draw_rounded_rect(draw, (rx, by, rx + 550, by + 350), BG2)
    draw.text((rx + 275, by + 15), "📥 Data Import", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    steps = ["1. Select CSV file", "2. Map columns to fields", "3. Preview validation", "4. Import → Success"]
    sy = by + 60
    for step in steps:
        draw.text((rx + 30, sy), step, font=font(ARIAL, 18), fill=WHITE, anchor="lt")
        sy += 40
    draw.text((rx + 30, sy + 20), "Ctrl+Shift+0", font=font(ARIAL_B, 16), fill=GOLD, anchor="lt")

    # Demo Companies
    dx = 1320
    draw_rounded_rect(draw, (dx, by, dx + 500, by + 350), BG2)
    draw.text((dx + 250, by + 15), "🏢 Demo Companies", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    companies = [
        ("🏪 Trading", "تجارية"),
        ("💻 Services", "خدمات"),
        ("🏭 Manufacturing", "إنتاج"),
        ("🚢 Import/Export", "استيراد-تصدير"),
    ]
    cy = by + 60
    for name, ar in companies:
        draw_rounded_rect(draw, (dx + 20, cy, dx + 480, cy + 50), (30, 35, 44))
        draw.text((dx + 40, cy + 8), name, font=font(ARIAL_B, 16), fill=WHITE, anchor="lt")
        draw.text((dx + 460, cy + 8), ar, font=font(AMIRI, 14), fill=GRAY, anchor="rt")
        cy += 58
    draw.text((dx + 250, cy + 30), "F9 to load instantly", font=font(ARIAL, 16), fill=GOLD, anchor="mt")

    # Multi-currency + Export
    ey = 600
    draw_rounded_rect(draw, (80, ey, 900, ey + 380), BG2)
    draw.text((490, ey + 15), "💱 Multi-Currency + 📄 Export", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    currencies = ["DZD", "EUR", "USD", "GBP", "SAR", "AED", "TND"]
    cx = 130
    for cur in currencies:
        draw_rounded_rect(draw, (cx, ey + 60, cx + 100, ey + 100), (30, 35, 44))
        draw.text((cx + 50, ey + 72), cur, font=font(ARIAL_B, 16), fill=GOLD, anchor="mm")
        cx += 110
    draw.text((130, ey + 130), "Export formats:", font=font(ARIAL_B, 18), fill=WHITE, anchor="lt")
    fmts = [("PDF", RED), ("Excel", GREEN), ("CSV", CYAN), ("HTML", ORANGE), ("TXT", GRAY)]
    fx = 130
    for fmt, clr in fmts:
        draw_rounded_rect(draw, (fx, ey + 165, fx + 80, ey + 200), clr)
        draw.text((fx + 40, ey + 175), fmt, font=font(ARIAL_B, 14), fill=WHITE, anchor="mm")
        fx += 95

    # Unified export layer info
    draw.text((130, ey + 230), "Unified Export Layer (ui/exporters.py)", font=font(ARIAL_B, 16), fill=GOLD, anchor="lt")
    draw.text((130, ey + 260), "new_workbook / add_excel_sheet / style_header_row", font=font(ARIAL, 14), fill=GRAY, anchor="lt")
    draw.text((130, ey + 285), "3 screens migrated • 180 lines boilerplate eliminated", font=font(ARIAL, 14), fill=GRAY, anchor="lt")

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_09_productivity.png"))
    print("  slide_09_productivity.png")


def slide_10():
    """Security + Architecture"""
    img, draw = slide_bg()
    section_number(draw, 9)
    draw.text((180, 70), "Security & Architecture", font=font(ARIAL_B, 48), fill=WHITE, anchor="lt")
    draw.text((180, 125), "الأمان والبنية — PBKDF2 + AES-256 + CI/CD", font=font(AMIRI, 30), fill=GOLD, anchor="lt")

    # Security features
    bx, by = 80, 220
    draw_rounded_rect(draw, (bx, by, bx + 550, by + 400), BG2)
    draw.text((bx + 275, by + 15), "🔒 Security", font=font(ARIAL_B, 28), fill=WHITE, anchor="mt")
    sec = [
        ("PBKDF2 (100K iterations + salt)", "تشفير كلمات المرور"),
        ("AES-256-GCM vault encryption", "خزنة مشفّرة"),
        ("2FA authentication", "مصادقة ثنائية"),
        ("User roles & permissions", "أدوار وصلاحيات"),
        ("HTTPS-only auto-update", "تحديث آمن"),
        ("Encrypted SMTP/API keys", "مفاتيح مشفّرة"),
    ]
    sy = by + 60
    for en, ar in sec:
        draw.text((bx + 30, sy), "✅", font=font(ARIAL, 16), fill=GREEN, anchor="lt")
        draw.text((bx + 55, sy), en, font=font(ARIAL, 16), fill=WHITE, anchor="lt")
        draw.text((bx + 55, sy + 22), ar, font=font(AMIRI, 14), fill=GRAY, anchor="lt")
        sy += 52

    # Architecture
    rx = 700
    draw_rounded_rect(draw, (rx, by, rx + 1100, by + 400), BG2)
    draw.text((rx + 550, by + 15), "🏗️ Architecture", font=font(ARIAL_B, 28), fill=WHITE, anchor="mt")
    layers = [
        ("Presentation", "ui/views (35 screens, lazy-loaded)", BLUE),
        ("Business Logic", "modules/ (37 engines)", GREEN),
        ("Data Layer", "SQLite + WAL + connection pool", ORANGE),
        ("Persistence", "accounting_platform.db", PURPLE),
    ]
    ly = by + 70
    for name, desc, clr in layers:
        draw_rounded_rect(draw, (rx + 30, ly, rx + 1070, ly + 60), clr)
        draw.text((rx + 50, ly + 8), name, font=font(ARIAL_B, 20), fill=WHITE, anchor="lt")
        draw.text((rx + 50, ly + 34), desc, font=font(ARIAL, 16), fill=(200, 200, 200), anchor="lt")
        ly += 75

    # Performance metrics
    py = 660
    draw_rounded_rect(draw, (80, py, 1840, py + 320), BG2)
    draw.text((960, py + 15), "⚡ Performance Metrics (v3.1.7)", font=font(ARIAL_B, 24), fill=WHITE, anchor="mt")
    metrics = [
        ("44ms", "Cold Start", "إقلاع", GREEN),
        ("<100ms", "View Load", "تحميل مشهد", GREEN),
        ("45MB", "Peak Memory", "ذاكرة ذروة", GREEN),
        ("4.6×", "DB Write Gain", "تحسين الكتابة", GREEN),
        ("17×", "DB Read Gain", "تحسين القراءة", GREEN),
        ("1800", "Tests Passing", "اختبارات ناجحة", GREEN),
        ("100%", "Module Coverage", "تغطية الوحدات", GREEN),
        ("39s", "Full Suite Time", "وقت الاختبار", GREEN),
    ]
    mx = 130
    for val, en, ar, clr in metrics:
        draw_rounded_rect(draw, (mx, py + 60, mx + 200, py + 280), (30, 35, 44))
        draw.text((mx + 100, py + 80), val, font=font(ARIAL_B, 32), fill=clr, anchor="mt")
        draw.text((mx + 100, py + 130), en, font=font(ARIAL, 16), fill=WHITE, anchor="mt")
        draw.text((mx + 100, py + 160), ar, font=font(AMIRI, 14), fill=GRAY, anchor="mt")
        mx += 215

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_10_security.png"))
    print("  slide_10_security.png")


def slide_11():
    """Closing + CTA"""
    img, draw = slide_bg()
    # large centered content
    draw_circle(draw, W // 2, 200, 80, BLUE)
    draw.text((W // 2, 200), "SAP", font=font(ARIAL_B, 44), fill=GOLD, anchor="mm")
    draw.text((W // 2, 330), "Smart Accounting Platform", font=font(ARIAL_B, 64), fill=WHITE, anchor="mm")
    draw.text((W // 2, 400), "المنصة المحاسبية الذكية", font=font(AMIRI_B, 40), fill=GOLD, anchor="mm")
    draw.text((W // 2, 460), "v3.1.7", font=font(ARIAL_B, 30), fill=GRAY, anchor="mm")

    # feature summary
    features = [
        "35 Interactive Screens  •  20 Financial Ratios  •  6 Tax Calculators",
        "AI-Powered Insights  •  3 Languages (AR/EN/FR)  •  1800 Tests",
        "100% Algerian Tax Compliance  •  Cloud Sync  •  PDF/Excel Export",
    ]
    fy = 530
    for feat in features:
        draw.text((W // 2, fy), feat, font=font(ARIAL, 24), fill=WHITE, anchor="mm")
        fy += 40

    # download options
    draw_rounded_rect(draw, (W // 2 - 400, 680, W // 2 + 400, 840), BG2)
    draw.text((W // 2, 700), "📦 Download Options", font=font(ARIAL_B, 24), fill=GOLD, anchor="mt")
    downloads = [
        ("Installer", "66.9 MB", "Inno Setup — silent install"),
        ("Portable", "109 MB", "No installation needed"),
        ("Standalone", "143 MB", "Nuitka compiled exe"),
    ]
    dx = W // 2 - 360
    for name, size, desc in downloads:
        draw.text((dx, 740), name, font=font(ARIAL_B, 18), fill=WHITE, anchor="lt")
        draw.text((dx + 130, 740), size, font=font(ARIAL_B, 18), fill=GOLD, anchor="lt")
        draw.text((dx, 768), desc, font=font(ARIAL, 14), fill=GRAY, anchor="lt")
        dx += 250

    # patent info
    draw_rounded_rect(draw, (W // 2 - 300, 870, W // 2 + 300, 920), BLUE)
    draw.text((W // 2, 895), "🎓 Developed under Arrêté 1275 — One Diploma, One Startup",
              font=font(ARIAL, 18), fill=WHITE, anchor="mm")

    # CTA
    draw.text((W // 2, 960), "github.com/your-repo  |  ⭐ Star us  |  📧 Contact",
              font=font(ARIAL, 20), fill=GRAY, anchor="mm")

    bottom_bar(draw)
    img.save(os.path.join(OUT, "slide_11_closing.png"))
    print("  slide_11_closing.png")


# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating video tutorial slides...")
    slide_01()
    slide_02()
    slide_03()
    slide_04()
    slide_05()
    slide_06()
    slide_07()
    slide_08()
    slide_09()
    slide_10()
    slide_11()
    print(f"\nDone! 11 slides saved to {OUT}/")
    print("Combine with video editor + voice-over to create the tutorial.")