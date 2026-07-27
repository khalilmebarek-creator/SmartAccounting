# مشغل الاختبارات الشامل
# =========================

import unittest
import sys
import os
import time
from io import StringIO

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_all_tests():
    """تشغيل كل الاختبارات في المشروع"""
    
    print("=" * 70)
    print("🧪 تشغيل اختبارات المنصة المحاسبية الذكية")
    print("=" * 70)
    print()
    
    # اكتشاف الاختبارات تلقائياً
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # عداد للنتائج
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    duration = end_time - start_time
    
    # عرض النتائج
    output = stream.getvalue()
    print(output)
    
    print("=" * 70)
    print("📊 ملخص النتائج")
    print("=" * 70)
    print(f"✅ نجح:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ فشل:    {len(result.failures)}")
    print(f"⚠️ أخطاء:  {len(result.errors)}")
    print(f"⏭️  تخطي:   {len(result.skipped)}")
    print(f"⏱️  الوقت:  {duration:.2f} ثانية")
    print(f"📈 المجموع: {result.testsRun} اختبار")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("\n🎉🎉🎉 كل الاختبارات نجحت! المشروع 100% سليم 🎉🎉🎉\n")
        return 0
    else:
        print("\n❌ فيه اختبارات فشلت. راجع التفاصيل فوق.\n")
        return 1


def verify_project_structure():
    """التحقق من بنية المشروع"""
    print("=" * 70)
    print("🔍 التحقق من بنية المشروع")
    print("=" * 70)
    
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'PROJECT_MAP.md',
        'settings.json',
        'database/__init__.py',
        'database/db_connection.py',
        'database/db_schema.py',
        'database/db_operations.py',
        'modules/__init__.py',
        'modules/calculations.py',
        'modules/validation.py',
        'modules/analysis.py',
        'modules/audit.py',
        'modules/reporting.py',
        'modules/data_import.py',
        'modules/tax.py',
        'modules/tax_config.json',
        'utils/__init__.py',
        'utils/formatters.py',
        'utils/validators.py',
        'ui/__init__.py',
        'ui/main_window.py',
        'ui/app_state.py',
        'ui/run_ui.py',
        'ui/resources/style.qss',
        'ui/resources/style_dark.qss',
        'ui/resources/i18n.py',
        'ui/views/data_entry.py',
        'ui/views/dashboard.py',
        'ui/views/ratios_view.py',
        'ui/views/analysis_view.py',
        'ui/views/audit_view.py',
        'ui/views/reports_view.py',
        'ui/views/settings_view.py',
        'ui/views/chat_view.py',
        'ui/views/tax_view.py',
    ]
    
    missing = []
    present = []
    
    for filepath in required_files:
        full_path = os.path.join(base, filepath)
        if os.path.exists(full_path):
            present.append(filepath)
            print(f"  ✅ {filepath}")
        else:
            missing.append(filepath)
            print(f"  ❌ {filepath} - مفقود!")
    
    print()
    print(f"📁 الملفات الموجودة: {len(present)}/{len(required_files)}")
    
    if missing:
        print(f"\n⚠️ ملفات ناقصة ({len(missing)}):")
        for f in missing:
            print(f"   • {f}")
        return False
    
    print("✅ كل الملفات موجودة")
    return True


def verify_python_syntax():
    """التحقق من صحة syntax كل ملفات Python"""
    print("=" * 70)
    print("🔍 التحقق من syntax ملفات Python")
    print("=" * 70)
    
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_files = []
    
    for root, dirs, files in os.walk(base):
        # تجاهل __pycache__ و venv
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'venv', '.git')]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    
    for filepath in python_files:
        rel_path = os.path.relpath(filepath, base)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), filepath, 'exec')
            print(f"  ✅ {rel_path}")
        except SyntaxError as e:
            errors.append((rel_path, str(e)))
            print(f"  ❌ {rel_path} - خطأ syntax: {e}")
        except Exception as e:
            errors.append((rel_path, str(e)))
            print(f"  ⚠️ {rel_path} - {e}")
    
    print()
    print(f"📁 تم فحص: {len(python_files)} ملف")
    
    if errors:
        print(f"\n❌ أخطاء: {len(errors)}")
        return False
    
    print("✅ كل الملفات صحيحة من ناحية syntax")
    return True


def verify_imports():
    """التحقق من إمكانية استيراد كل الـ modules"""
    print("=" * 70)
    print("🔍 التحقق من imports")
    print("=" * 70)
    
    # إضافة مسار المشروع لـ sys.path
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base not in sys.path:
        sys.path.insert(0, base)
    
    modules_to_test = [
        'config',
        'database',
        'database.db_connection',
        'database.db_schema',
        'database.db_operations',
        'modules',
        'modules.calculations',
        'modules.validation',
        'modules.analysis',
        'modules.audit',
        'modules.reporting',
        'modules.data_import',
        'modules.tax',
        'utils',
        'utils.formatters',
        'utils.validators',
        'ui',
        'ui.app_state',
    ]
    
    failed = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            failed.append((module_name, str(e)))
            print(f"  ❌ {module_name} - {e}")
        except Exception as e:
            failed.append((module_name, str(e)))
            print(f"  ⚠️ {module_name} - {e}")
    
    print()
    if failed:
        print(f"❌ فشل استيراد: {len(failed)} module")
        return False
    
    print("✅ كل الـ modules قابلة للاستيراد")
    return True


if __name__ == '__main__':
    # 1. التحقق من البنية
    structure_ok = verify_project_structure()
    print()
    
    # 2. التحقق من syntax
    syntax_ok = verify_python_syntax()
    print()
    
    # 3. التحقق من imports
    imports_ok = verify_imports()
    print()
    
    # 4. تشغيل اختبارات unittest
    if structure_ok and syntax_ok and imports_ok:
        exit_code = run_all_tests()
    else:
        print("⚠️ تخطي الاختبارات بسبب أخطاء في البنية/Syntax")
        exit_code = 1

    # 5. تشغيل اختبارات pytest (test_tax.py)
    print()
    print("=" * 70)
    print("🧪 تشغيل اختبارات النظام الجبائي (pytest)")
    print("=" * 70)
    try:
        import pytest
        tax_result = pytest.main([
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_tax.py'),
            '-v', '--tb=short', '--no-header', '-W', 'ignore::DeprecationWarning'
        ])
        if tax_result == 0:
            print("\n✅ كل اختبارات الضرائب نجحت")
        else:
            print(f"\n⚠️ pytest return code: {tax_result}")
            exit_code = 1
    except ImportError:
        print("⚠️ pytest غير مثبت - تخطي اختبارات الضرائب")
    except Exception as e:
        print(f"⚠️ خطأ في تشغيل pytest: {e}")

    sys.exit(exit_code)
