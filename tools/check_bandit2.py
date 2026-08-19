import json
d = json.load(open("bandit_scan.json", "r", encoding="utf-8"))
results = d.get("results", [])
print(f"Total issues: {len(results)}")
sev = {}
cat = {}
for r in results:
    s = r["issue_severity"]
    c = r["test_id"]
    sev[s] = sev.get(s, 0) + 1
    cat[c] = cat.get(c, 0) + 1
print("By severity:", dict(sorted(sev.items())))
print("By category:", dict(sorted(cat.items())))
# Show HIGH issues
for r in results:
    if r["issue_severity"] == "HIGH":
        print(f"  HIGH: {r['test_id']} {r['filename']}:{r['line_number']} {r['issue_text']}")
# Show MEDIUM try-except-pass
for r in results:
    if r["test_id"] == "B110" and r["issue_severity"] in ("MEDIUM", "HIGH"):
        print(f"  {r['issue_severity']}: {r['filename']}:{r['line_number']} {r['issue_text']}")
