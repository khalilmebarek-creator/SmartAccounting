"""
أداة تحليل بصري للشاشات PyQt6
تلتقط لقطات لكل شاشة + تقارن بينها بـ SSIM + pHash
تُولّد تقرير HTML بجانب-جانب مع خريطة اختلافات
"""
import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from skimage.metrics import structural_similarity as ssim
import imagehash
from PIL import Image
import numpy as np
import cv2

SCREENSHOTS_DIR = Path(__file__).parent.parent / "artifacts" / "ui_screenshots"
REPORTS_DIR = Path(__file__).parent.parent / "artifacts" / "ui_reports"
BASELINE_DIR = SCREENSHOTS_DIR / "baseline"


def _get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def _import_all_views():
    """Import all view classes from the view registry."""
    from ui.views.data_entry import DataEntryView
    from ui.views.dashboard import DashboardView
    from ui.views.analysis_view import DuPontView
    from ui.views.ratios_view import RatiosView
    from ui.views.tax_view import TaxView
    from ui.views.audit_view import AuditView
    from ui.views.reports_view import ReportsView
    from ui.views.settings_view import SettingsView
    from ui.views.chat_view import ChatView
    from ui.views.advanced_dashboard_view import AdvancedDashboardView
    from ui.views.scenarios_view import ScenariosView
    from ui.views.benchmarks_view import BenchmarkView
    from ui.views.ai_insights_view import AIInsightsView
    from ui.views.cost_center_profitability_view import CostCenterProfitabilityView
    from ui.views.cashflow_view import CashFlowView
    from ui.views.comparative_view import ComparativeView
    from ui.views.zscore_view import ZScoreView
    from ui.views.forecasting_view import ForecastingView
    from ui.views.budget_view import BudgetView
    from ui.views.cost_center_view import CostCenterView
    from ui.views.breakeven_view import BreakEvenView
    from ui.views.data_import_view import DataImportView
    from ui.views.bank_sync_view import BankSyncView
    from ui.views.currency_view import CurrencyView
    from ui.views.cloud_sync_view import CloudSyncView
    from ui.views.demo_data_view import DemoDataView
    from ui.views.user_testing_view import UserTestingView
    from ui.views.ledger_view import LedgerView
    from ui.views.partners_view import PartnersView
    from ui.views.invoicing_view import InvoicingView
    from ui.views.inventory_view import InventoryView
    from ui.views.payroll_view import PayrollView
    from ui.views.budgeting_view import BudgetingView
    from ui.views.tax_calendar_view import TaxCalendarView
    from ui.views.ias_reports_view import IASReportsView
    from ui.views.ai_platform_view import AIPlatformView

    return {
        "data_entry": DataEntryView,
        "dashboard": DashboardView,
        "dupont": DuPontView,
        "ratios": RatiosView,
        "tax": TaxView,
        "audit": AuditView,
        "reports": ReportsView,
        "settings": SettingsView,
        "chat": ChatView,
        "advanced_dashboard": AdvancedDashboardView,
        "scenarios": ScenariosView,
        "benchmarks": BenchmarkView,
        "ai_insights": AIInsightsView,
        "cost_center_profitability": CostCenterProfitabilityView,
        "cashflow": CashFlowView,
        "comparative": ComparativeView,
        "zscore": ZScoreView,
        "forecasting": ForecastingView,
        "budget": BudgetView,
        "cost_center": CostCenterView,
        "breakeven": BreakEvenView,
        "data_import": DataImportView,
        "bank_sync": BankSyncView,
        "currency": CurrencyView,
        "cloud_sync": CloudSyncView,
        "demo_data": DemoDataView,
        "user_testing": UserTestingView,
        "ledger": LedgerView,
        "partners": PartnersView,
        "invoicing": InvoicingView,
        "inventory": InventoryView,
        "payroll": PayrollView,
        "budgeting": BudgetingView,
        "tax_calendar": TaxCalendarView,
        "ias_reports": IASReportsView,
        "ai_platform": AIPlatformView,
    }


def capture_all_screens(output_dir=None, width=1280, height=800):
    """Capture screenshots of all views."""
    output_dir = Path(output_dir) if output_dir else SCREENSHOTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    app = _get_app()
    views = _import_all_views()
    captured = {}

    for name, ViewClass in views.items():
        try:
            view = ViewClass()
            view.resize(width, height)
            view.show()
            QApplication.processEvents()

            pixmap = view.grab()
            path = output_dir / f"{name}.png"
            pixmap.save(str(path))
            captured[name] = str(path)
            print(f"  [OK] {name}: {path}")
            view.close()
            view.deleteLater()
            QApplication.processEvents()
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")

    return captured


def compare_two_images(img1_path, img2_path):
    """Compare two images using SSIM + pHash."""
    pil1 = Image.open(img1_path).convert("RGB")
    pil2 = Image.open(img2_path).convert("RGB")

    # Resize to same dimensions if different
    if pil1.size != pil2.size:
        pil2 = pil2.resize(pil1.size)

    arr1 = np.array(pil1)
    arr2 = np.array(pil2)

    # SSIM
    score_ssim, diff_map = ssim(arr1, arr2, channel_axis=2, full=True)

    # pHash
    hash1 = imagehash.phash(pil1)
    hash2 = imagehash.phash(pil2)
    hash_distance = hash1 - hash2

    # Pixel diff percentage
    diff_gray = ((1 - diff_map) * 255).astype(np.uint8)
    _, thresh = cv2.threshold(diff_gray, 200, 255, cv2.THRESH_BINARY)
    pixel_diff_pct = (np.count_nonzero(thresh) / thresh.size) * 100

    return {
        "ssim": round(score_ssim, 4),
        "pHash_distance": hash_distance,
        "pixel_diff_pct": round(pixel_diff_pct, 2),
        "diff_map": diff_map,
        "thresh": thresh,
    }


