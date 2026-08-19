import json

with open('bandit_all.json') as f:
    data = json.load(f)

results = data.get('results', [])

# Check SQL issues
sql_issues = [r for r in results if r['test_id'] == 'B608']
seen = set()
for r in sql_issues[:15]:
    fn = r['filename'].replace('C:\\Users\\khalile\\Desktop\\Accounting_Platform\\', '')
    key = fn + ':' + str(r['line_number'])
    if key not in seen:
        seen.add(key)
        code = r.get('code', '').strip()[:150]
        print(f'{fn}:{r["line_number"]}')
        print(f'  {code}')
        print()

print(f'\nTotal SQL: {len(sql_issues)}')
print(f'Unique locations: {len(seen)}')
