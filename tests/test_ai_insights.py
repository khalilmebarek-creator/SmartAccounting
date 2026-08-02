# اختبارات محرك الرؤى الذكية (ML Insights)
# =========================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.ai_insights import AIInsightsEngine


def _rising_series(n=12, base=100, step=10):
    return [base + i * step for i in range(n)]


def _seasonal_series(cycles=2):
    """سلسلة موسمية: أشهر يناير عالية وأغسطس منخفضة"""
    values = []
    monthly = [200, 150, 140, 130, 120, 115, 110, 100, 115, 130, 150, 180]
    for c in range(cycles):
        values.extend(monthly)
    return values


# ==================== Forecasting ====================

def test_forecast_linear_returns_n_points():
    """اختبار عدد نقاط التنبؤ"""
    engine = AIInsightsEngine()
    result = engine.forecast(_rising_series(), months=3, method="linear")
    assert len(result["forecast"]) == 3
    for p in result["forecast"]:
        assert "period" in p
        assert "value" in p
    print("✅ test_forecast_linear_returns_n_points")
    return True


def test_forecast_linear_increasing():
    """اختبار أن التنبؤ الخطي يتبع الاتجاه الصاعد"""
    engine = AIInsightsEngine()
    series = _rising_series()
    result = engine.forecast(series, months=3, method="linear")
    last = series[-1]
    assert result["forecast"][0]["value"] > last
    assert result["forecast"][2]["value"] > result["forecast"][1]["value"]
    print("✅ test_forecast_linear_increasing")
    return True


def test_forecast_confidence_intervals():
    """اختبار فترات الثقة"""
    engine = AIInsightsEngine()
    result = engine.forecast(_rising_series(), months=4, method="linear")
    assert len(result["confidence"]) == 4
    for ci in result["confidence"]:
        assert ci["lower"] <= ci["upper"]
        assert ci["period"] is not None
    print("✅ test_forecast_confidence_intervals")
    return True


def test_forecast_empty_series():
    """اختبار سلسلة فارغة لا تسبب خطأ"""
    engine = AIInsightsEngine()
    result = engine.forecast([], months=3)
    assert isinstance(result, dict)
    print("✅ test_forecast_empty_series")
    return True


def test_forecast_single_point():
    """اختبار سلسلة من نقطة واحدة تعمل كقيمة ثابتة"""
    engine = AIInsightsEngine()
    result = engine.forecast([100], months=3, method="linear")
    assert len(result["forecast"]) == 3
    for p in result["forecast"]:
        assert p["value"] == 100
    print("✅ test_forecast_single_point")
    return True


def test_forecast_moving_average():
    """اختبار طريقة المتوسط المتحرك"""
    engine = AIInsightsEngine()
    result = engine.forecast(_rising_series(), months=3, method="moving_average")
    assert len(result["forecast"]) == 3
    print("✅ test_forecast_moving_average")
    return True


def test_forecast_exp_smoothing():
    """اختبار طريقة التجانس الأسي"""
    engine = AIInsightsEngine()
    result = engine.forecast(_rising_series(), months=3, method="exp_smoothing")
    assert len(result["forecast"]) == 3
    print("✅ test_forecast_exp_smoothing")
    return True


def test_forecast_all_structure():
    """اختبار بنية التنبؤ الكامل (إيرادات/مصروفات/أرباح)"""
    engine = AIInsightsEngine()
    result = engine.forecast_all(
        _rising_series(), _rising_series(12, 50, 5), _rising_series(12, 20, 3),
        months=3, method="linear"
    )
    for key in ["revenue", "expenses", "profit"]:
        assert key in result
        assert "forecast" in result[key]
        assert "confidence" in result[key]
        assert "growth_rate_pct" in result[key]
    print("✅ test_forecast_all_structure")
    return True


def test_forecast_invalid_method_fallback():
    """اختبار أن الطريقة غير المعروفة تتراجع إلى الخطية"""
    engine = AIInsightsEngine()
    result = engine.forecast(_rising_series(), months=2, method="bogus")
    assert len(result["forecast"]) == 2
    print("✅ test_forecast_invalid_method_fallback")
    return True


# ==================== Anomaly Detection ====================

