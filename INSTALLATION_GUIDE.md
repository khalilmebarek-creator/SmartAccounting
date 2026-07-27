# INSTALLATION_GUIDE.md
## دليل التثبيت والتثبيت الأولي
### Smart Accounting Platform v2.5.0

---

## 1. متطلبات النظام

### المتطلبات الأساسية

| المكون | الحد الأدنى | الموصى به |
|--------|-----------|----------|
| نظام التشغيل | Windows 10 / Ubuntu 20.04 / macOS 11 | Windows 11 / Ubuntu 22.04 / macOS 14 |
| Python | 3.10+ | 3.13+ |
| الرام (RAM) | 4 GB | 8 GB+ |
| مساحة القرص | 500 MB | 1 GB+ |
| الشاشة | 1280×720 | 1920×1080+ |
| الإنترنت | غير مطلوب للتشغيل | مطلوب للتحديثات |

### المتطلبات البرمجية

- **Python 3.10 أو أحدث**: [python.org](https://python.org)
- **pip**: يأتي مع Python عادةً
- **Git** (اختياري): للتحميل من المستودع

### المكتبات المطلوبة

```
PyQt5>=5.15
matplotlib>=3.5
pandas>=1.4
openpyxl>=3.0
fpdf2>=2.7
cryptography>=41.0
```

> ⭐ **ملاحظة**: جميع المكتبات تُثبّت تلقائياً عبر `pip install -r requirements.txt`

---

## 2. خطوات التثبيت

### الطريقة 1: التثبيت من ملف ZIP

**الخطوة 1: تحميل المشروع**
```
1. افتح المتصفح وانتقل لصفحة المشروع
2. اضغط على "Code" → "Download ZIP"
3. احفظ الملف في مكان مناسب (مثلاً C:\Projects\)
4. اضغط بزر يمين على الملف → "Extract All"
5. اختر مسار الحفظ واضغط "Extract"
```

**الخطوة 2: فتح Terminal**
```
1. افتح File Explorer وانتقل لمجلد المشروع
2. اضغط Shift + Right Click في المجلد
3. اختر "Open PowerShell window here"
4. أو افتح cmd واكتب: cd C:\Projects\Accounting_Platform
```

**الخطوة 3: إنشاء بيئة افتراضية**
```
python -m venv .venv
```

**الخطوة 4: تفعيل البيئة الافتراضية**
```
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

> ⭐ **提示**: إذا ظهر خطأ في PowerShell، جرّب:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**الخطوة 5: تثبيت المكتبات**
```
pip install -r requirements.txt
```

**الخطوة 6: تشغيل الاختبارات للتحقق**
```
$env:PYTHONIOENCODING="utf-8"
python -m pytest tests/ -v
```

**الخطوة 7: تشغيل البرنامج**
```
python ui\run_ui.py
```

---

### الطريقة 2: التثبيت من Git

```
git clone https://github.com/your-repo/accounting-platform.git
cd accounting-platform
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python ui\run_ui.py
```

---

## 3. حل المشاكل الشائعة في التثبيت

### المشكلة 1: `python` not recognized

**الأعراض**: يظهر خطأ `'python' is not recognized`

**السبب**: Python غير مضاف للـ PATH

**الحل**:
1. أعد تثبيت Python
2. ضع علامة ✅ على "Add Python to PATH"
3. أعد تشغيل Terminal

---

### المشكلة 2: `pip` not found

**الأعراض**: خطأ `'pip' is not recognized`

**الحل**:
```
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

---

### المشكلة 3: خطأ في تثبيت PyQt5

**الأعراض**: خطأ أحمر أثناء `pip install PyQt5`

**السبب**: نسخة Python غير متوافقة

**الحل**:
```
pip install PyQt5==5.15.11
```
أو جرّب نسخة أقدم:
```
pip install PyQt5==5.15.9
```

---

### المشكلة 4: خطأ في cryptography على Windows

**الأعراض**: خطأ متعلق بـ `rust` أو `cryptography`

**الحل**:
```
pip install cryptography --only-binary=:all:
```

---

### المشكلة 5: `Permission denied`

**الأعراض**: خطأ صلاحية عند التثبيت

**الحل**:
```
pip install --user -r requirements.txt
```
أو شغّل Terminal كمسؤول (Run as Administrator)

---

### المشكلة 6: خطأ الترميز (Encoding)

**الأعراض**: أخطاء ترميز مع الحروف العربية

**الحل**: أضف هذا قبل تشغيل أي أمر:
```
$env:PYTHONIOENCODING="utf-8"
```

---

### المشكلة 7: `No module named 'ui'`

**الأعراض**: خطأ `ModuleNotFoundError: No module named 'ui'`

**السبب**: التشغيل من مجلد خاطئ

**الحل**: تأكد أنك في المجلد الجذر للمشروع:
```
cd C:\Users\you\Desktop\Accounting_Platform
python ui\run_ui.py
```

---

### المشكلة 8: `users.json` not found

**الأعراض**: تحذير عند أول تشغيل

**الحل**: هذا تحذير عادي. سيُنشأ الملف تلقائياً عند أول تسجيل دخول.

---

## 4. التحقق من التثبيت الصحيح

### اختبار سريع

شغّل هذا الأمر وأ确保 أن جميع النتائج ✅:

```
python -c "
import sys; print(f'Python: {sys.version}')
import PyQt5; print(f'PyQt5: {PyQt5.PYQT_VERSION_STR}')
import matplotlib; print(f'Matplotlib: {matplotlib.__version__}')
import pandas; print(f'Pandas: {pandas.__version__}')
import openpyxl; print(f'openpyxl: {openpyxl.__version__}')
import fpdf; print(f'fpdf2: {fpdf.__version__}')
import cryptography; print(f'Cryptography: {cryptography.__version__}')
print('All OK!')
"
```

### اختبار قاعدة البيانات

```
python -c "
from database.db_connection import DatabaseConnection
db = DatabaseConnection()
db.connect()
print('Database OK!')
db.disconnect()
"
```

### اختبار واجهة المستخدم

```
python ui\run_ui.py
# يجب أن تظهر شاشة تسجيل الدخول
```

---

## 5. الخطوات بعد التثبيت الأول

### 1. تغيير كلمة المرور الافتراضية
- سجّل دخول بـ: `admin@accounting.local` / `Admin@1234`
- سيطلب منك النظام تغيير كلمة المرور فوراً
- اختر كلمة مرور قوية (8+ أحرف، أرقام، رموز)

### 2. إدخال بيانات تجريبية
- من القائمة: `ملف → تشغيل البيانات التجريبية`
- سيُنشأ حساب تجريبي بكامل البيانات

### 3. تخصيص الإعدادات
- اختر لغة العرض (عربي/إنجليزي/فرنسي)
- اختر المظهر (فاتح/داكن)
- حدّث بيانات الشركة

### 4. عمل نسخة احتياطية
- من الإعدادات: `إنشاء نسخة احتياطية`
- احفظ النسخة في مكان آمن

---

## 6. هيكل الملفات بعد التثبيت

```
Accounting_Platform/
├── .venv/                    # البيئة الافتراضية
├── ui/                       # واجهة المستخدم
│   ├── views/                # الشاشات
│   ├── resources/            # الترجمات والأيقونات
│   ├── app_state.py          # حالة التطبيق
│   └── run_ui.py             # نقطة التشغيل
├── modules/                  # الوحدات المالية
├── database/                 # قاعدة البيانات
├── utils/                    # الأدوات المساعدة
├── tests/                    # اختبارات
├── users.json                # بيانات المستخدمين
├── accounting.db             # قاعدة البيانات الرئيسية
├── requirements.txt          # المكتبات المطلوبة
└── config.py                 # إعدادات النظام
```

---

## 7. روابط مفيدة

- [الدليل الرئيسي](README.md)
- [دليل المستخدم](USER_MANUAL.md)
- [解决问题](TROUBLESHOOTING.md)
- [النشر والتفعيل](DEPLOYMENT_GUIDE.md)
- [تحسين الأداء](PERFORMANCE_OPTIMIZATION.md)

---

*آخر تحديث: يوليو 2026*
*الإصدار: v2.5.0*
