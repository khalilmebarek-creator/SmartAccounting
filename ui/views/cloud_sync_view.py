# واجهة المزامنة السحابية والنسخ الاحتياطي
# ==========================================
# إدارة وجهات المزامنة + النسخ الاحتياطي المحلي + الاسترجاع + كلمة مرور التشفير + السجل

from ui.views._path import _  # noqa: F401

import os
import time

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QCheckBox,
    QSpinBox, QMessageBox, QFileDialog, QHeaderView, QFrame
)
from PyQt5.QtGui import QFont, QColor

from ui.views._base import BaseView
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from ui.widgets.messages import show_feature_denied
from commercial.entitlement import feature_allowed
from modules.cloud_sync import (
    cloud_sync_engine, DEFAULT_BACKUP_DIR, MAX_BACKUPS,
)

_ACTION_KEYS = {
    "push": "cloud_action_push",
    "pull": "cloud_action_pull",
    "backup": "cloud_action_backup",
    "restore": "cloud_action_restore",
}


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class CloudSyncView(BaseView):
    """واجهة المزامنة السحابية والنسخ الاحتياطي"""

    def __init__(self):
        super().__init__()
        self._engine = cloud_sync_engine
        self.setup_ui()
        self.refresh()

    @staticmethod
    def _make_stat(title):
        """كارت إحصائية مع مرجع لملصق القيمة."""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #888;")
        lbl_value = QLabel("0")
        lbl_value.setObjectName("statValue")
        font = QFont()
        font.setBold(True)
        font.setPointSize(15)
        lbl_value.setFont(font)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        frame.setLayout(layout)
        return frame, lbl_value

    # ===== البناء =====

    def setup_ui(self):
        self._make_header("cloud_title", "cloud_subtitle")

        # 1) الحالة
        status_layout = QGridLayout()
        f1, self.stat_destinations = self._make_stat(t("cloud_status_destinations"))
        f2, self.stat_last_event = self._make_stat(t("cloud_status_last_event"))
        f3, self.stat_auto = self._make_stat(t("cloud_status_auto_backup"))
        f4, self.stat_passphrase = self._make_stat(t("cloud_status_passphrase"))
        status_layout.addWidget(f1, 0, 0)
        status_layout.addWidget(f2, 0, 1)
        status_layout.addWidget(f3, 0, 2)
        status_layout.addWidget(f4, 0, 3)
        self._main_layout.addLayout(status_layout)

        # 2) وجهات المزامنة
        dest_card = self._make_card("cloud_destinations")
        self.dest_table = QTableWidget()
        self.dest_table.setColumnCount(4)
        self.dest_table.setHorizontalHeaderLabels([
            t("cloud_dest_name"), t("cloud_dest_path"),
            t("cloud_dest_auto"), t("cloud_dest_snapshots"),
        ])
        self.dest_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dest_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dest_table.setSelectionMode(QTableWidget.SingleSelection)
        self.dest_table.setEditTriggers(QTableWidget.NoEditTriggers)
        dest_card.layout().addWidget(self.dest_table)

        add_row = QHBoxLayout()
        self.dest_name = QLineEdit()
        self.dest_name.setPlaceholderText(t("cloud_name"))
        self.dest_path = QLineEdit()
        self.dest_path.setPlaceholderText(t("cloud_dest_path"))
        browse_btn = QPushButton(t("cloud_browse"))
        browse_btn.clicked.connect(self._browse_dest)
        add_btn = QPushButton(t("cloud_add"))
        add_btn.clicked.connect(self._add_dest)
        del_btn = QPushButton(t("cloud_delete"))
        del_btn.clicked.connect(self._delete_dest)
        push_btn = QPushButton(t("cloud_push"))
        push_btn.clicked.connect(self._push_selected)
        push_all_btn = QPushButton(t("cloud_push_all"))
        push_all_btn.clicked.connect(self._push_all)
        for w in (self.dest_name, self.dest_path, browse_btn, add_btn,
                  del_btn, push_btn, push_all_btn):
            add_row.addWidget(w)
        dest_card.layout().addLayout(add_row)
        self._main_layout.addWidget(dest_card)

        # 3) النسخ الاحتياطي والاسترجاع
        backup_card = self._make_card("cloud_backup_section")
        row1 = QHBoxLayout()
        backup_btn = QPushButton(t("cloud_backup_local"))
        backup_btn.clicked.connect(self._backup_local)
        row1.addWidget(backup_btn)
        row1.addWidget(QLabel(t("cloud_local_backups")))
        row1.addStretch()
        backup_card.layout().addLayout(row1)

        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels([
            t("cloud_file"), t("cloud_size"), t("cloud_time"), t("cloud_encrypted"),
        ])
        self.backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.backup_table.setSelectionMode(QTableWidget.SingleSelection)
        self.backup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        backup_card.layout().addWidget(self.backup_table)

        row2 = QHBoxLayout()
        restore_btn = QPushButton(t("cloud_restore"))
        restore_btn.clicked.connect(self._restore_selected)
        row2.addWidget(restore_btn)
        from_file_btn = QPushButton(t("cloud_restore_file"))
        from_file_btn.clicked.connect(self._restore_from_file)
        row2.addWidget(from_file_btn)
        row2.addWidget(QLabel(t("cloud_pull_from")))
        self.pull_combo = QComboBox()
        row2.addWidget(self.pull_combo)
        self.snap_combo = QComboBox()
        self.snap_combo.setMinimumWidth(260)
        row2.addWidget(self.snap_combo)
        refresh_snaps_btn = QPushButton(t("cloud_refresh_snaps"))
        refresh_snaps_btn.clicked.connect(self._refresh_pull_snapshots)
        row2.addWidget(refresh_snaps_btn)
        pull_btn = QPushButton(t("cloud_pull"))
        pull_btn.clicked.connect(self._pull)
        row2.addWidget(pull_btn)
        row2.addStretch()
        backup_card.layout().addLayout(row2)
        self._main_layout.addWidget(backup_card)

        # 4) الإعدادات التلقائية
        auto_card = self._make_card("cloud_auto_settings")
        auto_row = QHBoxLayout()
        self.auto_check = QCheckBox(t("cloud_auto_backup"))
        auto_row.addWidget(self.auto_check)
        auto_row.addWidget(QLabel(t("cloud_interval_hours")))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 24 * 30)
        self.interval_spin.setValue(24)
        self.interval_spin.setSuffix(" h")
        auto_row.addWidget(self.interval_spin)
        auto_row.addWidget(QLabel(t("cloud_max_backups")))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 200)
        self.max_spin.setValue(MAX_BACKUPS)
        auto_row.addWidget(self.max_spin)
        save_auto_btn = QPushButton(t("cloud_save"))
        save_auto_btn.clicked.connect(self._save_auto_settings)
        auto_row.addWidget(save_auto_btn)
        auto_row.addStretch()
        auto_card.layout().addLayout(auto_row)
        self._main_layout.addWidget(auto_card)

        # 5) كلمة المرور
        pass_card = self._make_card("cloud_passphrase")
        pass_row = QHBoxLayout()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText(t("cloud_passphrase"))
        pass_row.addWidget(self.pass_input)
        set_pass_btn = QPushButton(t("cloud_set_passphrase"))
        set_pass_btn.clicked.connect(self._set_passphrase)
        pass_row.addWidget(set_pass_btn)
        clear_pass_btn = QPushButton(t("cloud_clear_passphrase"))
        clear_pass_btn.clicked.connect(self._clear_passphrase)
        pass_row.addWidget(clear_pass_btn)
        pass_row.addStretch()
        pass_card.layout().addLayout(pass_row)
        self._main_layout.addWidget(pass_card)

        # 6) السجل
        hist_card = self._make_card("cloud_history")
        hist_row = QHBoxLayout()
        refresh_hist_btn = QPushButton(t("cloud_refresh_history"))
        refresh_hist_btn.clicked.connect(self._refresh_history)
        hist_row.addWidget(refresh_hist_btn)
        clear_hist_btn = QPushButton(t("cloud_clear_history"))
        clear_hist_btn.clicked.connect(self._clear_history)
        hist_row.addWidget(clear_hist_btn)
        export_hist_btn = QPushButton(t("cloud_export_csv"))
        export_hist_btn.clicked.connect(self._export_history)
        hist_row.addWidget(export_hist_btn)
        hist_row.addStretch()
        hist_card.layout().addLayout(hist_row)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            t("cloud_time"), t("cloud_action"), t("cloud_destination"),
            t("cloud_status"),
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.verticalHeader().setDefaultSectionSize(44)
        self.history_table.setMinimumHeight(200)
        hist_card.layout().addWidget(self.history_table)
        self._main_layout.addWidget(hist_card)

        self._main_layout.addStretch()

    # ===== التحديث =====

    def refresh(self):
        st = self._engine.status()
        self.stat_destinations.setText(str(st["destinations"]))
        last = st["last_event"]
        if last:
            text = (
                f"{t(_ACTION_KEYS.get(last['action'], 'cloud_action_backup'))} "
                f"· {time.strftime('%Y-%m-%d %H:%M', time.localtime(last['ts']))}"
            )
        else:
            text = t("cloud_never")
        self.stat_last_event.setText(text)
        self.stat_auto.setText(
            t("cloud_yes") if st["auto_backup"] else t("cloud_no")
        )
        self.stat_passphrase.setText(
            t("cloud_yes") if st["has_passphrase"] else t("cloud_no")
        )

        self._refresh_destinations()
        self._refresh_backups()
        self._refresh_pull_snapshots()
        self._refresh_auto_settings()
        self._refresh_history()

    def _refresh_destinations(self):
        dests = self._engine.list_destinations()
        self.dest_table.setRowCount(len(dests))
        for row, dest in enumerate(dests):
            snap_count = len(self._engine.list_snapshots(dest["path"]))
            self.dest_table.setItem(row, 0, QTableWidgetItem(dest.get("name", "")))
            self.dest_table.setItem(row, 1, QTableWidgetItem(dest.get("path", "")))
            self.dest_table.setItem(
                row, 2,
                QTableWidgetItem(t("cloud_yes") if dest.get("auto") else t("cloud_no")),
            )
            self.dest_table.setItem(row, 3, QTableWidgetItem(str(snap_count)))

        current = self.pull_combo.currentText()
        self.pull_combo.blockSignals(True)
        self.pull_combo.clear()
        for dest in dests:
            self.pull_combo.addItem(dest.get("name", ""), dest.get("id"))
        if current:
            self.pull_combo.setCurrentText(current)
        self.pull_combo.blockSignals(False)

    def _refresh_backups(self):
        snaps = self._engine.list_snapshots(DEFAULT_BACKUP_DIR)
        self.backup_table.setRowCount(len(snaps))
        for row, snap in enumerate(snaps):
            self.backup_table.setItem(row, 0, QTableWidgetItem(snap["name"]))
            self.backup_table.setItem(row, 1, QTableWidgetItem(_plain(
                f"{snap['size'] / 1024:.1f} KB"
            )))
            self.backup_table.setItem(
                row, 2,
                QTableWidgetItem(
                    time.strftime("%Y-%m-%d %H:%M", time.localtime(snap["timestamp"]))
                ),
            )
            self.backup_table.setItem(
                row, 3,
                QTableWidgetItem(t("cloud_yes") if snap["encrypted"] else t("cloud_no")),
            )

    def _refresh_pull_snapshots(self):
        dest_id = self.pull_combo.currentData()
        self.snap_combo.clear()
        if dest_id is None:
            return
        dest = next(
            (d for d in self._engine.list_destinations() if d.get("id") == dest_id),
            None,
        )
        if not dest:
            return
        for snap in self._engine.list_snapshots(dest["path"]):
            self.snap_combo.addItem(snap["name"])

    def _refresh_auto_settings(self):
        s = self._engine.settings()
        self.auto_check.setChecked(bool(s.get("auto_backup")))
        self.interval_spin.setValue(int(s.get("auto_backup_interval_hours", 24)))
        self.max_spin.setValue(int(s.get("max_backups", MAX_BACKUPS)))
        self.pass_input.clear()

    def _refresh_history(self):
        history = self._engine.history(100)
        self.history_table.setRowCount(len(history))
        for row, ev in enumerate(history):
            self.history_table.setItem(
                row, 0,
                QTableWidgetItem(
                    time.strftime("%Y-%m-%d %H:%M", time.localtime(ev["ts"]))
                ),
            )
            self.history_table.setItem(
                row, 1,
                QTableWidgetItem(t(_ACTION_KEYS.get(ev["action"], ev["action"]))),
            )
            self.history_table.setItem(row, 2, QTableWidgetItem(ev["destination"] or "-"))
            status = ev["status"]
            status_item = QTableWidgetItem(
                t("cloud_status_ok") if status == "ok" else t("cloud_status_error")
            )
            status_item.setForeground(
                QColor(ThemeColors.get("success") if status == "ok" else ThemeColors.get("error"))
            )
            self.history_table.setItem(row, 3, status_item)

    # ===== الإجراءات =====

    def _browse_dest(self):
        path = QFileDialog.getExistingDirectory(
            self, t("cloud_browse"), self.dest_path.text() or ""
        )
        if path:
            self.dest_path.setText(path)

    def _add_dest(self):
        path = self.dest_path.text().strip()
        if not path or not os.path.isdir(path):
            QMessageBox.warning(self, t("cloud_title"), t("cloud_invalid_path"))
            return
        self._engine.add_destination(
            self.dest_name.text().strip(), path, auto=False
        )
        self.dest_name.clear()
        self.dest_path.clear()
        self.refresh()

    def _delete_dest(self):
        row = self.dest_table.currentRow()
        if row < 0:
            return
        dests = self._engine.list_destinations()
        if row >= len(dests):
            return
        self._engine.remove_destination(dests[row]["id"])
        self.refresh()

    def _push_selected(self):
        row = self.dest_table.currentRow()
        dests = self._engine.list_destinations()
        if row < 0 or row >= len(dests):
            self._push_all()
            return
        self._do_push([dests[row]["id"]])

    def _push_all(self):
        self._do_push(None)

    def _do_push(self, dest_ids):
        if not feature_allowed("cloud_sync"):
            show_feature_denied(self, "cloud_sync")
            return
        try:
            results = self._engine.push(state, dest_ids, passphrase=None)
        except Exception as e:
            QMessageBox.critical(self, t("cloud_title"), f"{t('cloud_error')}\n{e}")
            self.refresh()
            return
        self.refresh()
        ok_count = sum(1 for r in results if r.get("ok"))
        if ok_count:
            QMessageBox.information(
                self, t("cloud_title"),
                f"{t('cloud_push_success')} ({ok_count}/{len(results)})",
            )

    def _backup_local(self):
        try:
            result = self._engine.backup_local(state)
        except Exception as e:
            QMessageBox.critical(self, t("cloud_title"), f"{t('cloud_error')}\n{e}")
            self.refresh()
            return
        self.refresh()
        QMessageBox.information(
            self, t("cloud_title"),
            f"{t('cloud_backup_done')}\n{_plain(result['path'])}",
        )

    def _restore_selected(self):
        row = self.backup_table.currentRow()
        if row < 0:
            return
        snap = self.backup_table.item(row, 0).text()
        if QMessageBox.question(
            self, t("cloud_title"), t("cloud_restore_confirm"),
        ) != QMessageBox.Yes:
            return
        try:
            self._engine.restore_backup(state, snap)
        except ValueError as e:
            self._show_snapshot_error(e)
            return
        except Exception as e:
            QMessageBox.critical(self, t("cloud_title"), f"{t('cloud_error')}\n{e}")
            return
        self.refresh()
        QMessageBox.information(self, t("cloud_title"), t("cloud_restore_done"))

    def _restore_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("cloud_restore_file"), "", "Snapshot (*.json)"
        )
        if not path:
            return
        if QMessageBox.question(
            self, t("cloud_title"), t("cloud_restore_confirm"),
        ) != QMessageBox.Yes:
            return
        try:
            self._engine.restore_from_file(state, path)
        except ValueError as e:
            self._show_snapshot_error(e)
            return
        except Exception as e:
            QMessageBox.critical(self, t("cloud_title"), f"{t('cloud_error')}\n{e}")
            return
        self.refresh()
        QMessageBox.information(self, t("cloud_title"), t("cloud_restore_done"))

    def _pull(self):
        if not feature_allowed("cloud_sync"):
            show_feature_denied(self, "cloud_sync")
            return
        dest_id = self.pull_combo.currentData()
        name = self.snap_combo.currentText()
        if dest_id is None or not name:
            return
        if QMessageBox.question(
            self, t("cloud_title"), t("cloud_restore_confirm"),
        ) != QMessageBox.Yes:
            return
        try:
            self._engine.pull(state, dest_id, name)
        except ValueError as e:
            self._show_snapshot_error(e)
            return
        except Exception as e:
            QMessageBox.critical(self, t("cloud_title"), f"{t('cloud_error')}\n{e}")
            return
        self.refresh()
        QMessageBox.information(self, t("cloud_title"), t("cloud_restore_done"))

    def _show_snapshot_error(self, error):
        key = str(error)
        message = {
            "passphrase_required": t("cloud_passphrase_required"),
            "checksum_mismatch": t("cloud_checksum_error"),
            "invalid_snapshot": t("cloud_invalid_snapshot"),
        }.get(key, str(error))
        QMessageBox.warning(self, t("cloud_title"), message)

    def _save_auto_settings(self):
        self._engine.set_setting("auto_backup", self.auto_check.isChecked())
        self._engine.set_setting(
            "auto_backup_interval_hours", self.interval_spin.value()
        )
        self._engine.set_setting("max_backups", self.max_spin.value())
        QMessageBox.information(self, t("cloud_title"), t("cloud_saved"))

    def _set_passphrase(self):
        value = self.pass_input.text()
        self._engine.set_passphrase(value)
        self.refresh()
        QMessageBox.information(self, t("cloud_title"), t("cloud_saved"))

    def _clear_passphrase(self):
        self._engine.set_passphrase("")
        self.pass_input.clear()
        self.refresh()

    def _clear_history(self):
        if QMessageBox.question(
            self, t("cloud_title"), t("cloud_clear_history_confirm"),
        ) != QMessageBox.Yes:
            return
        self._engine.clear_history()
        self.refresh()

    def _export_history(self):
        import csv
        path, _ = QFileDialog.getSaveFileName(
            self, t("cloud_export_csv"), "sync_history.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        history = self._engine.history(10000)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "action", "destination", "status", "size", "error"])
            for ev in history:
                writer.writerow([
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ev["ts"])),
                    ev["action"], ev["destination"], ev["status"],
                    ev["size"], ev["error"],
                ])
        QMessageBox.information(
            self, t("cloud_title"), f"{t('cloud_exported')}\n{path}"
        )