def test_detect_anomalies_finds_spike():
    """اختبار اكتشاف القفزة الشاذة"""
    engine = AIInsightsEngine()
    series = [100, 105, 98, 102, 1000, 104, 99, 103]
    result = engine.detect_anomalies(series, threshold=2.0)
    assert len(result) >= 1
    assert result[0]["index"] == 4
    print("✅ test_detect_anomalies_finds_spike")
    return True


def test_detect_anomalies_flat_series():
    """اختبار أن السلسلة المستقرة لا تولد شذوذاً"""
    engine = AIInsightsEngine()
    result = engine.detect_anomalies([100] * 10, threshold=2.0)
    assert result == []
    print("✅ test_detect_anomalies_flat_series")
    return True


def test_detect_anomalies_severity_field():
    """اختبار وجود درجة خطورة لكل شذوذ"""
    engine = AIInsightsEngine()
    series = [100, 105, 98, 102, 3000, 104]
    result = engine.detect_anomalies(series, threshold=2.0)
    assert len(result) >= 1
    for a in result:
        assert a["severity"] in ("low", "medium", "high")
        assert a["z_score"] > 0
    print("✅ test_detect_anomalies_severity_field")
    return True


def test_detect_transaction_anomalies_amounts():
    """اختبار كشف المعاملات الشاذة (قائمة أرقام)"""
    engine = AIInsightsEngine()
    amounts = [1000, 1200, 950, 1100, 50000, 1050, 980]
    result = engine.detect_transaction_anomalies(amounts, threshold=2.0)
    assert len(result) >= 1
    assert result[0]["amount"] == 50000
    print("✅ test_detect_transaction_anomalies_amounts")
    return True


def test_detect_transaction_anomalies_dicts():
    """اختبار كشف المعاملات الشاذة (قائمة قواميس)"""
    engine = AIInsightsEngine()
    transactions = [
        {"date": "2025-01-01", "description": "مشتريات", "amount": 1000},
        {"date": "2025-01-05", "description": "مشتريات", "amount": 1100},
        {"date": "2025-01-09", "description": "شاذة", "amount": 90000},
        {"date": "2025-01-12", "description": "مشتريات", "amount": 1050},
    ]
    result = engine.detect_transaction_anomalies(transactions, threshold=2.0)
    assert len(result) >= 1
    assert result[0]["description"] == "شاذة"
    print("✅ test_detect_transaction_anomalies_dicts")
    return True


def test_detect_ratio_anomalies():
    """اختبار كشف شذوذ النسب"""
    engine = AIInsightsEngine()
    current = {"current_ratio": 2.5, "debt_to_equity": 0.4, "net_profit_margin": 12.0}
    previous = {"current_ratio": 2.4, "debt_to_equity": 0.38, "net_profit_margin": 11.5}
    result = engine.detect_ratio_anomalies(current, previous, threshold=2.0)
    assert isinstance(result, list)
    for a in result:
        assert "ratio" in a
        assert "severity" in a
    print("✅ test_detect_ratio_anomalies")
    return True


def test_unexpected_profit_loss():
    """اختبار كشف انقلاب الربح إلى خسارة"""
    engine = AIInsightsEngine()
    profit = [50, 40, 45, -200, 30]
    result = engine.unexpected_profit_loss(profit)
    assert len(result) >= 1
    assert result[0]["period"] == 3
    print("✅ test_unexpected_profit_loss")
    return True


# ==================== Pattern Recognition ====================

def test_patterns_structure():
    """اختبار بنية تحليل الأنماط"""
    engine = AIInsightsEngine()
    result = engine.patterns(_seasonal_series(cycles=2))
    for key in ["trend", "seasonality", "cyclical", "risk_indicators"]:
        assert key in result
    print("✅ test_patterns_structure")
    return True


def test_patterns_seasonal_peak():
    """اختبار أن الذروة الموسمية تُكتشف (يناير)"""
    engine = AIInsightsEngine()
    result = engine.patterns(_seasonal_series(cycles=2))
    season = result["seasonality"]
    assert len(season["indexes"]) == 12
    assert season["peak_month"] == 1
    assert season["trough_month"] == 8
    print("✅ test_patterns_seasonal_peak")
    return True


def test_patterns_trend_growth():
    """اختبار اتجاه النمو الصاعد"""
    engine = AIInsightsEngine()
    result = engine.patterns(_rising_series())
    assert result["trend"]["direction"] == "up"
    assert result["trend"]["growth_rate_pct"] > 0
    print("✅ test_patterns_trend_growth")
    return True


