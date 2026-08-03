@echo off
cd /d C:\Users\khalile\Desktop\Accounting_Platform
.venv\Scripts\python.exe build_nuitka.py > nuitka_log.txt 2>&1
echo BUILD_DONE > nuitka_status.txt
