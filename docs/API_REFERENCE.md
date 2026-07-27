# مرجع الـ API — Smart Accounting Platform

## Module: modules/calculations.py

### CalculationEngine

#### current_ratio(current_assets, current_liabilities) → float
نسبة السيولة الجارية. تقي قدرة الشركة سداد التزاماتها قصيرة الأجل.

#### quick_ratio(current_assets, inventory, current_liabilities) → float
النسبة السريعة. كـ current_ratio لكن بدون المخزون.

#### gross_profit_margin(gross_profit, revenue) → float
هامش الربح الإجمالي (%).

#### net_profit_margin(net_income, revenue) → float
هامش صافي الربح (%).

#### roa(net_income, total_assets) → float
العائد على الأصول (%).

#### roe(net_income, equity) → float
العائد على حقوق الملكية (%).

#### asset_turnover(revenue, total_assets) → float
معدل دوران الأصول.

#### receivables_turnover(revenue, average_receivables) → float
معدل دوران الذمم المدينة.

#### days_sales_outstanding(receivables_turnover) → float
عدد أيام تحصيل الذمم.

#### inventory_turnover(cost_of_goods_sold, average_inventory) → float
معدل دوران المخزون.

#### debt_to_equity(total_liabilities, equity) → float
نسبة الدين إلى حقوق الملكية.

#### debt_ratio(total_liabilities, total_assets) → float
نسبة الدين الكلي.

#### z_score(working_capital, retained_earnings, ebit, market_value_equity, book_value_debt, sales, total_assets) → dict
Altman Z-Score. المخرجات:
```python
{
    "z_score": float,       # القيمة (0-5+)
    "status": str,          # "safe" | "grey" | "danger"
    "status_en": str,       # "Safe" | "Grey Zone" | "Danger"
    "status_fr": str,       # "Sûr" | "Zone Grise" | "Danger"
    "components": {
        "x1": float, "x2": float, "x3": float, "x4": float, "x5": float
    }
}
```

#### calculate_all_ratios(financial_data) → dict | None
حساب جميع النسب دفعة واحدة. المدخل:
```python
{
    "current_assets": float,
    "inventory": float,
    "current_liabilities": float,
    "gross_profit": float,
    "net_income": float,
    "revenue": float,
    "total_assets": float,
    "equity": float,
    "cost_of_goods_sold": float,
    "average_receivables": float,
    "average_inventory": float,
    "total_liabilities": float,
}
```

---

## Module: modules/tax.py

### TaxEngine

#### calculate_ibs(net_income, sector="other") → dict
IBS — ضريبة الدخل للمؤسسات. sector: "production" | "construction" | "other"
```python
{"ibs_amount": float, "ibs_rate": float, "effective_rate": float}
```

#### calculate_tva(collected, paid, rate=0.19) → dict
TVA — ضريبة القيمة المضافة.
```python
{"collected": float, "paid": float, "net": float}
```

#### calculate_irg(gross_salary) → dict
IRG — ضريبة الدخل للعامل (تدريجية 0%-35%).
```python
{"gross": float, "irg": float, "net": float, "rate": float}
```

#### calculate_cnas(gross_salary, employees=1) → dict
التأمينات الاجتماعية.
```python
{"employer": float, "employee": float, "total": float}
```

#### calculate_cnac(gross_salary, employees=1) → dict
صندوق عمال البناء.
```python
{"employer": float, "employee": float, "total": float}
```

#### simulate(data) → dict
محاكاة شاملة لجميع الضرائب.
```python
{
    "ibs": {...}, "tva": {...}, "irg": {...},
    "cnas": {...}, "cnac": {...}, "vf": {...},
    "total_taxes": float, "tax_burden_pct": float
}
```

---

## Module: modules/fraud_detection.py

### FraudDetector (Singleton: fraud_detector)

#### check_data_change(field, old_value, new_value, user="system") → list[dict]
فحص تغير البيانات. يتحقق من large_change (>20%) و negative_revenue.

#### check_balance_sheet(data, user="system") → list[dict]
فحص التوازن المحاسبي: الأصول = الخصوم + حقوق الملكية.

#### check_rapid_edits(user="system") → list[dict]
كشف التعديلات السريعة (>5 تعديلات في ثانية).

