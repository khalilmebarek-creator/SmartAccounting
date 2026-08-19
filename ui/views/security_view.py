"""Security View — fraud detection alerts and email notifications."""

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QTextEdit, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (QColor)

from ui.resources.i18n import t
from ui.app_state import ThemeColors
from modules.fraud_detection import fraud_detector, SEVERITY_ICONS
from modules.email_notifier import email_notifier


class SecurityView(QWidget):
    """Security and fraud detection dashboard."""

    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        self.title_label = QLabel(t("security_title"))
        self.title_label.setObjectName("headerTitle")
        main_layout.addWidget(self.title_label)

        # Stats cards
        stats_layout = QHBoxLayout()
        self.stat_total = self._make_stat_card(t("security_total"), "0", ThemeColors.get('info'))
        self.stat_high = self._make_stat_card(t("security_high"), "0", ThemeColors.get('error'))
        self.stat_medium = self._make_stat_card(t("security_medium"), "0", ThemeColors.get('warning'))
        self.stat_low = self._make_stat_card(t("security_low"), "0", ThemeColors.get('success'))
        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_high)
        stats_layout.addWidget(self.stat_medium)
        stats_layout.addWidget(self.stat_low)
        main_layout.addLayout(stats_layout)

        # Filter + buttons
        toolbar = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            t("security_filter_all"),
            t("security_filter_high"),
            t("security_filter_medium"),
            t("security_filter_low"),
        ])
        self.filter_combo.currentIndexChanged.connect(self._refresh_table)
        toolbar.addWidget(self.filter_combo)

        self.refresh_btn = QPushButton(t("security_refresh"))
        self.refresh_btn.clicked.connect(self._refresh_table)
        toolbar.addWidget(self.refresh_btn)

        self.send_summary_btn = QPushButton(t("security_send_summary"))
        self.send_summary_btn.clicked.connect(self._send_summary)
        toolbar.addWidget(self.send_summary_btn)

        self.clear_btn = QPushButton(t("security_clear"))
        self.clear_btn.clicked.connect(self._clear_alerts)
        toolbar.addWidget(self.clear_btn)

        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(6)
        self.alerts_table.setHorizontalHeaderLabels([
            t("security_col_time"), t("security_col_severity"),
            t("security_col_rule"), t("security_col_field"),
            t("security_col_detail"), t("security_col_values"),
        ])
        self.alerts_table.horizontalHeader().setStretchLastSection(True)
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.alerts_table.selectionModel().selectionChanged.connect(self._show_detail)
        main_layout.addWidget(self.alerts_table)

        # Detail panel
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(120)
        self.detail_text.setObjectName("infoText")
        main_layout.addWidget(self.detail_text)

        self.setLayout(main_layout)

    def _make_stat_card(self, title, value, color):
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setMinimumHeight(80)
        layout = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("subtitleLabel")
        lbl_value = QLabel(value)
        lbl_value.setObjectName("statValue")
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = lbl_value.font()
        font.setBold(True)
        font.setPointSize(18)
        lbl_value.setFont(font)
        lbl_value.setStyleSheet(f"color: {color};")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return frame

    def _refresh_table(self):
        try:
            counts = fraud_detector.get_alert_count()
            cards = [self.stat_total, self.stat_high, self.stat_medium, self.stat_low]
            values = [str(counts["total"]), str(counts["high"]), str(counts["medium"]), str(counts["low"])]
            for card, val in zip(cards, values):
                lbl = card.findChild(QLabel, "statValue")
                if lbl:
                    lbl.setText(val)

            filter_idx = self.filter_combo.currentIndex()
            severity_map = {0: None, 1: "high", 2: "medium", 3: "low"}
            severity = severity_map.get(filter_idx)
            alerts = fraud_detector.get_alerts(severity_filter=severity, limit=200)

            self.alerts_table.setRowCount(len(alerts))
            for i, alert in enumerate(reversed(alerts)):
                severity = alert.get("severity", "low")
                icon = SEVERITY_ICONS.get(severity, "⚪")

                time_item = QTableWidgetItem(alert.get("time", ""))
                sev_item = QTableWidgetItem(f"{icon} {severity.upper()}")
                rule_item = QTableWidgetItem(alert.get("rule", ""))
                field_item = QTableWidgetItem(alert.get("field", ""))
                detail_item = QTableWidgetItem(alert.get("detail", ""))
                values_item = QTableWidgetItem(f"{alert.get('old_value', '')} → {alert.get('new_value', '')}")

                if severity == "high":
                    for item in [sev_item]:
                        item.setForeground(QColor(ThemeColors.get('error')))
                elif severity == "medium":
                    for item in [sev_item]:
                        item.setForeground(QColor(ThemeColors.get('warning')))

                self.alerts_table.setItem(i, 0, time_item)
                self.alerts_table.setItem(i, 1, sev_item)
                self.alerts_table.setItem(i, 2, rule_item)
                self.alerts_table.setItem(i, 3, field_item)
                self.alerts_table.setItem(i, 4, detail_item)
                self.alerts_table.setItem(i, 5, values_item)
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("security_view").error(f"Failed to refresh table: {e}")

    def _show_detail(self):
        try:
            rows = self.alerts_table.selectionModel().selectedRows()
            if not rows:
                return
            row = rows[0].row()
            rule = self.alerts_table.item(row, 2).text() if self.alerts_table.item(row, 2) else ""
            detail = self.alerts_table.item(row, 4).text() if self.alerts_table.item(row, 4) else ""
            values = self.alerts_table.item(row, 5).text() if self.alerts_table.item(row, 5) else ""
            self.detail_text.setText(f"Rule: {rule}\nDetail: {detail}\nValues: {values}")
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("security_view").error(f"Failed to show detail: {e}")

    def _send_summary(self):
        if not email_notifier.is_configured():
            QMessageBox.warning(self, t("warning"), t("security_email_not_configured"))
            return
        counts = fraud_detector.get_alert_count()
        high_alerts = fraud_detector.get_alerts(severity_filter="high", limit=10)
        ok, msg = email_notifier.send_summary(counts, high_alerts)
        if ok:
            QMessageBox.information(self, t("success"), t("security_summary_sent"))
        else:
            QMessageBox.critical(self, t("error"), f"{t('security_summary_fail')}\n{msg}")

    def _clear_alerts(self):
        reply = QMessageBox.question(
            self, t("confirm_delete_title"), t("security_clear_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            fraud_detector.clear_alerts()
            self._refresh_table()

    def retranslate(self):
        self.title_label.setText(t("security_title"))
        self.refresh_btn.setText(t("security_refresh"))
        self.send_summary_btn.setText(t("security_send_summary"))
        self.clear_btn.setText(t("security_clear"))
        self.alerts_table.setHorizontalHeaderLabels([
            t("security_col_time"), t("security_col_severity"),
            t("security_col_rule"), t("security_col_field"),
            t("security_col_detail"), t("security_col_values"),
        ])
        current_idx = self.filter_combo.currentIndex()
        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()
        self.filter_combo.addItems([
            t("security_filter_all"),
            t("security_filter_high"),
            t("security_filter_medium"),
            t("security_filter_low"),
        ])
        if 0 <= current_idx < self.filter_combo.count():
            self.filter_combo.setCurrentIndex(current_idx)
        self.filter_combo.blockSignals(False)
