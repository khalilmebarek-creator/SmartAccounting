"""Fraud Detection Engine — detects suspicious financial data modifications."""

import json
import os
import time
from datetime import datetime
from collections import deque
from utils.app_logger import get_logger

logger = get_logger("fraud_detection")

LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "fraud_log.json"
)

SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"

SEVERITY_ICONS = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
}

FLUSH_INTERVAL = 5.0
FLUSH_THRESHOLD = 10


class FraudDetector:
    """Monitors financial data changes and flags suspicious activity."""

    def __init__(self):
        self._alerts = deque(maxlen=500)
        self._previous_data = {}
        self._edit_times = []
        self._audit_approved = False
        self._dirty = False
        self._last_flush = time.time()
        self._pending_count = 0
        self._load()

    def _load(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._alerts = deque(data[-500:], maxlen=500)
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted fraud log: {e}")
            except Exception as e:
                logger.error(f"Failed to load fraud log: {e}")

    def _save(self):
        tmp_path = LOG_FILE + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(list(self._alerts), f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, LOG_FILE)
            self._dirty = False
            self._pending_count = 0
            self._last_flush = time.time()
        except Exception as e:
            logger.error(f"Failed to save fraud log: {e}")

    def _maybe_flush(self):
        self._pending_count += 1
        now = time.time()
        if (self._pending_count >= FLUSH_THRESHOLD or
                (now - self._last_flush) >= FLUSH_INTERVAL):
            self._save()

    def flush(self):
        if self._dirty:
            self._save()

    def check_data_change(self, field, old_value, new_value, user="system"):
        """Check a single field change against all fraud rules."""
        alerts = []

        # Rule 1: Large change (>20%)
        if old_value and old_value != 0:
            try:
                change_pct = abs(float(new_value) - float(old_value)) / abs(float(old_value))
                if change_pct > 0.20:
                    alerts.append(self._create_alert(
                        severity=SEVERITY_MEDIUM,
                        rule="large_change",
                        field=field,
                        detail=f"Change of {change_pct:.1%} detected",
                        old_val=old_value,
                        new_val=new_value,
                        user=user,
                    ))
            except (ValueError, TypeError):
                pass

        # Rule 2: Negative revenue
        if "revenue" in field.lower() or "إيراد" in field:
            try:
                if float(new_value) < 0:
                    alerts.append(self._create_alert(
                        severity=SEVERITY_HIGH,
                        rule="negative_revenue",
                        field=field,
                        detail="Revenue cannot be negative",
                        old_val=old_value,
                        new_val=new_value,
                        user=user,
                    ))
            except (ValueError, TypeError):
                pass

        # Store current data for comparison
        self._previous_data[field] = new_value

        for alert in alerts:
            self._alerts.append(alert)
        self._dirty = True
        self._maybe_flush()
        return alerts

    def check_balance_sheet(self, data, user="system"):
        """Check balance sheet equation: assets = liabilities + equity.
        Only alerts when the equation is actually violated."""
        total_assets = data.get("total_assets", 0)
        total_liabilities = data.get("total_liabilities", 0)
        equity = data.get("equity", 0)

        if total_assets == 0 and total_liabilities == 0 and equity == 0:
            return []

        diff = abs(total_assets - (total_liabilities + equity))
        if diff > 1:
            alert = self._create_alert(
                severity=SEVERITY_MEDIUM,
                rule="balance_check",
                field="balance_sheet",
                detail=f"Assets ({total_assets:,.0f}) ≠ Liabilities+Equity ({total_liabilities + equity:,.0f}), diff={diff:,.0f}",
                old_val="",
                new_val=str(total_assets),
                user=user,
            )
            self._alerts.append(alert)
            self._dirty = True
            self._maybe_flush()
            return [alert]
        return []

    def check_rapid_edits(self, user="system"):
        """Check if too many edits happened in short time (< 5 min)."""
        now = datetime.now()
        self._edit_times.append(now)

        # Keep only last 5 minutes
        self._edit_times = [
            t for t in self._edit_times
            if (now - t).total_seconds() < 300
        ]

        if len(self._edit_times) > 5:
            alert = self._create_alert(
                severity=SEVERITY_HIGH,
                rule="rapid_edits",
                field="multiple",
                detail=f"{len(self._edit_times)} edits in 5 minutes",
                old_val="",
                new_val="",
                user=user,
            )
            self._alerts.append(alert)
            self._dirty = True
            self._maybe_flush()
            return [alert]
        return []

    def check_after_audit(self, field, new_value, user="system"):
        """Flag changes made after audit approval."""
        if self._audit_approved:
            alert = self._create_alert(
                severity=SEVERITY_HIGH,
                rule="post_audit_change",
                field=field,
                detail="Change made after audit approval",
                old_val="",
                new_val=new_value,
                user=user,
            )
            self._alerts.append(alert)
            self._dirty = True
            self._maybe_flush()
            return [alert]
        return []

    def mark_audit_approved(self):
        self._audit_approved = True

    def mark_audit_reset(self):
        self._audit_approved = False

    def check_tax_consistency(self, financial_data, tax_summary):
        """Check if taxes are consistent with income."""
        if not financial_data or not tax_summary:
            return []
        alerts = []
        net_income = financial_data.get("net_income", 0)
        total_taxes = tax_summary.get("total_taxes", 0)

        if net_income > 0 and total_taxes == 0:
            alerts.append(self._create_alert(
                severity=SEVERITY_MEDIUM,
                rule="no_taxes_with_profit",
                field="taxes",
                detail="Company has profit but no taxes calculated",
                old_val="",
                new_val=str(total_taxes),
                user="system",
            ))

        if total_taxes > 0 and net_income <= 0:
            alerts.append(self._create_alert(
                severity=SEVERITY_HIGH,
                rule="taxes_with_loss",
                field="taxes",
                detail="Taxes calculated but company has loss",
                old_val="",
                new_val=str(total_taxes),
                user="system",
            ))

        for alert in alerts:
            self._alerts.append(alert)
        self._dirty = True
        self._maybe_flush()
        return alerts

    def _create_alert(self, severity, rule, field, detail, old_val, new_val, user):
        alert = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "severity": severity,
            "rule": rule,
            "field": field,
            "detail": detail,
            "old_value": str(old_val),
            "new_value": str(new_val),
            "user": user,
            "icon": SEVERITY_ICONS.get(severity, "⚪"),
        }
        if severity == SEVERITY_HIGH:
            logger.warning(f"HIGH alert: {rule} on {field} ({old_val} -> {new_val}) user={user}")
        elif severity == SEVERITY_MEDIUM:
            logger.info(f"MEDIUM alert: {rule} on {field} ({old_val} -> {new_val})")
        return alert

    def get_alerts(self, severity_filter=None, limit=100):
        alerts = list(self._alerts)
        if severity_filter:
            alerts = [a for a in alerts if a["severity"] == severity_filter]
        return alerts[-limit:]

    def get_alert_count(self):
        return {
            "total": len(self._alerts),
            "high": sum(1 for a in self._alerts if a["severity"] == SEVERITY_HIGH),
            "medium": sum(1 for a in self._alerts if a["severity"] == SEVERITY_MEDIUM),
            "low": sum(1 for a in self._alerts if a["severity"] == SEVERITY_LOW),
        }

    def clear_alerts(self):
        self._alerts.clear()
        self._save()


# Singleton
fraud_detector = FraudDetector()
