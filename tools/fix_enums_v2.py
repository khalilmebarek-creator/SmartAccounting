"""Fix remaining PyQt6 incompatibilities - v2 simple approach."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

count = 0
for f in ROOT.rglob("*.py"):
    if ".venv" in str(f) or "fix_" in f.name or "migrate_" in f.name or "check_" in f.name:
        continue
    c = f.read_text(encoding="utf-8", errors="ignore")
    orig = c

    # Fix QFont.Bold → QFont.Weight.Bold
    c = c.replace("QFont.Bold", "QFont.Weight.Bold")
    c = c.replace("QFont.Normal", "QFont.Weight.Normal")
    c = c.replace("QFont.Light", "QFont.Weight.Light")

    # Fix QTableWidget enums
    c = c.replace("QTableWidget.SingleSelection", "QTableWidget.SelectionMode.SingleSelection")
    c = c.replace("QTableWidget.NoEditTriggers", "QTableWidget.EditTrigger.NoEditTriggers")
    c = c.replace("QTableWidget.ContiguousSelection", "QTableWidget.SelectionMode.ContiguousSelection")

    # Fix QAbstractItemView enums
    c = c.replace("QAbstractItemView.SingleSelection", "QAbstractItemView.SelectionMode.SingleSelection")
    c = c.replace("QAbstractItemView.NoEditTriggers", "QAbstractItemView.EditTrigger.NoEditTriggers")
    c = c.replace("QAbstractItemView.SelectRows", "QAbstractItemView.SelectionBehavior.SelectRows")

    # Fix QMessageBox enums
    for old, new in [
        ("QMessageBox.Warning", "QMessageBox.Icon.Warning"),
        ("QMessageBox.Critical", "QMessageBox.Icon.Critical"),
        ("QMessageBox.Information", "QMessageBox.Icon.Information"),
        ("QMessageBox.Question", "QMessageBox.Icon.Question"),
        ("QMessageBox.Ok", "QMessageBox.StandardButton.Ok"),
        ("QMessageBox.Cancel", "QMessageBox.StandardButton.Cancel"),
        ("QMessageBox.Yes", "QMessageBox.StandardButton.Yes"),
        ("QMessageBox.No", "QMessageBox.StandardButton.No"),
        ("QMessageBox.Save", "QMessageBox.StandardButton.Save"),
        ("QMessageBox.Discard", "QMessageBox.StandardButton.Discard"),
        ("QMessageBox.Apply", "QMessageBox.StandardButton.Apply"),
        ("QMessageBox.Close", "QMessageBox.StandardButton.Close"),
        ("QMessageBox.YesAll", "QMessageBox.StandardButton.YesAll"),
        ("QMessageBox.NoAll", "QMessageBox.StandardButton.NoAll"),
    ]:
        c = c.replace(old, new)

    # Fix QFileDialog.Option
    for old, new in [
        ("QFileDialog.AnyFile", "QFileDialog.Option.AnyFile"),
        ("QFileDialog.ExistingFile", "QFileDialog.Option.ExistingFile"),
        ("QFileDialog.Directory", "QFileDialog.Option.Directory"),
        ("QFileDialog.ExistingFiles", "QFileDialog.Option.ExistingFiles"),
        ("QFileDialog.DontUseNativeDialog", "QFileDialog.Option.DontUseNativeDialog"),
        ("QFileDialog.ShowDirsOnly", "QFileDialog.Option.ShowDirsOnly"),
    ]:
        c = c.replace(old, new)

    # Fix QLineEdit.EchoMode
    c = c.replace("QLineEdit.PasswordEchoOnEdit", "QLineEdit.EchoMode.PasswordEchoOnEdit")

    # Fix QHeaderView.ResizeMode
    c = c.replace("QHeaderView.Stretch", "QHeaderView.ResizeMode.Stretch")
    c = c.replace("QHeaderView.ResizeToContents", "QHeaderView.ResizeMode.ResizeToContents")
    c = c.replace("QHeaderView.Fixed", "QHeaderView.ResizeMode.Fixed")
    c = c.replace("QHeaderView.Interactive", "QHeaderView.ResizeMode.Interactive")

    # Fix QAction/QShortcut - moved from QtWidgets to QtGui in PyQt6
    if "QAction" in c and "from PyQt6.QtWidgets import" in c:
        # Remove QAction from QtWidgets imports
        c = re.sub(
            r'(from PyQt6\.QtWidgets import \()([^)]*?)QAction,?([^)]*?\))',
            lambda m: m.group(1) + m.group(2).replace("QAction,", "").replace("QAction", "") + m.group(3),
            c, flags=re.DOTALL
        )
        # Also handle multiline
        c = re.sub(r',?\s*QAction\s*,?\s*\n', '\n', c)

        # Add QAction to QtGui imports
        if "from PyQt6.QtGui import" in c:
            if "QAction" not in re.search(r'from PyQt6\.QtGui import \(([^)]+)\)', c, re.DOTALL).group(1):
                c = c.replace(
                    "from PyQt6.QtGui import (",
                    "from PyQt6.QtGui import (QAction, ",
                    1
                )
                # Clean up double commas or empty slots
                c = c.replace("(, ", "(")
        else:
            # No QtGui import, add one
            c = c.replace(
                "from PyQt6.QtCore",
                "from PyQt6.QtGui import QAction\nfrom PyQt6.QtCore",
                1
            )

    if "QShortcut" in c and "from PyQt6.QtWidgets import" in c:
        # Remove QShortcut from QtWidgets imports
        c = re.sub(r',?\s*QShortcut\s*,?\s*\n', '\n', c)
        c = re.sub(r',?\s*QShortcut\s*,?\)', ')', c)

        # Add QShortcut to QtGui imports
        if "from PyQt6.QtGui import" in c:
            if "QShortcut" not in re.search(r'from PyQt6\.QtGui import \(([^)]+)\)', c, re.DOTALL).group(1):
                c = c.replace(
                    "from PyQt6.QtGui import (",
                    "from PyQt6.QtGui import (QShortcut, ",
                    1
                )
                c = c.replace("(, ", "(")
        else:
            c = c.replace(
                "from PyQt6.QtCore",
                "from PyQt6.QtGui import QShortcut\nfrom PyQt6.QtCore",
                1
            )

    if c != orig:
        f.write_text(c, encoding="utf-8")
        count += 1
        print(f"  Fixed: {f.relative_to(ROOT)}")

print(f"Fixed {count} files")
