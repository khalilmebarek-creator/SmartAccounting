import ast
from pathlib import Path
for f in sorted(Path("ui/views").glob("*.py")):
    if f.stem.startswith("_") or f.stem in ("view_registry", "screens_assignment_view"):
        continue
    try:
        tree = ast.parse(f.read_text(encoding="utf-8"))
        classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
        print(f"{f.stem}: {classes}")
    except Exception as e:
        print(f"{f.stem}: ERROR {e}")
