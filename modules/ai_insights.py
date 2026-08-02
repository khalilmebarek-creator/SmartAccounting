# محرك الرؤى الذكية المدعومة بالتعلم الآلي
# ==========================================
# Forecasting + Anomaly Detection + Pattern Recognition + Smart Recommendations + Alerts

import numpy as np

from utils.app_logger import get_logger

log = get_logger("ai_insights")


class AIInsightsEngine:
    """محرك الرؤى الذكية — تنبؤ، كشف شذوذ، أنماط، توصيات، تنبيهات"""

    SEVERITY_LEVELS = ("low", "medium", "high")

    def __init__(self, history=None):
        self.history = history or []

    # ==================== Forecasting ====================

    def forecast(self, series, months=6, method="linear"):
        """التنبؤ بسلسلة زمنية مع فترات ثقة"""
        series = [float(v) for v in (series or []) if v is not None]
        if not series:
            log.warning("forecast: empty series")
            return {"error": "empty_series", "forecast": [], "confidence": []}

        months = max(1, int(months))
        n = len(series)

        if method == "moving_average":
            return self._moving_average_forecast(series, months)
        if method == "exp_smoothing":
            return self._exp_smoothing_forecast(series, months)
        return self._linear_forecast(series, months)

    def _linear_forecast(self, series, months):
        """انحدار خطي مع فترات ثقة 95%"""
        n = len(series)
        last = series[-1]
        if n < 2:
            forecast = [{"period": i + 1, "value": round(last, 2)} for i in range(months)]
            confidence = [{"period": i + 1, "lower": round(last, 2), "upper": round(last, 2)}
                          for i in range(months)]
            return self._wrap(series, months, forecast, confidence, "linear",
                              slope=0, r2=None, mae=0.0, direction="flat", last=last)

        t = np.arange(n, dtype=float)
        slope, intercept = np.polyfit(t, series, 1)
        fitted = intercept + slope * t
        residuals = np.array(series) - fitted
        se = float(np.sqrt(np.mean(residuals ** 2)))
        mae = float(np.mean(np.abs(residuals)))
        sxx = float(np.sum((t - t.mean()) ** 2))
        xbar = float(t.mean())

        forecast = []
        confidence = []
        for i in range(months):
            x_new = n + i
            pred = float(intercept + slope * x_new)
            half = 1.96 * se * np.sqrt(1 + 1 / n + (x_new - xbar) ** 2 / sxx) if sxx > 0 else 0.0
            forecast.append({"period": i + 1, "value": round(pred, 2)})
            confidence.append({
                "period": i + 1,
                "lower": round(pred - half, 2),
                "upper": round(pred + half, 2),
            })

        r2 = self._r2(series, fitted)
        direction = "up" if slope > 0.5 else ("down" if slope < -0.5 else "flat")
        return self._wrap(series, months, forecast, confidence, "linear",
                          slope=slope, r2=r2, mae=mae, direction=direction, last=last)

    def _moving_average_forecast(self, series, months):
        """متوسط متحرك (نافذة 3)"""
        n = len(series)
        last = series[-1]
        window = min(3, n)
        last_avg = float(np.mean(series[-window:]))
        residuals = np.array(series) - last_avg
        se = float(np.std(residuals))

        forecast = [{"period": i + 1, "value": round(last_avg, 2)} for i in range(months)]
        half = 1.96 * se if se > 0 else 0.0
        confidence = [{
            "period": i + 1,
            "lower": round(last_avg - half, 2),
            "upper": round(last_avg + half, 2),
        } for i in range(months)]
        return self._wrap(series, months, forecast, confidence, "moving_average",
                          slope=0, r2=None, mae=float(np.mean(np.abs(residuals))),
                          direction="flat", last=last)

    def _exp_smoothing_forecast(self, series, months, alpha=0.3):
        """تجانس أسي"""
        n = len(series)
        last = series[-1]
        smooth = series[0]
        smoothed_history = [smooth]
        for x in series[1:]:
            smooth = alpha * x + (1 - alpha) * smooth
            smoothed_history.append(smooth)
        residuals = np.array(series) - np.array(smoothed_history)
        se = float(np.std(residuals))

        forecast = [{"period": i + 1, "value": round(smooth, 2)} for i in range(months)]
        half = 1.96 * se if se > 0 else 0.0
        confidence = [{
            "period": i + 1,
            "lower": round(smooth - half, 2),
            "upper": round(smooth + half, 2),
        } for i in range(months)]
        return self._wrap(series, months, forecast, confidence, "exp_smoothing",
                          slope=0, r2=None, mae=float(np.mean(np.abs(residuals))),
                          direction="flat", last=last)

    def _wrap(self, series, months, forecast, confidence, method,
              slope, r2, mae, direction, last):
        mean_val = float(np.mean(series))
        growth = 0.0
        if last > 0 and forecast:
            growth = (forecast[-1]["value"] / last - 1) * 100
        elif mean_val > 0:
            growth = slope / mean_val * 100
        return {
            "method": method,
            "months": months,
            "history_len": len(series),
            "forecast": forecast,
            "confidence": confidence,
            "r2": r2,
            "mae": mae,
            "trend_direction": direction,
            "last_value": round(last, 2),
            "growth_rate_pct": round(growth, 2),
        }

    @staticmethod
    def _r2(series, fitted):
        try:
            sstot = float(np.sum((np.array(series) - np.mean(series)) ** 2))
            if sstot == 0:
                return None
            ssres = float(np.sum((np.array(series) - fitted) ** 2))
            return round(1 - ssres / sstot, 4)
        except Exception:
            return None

    def forecast_all(self, revenue, expenses, profit, months=6, method="linear"):
        """التنبؤ بالإيرادات والمصروفات والأرباح معاً"""
        result = {}
        for key, series in (("revenue", revenue), ("expenses", expenses), ("profit", profit)):
            fc = self.forecast(series, months, method)
            if "error" in fc:
                result[key] = {"forecast": [], "confidence": [], "growth_rate_pct": 0.0}
            else:
                result[key] = {
                    "forecast": fc["forecast"],
                    "confidence": fc["confidence"],
                    "growth_rate_pct": fc["growth_rate_pct"],
                }
        return result

    # ==================== Anomaly Detection ====================

    def detect_anomalies(self, series, threshold=2.0):
        """كشف الشذوذ في سلسلة زمنية عبر z-score"""
        series = [float(v) for v in (series or []) if v is not None]
        if len(series) < 3:
            return []
        arr = np.array(series)
        mean = float(arr.mean())
        std = float(arr.std())
        if std == 0:
            return []
        anomalies = []
        for i, value in enumerate(series):
            z = abs((value - mean) / std)
            if z > threshold:
                anomalies.append({
                    "index": i,
                    "value": round(value, 2),
                    "expected": round(mean, 2),
                    "z_score": round(z, 2),
                    "severity": self._severity(z),
                })
        return anomalies

    def detect_transaction_anomalies(self, transactions, threshold=2.0):
        """كشف المعاملات الشاذة عبر قاعدة IQR"""
        if not transactions:
            return []
        items = []
        for tx in transactions:
            if isinstance(tx, dict):
                items.append(tx)
            else:
                items.append({"amount": tx, "description": ""})
        amounts = np.array([float(i.get("amount", 0)) for i in items], dtype=float)
        if len(amounts) < 4:
            return []
        q1 = float(np.percentile(amounts, 25))
        q3 = float(np.percentile(amounts, 75))
        iqr = q3 - q1
        if iqr == 0:
            return []
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mean = float(amounts.mean())
        std = float(amounts.std())
        anomalies = []
        for i, item in enumerate(items):
            amount = float(item.get("amount", 0))
            if amount < lower or amount > upper:
                z = abs(amount - mean) / std if std > 0 else 0.0
                anomalies.append({
                    "amount": round(amount, 2),
                    "description": item.get("description", ""),
                    "date": item.get("date", ""),
                    "score": round(z, 2),
                    "lower_bound": round(lower, 2),
                    "upper_bound": round(upper, 2),
                    "severity": self._severity(z),
                })
        anomalies.sort(key=lambda a: a["amount"], reverse=True)
        return anomalies

    def detect_ratio_anomalies(self, current, previous, threshold=2.0):
        """كشف تغيرات النسب غير المتوقعة"""
        current = current or {}
        previous = previous or {}
        anomalies = []
        for key, value in current.items():
            prev = previous.get(key)
            if prev is None or prev == 0:
                continue
            try:
                change = abs(float(value) - float(prev)) / abs(float(prev))
            except (ValueError, TypeError):
                continue
            if change > max(0.5, threshold * 0.1):
                anomalies.append({
                    "ratio": key,
                    "current": float(value),
                    "previous": float(prev),
                    "change_pct": round(change * 100, 2),
                    "severity": self._severity(change / 0.1),
                })
        return anomalies

    def unexpected_profit_loss(self, profit_series):
        """كشف انقلاب الربح إلى خسارة أو العكس"""
        profit_series = [float(v) for v in (profit_series or []) if v is not None]
        result = []
        for i in range(1, len(profit_series)):
            prev = profit_series[i - 1]
            value = profit_series[i]
            if prev > 0 >= value:
                result.append({
                    "period": i,
                    "value": round(value, 2),
                    "previous": round(prev, 2),
                    "type": "loss_after_profit",
                })
            elif prev < 0 <= value:
                result.append({
                    "period": i,
                    "value": round(value, 2),
                    "previous": round(prev, 2),
                    "type": "profit_after_loss",
                })
        return result

    @staticmethod
    def _severity(z):
        if z >= 3:
            return "high"
        if z >= 2.5:
            return "medium"
        return "low"

    # ==================== Pattern Recognition ====================

    def patterns(self, series, periods_per_year=12):
        """تحليل الأنماط: الاتجاه + الموسمية + الدورات + مؤشرات المخاطر"""
        series = [float(v) for v in (series or []) if v is not None]
        trend = self._trend(series)
        seasonality = self._seasonality(series, periods_per_year)
        cyclical = self._cyclical(series)
        risk = self._risk_indicators(series)
        return {
            "trend": trend,
            "seasonality": seasonality,
            "cyclical": cyclical,
            "risk_indicators": risk,
        }

    def _trend(self, series):
        n = len(series)
        if n < 2:
            return {"slope": 0.0, "direction": "flat", "growth_rate_pct": 0.0}
        t = np.arange(n, dtype=float)
        slope, _ = np.polyfit(t, series, 1)
        mean = float(np.mean(series))
        growth = slope / mean * 100 if mean > 0 else 0.0
        direction = "up" if slope > 0.5 else ("down" if slope < -0.5 else "flat")
        return {
            "slope": round(float(slope), 4),
            "direction": direction,
            "growth_rate_pct": round(float(growth), 2),
        }

    def _seasonality(self, series, periods_per_year):
        n = len(series)
        if n < periods_per_year * 2:
            return {
                "indexes": [], "peak_month": None, "trough_month": None,
                "seasonal_strength": 0.0, "complete_cycles": 0,
            }
        n_cycles = n // periods_per_year
        arr = np.array(series[:n_cycles * periods_per_year])
        arr = arr.reshape(n_cycles, periods_per_year)
        month_means = arr.mean(axis=0)
        overall = float(arr.mean())
        if overall == 0:
            return {
                "indexes": [0.0] * periods_per_year,
                "peak_month": 1, "trough_month": 1,
                "seasonal_strength": 0.0, "complete_cycles": n_cycles,
            }
        indexes = month_means / overall
        peak = int(np.argmax(indexes)) + 1
        trough = int(np.argmin(indexes)) + 1
        return {
            "indexes": [round(float(x), 4) for x in indexes],
            "peak_month": peak,
            "trough_month": trough,
            "seasonal_strength": round(float(indexes.max() - indexes.min()), 4),
            "complete_cycles": n_cycles,
        }

    def _cyclical(self, series):
        n = len(series)
        if n < 6:
            return {"cycle_length": 1, "stability": 0.0}
        t = np.arange(n, dtype=float)
        try:
            slope, intercept = np.polyfit(t, series, 1)
            detrended = np.array(series) - (intercept + slope * t)
        except Exception:
            detrended = np.array(series)
        detrended = detrended - detrended.mean()
        std = float(detrended.std())
        if std == 0:
            return {"cycle_length": 1, "stability": 0.0}
        max_lag = min(n // 2, 12)
        best_lag, best_corr = 1, 0.0
        for lag in range(2, max_lag + 1):
            corr = float(np.corrcoef(detrended[:-lag], detrended[lag:])[0, 1])
            if corr > best_corr:
                best_corr = corr
                best_lag = lag
        return {
            "cycle_length": best_lag if best_corr > 0 else 1,
            "stability": round(best_corr, 4),
        }

    def _risk_indicators(self, series):
        if not series:
            return []
        arr = np.array(series)
        mean = float(arr.mean())
        std = float(arr.std())
        volatility = std / mean * 100 if mean > 0 else 0.0
        peak = -float("inf")
        max_drawdown = 0.0
        for value in arr:
            peak = max(peak, float(value))
            if peak > 0:
                drawdown = (peak - float(value)) / peak
                max_drawdown = max(max_drawdown, drawdown)
        negative_months = int(np.sum(arr < 0))
        return [
            {"name": "volatility", "value": round(volatility, 2),
             "level": self._level(volatility, 10, 30)},
            {"name": "max_drawdown", "value": round(max_drawdown * 100, 2),
             "level": self._level(max_drawdown * 100, 20, 40)},
            {"name": "negative_months", "value": negative_months,
             "level": "high" if negative_months > 3 else ("medium" if negative_months > 0 else "low")},
        ]

    @staticmethod
    def _level(value, low_threshold, high_threshold):
        if value >= high_threshold:
            return "high"
        if value >= low_threshold:
            return "medium"
        return "low"

    # ==================== Smart Recommendations ====================

    def recommendations(self, ratios=None, cash=0, monthly_expenses=0, revenue_growth=0.0):
        """توصيات ذكية: تحسين النسب، النقدية، الكفاءة، فرص النمو"""
        ratios = ratios or {}
        recs = []

        current_ratio = ratios.get("current_ratio", 0)
        if 0 < current_ratio < 1.5:
            recs.append({"category": "weak_ratio", "priority": "high",
                         "title": "current_ratio", "detail": "current_ratio_low"})

        quick_ratio = ratios.get("quick_ratio", 0)
        if 0 < quick_ratio < 1.0:
            recs.append({"category": "weak_ratio", "priority": "high",
                         "title": "quick_ratio", "detail": "quick_ratio_low"})

        debt = ratios.get("debt_to_equity", 0)
        if debt > 1.5:
            recs.append({"category": "weak_ratio", "priority": "high",
                         "title": "debt_to_equity", "detail": "debt_high"})

        npm = ratios.get("net_profit_margin", 0)
        if 0 < npm < 5:
            recs.append({"category": "weak_ratio", "priority": "medium",
                         "title": "net_profit_margin", "detail": "margin_low"})

        roe = ratios.get("roe", 0)
        if 0 < roe < 10:
            recs.append({"category": "weak_ratio", "priority": "medium",
                         "title": "roe", "detail": "roe_low"})

        if monthly_expenses > 0:
            cash_months = cash / monthly_expenses
            if cash_months < 3:
                recs.append({"category": "cash", "priority": "high",
                             "title": "cash_reserves", "detail": f"cash_months:{cash_months:.1f}"})
            elif cash_months < 6:
                recs.append({"category": "cash", "priority": "low",
                             "title": "cash_reserves", "detail": f"cash_months:{cash_months:.1f}"})

        turnover = ratios.get("asset_turnover", 0)
        if 0 < turnover < 1:
            recs.append({"category": "efficiency", "priority": "medium",
                         "title": "asset_turnover", "detail": "turnover_low"})

        if revenue_growth >= 0.15:
            recs.append({"category": "growth", "priority": "high",
                         "title": "growth_opportunity", "detail": f"growth:{revenue_growth * 100:.0f}%"})

        return recs

    # ==================== Smart Alerts ====================

    def alerts(self, forecasts=None, anomalies=None, patterns=None, ratios=None, recommendations=None):
        """تنبيهات ذكية: تحذيرات تنبؤية + فرص + مخاطر + إجراءات"""
        forecasts = forecasts or {}
        anomalies = anomalies or []
        patterns = patterns or {}
        recommendations = recommendations or []
        alerts = []

        high = sum(1 for a in anomalies if a.get("severity") == "high")
        medium = sum(1 for a in anomalies if a.get("severity") == "medium")
        if high:
            alerts.append({"type": "risk", "severity": "high", "message": "anomalies_high"})
        elif medium:
            alerts.append({"type": "risk", "severity": "medium", "message": "anomalies_medium"})
        elif anomalies:
            alerts.append({"type": "risk", "severity": "low", "message": "anomalies_low"})

        profit_growth = forecasts.get("profit", {}).get("growth_rate_pct", 0) or 0
        if profit_growth < -10:
            alerts.append({"type": "predictive_warning", "severity": "high", "message": "profit_declining"})
        elif profit_growth < 0:
            alerts.append({"type": "predictive_warning", "severity": "medium", "message": "profit_slowdown"})

        revenue_growth = forecasts.get("revenue", {}).get("growth_rate_pct", 0) or 0
        if revenue_growth >= 15:
            alerts.append({"type": "opportunity", "severity": "high", "message": "revenue_growth"})
        elif revenue_growth >= 8:
            alerts.append({"type": "opportunity", "severity": "low", "message": "revenue_steady"})

        for indicator in patterns.get("risk_indicators", []):
            if indicator.get("level") == "high":
                alerts.append({"type": "risk", "severity": "high",
                               "message": f"risk_{indicator.get('name', '')}"})

        for rec in recommendations:
            alerts.append({
                "type": "action",
                "severity": rec.get("priority", "medium"),
                "message": rec.get("title", "recommendation"),
            })

        return alerts

    # ==================== Unified ====================

    def generate_insights(self, revenue_history, expense_history, profit_history,
                          transactions=None, ratios=None, months=6, method="linear"):
        """توليد موحّد لكل الرؤى الذكية"""
        forecasts = self.forecast_all(revenue_history, expense_history, profit_history, months, method)

        series_anomalies = self.detect_anomalies(profit_history)
        transaction_anomalies = self.detect_transaction_anomalies(transactions) if transactions else []

        patterns = self.patterns(revenue_history or profit_history)

        revenue_growth = forecasts.get("revenue", {}).get("growth_rate_pct", 0) / 100.0
        monthly_expenses = float(np.mean(expense_history)) if expense_history else 0.0
        cash = (ratios or {}).get("cash", 0) or 0
        recommendations = self.recommendations(ratios, cash, monthly_expenses, revenue_growth)

        alerts = self.alerts(forecasts, series_anomalies, patterns, ratios, recommendations)

        return {
            "forecasts": forecasts,
            "anomalies": {
                "profit": series_anomalies,
                "transactions": transaction_anomalies,
            },
            "patterns": patterns,
            "recommendations": recommendations,
            "alerts": alerts,
        }


# Singleton
ai_insights_engine = AIInsightsEngine()
