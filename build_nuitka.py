# Nuitka Build Script for Smart Accounting Platform
# ==================================================
# Usage: .venv\Scripts\python.exe build_nuitka.py

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("  Smart Accounting Platform - Nuitka Build")
    print("  (Compiles Python to C → Native Machine Code)")
    print("=" * 60)

    # Clean previous builds
    for d in ["build_nuitka", "dist_nuitka"]:
        if os.path.exists(d):
            import shutil
            shutil.rmtree(d)
            print(f"Cleaned: {d}")

    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--enable-plugin=pyqt5",
        "--enable-plugin=numpy",
        "--include-data-dir=ui/resources=ui/resources",
        "--include-data-dir=modules=modules",
        "--include-data-dir=templates=templates",
        "--include-data-files=resources/app_icon.ico=app_icon.ico",
        "--windows-console-mode=disable",
        "--windows-icon-from-ico=resources/app_icon.ico",
        "--output-dir=dist_nuitka",
        "--output-filename=SmartAccounting.exe",
        "--nofollow-import-to=tkinter,unittest,test,scipy",
        "--company-name=Smart Accounting Team",
        "--product-name=Smart Accounting Platform",
        "--product-version=3.0.0",
        "--file-description=Educational Accounting Software",
        "--file-version=3.0.0.0",
        "--assume-yes-for-downloads",
        "ui/run_ui.py",
    ]

    print("\nBuilding with Nuitka (this may take 5-15 minutes)...\n")

    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("  BUILD SUCCESSFUL!")
        print("  Output: dist_nuitka/ui/run_ui.dist/SmartAccounting.exe")
        print("=" * 60)
    else:
        print("\nBUILD FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
