"""Geometry audit: flag overlapping / clipped / zero-size widgets per screen.

Usage: python tools/geometry_audit.py
Builds each view offscreen at 1280x800 and reports:
  - input fields overlapping table widgets (fields drawn over tables)
  - widgets extending beyond their parent's horizontal bounds
  - visible input fields with height < 38px
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QDateEdit,
)

app = QApplication.instance() or QApplication(sys.argv)

from ui.views.view_registry import VIEW_REGISTRY
from ui.app_state import state

state.clear()

INPUT_TYPES = (QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit)


def audit_view(view: QWidget, name: str, vid: int):
    view.resize(1280, 800)
    view.show()
    app.processEvents()

    issues = []
    tables = view.findChildren(QTableWidget)
    inputs = [w for w in view.findChildren(QWidget) if isinstance(w, INPUT_TYPES)]

    for inp in inputs:
        if not inp.isVisible():
            continue
        r = inp.geometry()
        mapped = inp.mapTo(view, r.topLeft())
        rect = inp.rect().translated(mapped)
        if rect.height() < 38:
            issues.append(f"field {type(inp).__name__} height {rect.height()}px < 38")
        parent = inp.parentWidget()
        if parent:
            if rect.right() > parent.width() + 4:
                issues.append(
                    f"field {type(inp).__name__} overflows right by "
                    f"{rect.right() - parent.width()}px")
        for tbl in tables:
            if not tbl.isVisible():
                continue
            tr = tbl.rect().translated(tbl.mapTo(view, tbl.rect().topLeft()))
            if rect.intersects(tr):
                issues.append(
                    f"field {type(inp).__name__} overlaps a table "
                    f"(at {rect.left()},{rect.top()})")
                break

    for tbl in tables:
        if not tbl.isVisible():
            continue
        tr = tbl.rect().translated(tbl.mapTo(view, tbl.rect().topLeft()))
        parent = tbl.parentWidget()
        if parent and tr.right() > parent.width() + 4:
            issues.append(
                f"table overflows right by {tr.right() - parent.width()}px")

    view.hide()
    return issues


def main():
    import importlib
    total = 0
    for vid in sorted(VIEW_REGISTRY):
        name, module_name, cls = VIEW_REGISTRY[vid]
        try:
            module = importlib.import_module(module_name)
            view = getattr(module, cls)()
        except Exception as exc:
            print(f"[{vid}] {name}: LOAD ERROR {exc}")
            continue
        issues = audit_view(view, name, vid)
        for i in issues:
            print(f"[{vid}] {name}: {i}")
            total += 1
        view.deleteLater()
    print(f"\nTOTAL issues: {total}")


if __name__ == "__main__":
    main()
