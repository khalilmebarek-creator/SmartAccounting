"""Fix remaining unscoped enums."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

EXTRAS = [
    ("QHeaderView.Stretch", "QHeaderView.ResizeMode.Stretch"),
    ("Qt.PointingHandCursor", "Qt.CursorShape.PointingHandCursor"),
    ("Qt.RichText", "Qt.TextFormat.RichText"),
    ("Qt.ShiftModifier", "Qt.KeyboardModifier.ShiftModifier"),
    ("Qt.KeepAspectRatio", "Qt.AspectRatioMode.KeepAspectRatio"),
    ("Qt.SmoothTransformation", "Qt.TransformationMode.SmoothTransformation"),
]

count = 0
for f in ROOT.rglob("*.py"):
    if ".venv" in str(f) or "migrate_pyqt6" in str(f) or "check_enums" in str(f) or "fix_enums" in str(f):
        continue
    c = f.read_text(encoding="utf-8", errors="ignore")
    orig = c
    for old, new in EXTRAS:
        c = c.replace(old, new)
    # Remove AA_ enums (removed in PyQt6, no longer needed)
    c = re.sub(r"\n\s*QApplication\.setAttribute\(Qt\.AA_\w+.*?\)\n", "\n", c)
    if c != orig:
        f.write_text(c, encoding="utf-8")
        count += 1
        print(f"  Fixed: {f.relative_to(ROOT)}")

print(f"Fixed {count} files")
