# محرك التنبؤ المالي المتقدم (ML)
# ================================
# scikit-learn اختياري + احتياط إحصائي
# Isolation Forest للشذوذ + Random Forest للتنبؤ + تصنيف المخاطر

import hashlib
from datetime import date
from utils.app_logger import get_logger

log = get_logger("ml_insights")

try:
    import sklearn.ensemble as _sk_en
    import sklearn.linear_model as _sk_lm
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class MLInsightError(Exception):
    pass


class MLForecaster:
    """تنبؤ مالي متقدم: انحدار متعدد + Random Forest + فترات ثقة."""

    def __init__(self):
        self._model = None

    def forecast_linear(self, x_values, y_values, steps=3):
        """انحدار خطي متعدد (scikit-learn) أو بسيط (numpy). Returns: list of predictions."""
        if not x_values or len(x_values) < 2:
            raise MLInsightError("need at least 2 data points")
        if len(x_values) != len(y_values):
            raise MLInsightError("x and y must be same length")
        if HAS_SKLEARN:
            X = [[i] for i in range(len(y_values))]
            model = _sk_lm.LinearRegression().fit(X, y_values)
            preds = model.predict([[len(y_values) + i] for i in range(steps)])
            return [round(float(p), 2) for p in preds]
        else:
            n = len(y_values)
            mean = sum(y_values) / n
            xm = sum(range(n)) / n
            num = sum((i - xm) * (y_values[i] - mean) for i in range(n))
            den = sum((i - xm) ** 2 for i in range(n))
            slope = num / den if den else 0
            intercept = mean - slope * xm
            return [round(intercept + slope * (n + i), 2) for i in range(steps)]

    def forecast_forest(self, x_values, y_values, steps=3):
        """تنبؤ Random Forest مع فترات ثقة بسيطة."""
        if not HAS_SKLEARN:
            return self.forecast_linear(x_values, y_values, steps)
        if len(x_values) < 5:
            return self.forecast_linear(x_values, y_values, steps)
        X = [[i, i % 12, i % 4] for i in range(len(y_values))]
        rf = _sk_en.RandomForestRegressor(n_estimators=50, random_state=42)
        rf.fit(X, y_values)
        preds = rf.predict([[len(y_values) + i, (len(y_values) + i) % 12,
                             (len(y_values) + i) % 4] for i in range(steps)])
        return [round(float(p), 2) for p in preds]

    def confidence_interval(self, predictions, y_values, z=1.96):
        """فترة ثقة 95%. Returns: (lower, upper) لكل تنبؤ."""
        n = len(y_values)
        if n < 2:
            return [(p, p) for p in predictions]
        import math
        mean = sum(y_values) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in y_values) / (n - 1)) if n > 1 else 0
        margin = z * std
        return [(round(p - margin, 2), round(p + margin, 2)) for p in predictions]


class AnomalyDetector:
    """كشف الشذوذ المالي: Isolation Forest + IQR + z-score."""

    def __init__(self):
        pass

    def detect_isolation_forest(self, data_series, contamination=0.1):
        """كشف شذوذ بـ Isolation Forest (scikit-learn) أو IQR احتياطي."""
        if not data_series or len(data_series) < 4:
            return []
        if HAS_SKLEARN:
            X = [[v] for v in data_series]
            iso = _sk_en.IsolationForest(contamination=contamination,
                                          random_state=42)
            labels = iso.fit_predict(X)
            return [i for i, lbl in enumerate(labels) if lbl == -1]
        return self.detect_iqr(data_series)

    def detect_iqr(self, data_series, multiplier=1.5):
        """IQR method. Returns: list of anomalous indices."""
        if not data_series:
            return []
        sorted_vals = sorted(data_series)
        n = len(sorted_vals)
        q1 = sorted_vals[n // 4]
        q3 = sorted_vals[3 * n // 4]
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        return [i for i, v in enumerate(data_series) if v < lower or v > upper]

    def detect_zscore(self, data_series, threshold=2.0):
        """z-score detection. Returns: list of (index, z_score)."""
        if not data_series or len(data_series) < 3:
            return []
        import math
        n = len(data_series)
        mean = sum(data_series) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in data_series) / n) if n > 0 else 0
        if std == 0:
            return []
        return [(i, round((v - mean) / std, 2))
                for i, v in enumerate(data_series)
                if abs((v - mean) / std) > threshold]


class RiskScorer:
    """نموذج تقييم المخاطر المالية: سيولة + ربحية + مديونية + نمو."""

    def score(self, ratios, financial_data=None):
        """حساب درجة المخاطر من 0 (آمن) إلى 100 (خطر شديد).
        
        Returns: {score, level, factors, recommendations}
        """
        score = 0.0
        factors = {}
        data = ratios or {}
        fd = financial_data or {}

        current_ratio = float(data.get("current_ratio") or 0)
        if current_ratio > 0:
            if current_ratio < 1.0:
                score += 25
                factors["liquidity"] = "critical"
            elif current_ratio < 1.5:
                score += 10
                factors["liquidity"] = "warning"

        debt_ratio = float(data.get("debt_ratio") or 0)
        if debt_ratio > 0.8:
            score += 25
            factors["leverage"] = "critical"
        elif debt_ratio > 0.6:
            score += 10
            factors["leverage"] = "warning"

        roe = float(data.get("roe") or 0)
        if roe < 0:
            score += 20
            factors["profitability"] = "critical"
        elif roe < 5:
            score += 8
            factors["profitability"] = "warning"

        net_margin = float(data.get("net_profit_margin") or 0)
        if net_margin < 0:
            score += 15
            factors["margins"] = "critical"
        elif net_margin < 3:
            score += 5
            factors["margins"] = "warning"

        score = min(score, 100)

        if score >= 70:
            level, color = "خطر شديد", "red"
            recs = ["تحسين السيولة فوراً", "إعادة جدولة الديون"]
        elif score >= 40:
            level, color = "تحذير", "orange"
            recs = ["مراقبة نسبة المديونية", "تحسين هامش الربح"]
        elif score >= 20:
            level, color = "انتباه", "yellow"
            recs = ["متابعة مؤشرات الأداء", "تنويع مصادر الإيراد"]
        else:
            level, color = "آمن", "green"
            recs = ["الوضع المالي مستقر", "مواصلة استراتيجية النمو"]

        return {
            "score": round(score, 1),
            "level": level,
            "factors": factors,
            "recommendations": recs,
        }


ml_forecaster = MLForecaster()
anomaly_detector = AnomalyDetector()
risk_scorer = RiskScorer()
