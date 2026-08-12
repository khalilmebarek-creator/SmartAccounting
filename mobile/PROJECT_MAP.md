# PROJECT_MAP.md — SmartAccounting Mobile (تطبيق الجوال)

> آخر تحديث: 2026-08-12 | الإصدار: 1.1.0

## TECH_STACK

| المكوّن | الإصدار | ملاحظات |
|---------|---------|---------|
| Flutter SDK (stable) | 3.44.7 | Dart 3.12.2 — مُثبت في `C:\Users\khalile\flutter` |
| JDK | Temurin 17.0.20 | في `C:\Users\khalile\android\jdk17` |
| Android SDK | platform 36 / build-tools 36.0.0 | في `C:\Users\khalile\android\sdk` |
| AGP / Gradle / Kotlin | 8.9.1 / 8.11.1 / 2.1.20 | AGP 9 مرفوض: تعارض file_picker (يتطلب builtInKotlin) مع flutter_local_notifications (يطبّق KGP بنفسه) |
| cryptography (Dart) | 2.9.0 | Argon2id + AES-256-GCM — فك تشفير SACF1 من سطح المكتب |
| file_picker | 11.0.3 | واجهة 11: استدعاء static `FilePicker.pickFiles()` (لا `.platform`) |
| flutter_local_notifications | 22.3.0 | يتطلب timezone + TZDateTime + coreLibraryDesugaring |
| timezone | 0.11.1 | مطلوب لـ zonedSchedule |
| shared_preferences / path_provider | 2.5.5 / 2.1.6 | اللغة/الثيم + تخزين آخر snapshot |
| crypto | 3.0.7 | sha256 لفحص checksum |

## SYSTEM_FLOW — رحلة المستخدم

```
1. فتح التطبيق → اللغة من التفضيلات (عربي افتراضياً RTL كامل)
2. استعادة آخر snapshot من التخزين المحلي (يعمل دون اتصال)
3. أو تحميل ملف snapshot من السحابة (OneDrive/Dropbox/Drive) عبر file_picker
4. ملف مشفّر → حوار كلمة المرور → فك SACF1 (Argon2id + AES-GCM)
5. لوحة القيادة: بطاقات KPI + درجة الصحة 0-100
6. تبويبات: لوحة / 20 نسبة / صحة AI (رادار) / تقويم جبائي / IAS
7. عند تحميل البيانات: جدولة تنبيهات محلية (قبل 3 أيام من كل استحقاق، 09:00)
8. فحص checksum sha256 — أي تلاعب بالملف يُرفض
```

## ARCHITECTURE — تقسيم Domain (~16 ملفاً)

```
lib/
  main.dart                      نقطة الدخول + الحاويات + تدفق تحميل الملفات
  core/  app_logger.dart         غير حظري (ring buffer 500 + flush على isolate)
  core/  i18n.dart               AR/EN/FR خريطة مفاتيح (207 مفتاحاً × 3)
  core/  theme.dart              Material 3 فاتح/داكن
  core/  app_state.dart          InheritedWidget (AppState + AppController)
  data/  snapshot_model.dart     نموذج بيانات الـ payload
  data/  snapshot_loader.dart    تحليل wrapper + فك SACF1 (متوافق مع سطح المكتب)
  data/  ai_health.dart          معادلات Health Score مطابقة لـ modules/ai_platform.py
  data/  tax_notifier.dart       خطة تنبيهات (pure) + غلاف plugin رقيق
  data/  local_store.dart        التفضيلات + آخر snapshot
  features/ dashboard|ratios|ai_health|tax_calendar|ias
  widgets/ kpi_card|ratio_bar|risk_radar (CustomPainter بلا اعتماديات رسوم)
```

**قرارات**: لا State Management خارجي (setState + InheritedWidget)؛ لا مكتبات رسوم (CustomPainter + LinearProgressIndicator)؛ الأرقام تُعرض ولا تُحسب من جديد (المصدر الوحيد = محركات سطح المكتب) عدا Health Score المطابق بالمعادلات.

## ORPHANS & PENDING

- [x] ~~M1 الهيكل + 3 لغات RTL~~ — 11 widget test
- [x] ~~M2 تحميل JSON + فك AES-GCM~~ — 12 اختباراً (fixture حقيقي من سطح المكتب)
- [x] ~~M3 الشاشات الخمس + parity~~ — 6 اختبارات (مطابقة desktop engine)
- [x] ~~M4 تنبيهات التقويم~~ — 7 اختبارات
- [x] ~~M5 APK~~ — arm64 18.2MB / v7a 15.7MB / x86_64 19.6MB
- [x] ~~M6 لوحة قيادة مطوّرة~~ — رسم أعمدة CustomPainter + بطاقة Z-Score + أسهم اتجاه vs الملف السابق + بطاقة معلومات الشركة (4 widget tests)
- [x] ~~M7 ملخص تنفيذي + توصيات~~ — ai_summary.dart بمطابقة حرفية مع ai_platform.py (4 parity tests: سلاسل عربية مطابقة fixture سطح المكتب)
- [x] ~~M8 صور شاشات للدفاع~~ — 10 golden PNG (ar/en) بخط Amiri في mobile/screenshots/
- [ ] iOS build — يتطلب macOS/Xcode
- [ ] توقيع release رسمي (keystore مستقل) — حالياً debug signing
- [ ] دفع تنبيهات خادم (FCM) — التنبيهات حالياً محلية
- [ ] تزامن ثنائي الاتجاه (إدخال من الجوال) — خارج النطاق المقصود (عرض فقط)

## ملاحظات البناء

- AGP 9.0.1 (قالب Flutter) يفشل مع pluginين متناقضين → رُجّع إلى AGP 8.9.1 + Gradle 8.11.1 + Kotlin 2.1.20
- flutter_local_notifications 22.3 يتطلب `isCoreLibraryDesugaringEnabled = true` + `desugar_jdk_libs:2.1.5`
- بيئة التطوير على هذا الجهاز: JAVA_HOME=C:\Users\khalile\android\jdk17 + SDK في C:\Users\khalile\android\sdk
- fixtures الاختبارات تُولَّد من سطح المكتب: `python tools/gen_mobile_fixtures.py`
