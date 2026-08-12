# يولد fixtures لاختبارات تطبيق الجوال من محركات سطح المكتب
# الخرج: mobile/test/fixtures/demo_snapshot_plain.json + _encrypted.json + health_expected.json
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.app_state import state
from modules.cloud_sync import _build_payload

state.clear()
state.company_name = "Mobile Test Co"
state.company_name_fr = "Mobile Test Co FR"
state.financial_data = {
    "fiscal_year": 2024,
    "current_assets": 150000, "inventory": 25000, "cash": 12000,
    "total_assets": 600000, "current_liabilities": 60000,
    "total_liabilities": 220000, "equity": 380000,
    "revenue": 250000, "cogs": 140000, "gross_profit": 50000,
    "operating_expenses": 25000, "net_income": 20000,
    "avg_receivables": 45000, "avg_inventory": 25000,
    "avg_payables": 20000,
}
state.ratios = {
    "current_ratio": 2.5, "quick_ratio": 1.5, "cash_ratio": 0.2,
    "gross_margin": 20.0, "net_profit_margin": 8.0, "operating_margin": 10.0,
    "roa": 3.33, "roe": 5.26, "return_on_capital": 4.5,
    "debt_to_equity": 0.58, "debt_ratio": 36.67, "interest_coverage": 6.0,
    "asset_turnover": 0.42, "inventory_turnover": 5.6,
    "receivables_turnover": 5.56, "payables_turnover": 7.0,
    "working_capital_ratio": 1.5, "z_score": 3.2,
}
state.tax_obligations = [
    {"tax_type": "TVA", "due_day": 20, "month": 8, "status": "pending", "amount": 3958.33},
    {"tax_type": "CNAS", "due_day": 30, "month": 8, "status": "pending", "amount": 1500.0},
]

payload = _build_payload(state)

from modules import cloud_sync
import hashlib

raw = json.dumps(payload, ensure_ascii=False)
wrapper_plain = {
    "app": "SmartAccounting",
    "format": 1,
    "timestamp": 1755010000.0,
    "destination": "fixtures",
    "encrypted": False,
    "checksum": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    "data": raw,
}
wrapper_encrypted = {
    "app": "SmartAccounting",
    "format": 1,
    "timestamp": 1755010000.0,
    "destination": "fixtures",
    "encrypted": True,
    "checksum": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    "data": cloud_sync.encrypt_payload(payload, "test-pass"),
}

from modules.ai_platform import compute_health_score, compute_risk_radar, platform_analysis
health_expected = {
    "health": compute_health_score(),
    "radar": compute_risk_radar(),
    "summary": platform_analysis()["executive_summary"],
    "recommendations": platform_analysis()["recommendations"],
}

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "mobile", "test", "fixtures")
os.makedirs(out_dir, exist_ok=True)
for name, obj in (
    ("demo_snapshot_plain.json", wrapper_plain),
    ("demo_snapshot_encrypted.json", wrapper_encrypted),
    ("health_expected.json", health_expected),
):
    with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    print(f"wrote {name}")
print("OK")