#### check_after_audit(field, new_value, user="system") → list[dict]
كشف التعديلات بعد اعتماد التدقيق.

#### check_tax_consistency(financial_data, tax_summary) → list[dict]
تناسق الضرائب مع الأرباح/الخسائر.

#### mark_audit_approved()
تحديد أن التدقيق اعتمد.

#### mark_audit_reset()
إعادة تعيين حالة التدقيق.

#### get_alerts(severity_filter=None, limit=100) → list[dict]
الحصول على التنبيهات مع فلتر حسب الشدة.

#### get_alert_count() → dict
```python
{"total": int, "high": int, "medium": int, "low": int}
```

---

## Module: modules/user_manager.py

### UserManager (Singleton: user_manager)

#### login(username, password) → (bool, str)
تسجيل الدخول. يُرجع (True, "OK") أو (False, سبب الخطأ).

#### logout()
تسجيل الخروج.

#### register(username, password, display_name="", role="viewer") → (bool, str)
تسجيل مستخدم جديد. role: "admin" | "viewer".

#### delete_user(username) → (bool, str)
حذف مستخدم. لا يمكن حذف "admin".

#### is_admin() → bool
هل المستخدم الحالي مدير؟

#### is_logged_in() → bool
هل يوجد مستخدم مسجل الدخول؟

#### get_current_user() → dict | None
```python
{"username": str, "role": str, "display_name": str}
```

#### get_all_users() → list[dict]
قائمة بجميع المستخدمين.

---

## Module: modules/activity_log.py

### ActivityLog (Singleton: activity_log)

#### log(action, details="")
تسجيل حدث.

#### get_entries(limit=100) → list[dict]
```python
[{"time": str, "action": str, "details": str}]
```

#### clear()
مسح السجل.

---

## Module: modules/email_notifier.py

### EmailNotifier (Singleton: email_notifier)

#### configure(smtp_server, smtp_port, sender_email, sender_password, manager_email)
إعداد خادم الإيميل.

#### send_alert(alert) → (bool, str)
إرسال تنبيه بالإيميل.

#### send_summary(data, alerts) → (bool, str)
إرسال ملخص بالإيميل.

#### is_configured() → bool
هل الإيميل مُعد؟

---

## Module: ui/app_state.py

### AppState (Singleton: state)

#### الخصائص
| الخاصية | النوع | الوصف |
|---------|-------|-------|
| company_name | str | اسم الشركة |
| fiscal_year | int | السنة المالية |
| financial_data | dict | البيانات المالية |
| ratios | dict | النسب المحسوبة |
| dupont | dict | تحليل DuPont |
| tax_data | dict | بيانات الضرائب |
| tax_summary | dict | ملخص الضرائب |
| language | str | اللغة (ar/en/fr) |
| theme | str | السمة (light/dark) |

#### الدوال
| الدالة | الوصف |
|--------|-------|
| save_data() | حفظ البيانات في JSON |
| load_data() | تحميل البيانات من JSON |
| save_settings() | حفظ الإعدادات |
| clear() | مسح كل البيانات |
| has_data() | هل في بيانات محسوبة |
| summary() | ملخص نصي سريع |

---

## Module: modules/audit.py

### AuditEngine

#### run_audit(financial_data, ratios) → dict
```python
{
    "issues": [{"type": str, "severity": str, "message": str, "field": str}],
    "warnings": [{"type": str, "severity": str, "message": str}],
    "summary": {"total_issues": int, "total_warnings": int, "score": int}
}
```

---

## Module: modules/comparative.py

### ComparativeEngine

#### compare(data_period1, data_period2) → dict
مقارنة بين فترتين ماليتين.

---

## Module: modules/cashflow.py

### CashFlowEngine

#### calculate(data) → dict
```python
{
    "operating": float,
    "investing": float,
    "financing": float,
    "net_change": float,
    "beginning": float,
    "ending": float
}
```

---

## Module: modules/backup.py

### BackupManager

#### backup(path) → (bool, str)
نسخ احتياطي لقاعدة البيانات.

#### restore(path) → (bool, str)
استعادة من نسخة احتياطية.

#### export_all_to_json(directory) → (bool, int)
تصدير جميع الجداول إلى JSON.

#### import_from_json(path) → (bool, str)
استيراد بيانات من JSON.
