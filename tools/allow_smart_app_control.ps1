# =============================================================
# Smart Accounting Platform - Smart App Control Helper
# =============================================================
# يفحص حالة Smart App Control ويشرح كيفية إيقافه، ثم يضيف
# استثناء Defender للمثبّت والتطبيق حتى يعمل فوراً.
#
# الاستخدام:
#   PowerShell (Administrator):
#     powershell -ExecutionPolicy Bypass -File tools\allow_smart_app_control.ps1
# =============================================================

$ErrorActionPreference = "Stop"

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-SACState {
    param($Value)
    switch ($Value) {
        0 { "Off (مُعطّل)" }
        1 { "On / Enforcement (مفعّل بالكامل)" }
        2 { "On / Warning (تفعيل جزئي - تحذير)" }
        default { "غير معروف" }
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Smart App Control - Helper v1.0" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1) فحص حالة Smart App Control
$sac = (Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy" -ErrorAction SilentlyContinue).VerifiedAndReputablePolicyState
if ($null -eq $sac) {
    Write-Host "[1] حالة Smart App Control: غير مفعّل (لا توجد سياسة)." -ForegroundColor Green
} else {
    Write-Host "[1] حالة Smart App Control: $(Get-SACState $sac)" -ForegroundColor Yellow
    if ($sac -ge 1) {
        Write-Host ""
        Write-Host "    المشكلة: Windows 11 يحجب الـ exe غير الموقّع رقمياً." -ForegroundColor Red
        Write-Host "    الإيقاف يتم من إعدادات Windows (لا يمكن إعادته دون إعادة تثبيت النظام):" -ForegroundColor Yellow
        Write-Host "      Windows Security (أمان Windows)" -ForegroundColor White
        Write-Host "        -> App & browser control (التحكم في التطبيق والمتصفح)" -ForegroundColor White
        Write-Host "        -> Smart App Control settings -> Off" -ForegroundColor White
    }
}

Write-Host ""

# 2) إضافة استثناء Defender للمثبّت والتطبيق
Write-Host "[2] إضافة استثناء Defender للمثبّت ومجلد التطبيق..." -ForegroundColor Cyan
$root = Split-Path -Parent $PSScriptRoot
$installerDir = Join-Path $root "installer_output"
$distDir = Join-Path $root "dist_nuitka"

$targets = @()
if (Test-Path $installerDir) {
    Get-ChildItem -Path $installerDir -Filter "*.exe" | ForEach-Object { $targets += $_.FullName }
}
if (Test-Path $distDir) {
    $targets += $distDir
}

if ($targets.Count -eq 0) {
    Write-Host "    لم يُعثر على مثبّت أو build — سأضيف استثناء لمجلد المشروع بأكمله." -ForegroundColor Yellow
    $targets += $root
}

if (-not (Test-Admin)) {
    Write-Host "    تنبيه: يحتاج صلاحيات Administrator لإضافة الاستثناء. أعد التشغيل كمسؤول." -ForegroundColor Red
} else {
    foreach ($t in $targets) {
        try {
            Add-MpPreference -ExclusionPath $t -ErrorAction Stop
            Write-Host "    أُضيف الاستثناء: $t" -ForegroundColor Green
        } catch {
            Write-Host "    فشل إضافة الاستثناء: $t" -ForegroundColor Red
            Write-Host "    $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""

# 3) فحص توقيع الـ exe إن وُجد
$exe = Join-Path $distDir "run_ui.dist\SmartAccounting.exe"
if (Test-Path $exe) {
    $sig = Get-AuthenticodeSignature -FilePath $exe
    Write-Host "[3] حالة توقيع SmartAccounting.exe: $($sig.Status)" -ForegroundColor Cyan
    if ($sig.Status -ne "Valid") {
        Write-Host "    غير موقّع رقمياً — هذا هو سبب الحجب. الحل العملي: إيقاف Smart App Control كما في الخطوة [1]." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "انتهى. إذا بقيت المشكلة، راجع: docs/USER_GUIDE.md -> قسم استكشاف الأخطاء" -ForegroundColor Green