def test_patterns_trend_down():
    """اختبار الاتجاه الهابط"""
    engine = AIInsightsEngine()
    result = engine.patterns([100 - i * 5 for i in range(12)])
    assert result["trend"]["direction"] == "down"
    print("✅ test_patterns_trend_down")
    return True


def test_patterns_risk_indicators():
    """اختبار مؤشرات المخاطر"""
    engine = AIInsightsEngine()
    result = engine.patterns([100, 110, 40, 105, 95, 60, 120, 90])
    risks = result["risk_indicators"]
    assert len(risks) >= 2
    names = [r["name"] for r in risks]
    assert "volatility" in names
    assert "max_drawdown" in names
    print("✅ test_patterns_risk_indicators")
    return True


def test_patterns_cyclical():
    """اختبار مؤشرات الدورات"""
    engine = AIInsightsEngine()
    result = engine.patterns(_seasonal_series(cycles=2))
    assert result["cyclical"]["cycle_length"] >= 1
    print("✅ test_patterns_cyclical")
    return True


# ==================== Smart Recommendations ====================

def test_recommendations_weak_ratios():
    """اختبار توصيات تحسين النسب الضعيفة"""
    engine = AIInsightsEngine()
    ratios = {
        "current_ratio": 0.8,
        "quick_ratio": 0.6,
        "debt_to_equity": 3.5,
        "net_profit_margin": 2.0,
        "roe": 4.0,
        "asset_turnover": 0.9,
    }
    result = engine.recommendations(ratios, cash=100000, monthly_expenses=200000, revenue_growth=0.1)
    cats = [r["category"] for r in result]
    assert "weak_ratio" in cats
    print("✅ test_recommendations_weak_ratios")
    return True


def test_recommendations_cash():
    """اختبار توصيات تحسين النقدية"""
    engine = AIInsightsEngine()
    ratios = {"current_ratio": 1.8, "debt_to_equity": 0.4, "net_profit_margin": 10.0, "roe": 15.0}
    result = engine.recommendations(ratios, cash=50000, monthly_expenses=200000, revenue_growth=0.05)
    cats = [r["category"] for r in result]
    assert "cash" in cats
    print("✅ test_recommendations_cash")
    return True


def test_recommendations_growth_opportunity():
    """اختبار توصيات فرص النمو"""
    engine = AIInsightsEngine()
    ratios = {"current_ratio": 2.0, "debt_to_equity": 0.4, "net_profit_margin": 12.0, "roe": 18.0}
    result = engine.recommendations(ratios, cash=1000000, monthly_expenses=100000, revenue_growth=0.25)
    cats = [r["category"] for r in result]
    assert "growth" in cats
    print("✅ test_recommendations_growth_opportunity")
    return True


def test_recommendations_returns_list():
    """اختبار أن التوصيات دائماً قائمة"""
    engine = AIInsightsEngine()
    result = engine.recommendations({}, cash=0, monthly_expenses=0, revenue_growth=0)
    assert isinstance(result, list)
    print("✅ test_recommendations_returns_list")
    return True


# ==================== Smart Alerts ====================

def test_alerts_structure():
    """اختبار بنية التنبيهات"""
    engine = AIInsightsEngine()
    result = engine.alerts(
        forecasts=None, anomalies=[], patterns=None, ratios={}
    )
    assert isinstance(result, list)
    for a in result:
        assert a["type"] in ("predictive_warning", "opportunity", "risk", "action")
        assert a["severity"] in ("low", "medium", "high")
        assert "message" in a
    print("✅ test_alerts_structure")
    return True


def test_alerts_risk_from_anomalies():
    """اختبار تحويل الشذوذ إلى تنبيهات خطر"""
    engine = AIInsightsEngine()
    anomalies = [
        {"index": 3, "value": 5000, "expected": 100, "z_score": 30, "severity": "high"}
    ]
    result = engine.alerts(forecasts=None, anomalies=anomalies, patterns=None, ratios={})
    types = [a["type"] for a in result]
    assert "risk" in types
    print("✅ test_alerts_risk_from_anomalies")
    return True


