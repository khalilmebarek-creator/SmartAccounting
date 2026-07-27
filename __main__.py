# تشغيل المشروع عبر: python -m accounting_platform
# ================================================

import sys
import os

# التأكد من أن مسار المشروع في sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """نقطة الدخول الرئيسية"""
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from main import main as cli_main
        cli_main()
    else:
        from ui.run_ui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
