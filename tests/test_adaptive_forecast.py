# اختبارات التنبؤ التكيفي (الاختيار التلقائي للطريقة + ضبط alpha)
# ===============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.adaptive_forecast import AdaptiveForecaster, adaptive_forecast, METHODS, ALPHAS
from modules import forecast_memory


def _rising_series(n=12, base=100, step=10):
    return [base + i * step for i in range(n)]


def _noisy_series(n=12, base=100, noise=5):
    import random
    random.seed(42)
    return [base + i * 10 + random.uniform(-noise, noise) for i in range(n)]


# ==================== backtesting ====================

def test_backtest_linear_lowest_on_linear_series():
    """على سلسلة خطية نظيفة، الخطأ الرجعي للخطي أقل من المتوسط المتحرك"""
    fc = AdaptiveForecaster()
    series = _rising_series()
    lin = fc.backtest_error(series, "linear")
    ma = fc.backtest_error(series, "moving_average")
    assert lin < ma


def test_choose_method_picks_linear_on_linear_series():
    """الاختيار التلقائي يرجّح الخطي على سلسلة خطية"""
    fc = AdaptiveForecaster()
    method, scores = fc.choose_method(_rising_series(), metric="profit")
    assert method == "linear"
    assert set(scores.keys()) == set(METHODS)


def test_best_alpha_returns_valid_alpha():
    """best_alpha يعيد alpha ضمن القيم المسموحة وخطأ محدوداً"""
    fc = AdaptiveForecaster()
    alpha, err = fc.best_alpha(_noisy_series())
    assert alpha in ALPHAS
    assert err < float("inf")


def test_backtest_error_exp_smoothing_uses_alpha():
    """معامل alpha يؤثر فعلياً على الخطأ الرجعي للتجانس الأسي"""
    fc = AdaptiveForecaster(hold_out=3)
    series = _noisy_series()
    err_low = fc.backtest_error(series, "exp_smoothing", alpha=0.1)
    err_high = fc.backtest_error(series, "exp_smoothing", alpha=0.9)
    assert err_low != err_high


# ==================== forecast_auto ====================

def test_forecast_auto_shape():
    """forecast_auto يعيد نقاط تنبؤ + الطريقة المختارة + درجات الطرق"""
    fc = AdaptiveForecaster()
    result = fc.forecast_auto(_rising_series(), months=3, metric="profit")
    assert "error" not in result
    assert len(result["forecast"]) == 3
    assert result["chosen_method"] in METHODS
    assert set(result["method_scores"].keys()) == set(METHODS)
    assert result["adaptive"] is True


def test_forecast_auto_empty_series():
    """سلسلة فارغة تعيد خطأ empty_series"""
    fc = AdaptiveForecaster()
    result = fc.forecast_auto([], months=3, metric="profit")
    assert "error" in result


def test_adaptive_forecast_returns_all_metrics():
    """adaptive_forecast يعيد التنبؤات والـ meta لكل المقاييس الثلاثة"""
    series = _noisy_series()
    forecasts, meta = adaptive_forecast(series, series, series, months=6, persist=False)
    for key in ("revenue", "expenses", "profit"):
        assert "forecast" in forecasts[key]
        assert "confidence" in forecasts[key]
        assert meta[key]["method"] in METHODS


# ==================== فروع إضافية (تغطية كاملة) ====================

def test_backtest_error_short_series_inf():
    """سلسلة أقصر من hold_out تعيد خطأً لا نهائياً"""
    fc = AdaptiveForecaster(hold_out=3)
    assert fc.backtest_error([1, 2, 3], "linear") == float("inf")


def test_backtest_error_linear_skips_single_point_train():
    """الانحدار الخطي يتجاهل نقاط التدريب ذات الطول 1"""
    fc = AdaptiveForecaster(hold_out=3)
    assert fc.backtest_error([1, 2, 3, 4], "linear") != float("inf")


def test_backtest_error_no_errors_inf():
    """لا نقاط صالحة للتقييم تعيد خطأً لا نهائياً"""
    fc = AdaptiveForecaster(hold_out=1)
    assert fc.backtest_error([5, 6], "linear") == float("inf")


def test_predict_next_linear_single_point():
    """التنبؤ الخطي بنقطة تدريب واحدة يعيد آخر قيمة"""
    fc = AdaptiveForecaster()
    assert fc._predict_next([5.0], "linear") == 5.0


def test_score_methods_blends_memory():
    """المزج بين الخطأ الرجعي والذاكرة (0.6 + 0.4)"""
    fc = AdaptiveForecaster(memory={
        "profit": {"linear": 2.0, "moving_average": 2.0, "exp_smoothing": 2.0}})
    scores = fc.score_methods(_rising_series(), metric="profit")
    for m in METHODS:
        v = scores[m]
        assert v["memory_error"] == 2.0
        assert v["backtest_error"] != float("inf")
        assert abs(v["error"] - (0.6 * v["backtest_error"] + 0.4 * 2.0)) < 1e-9


def test_score_methods_inf_backtest_uses_memory():
    """عند خطأ رجعي لا نهائي يُستخدم خطأ الذاكرة مباشرة"""
    fc = AdaptiveForecaster(memory={"profit": {"linear": 2.5}})
    scores = fc.score_methods([1, 2], metric="profit")
    assert scores["linear"]["error"] == 2.5
    assert scores["moving_average"]["error"] == float("inf")


def test_choose_method_all_invalid_fallback():
    """كل الطرق غير صالحة تعيد الخطي كاحتياطي"""
    fc = AdaptiveForecaster()
    method, _ = fc.choose_method([1, 2], metric="profit")
    assert method == "linear"


def test_forecast_auto_exp_smoothing_branch():
    """عندما تتفوق الذاكرة على التجانس الأسي يُستخدم مساره"""
    fc = AdaptiveForecaster(memory={
        "profit": {"linear": 999.0, "moving_average": 999.0, "exp_smoothing": 0.01}})
    result = fc.forecast_auto(_rising_series(), months=3, metric="profit")
    assert result["chosen_method"] == "exp_smoothing"
    assert len(result["forecast"]) == 3


def test_adaptive_forecast_empty_series():
    """مقاييس فارغة تعيد تنبؤات فارغة دون انهيار"""
    forecasts, meta = adaptive_forecast([], [], [], months=6, persist=False)
    for key in ("revenue", "expenses", "profit"):
        assert forecasts[key]["forecast"] == []
    assert meta == {}


def test_adaptive_forecast_persists(tmp_path):
    """persist=True يكتب الذاكرة على القرص"""
    path = os.path.join(str(tmp_path), "mem.json")
    series = _noisy_series()
    adaptive_forecast(series, series, series, months=6, persist=True, memory={}, path=path)
    assert os.path.isfile(path)
    assert "profit" in forecast_memory.load_memory(path)