def test_alerts_predictive_declining_forecast():
    """اختبار تحذير تنبؤي عند انخفاض الأرباح المتوقعة"""
    engine = AIInsightsEngine()
    forecasts = {
        "profit": {
            "growth_rate_pct": -15.0,
            "forecast": [{"period": 1, "value": 100}, {"period": 2, "value": 80}],
        }
    }
    result = engine.alerts(forecasts=forecasts, anomalies=[], patterns=None, ratios={})
    types = [a["type"] for a in result]
    assert "predictive_warning" in types
    print("✅ test_alerts_predictive_declining_forecast")
    return True


def test_alerts_opportunity_growth():
    """اختبار تنبيه الفرصة عند نمو الإيرادات المتوقعة"""
    engine = AIInsightsEngine()
    forecasts = {
        "revenue": {"growth_rate_pct": 18.0},
        "profit": {"growth_rate_pct": 5.0},
    }
    result = engine.alerts(forecasts=forecasts, anomalies=[], patterns=None, ratios={})
    types = [a["type"] for a in result]
    assert "opportunity" in types
    print("✅ test_alerts_opportunity_growth")
    return True


def test_alerts_action_from_recommendations():
    """اختبار اقتراحات إجراءات من التوصيات"""
    engine = AIInsightsEngine()
    recommendations = [{"category": "cash", "title": "تعزيز النقدية", "detail": "خفض المصروفات"}]
    result = engine.alerts(
        forecasts=None, anomalies=[], patterns=None, ratios={},
        recommendations=recommendations
    )
    types = [a["type"] for a in result]
    assert "action" in types
    print("✅ test_alerts_action_from_recommendations")
    return True


# ==================== Unified ====================

def test_generate_insights_unified():
    """اختبار التوليد الموحّد للرؤى"""
    engine = AIInsightsEngine()
    result = engine.generate_insights(
        revenue_history=_seasonal_series(cycles=2),
        expense_history=_rising_series(24, 50, 3),
        profit_history=[x - 50 for x in _seasonal_series(cycles=2)],
        ratios={"current_ratio": 1.2, "debt_to_equity": 1.8, "net_profit_margin": 8.0},
        months=3
    )
    for key in ["forecasts", "anomalies", "patterns", "recommendations", "alerts"]:
        assert key in result
    assert "revenue" in result["forecasts"]
    print("✅ test_generate_insights_unified")
    return True


def test_empty_history_graceful():
    """اختبار عدم انهيار المحرك على بيانات فارغة"""
    engine = AIInsightsEngine()
    result = engine.generate_insights(
        revenue_history=[], expense_history=[], profit_history=[], ratios={}, months=3
    )
    assert isinstance(result, dict)
    assert "forecasts" in result
    print("✅ test_empty_history_graceful")
    return True


if __name__ == "__main__":
    print("🧪 بدء اختبارات محرك الرؤى الذكية...")
    print("=" * 50)

    tests = [
        test_forecast_linear_returns_n_points,
        test_forecast_linear_increasing,
        test_forecast_confidence_intervals,
        test_forecast_empty_series,
        test_forecast_single_point,
        test_forecast_moving_average,
        test_forecast_exp_smoothing,
        test_forecast_all_structure,
        test_forecast_invalid_method_fallback,
        test_detect_anomalies_finds_spike,
        test_detect_anomalies_flat_series,
        test_detect_anomalies_severity_field,
        test_detect_transaction_anomalies_amounts,
        test_detect_transaction_anomalies_dicts,
        test_detect_ratio_anomalies,
        test_unexpected_profit_loss,
        test_patterns_structure,
        test_patterns_seasonal_peak,
        test_patterns_trend_growth,
        test_patterns_trend_down,
        test_patterns_risk_indicators,
        test_patterns_cyclical,
        test_recommendations_weak_ratios,
        test_recommendations_cash,
        test_recommendations_growth_opportunity,
        test_recommendations_returns_list,
        test_alerts_structure,
        test_alerts_risk_from_anomalies,
        test_alerts_predictive_declining_forecast,
        test_alerts_opportunity_growth,
        test_alerts_action_from_recommendations,
        test_generate_insights_unified,
        test_empty_history_graceful,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print("=" * 50)
    print(f"النتائج: {passed} نجح / {failed} فشل / {passed + failed} إجمالي")

    if failed == 0:
        print("🎉 كل اختبارات الرؤى الذكية نجحت!")
    else:
        print("⚠️ بعض الاختبارات فشلت")
