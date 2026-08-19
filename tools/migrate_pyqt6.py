"""
سكربت ترحيل PyQt6 → PyQt6
يركّز على ملفات المشروع فقط (لا يلمس .venv)
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# === 1. استبدال الاستيرادات ===
IMPORT_REPLACEMENTS = [
    ("from PyQt6.QtWidgets", "from PyQt6.QtWidgets"),
    ("from PyQt6.QtCore", "from PyQt6.QtCore"),
    ("from PyQt6.QtGui", "from PyQt6.QtGui"),
    ("from PyQt6.QtSvg", "from PyQt6.QtSvg"),
    ("from PyQt6.QtPrintSupport", "from PyQt6.QtPrintSupport"),
    ("from PyQt6.QtNetwork", "from PyQt6.QtNetwork"),
    ("from PyQt6.QtTest", "from PyQt6.QtTest"),
    ("import PyQt6", "import PyQt6"),
    ("PyQt6.", "PyQt6."),
]

# === 2. إصلاح Enums (non-scoped → scoped) ===
ENUM_REPLACEMENTS = [
    # Qt
    ("Qt.AlignmentFlag.AlignLeft", "Qt.AlignmentFlag.AlignLeft"),
    ("Qt.AlignmentFlag.AlignRight", "Qt.AlignmentFlag.AlignRight"),
    ("Qt.AlignmentFlag.AlignCenter", "Qt.AlignmentFlag.AlignCenter"),
    ("Qt.AlignmentFlag.AlignTop", "Qt.AlignmentFlag.AlignTop"),
    ("Qt.AlignmentFlag.AlignBottom", "Qt.AlignmentFlag.AlignBottom"),
    ("Qt.AlignmentFlag.AlignHCenter", "Qt.AlignmentFlag.AlignHCenter"),
    ("Qt.AlignmentFlag.AlignVCenter", "Qt.AlignmentFlag.AlignVCenter"),
    ("Qt.AlignmentFlag.AlignJustify", "Qt.AlignmentFlag.AlignJustify"),
    ("Qt.AlignmentFlag.AlignBaseline", "Qt.AlignmentFlag.AlignBaseline"),
    # WindowFlags
    ("Qt.Window", "Qt.WindowType.Window"),
    ("Qt.WindowType.Dialog", "Qt.WindowType.Dialog"),
    ("Qt.WindowType.FramelessWindowHint", "Qt.WindowType.FramelessWindowHint"),
    ("Qt.WindowType.WindowStaysOnTopHint", "Qt.WindowType.WindowStaysOnTopHint"),
    ("Qt.WindowType.WindowCloseButtonHint", "Qt.WindowType.WindowCloseButtonHint"),
    ("Qt.WindowType.SplashScreen", "Qt.WindowType.SplashScreen"),
    ("Qt.WindowType.Tool", "Qt.WindowType.Tool"),
    ("Qt.WindowType.Popup", "Qt.WindowType.Popup"),
    ("Qt.WindowType.SubWindow", "Qt.WindowType.SubWindow"),
    # TextInteractionFlags
    ("Qt.TextInteractionFlag.TextSelectableByMouse", "Qt.TextInteractionFlag.TextSelectableByMouse"),
    ("Qt.TextInteractionFlag.TextBrowserInteraction", "Qt.TextInteractionFlag.TextBrowserInteraction"),
    ("Qt.TextInteractionFlag.NoTextInteraction", "Qt.TextInteractionFlag.NoTextInteraction"),
    # Orientation
    ("Qt.Orientation.Horizontal", "Qt.Orientation.Horizontal"),
    ("Qt.Orientation.Vertical", "Qt.Orientation.Vertical"),
    # SortOrder
    ("Qt.SortOrder.AscendingOrder", "Qt.SortOrder.AscendingOrder"),
    ("Qt.SortOrder.DescendingOrder", "Qt.SortOrder.DescendingOrder"),
    # MatchFlag
    ("Qt.MatchFlag.MatchExactly", "Qt.MatchFlag.MatchExactly"),
    ("Qt.MatchFlag.MatchContains", "Qt.MatchFlag.MatchContains"),
    ("Qt.MatchFlag.MatchStartsWith", "Qt.MatchFlag.MatchStartsWith"),
    ("Qt.MatchFlag.MatchEndsWith", "Qt.MatchFlag.MatchEndsWith"),
    ("Qt.MatchFlag.MatchCaseSensitive", "Qt.MatchFlag.MatchCaseSensitive"),
    ("Qt.MatchFlag.MatchWrap", "Qt.MatchFlag.MatchWrap"),
    # CheckState
    ("Qt.CheckState.Checked", "Qt.CheckState.Checked"),
    ("Qt.CheckState.Unchecked", "Qt.CheckState.Unchecked"),
    ("Qt.CheckState.PartiallyChecked", "Qt.CheckState.PartiallyChecked"),
    # ItemFlag
    ("Qt.ItemFlag.ItemIsEnabled", "Qt.ItemFlag.ItemIsEnabled"),
    ("Qt.ItemFlag.ItemIsSelectable", "Qt.ItemFlag.ItemIsSelectable"),
    ("Qt.ItemFlag.ItemIsEditable", "Qt.ItemFlag.ItemIsEditable"),
    ("Qt.ItemFlag.ItemIsCheckable", "Qt.ItemFlag.ItemIsCheckable"),
    ("Qt.ItemFlag.ItemIsTristate", "Qt.ItemFlag.ItemIsTristate"),
    # Key
    ("Qt.Key.Key_Escape", "Qt.Key.Key_Escape"),
    ("Qt.Key.Key_Return", "Qt.Key.Key_Return"),
    ("Qt.Key.Key_Enter", "Qt.Key.Key_Enter"),
    ("Qt.Key.Key_Tab", "Qt.Key.Key_Tab"),
    ("Qt.Key.Key_Backtab", "Qt.Key.Key_Backtab"),
    ("Qt.Key.Key_Delete", "Qt.Key.Key_Delete"),
    ("Qt.Key.Key_Insert", "Qt.Key.Key_Insert"),
    ("Qt.Key.Key_Home", "Qt.Key.Key_Home"),
    ("Qt.Key.Key_End", "Qt.Key.Key_End"),
    ("Qt.Key.Key_Left", "Qt.Key.Key_Left"),
    ("Qt.Key.Key_Right", "Qt.Key.Key_Right"),
    ("Qt.Key.Key_Up", "Qt.Key.Key_Up"),
    ("Qt.Key.Key_Down", "Qt.Key.Key_Down"),
    ("Qt.Key.Key_PageUp", "Qt.Key.Key_PageUp"),
    ("Qt.Key.Key_PageDown", "Qt.Key.Key_PageDown"),
    ("Qt.Key.Key_Space", "Qt.Key.Key_Space"),
    ("Qt.Key.Key_F1", "Qt.Key.Key_F1"),
    ("Qt.Key.Key_F2", "Qt.Key.Key_F2"),
    ("Qt.Key.Key_F3", "Qt.Key.Key_F3"),
    ("Qt.Key.Key_F4", "Qt.Key.Key_F4"),
    ("Qt.Key.Key_F5", "Qt.Key.Key_F5"),
    ("Qt.Key.Key_F6", "Qt.Key.Key_F6"),
    ("Qt.Key.Key_F7", "Qt.Key.Key_F7"),
    ("Qt.Key.Key_F8", "Qt.Key.Key_F8"),
    ("Qt.Key.Key_F9", "Qt.Key.Key_F9"),
    ("Qt.Key.Key_F10", "Qt.Key.Key_F10"),
    ("Qt.Key.Key_F11", "Qt.Key.Key_F11"),
    ("Qt.Key.Key_F12", "Qt.Key.Key_F12"),
    # FocusPolicy
    ("Qt.FocusPolicy.NoFocus", "Qt.FocusPolicy.NoFocus"),
    ("Qt.FocusPolicy.TabFocus", "Qt.FocusPolicy.TabFocus"),
    ("Qt.FocusPolicy.ClickFocus", "Qt.FocusPolicy.ClickFocus"),
    ("Qt.FocusPolicy.StrongFocus", "Qt.FocusPolicy.StrongFocus"),
    ("Qt.FocusPolicy.WheelFocus", "Qt.FocusPolicy.WheelFocus"),
    # ContextMenuPolicy
    ("Qt.ContextMenuPolicy.DefaultContextMenu", "Qt.ContextMenuPolicy.DefaultContextMenu"),
    ("Qt.ContextMenuPolicy.NoContextMenu", "Qt.ContextMenuPolicy.NoContextMenu"),
    ("Qt.ContextMenuPolicy.ActionsContextMenu", "Qt.ContextMenuPolicy.ActionsContextMenu"),
    ("Qt.ContextMenuPolicy.CustomContextMenu", "Qt.ContextMenuPolicy.CustomContextMenu"),
    # WindowState
    ("Qt.WindowState.WindowNoState", "Qt.WindowState.WindowNoState"),
    ("Qt.WindowState.WindowMinimized", "Qt.WindowState.WindowMinimized"),
    ("Qt.WindowState.WindowMaximized", "Qt.WindowState.WindowMaximized"),
    ("Qt.WindowState.WindowFullScreen", "Qt.WindowState.WindowFullScreen"),
    ("Qt.WindowState.WindowActive", "Qt.WindowState.WindowActive"),
    # WidgetAttribute
    ("Qt.WidgetAttribute.WA_DeleteOnClose", "Qt.WidgetAttribute.WA_DeleteOnClose"),
    ("Qt.WidgetAttribute.WA_TranslucentBackground", "Qt.WidgetAttribute.WA_TranslucentBackground"),
    ("Qt.WidgetAttribute.WA_DontShowOnScreen", "Qt.WidgetAttribute.WA_DontShowOnScreen"),
    ("Qt.WidgetAttribute.WA_ShowWithoutActivating", "Qt.WidgetAttribute.WA_ShowWithoutActivating"),
    ("Qt.WidgetAttribute.WA_StyledBackground", "Qt.WidgetAttribute.WA_StyledBackground"),
    ("Qt.WidgetAttribute.WA_Hover", "Qt.WidgetAttribute.WA_Hover"),
    ("Qt.WidgetAttribute.WA_MouseTracking", "Qt.WidgetAttribute.WA_MouseTracking"),
    ("Qt.WidgetAttribute.WA_KeyCompression", "Qt.WidgetAttribute.WA_KeyCompression"),
    ("Qt.WidgetAttribute.WA_InputMethodEnabled", "Qt.WidgetAttribute.WA_InputMethodEnabled"),
    ("Qt.WidgetAttribute.WA_OpaquePaintEvent", "Qt.WidgetAttribute.WA_OpaquePaintEvent"),
    ("Qt.WidgetAttribute.WA_StaticContents", "Qt.WidgetAttribute.WA_StaticContents"),
    # FillRule
    ("Qt.FillRule.OddEvenFill", "Qt.FillRule.OddEvenFill"),
    ("Qt.FillRule.WindingFill", "Qt.FillRule.WindingFill"),
    # LayoutDirection
    ("Qt.LayoutDirection.LeftToRight", "Qt.LayoutDirection.LeftToRight"),
    ("Qt.LayoutDirection.RightToLeft", "Qt.LayoutDirection.RightToLeft"),
    # ShortcutContext
    ("Qt.ShortcutContext.WindowShortcut", "Qt.ShortcutContext.WindowShortcut"),
    ("Qt.ShortcutContext.WidgetShortcut", "Qt.ShortcutContext.WidgetShortcut"),
    ("Qt.ShortcutContext.ApplicationShortcut", "Qt.ShortcutContext.ApplicationShortcut"),

    # QSizePolicy
    ("QSizePolicy.Policy.Expanding", "QSizePolicy.Policy.Expanding"),
    ("QSizePolicy.Policy.Preferred", "QSizePolicy.Policy.Preferred"),
    ("QSizePolicy.Policy.Fixed", "QSizePolicy.Policy.Fixed"),
    ("QSizePolicy.Policy.Minimum", "QSizePolicy.Policy.Minimum"),
    ("QSizePolicy.Policy.Maximum", "QSizePolicy.Policy.Maximum"),
    ("QSizePolicy.Policy.MinimumExpanding", "QSizePolicy.Policy.MinimumExpanding"),
    ("QSizePolicy.Policy.Ignored", "QSizePolicy.Policy.Ignored"),
    ("QSizePolicy.Policy.Expanding", "QSizePolicy.Policy.Expanding"),
    ("QSizePolicy.Policy.MinimumExpanding", "QSizePolicy.Policy.MinimumExpanding"),

    # QHeaderView
    ("QHeaderView.ResizeMode.Stretch", "QHeaderView.ResizeMode.Stretch"),
    ("QHeaderView.ResizeMode.ResizeToContents", "QHeaderView.ResizeMode.ResizeToContents"),
    ("QHeaderView.Fixed", "QHeaderView.ResizeMode.Fixed"),
    ("QHeaderView.ResizeMode.Interactive", "QHeaderView.ResizeMode.Interactive"),
    ("QHeaderView.Custom", "QHeaderView.ResizeMode.Custom"),

    # QAbstractItemView
    ("QAbstractItemView.EditTrigger.NoEditTriggers", "QAbstractItemView.EditTrigger.NoEditTriggers"),
    ("QAbstractItemView.EditTrigger.AllEditTriggers", "QAbstractItemView.EditTrigger.AllEditTriggers"),
    ("QAbstractItemView.EditTrigger.DoubleClicked", "QAbstractItemView.EditTrigger.DoubleClicked"),
    ("QAbstractItemView.EditTrigger.EditKeyPressed", "QAbstractItemView.EditTrigger.EditKeyPressed"),
    ("QAbstractItemView.EditTrigger.SelectedClicked", "QAbstractItemView.EditTrigger.SelectedClicked"),
    ("QAbstractItemView.SelectionMode.ContiguousSelection", "QAbstractItemView.SelectionMode.ContiguousSelection"),
    ("QAbstractItemView.SelectionMode.ExtendedSelection", "QAbstractItemView.SelectionMode.ExtendedSelection"),
    ("QAbstractItemView.SelectionMode.MultiSelection", "QAbstractItemView.SelectionMode.MultiSelection"),
    ("QAbstractItemView.SelectionMode.NoSelection", "QAbstractItemView.SelectionMode.NoSelection"),
    ("QAbstractItemView.SelectionMode.SingleSelection", "QAbstractItemView.SelectionMode.SingleSelection"),
    ("QAbstractItemView.SelectionBehavior.SelectRows", "QAbstractItemView.SelectionBehavior.SelectRows"),
    ("QAbstractItemView.SelectionBehavior.SelectColumns", "QAbstractItemView.SelectionBehavior.SelectColumns"),
    ("QAbstractItemView.SelectionBehavior.SelectItems", "QAbstractItemView.SelectionBehavior.SelectItems"),

    # QTableWidget
    ("QTableWidget.SelectRows", "QTableWidget.SelectionBehavior.SelectRows"),
    ("QTableWidget.NoEditTriggers", "QTableWidget.EditTrigger.NoEditTriggers"),
    ("QTableWidget.ContiguousSelection", "QTableWidget.SelectionMode.ContiguousSelection"),

    # QComboBox
    ("QComboBox.InsertPolicy.NoInsert", "QComboBox.InsertPolicy.NoInsert"),
    ("QComboBox.InsertPolicy.InsertAtBottom", "QComboBox.InsertPolicy.InsertAtBottom"),
    ("QComboBox.InsertPolicy.InsertAtTop", "QComboBox.InsertPolicy.InsertAtTop"),
    ("QComboBox.InsertPolicy.InsertAtCurrent", "QComboBox.InsertPolicy.InsertAtCurrent"),
    ("QComboBox.InsertPolicy.InsertAlphabetically", "QComboBox.InsertPolicy.InsertAlphabetically"),

    # QFrame
    ("QFrame.Box", "QFrame.Shape.Box"),
    ("QFrame.Shape.Panel", "QFrame.Shape.Panel"),
    ("QFrame.Shape.StyledPanel", "QFrame.Shape.StyledPanel"),
    ("QFrame.Shape.HLine", "QFrame.Shape.HLine"),
    ("QFrame.Shape.VLine", "QFrame.Shape.VLine"),
    ("QFrame.Shape.NoFrame", "QFrame.Shape.NoFrame"),
    ("QFrame.Shadow.Plain", "QFrame.Shadow.Plain"),
    ("QFrame.Shadow.Raised", "QFrame.Shadow.Raised"),
    ("QFrame.Shadow.Sunken", "QFrame.Shadow.Sunken"),

    # QLineEdit
    ("QLineEdit.EchoMode.NoEcho", "QLineEdit.EchoMode.NoEcho"),
    ("QLineEdit.EchoMode.Normal", "QLineEdit.EchoMode.Normal"),
    ("QLineEdit.EchoMode.Password", "QLineEdit.EchoMode.Password"),
    ("QLineEdit.EchoMode.PasswordEchoOnEdit", "QLineEdit.EchoMode.PasswordEchoOnEdit"),

    # QMessageBox
    ("QMessageBox.ButtonRole.NoRole", "QMessageBox.ButtonRole.NoRole"),
    ("QMessageBox.ButtonRole.AcceptRole", "QMessageBox.ButtonRole.AcceptRole"),
    ("QMessageBox.ButtonRole.RejectRole", "QMessageBox.ButtonRole.RejectRole"),
    ("QMessageBox.ButtonRole.DestructiveRole", "QMessageBox.ButtonRole.DestructiveRole"),
    ("QMessageBox.ButtonRole.ActionRole", "QMessageBox.ButtonRole.ActionRole"),
    ("QMessageBox.ButtonRole.HelpRole", "QMessageBox.ButtonRole.HelpRole"),
    ("QMessageBox.ButtonRole.YesRole", "QMessageBox.ButtonRole.YesRole"),
    ("QMessageBox.ButtonRole.NoRole", "QMessageBox.ButtonRole.NoRole"),
    ("QMessageBox.ButtonRole.ApplyRole", "QMessageBox.ButtonRole.ApplyRole"),
    # QMessageBox StandardButtons
    ("QMessageBox.StandardButton.Ok", "QMessageBox.StandardButton.Ok"),
    ("QMessageBox.StandardButton.Cancel", "QMessageBox.StandardButton.Cancel"),
    ("QMessageBox.Yes", "QMessageBox.StandardButton.Yes"),
    ("QMessageBox.No", "QMessageBox.StandardButton.No"),
    ("QMessageBox.StandardButton.Abort", "QMessageBox.StandardButton.Abort"),
    ("QMessageBox.StandardButton.Retry", "QMessageBox.StandardButton.Retry"),
    ("QMessageBox.Ignore", "QMessageBox.StandardButton.Ignore"),
    ("QMessageBox.StandardButton.YesAll", "QMessageBox.StandardButton.YesAll"),
    ("QMessageBox.StandardButton.NoAll", "QMessageBox.StandardButton.NoAll"),
    # QMessageBox Icon
    ("QMessageBox.Icon.Information", "QMessageBox.Icon.Information"),
    ("QMessageBox.Icon.Warning", "QMessageBox.Icon.Warning"),
    ("QMessageBox.Icon.Critical", "QMessageBox.Icon.Critical"),
    ("QMessageBox.Icon.Question", "QMessageBox.Icon.Question"),

    # QFileDialog
    ("QFileDialog.Option.AnyFile", "QFileDialog.Option.AnyFile"),
    ("QFileDialog.Option.ExistingFile", "QFileDialog.Option.ExistingFile"),
    ("QFileDialog.Option.Directory", "QFileDialog.Option.Directory"),
    ("QFileDialog.Option.ExistingFiles", "QFileDialog.Option.ExistingFiles"),
    ("QFileDialog.Option.DontUseNativeDialog", "QFileDialog.Option.DontUseNativeDialog"),

    # QColorDialog
    ("QColorDialog.ColorDialogOption.NoAlpha", "QColorDialog.ColorDialogOption.NoAlpha"),
    ("QColorDialog.ColorDialogOption.ShowAlphaChannel", "QColorDialog.ColorDialogOption.ShowAlphaChannel"),
    ("QColorDialog.DontUseNativeDialog", "QColorDialog.ColorDialogOption.DontUseNativeDialog"),

    # QFontDialog
    ("QFontDialog.FontDialogOption.NoButtons", "QFontDialog.FontDialogOption.NoButtons"),
    ("QFontDialog.DontUseNativeDialog", "QFontDialog.FontDialogOption.DontUseNativeDialog"),

    # QSizePolicy (already added above, but check for 'Min' etc)
    ("QSizePolicy.Policy.Minimum", "QSizePolicy.Policy.Minimum"),
    ("QSizePolicy.Policy.Maximum", "QSizePolicy.Policy.Maximum"),
    ("QSizePolicy.Policy.Expanding", "QSizePolicy.Policy.Expanding"),

    # QHeaderView
    ("QHeaderView.ResizeMode.Stretch", "QHeaderView.ResizeMode.Stretch"),

    # QItemSelectionModel
    ("QItemSelectionModel.SelectionFlag.ClearAndSelect", "QItemSelectionModel.SelectionFlag.ClearAndSelect"),
    ("QItemSelectionModel.Select", "QItemSelectionModel.SelectionFlag.Select"),
    ("QItemSelectionModel.SelectionFlag.Deselect", "QItemSelectionModel.SelectionFlag.Deselect"),
    ("QItemSelectionModel.SelectionFlag.Toggle", "QItemSelectionModel.SelectionFlag.Toggle"),
    ("QItemSelectionModel.Current", "QItemSelectionModel.SelectionFlag.Current"),

    # QTextEdit
    ("QTextEdit.LineWrapMode.NoWrap", "QTextEdit.LineWrapMode.NoWrap"),
    ("QTextEdit.LineWrapMode.WidgetWidth", "QTextEdit.LineWrapMode.WidgetWidth"),
    ("QTextEdit.LineWrapMode.FixedPixelWidth", "QTextEdit.LineWrapMode.FixedPixelWidth"),
    ("QTextEdit.LineWrapMode.FixedColumnWidth", "QTextEdit.LineWrapMode.FixedColumnWidth"),

    # QProgressBar
    ("QProgressBar.Direction.TopToBottom", "QProgressBar.Direction.TopToBottom"),
    ("QProgressBar.Direction.BottomToTop", "QProgressBar.Direction.BottomToTop"),

    # QPainter
    ("QPainter.CompositionMode.CompositionMode_SourceOver", "QPainter.CompositionMode.CompositionMode_SourceOver"),
    ("QPainter.CompositionMode_Source", "QPainter.CompositionMode.CompositionMode_Source"),
    ("QPainter.CompositionMode.CompositionMode_DestinationOver", "QPainter.CompositionMode.CompositionMode_DestinationOver"),
    ("QPainter.CompositionMode.CompositionMode_Clear", "QPainter.CompositionMode.CompositionMode_Clear"),
    ("QPainter.CompositionMode.CompositionMode_SourceAtop", "QPainter.CompositionMode.CompositionMode_SourceAtop"),
    ("QPainter.CompositionMode.CompositionMode_DestinationAtop", "QPainter.CompositionMode.CompositionMode_DestinationAtop"),
    ("QPainter.CompositionMode.CompositionMode_SourceIn", "QPainter.CompositionMode.CompositionMode_SourceIn"),
    ("QPainter.CompositionMode.CompositionMode_DestinationIn", "QPainter.CompositionMode.CompositionMode_DestinationIn"),
    ("QPainter.CompositionMode.CompositionMode_SourceOut", "QPainter.CompositionMode.CompositionMode_SourceOut"),
    ("QPainter.CompositionMode.CompositionMode_DestinationOut", "QPainter.CompositionMode.CompositionMode_DestinationOut"),
    ("QPainter.CompositionMode.CompositionMode_SourceOver", "QPainter.CompositionMode.CompositionMode_SourceOver"),
    ("QPainter.CompositionMode.CompositionMode_Lighten", "QPainter.CompositionMode.CompositionMode_Lighten"),
    ("QPainter.CompositionMode.CompositionMode_Darken", "QPainter.CompositionMode.CompositionMode_Darken"),
    ("QPainter.CompositionMode.CompositionMode_ColorDodge", "QPainter.CompositionMode.CompositionMode_ColorDodge"),
    ("QPainter.CompositionMode.CompositionMode_ColorBurn", "QPainter.CompositionMode.CompositionMode_ColorBurn"),
    ("QPainter.CompositionMode.CompositionMode_HardLight", "QPainter.CompositionMode.CompositionMode_HardLight"),
    ("QPainter.CompositionMode.CompositionMode_SoftLight", "QPainter.CompositionMode.CompositionMode_SoftLight"),
    ("QPainter.CompositionMode.CompositionMode_Difference", "QPainter.CompositionMode.CompositionMode_Difference"),
    ("QPainter.CompositionMode.CompositionMode_Exclusion", "QPainter.CompositionMode.CompositionMode_Exclusion"),
    ("QPainter.CompositionMode.CompositionMode_Multiply", "QPainter.CompositionMode.CompositionMode_Multiply"),
    ("QPainter.CompositionMode.CompositionMode_Screen", "QPainter.CompositionMode.CompositionMode_Screen"),
    ("QPainter.CompositionMode.CompositionMode_Overlay", "QPainter.CompositionMode.CompositionMode_Overlay"),
    ("QPainter.CompositionMode.CompositionMode_ColorBurn", "QPainter.CompositionMode.CompositionMode_ColorBurn"),
    ("QPainter.CompositionMode.CompositionMode_Hue", "QPainter.CompositionMode.CompositionMode_Hue"),
    ("QPainter.CompositionMode.CompositionMode_Saturation", "QPainter.CompositionMode.CompositionMode_Saturation"),
    ("QPainter.CompositionMode_Color", "QPainter.CompositionMode.CompositionMode_Color"),
    ("QPainter.CompositionMode.CompositionMode_Value", "QPainter.CompositionMode.CompositionMode_Value"),

    # QDesktopWidget → QScreen (handled separately)
]

# === 3. إصلاح exec_() ===
EXEC_REPLACEMENTS = [
    (r'\.exec_\(\)', '.exec()'),
    (r'\.exec_\("', '.exec("'),
]


def migrate_file(filepath):
    """Migrate a single file from PyQt6 to PyQt6."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return False

    original = content

    # Skip .venv files
    if ".venv" in str(filepath):
        return False

    # Only process files that actually contain PyQt6
    if "PyQt6" not in content and "PyQt6" not in filepath.name:
        return False

    # 1. Replace imports
    for old, new in IMPORT_REPLACEMENTS:
        content = content.replace(old, new)

    # 2. Replace enums (do longest first to avoid partial matches)
    sorted_enums = sorted(ENUM_REPLACEMENTS, key=lambda x: -len(x[0]))
    for old, new in sorted_enums:
        # Only replace if not already scoped
        if new.split(".")[-1] not in content.split(old)[0] if old in content else True:
            content = content.replace(old, new)

    # 3. Fix exec_() → exec()
    for pattern, replacement in EXEC_REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    # 4. Fix QDesktopWidget → QScreen
    content = content.replace("QApplication.primaryScreen()", "QApplication.primaryScreen()")

    # 5. Fix pyplot backend
    content = content.replace(
        "matplotlib.use('Agg')",
        "matplotlib.use('Agg')"
    )

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    migrated = []
    skipped = []

    for filepath in sorted(PROJECT_ROOT.rglob("*.py")):
        if ".venv" in str(filepath) or "site-packages" in str(filepath):
            continue

        if migrate_file(filepath):
            migrated.append(filepath.relative_to(PROJECT_ROOT))
        else:
            skipped.append(filepath.relative_to(PROJECT_ROOT))

    print(f"Migrated: {len(migrated)} files")
    for f in migrated:
        print(f"  [OK] {f}")

    print(f"\nSkipped: {len(skipped)} files")


if __name__ == "__main__":
    main()
