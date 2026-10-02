# التنبؤ التكيفي (التعلّم الذاتي)
# =================================
# اختيار تلقائي لأفضل طريقة تنبؤ (خطي/متوسط متحرك/تجانس أسي) عبر
# اختبار رجعي (walk-forward) + ضبط alpha تلقائياً + مزج مع ذاكرة أداء
# متراكمة عبر الجلسات (modules/forecast_memory.py).

import numpy as np

from modules.ai_insights import AIInsightsEngine
from modules import forecast_memory
from utils.app_logger import get_logger

log = get_logger("adaptive_forecast")

METHODS = ("linear", "moving_average", "exp_smoothing")
ALPHAS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)

# وزن المزج بين الخطأ الرجعي الحالي والذاكرة المتراكمة
_BLEND_BACKTEST = 0.6
_BLEND_MEMORY = 0.4


class AdaptiveForecaster:
    """يختار تلقائياً أفضل طريقة تنبؤ لسلسلة زمنية معيّنة"""

    def __init__(self, engine=None, memory=None, hold_out=3):
        self.engine = engine or AIInsightsEngine()
        self.memory = memory if memory is not None else {}
        self.hold_out = max(1, int(hold_out))

    # ==================== backtesting ====================

    @staticmethod
    def _series(series):
        return [float(v) for v in (series or []) if v is not None]

    def _predict_next(self, train, method, alpha=None):
        """تنبؤ خطوة واحدة بناءً على نقاط التدريب"""
        if method == "moving_average":
            window = min(3, len(train))
            return float(np.mean(train[-window:]))
        if method == "exp_smoothing":
            a = alpha if alpha is not None else 0.3
            smooth = train[0]
            for x in train[1:]:
                smooth = a * x + (1 - a) * smooth
            return float(smooth)
        # linear
        if len(train) < 2:
            return float(train[-1])
        t = np.arange(len(train), dtype=float)
        slope, intercept = np.polyfit(t, train, 1)
        return float(intercept + slope * len(train))

    def backtest_error(self, series, method, alpha=None):
        """خطأ RMSE للاختبار الرجعي (walk-forward) على آخر hold_out نقطة"""
        s = self._series(series)
        if len(s) <= self.hold_out:
            return float("inf")
        errors = []
        start = len(s) - self.hold_out
        for i in range(start, len(s)):
            train = s[:i]
            if method == "linear" and len(train) < 2:
                continue
            pred = self._predict_next(train, method, alpha)
            errors.append((pred - s[i]) ** 2)
        if not errors:
            return float("inf")
        return float(np.sqrt(np.mean(errors)))

    def best_alpha(self, series):
        """أفضل معامل تجانس أسي (أدنى خطأ رجعي)"""
        best, best_err = 0.3, float("inf")
        for a in ALPHAS:
            err = self.backtest_error(series, "exp_smoothing", alpha=a)
            if err < best_err:
                best, best_err = a, err
        return best, best_err

    # ==================== scoring ====================

    def score_methods(self, series, metric="profit"):
        """درجة كل طريقة = مزج (خطأ رجعي حالياً + خطأ الذاكرة المتراكم)"""
        scores = {}
        for method in METHODS:
            if method == "exp_smoothing":
                alpha, backtest = self.best_alpha(series)
            else:
                alpha, backtest = None, self.backtest_error(series, method)
            mem = forecast_memory.get_memory_error(self.memory, metric, method)
            if backtest == float("inf"):
                score = float("inf") if mem is None else float(mem)
            elif mem is None:
                score = backtest
            else:
                score = _BLEND_BACKTEST * backtest + _BLEND_MEMORY * float(mem)
            scores[method] = {
                "error": score,
                "backtest_error": backtest,
                "memory_error": mem,
                "alpha": alpha,
            }
        return scores

    def choose_method(self, series, metric="profit"):
        """أفضل طريقة (أدنى درجة خطأ). يعيد (method, scores)."""
        scores = self.score_methods(series, metric)
        valid = {m: s for m, s in scores.items() if s["error"] != float("inf")}
        if not valid:
            return "linear", scores
        best = min(valid, key=lambda m: valid[m]["error"])
        return best, scores

    # ==================== forecast ====================

    def forecast_auto(self, series, months=6, metric="profit"):
        """تنبؤ تلقائي: اختيار الطريقة + ضبط alpha + نتائج + درجات"""
        s = self._series(series)
        if not s:
            log.warning("forecast_auto: empty series (%s)", metric)
            return {"error": "empty_series", "forecast": [], "confidence": []}

        months = max(1, int(months))
        method, scores = self.choose_method(s, metric)
        alpha = scores[method].get("alpha")

        if method == "exp_smoothing" and alpha is not None:
            result = self.engine._exp_smoothing_forecast(s, months, alpha=alpha)
        else:
            result = self.engine.forecast(s, months, method)

        result["chosen_method"] = method
        result["method_scores"] = {
            m: {
                "error": None if v["error"] == float("inf") else round(v["error"], 4),
                "backtest_error": None if v["backtest_error"] == float("inf")
                else round(v["backtest_error"], 4),
                "memory_error": v["memory_error"],
            }
            for m, v in scores.items()
        }
        result["adaptive"] = True
        return result


def adaptive_forecast(revenue, expenses, profit, months=6, persist=True, memory=None, path=None):
    """تنبؤ تكيفي للمقاييس الثلاثة. يعيد (forecasts, meta).

    forecasts بنفس شكل engine.forecast_all؛ meta تحمل الطريقة المختارة
    ودرجات كل طريقة لكل مقياس. عند persist=True تُسجَّل الأخطاء الرجعية
    في الذاكرة وتُحفظ (على `path` إن أُعطي، وإلا الملف الافتراضي).
    """
    mem = forecast_memory.load_memory(path) if memory is None else memory
    fc = AdaptiveForecaster(memory=mem)

    forecasts, meta = {}, {}
    for key, series in (("revenue", revenue), ("expenses", expenses), ("profit", profit)):
        result = fc.forecast_auto(series, months, metric=key)
        if "error" in result:
            forecasts[key] = {"forecast": [], "confidence": [], "growth_rate_pct": 0.0}
            continue
        forecasts[key] = {
            "forecast": result["forecast"],
            "confidence": result["confidence"],
            "growth_rate_pct": result["growth_rate_pct"],
        }
        meta[key] = {
            "method": result["chosen_method"],
            "scores": result["method_scores"],
        }
        if persist:
            for m, v in result["method_scores"].items():
                bt = v.get("backtest_error")
                forecast_memory.record_outcome(key, m, bt, memory=mem)

    if persist:
        forecast_memory.save_memory(mem, path)

    log.info("adaptive_forecast: %s", {k: v["method"] for k, v in meta.items()})
    return forecasts, meta
