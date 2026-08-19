"""Check for remaining unscoped PyQt6 enums."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Known scoped prefixes
QT_ENUMS = {"AlignmentFlag", "WindowType", "TextInteractionFlag", "Orientation",
            "SortOrder", "MatchFlag", "CheckState", "ItemFlag", "Key",
            "FocusPolicy", "ContextMenuPolicy", "WindowState", "WidgetAttribute",
            "FillRule", "LayoutDirection", "ShortcutContext", "PyQt6",
            "Signal", "Slot", "Property", "pyqtSignal", "pyqtSlot", "pyqtProperty"}

SKIP = {"PyQt6", "Signal", "Slot", "Property", "QCore", "QWidgets", "QGui",
        "QSplashScreen", "QApplication", "QDesktopWidget", "pyqtSignal", "pyqtSlot",
        "pyqtProperty", "QMessageBox", "QFileDialog", "QColorDialog", "QFontDialog",
        "QInputDialog", "QProgressDialog"}

issues = []

for f in ROOT.rglob("*.py"):
    if ".venv" in str(f) or "migrate_pyqt6" in str(f):
        continue
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        # Check Qt.UnscopedEnum
        for m in re.finditer(r'(?<!\w)Qt\.([A-Z][A-Za-z_]+)', line):
            val = m.group(1)
            if val in QT_ENUMS or val in SKIP:
                continue
            if val[0].isupper() and '.' not in val:
                issues.append(f'{f.relative_to(ROOT)}:{i}: Qt.{val}')

        # Check QSizePolicy.UnscopedEnum
        for m in re.finditer(r'QSizePolicy\.([A-Z][A-Za-z_]+)', line):
            val = m.group(1)
            if val in ("Policy", "setHorizontalStretch", "setVerticalStretch",
                       "horizontalStretch", "verticalStretch", "setHeightForWidth",
                       "hasHeightForWidth", "controlType", "setControlType"):
                continue
            issues.append(f'{f.relative_to(ROOT)}:{i}: QSizePolicy.{val}')

        # Check QHeaderView.UnscopedEnum
        for m in re.finditer(r'QHeaderView\.([A-Z][A-Za-z_]+)', line):
            val = m.group(1)
            if val in ("ResizeMode", "setSectionResizeMode", "sectionResizeMode",
                       "setStretchLastSection", "setSectionHidden", "isSectionHidden",
                       "horizontalHeader", "verticalHeader", "viewport"):
                continue
            issues.append(f'{f.relative_to(ROOT)}:{i}: QHeaderView.{val}')

issues = sorted(set(issues))
if issues:
    print(f"Found {len(issues)} unscoped enums:")
    for x in issues:
        print(f"  {x}")
else:
    print("All enums properly scoped!")
