import json
d = json.load(open("artifacts/ui_reports/layout_analysis.json", "r", encoding="utf-8"))

# Ledger details
ledger = d.get("ledger", {})
texts = ledger.get("texts", [])
print("=== LEDGER TEXTS ===")
for t in texts[:30]:
    print(f"  [{t['x']:4d},{t['y']:4d} {t['w']:3d}x{t['h']:3d}] conf={t['conf']:3d} '{t['text']}'")

issues = ledger.get("issues", [])
print(f"\n=== LEDGER ISSUES ({len(issues)}) ===")
for i in issues:
    print(f"  {i['type']}: {i}")
