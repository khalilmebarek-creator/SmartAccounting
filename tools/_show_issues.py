import json
d = json.load(open("artifacts/ui_reports/layout_analysis.json", "r", encoding="utf-8"))

# Show screens with overlaps
for name, data in sorted(d.items()):
    issues = data.get("issues", [])
    overlaps = [i for i in issues if i["type"] == "overlap"]
    if overlaps:
        print(f"\n=== {name} — OVERLAPS ===")
        for o in overlaps:
            print(f"  {o['severity']}: {o['detail']}")

# Show worst table_misalignment screens
print("\n\n=== WORST TABLE MISALIGNMENT (top 10) ===")
ranked = []
for name, data in d.items():
    issues = data.get("issues", [])
    misalign = [i for i in issues if i["type"] == "table_misalignment"]
    if misalign:
        ranked.append((name, len(misalign), misalign))
ranked.sort(key=lambda x: -x[1])
for name, count, mis in ranked[:10]:
    print(f"\n  {name}: {count} issues")
    for m in mis[:5]:
        print(f"    - {m['detail']}")
