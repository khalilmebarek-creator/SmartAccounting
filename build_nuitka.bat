@echo off
cd /d C:\Users\khalile\Desktop\Accounting_Platform
.venv\Scripts\python.exe -m nuitka --standalone --assume-yes-for-downloads --output-dir=dist_nuitka --output-filename=SmartAccounting.exe --nofollow-import-to=tkinter,unittest,test,scipy --windows-console-mode=disable --windows-icon-from-ico=resources/app_icon.ico --include-data-dir=ui/resources=ui/resources --include-data-dir=modules=modules --include-data-dir=templates=templates --include-data-files=resources/app_icon.ico=app_icon.ico --enable-plugin=pyqt5 ui/run_ui.py > nuitka_log.txt 2>&1
echo BUILD_DONE > nuitka_status.txt