def compare_screenshots(dir_a, dir_b):
    """Compare all screenshots between two directories."""
    results = {}
    dir_a, dir_b = Path(dir_a), Path(dir_b)

    for img in sorted(dir_a.glob("*.png")):
        name = img.stem
        other = dir_b / img.name
        if not other.exists():
            results[name] = {"status": "missing_in_b"}
            continue

        try:
            comparison = compare_two_images(str(img), str(other))
            results[name] = {
                "status": "compared",
                "ssim": comparison["ssim"],
                "pHash_distance": comparison["pHash_distance"],
                "pixel_diff_pct": comparison["pixel_diff_pct"],
                "issues": [],
            }

            # Detect issues
            if comparison["ssim"] < 0.95:
                results[name]["issues"].append(f"SSIM={comparison['ssim']:.3f} < 0.95 ((layout differs)")
            if comparison["pHash_distance"] > 5:
                results[name]["issues"].append(f"pHash distance={comparison['pHash_distance']} > 5 (visual differs)")
            if comparison["pixel_diff_pct"] > 1.0:
                results[name]["issues"].append(f"Pixel diff={comparison['pixel_diff_pct']:.1f}% > 1%")

            # Save diff image
            diff_dir = Path(dir_a).parent / "diffs"
            diff_dir.mkdir(exist_ok=True)
            diff_img = (comparison["thresh"])
            cv2.imwrite(str(diff_dir / f"{name}_diff.png"), diff_img)

        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}

    return results


def generate_html_report(results, output_path=None):
    """Generate HTML report with side-by-side comparison."""
    output_path = Path(output_path) if output_path else REPORTS_DIR / f"report_{datetime.now():%Y%m%d_%H%M%S}.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, data in sorted(results.items()):
        if data["status"] != "compared":
            continue
        issues_html = "".join(f"<li>{i}</li>" for i in data.get("issues", []))
        ssim_color = "#4caf50" if data["ssim"] >= 0.95 else "#f44336"
        rows.append(f"""
        <tr>
          <td><strong>{name}</strong></td>
          <td style="color:{ssim_color}">{data['ssim']:.4f}</td>
          <td>{data['pHash_distance']}</td>
          <td>{data['pixel_diff_pct']:.2f}%</td>
          <td><ul>{issues_html}</ul></td>
          <td><a href="diffs/{name}_diff.png" target="_blank">View</a></td>
        </tr>""")

    total = len([r for r in results.values() if r["status"] == "compared"])
    issues_count = len([r for r in results.values() if r["status"] == "compared" and r.get("issues")])

    html = f"""<!DOCTYPE html>
<html dir="rtl"><head><meta charset="utf-8">
<title>تقرير تحليل بصري - Smart Accounting</title>
<style>
body {{ font-family: Arial; margin: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ color: #00d4ff; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
th, td {{ border: 1px solid #333; padding: 10px; text-align: center; }}
th {{ background: #16213e; }}
tr:nth-child(even) {{ background: #0f3460; }}
.ok {{ color: #4caf50; }}
.bad {{ color: #f44336; }}
.summary {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
</style></head><body>
<h1>تقرير تحليل بصري للشاشات</h1>
<div class="summary">
<strong>التاريخ:</strong> {datetime.now():%Y-%m-%d %H:%M}<br>
<strong>إجمالي الشاشات:</strong> {total}<br>
<strong>شاشات بها مشاكل:</strong> <span class="bad">{issues_count}</span><br>
<strong>شاشات سليمة:</strong> <span class="ok">{total - issues_count}</span>
</div>
<table>
<tr><th>الشاشة</th><th>SSIM</th><th>pHash</th><th>Pixel Diff</th><th>المشاكل</th><th>خريطة</th></tr>
{''.join(rows)}
</table></body></html>"""

    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="تحليل بصري لشاشات PyQt6")
    sub = parser.add_subparsers(dest="command")

    cap = sub.add_parser("capture", help="التقط لقطات لجميع الشاشات")
    cap.add_argument("--output", help="مجلد الحفظ")
    cap.add_argument("--width", type=int, default=1280)
    cap.add_argument("--height", type=int, default=800)

    cmp = sub.add_parser("compare", help="قارن بين مجلدين")
    cmp.add_argument("dir_a", help="المجلد الأول (baseline)")
    cmp.add_argument("dir_b", help="المجلد الثاني (الحالي)")

    args = parser.parse_args()

    if args.command == "capture":
        print("=== التقط لقطات الشاشات ===")
        captured = capture_all_screens(args.output, args.width, args.height)
        print(f"\nتم التقاط {len(captured)} شاشة")

    elif args.command == "compare":
        print(f"=== مقارنة: {args.dir_a} vs {args.dir_b} ===")
        results = compare_screenshots(args.dir_a, args.dir_b)
        report = generate_html_report(results)
        print(f"\nالتقرير: {report}")

        # Summary
        issues = {k: v for k, v in results.items() if v.get("issues")}
        if issues:
            print(f"\n⚠️  {len(issues)} شاشات بها مشاكل:")
            for name, data in issues.items():
                print(f"  - {name}: {data['ssim']:.3f} SSIM, {data['pixel_diff_pct']:.1f}% diff")
        else:
            print("\n✅ جميع الشاشات متطابقة")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
