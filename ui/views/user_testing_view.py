# واجهة اختبار المستخدمين الحقيقيين
# ===================================
# مجموعات مستخدمين (محاسب/مدير/مالك/CFO) × سيناريوهات اختبار × جمع ملاحظات
# + درجة رضا + تقارير (ملاحظات/مشكلات/تحسينات) + تصدير JSON/Excel/PDF/CSV

from ui.views._path import _  # noqa: F401


from PyQt6.QtWidgets import (
    QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QLineEdit,
    QSpinBox, QTextEdit, QMessageBox, QFileDialog,
    QHeaderView,
)

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.user_testing import (
    UserTestingEngine, USER_GROUPS, SCENARIOS, FEEDBACK_CATEGORIES,
    PRIORITIES, STATUSES,
)

_GROUP_KEYS = {"accountant": "ut_group_accountant", "manager": "ut_group_manager",
               "business_owner": "ut_group_owner", "cfo": "ut_group_cfo"}
_SCENARIO_KEYS = {"data_entry": "ut_scenario_data_entry",
                  "report_generation": "ut_scenario_report_generation",
                  "analysis": "ut_scenario_analysis",
                  "decision_making": "ut_scenario_decision_making",
                  "issue_resolution": "ut_scenario_issue_resolution"}
_CATEGORY_KEYS = {"usability": "ut_category_usability",
                  "performance": "ut_category_performance",
                  "features": "ut_category_features",
                  "bugs": "ut_category_bugs",
                  "suggestions": "ut_category_suggestions"}
_PRIORITY_KEYS = {"low": "ut_priority_low", "medium": "ut_priority_medium",
                  "high": "ut_priority_high", "critical": "ut_priority_critical"}
_STATUS_KEYS = {"open": "ut_status_open", "in_progress": "ut_status_in_progress",
                "resolved": "ut_status_resolved", "closed": "ut_status_closed"}
_LEVEL_KEYS = {"excellent": "ut_level_excellent", "good": "ut_level_good",
               "average": "ut_level_average", "poor": "ut_level_poor"}
_LEVEL_COLORS = {"excellent": "#27AE60", "good": "#2ECC71",
                 "average": "#F39C12", "poor": "#E74C3C"}


def _fill_combo(combo, values, key_map):
    combo.blockSignals(True)
    combo.clear()
    for value in values:
        combo.addItem(t(key_map[value]), value)
    combo.blockSignals(False)


class UserTestingView(BaseView):
    """واجهة اختبار المستخدمين الحقيقيين وجمع الملاحظات"""

    def __init__(self):
        super().__init__()
        self._engine = UserTestingEngine()
        self._current_sid = None
        self.setup_ui()
        self.refresh()

    # ===== بناء الواجهة =====

    def setup_ui(self):
        self._make_header("ut_title", "ut_subtitle")

        self._build_session_card()
        self._build_feedback_card()
        self._build_stats()
        self._build_table_card()
        self._build_reports_card()

        self._main_layout.addStretch()
    def _build_session_card(self):
        """بطاقة الجلسة: الاسم/المجموعة/السيناريو"""

        # 1) الجلسة
        session_card = self._make_card("ut_sessions_card")
        form = QGridLayout()
        form.setSpacing(8)
        form.setColumnStretch(1, 3)
        form.setColumnStretch(3, 3)
        form.addWidget(QLabel(t("ut_session_name")), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumHeight(40)
        form.addWidget(self.name_edit, 0, 1)
        form.addWidget(QLabel(t("ut_tester_name")), 0, 2)
        self.tester_edit = QLineEdit()
        self.tester_edit.setMinimumHeight(40)
        form.addWidget(self.tester_edit, 0, 3)
        form.addWidget(QLabel(t("ut_user_group")), 1, 0)
        self.group_combo = QComboBox()
        self.group_combo.setMinimumHeight(40)
        _fill_combo(self.group_combo, USER_GROUPS, _GROUP_KEYS)
        form.addWidget(self.group_combo, 1, 1)
        form.addWidget(QLabel(t("ut_scenario")), 1, 2)
        self.scenario_combo = QComboBox()
        self.scenario_combo.setMinimumHeight(40)
        _fill_combo(self.scenario_combo, SCENARIOS, _SCENARIO_KEYS)
        form.addWidget(self.scenario_combo, 1, 3)
        form.addWidget(QLabel(t("ut_environment")), 2, 0)
        self.environment_edit = QLineEdit()
        self.environment_edit.setMinimumHeight(40)
        form.addWidget(self.environment_edit, 2, 1)
        self.session_combo = QComboBox()
        self.session_combo.setMinimumWidth(220)
        self.session_combo.setMinimumHeight(40)
        self.session_combo.currentIndexChanged.connect(self._on_session_changed)
        form.addWidget(QLabel(t("ut_sessions")), 2, 2)
        form.addWidget(self.session_combo, 2, 3)
        session_card.layout().addLayout(form)
        actions = QHBoxLayout()
        self.new_btn = QPushButton(t("ut_new_session"))
        self.new_btn.setObjectName("primaryBtn")
        self.new_btn.clicked.connect(self._create_session)
        actions.addWidget(self.new_btn)
        self.demo_btn = QPushButton(t("ut_load_demo"))
        self.demo_btn.clicked.connect(self._load_demo)
        actions.addWidget(self.demo_btn)
        self.save_db_btn = QPushButton(t("ut_save_db"))
        self.save_db_btn.clicked.connect(self._save_db)
        actions.addWidget(self.save_db_btn)
        self.load_db_btn = QPushButton(t("ut_load_db"))
        self.load_db_btn.clicked.connect(self._load_db)
        actions.addWidget(self.load_db_btn)
        self.delete_btn = QPushButton(t("ut_delete_session"))
        self.delete_btn.clicked.connect(self._delete_session)
        actions.addWidget(self.delete_btn)
        actions.addStretch()
        session_card.layout().addLayout(actions)
        self._main_layout.addWidget(session_card)

    def _build_feedback_card(self):
        """بطاقة إضافة ملاحظة"""

        # 2) إضافة ملاحظة
        feedback_card = self._make_card("ut_feedback_card")
        frow = QGridLayout()
        frow.setSpacing(8)
        frow.setColumnStretch(1, 3)
        frow.setColumnStretch(3, 3)
        frow.setColumnStretch(5, 3)
        frow.addWidget(QLabel(t("ut_category")), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(40)
        _fill_combo(self.category_combo, FEEDBACK_CATEGORIES, _CATEGORY_KEYS)
        frow.addWidget(self.category_combo, 0, 1)
        frow.addWidget(QLabel(t("ut_priority")), 0, 2)
        self.priority_combo = QComboBox()
        self.priority_combo.setMinimumHeight(40)
        _fill_combo(self.priority_combo, PRIORITIES, _PRIORITY_KEYS)
        frow.addWidget(self.priority_combo, 0, 3)
        frow.addWidget(QLabel(t("ut_status")), 0, 4)
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(40)
        _fill_combo(self.status_combo, STATUSES, _STATUS_KEYS)
        frow.addWidget(self.status_combo, 0, 5)
        frow.addWidget(QLabel(t("ut_rating")), 1, 0)
        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(1, 5)
        self.rating_spin.setValue(4)
        self.rating_spin.setMinimumHeight(40)
        frow.addWidget(self.rating_spin, 1, 1)
        frow.addWidget(QLabel(t("ut_title_field")), 1, 2)
        self.title_edit = QLineEdit()
        self.title_edit.setMinimumHeight(40)
        frow.addWidget(self.title_edit, 1, 3, 1, 3)
        feedback_card.layout().addLayout(frow)
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText(t("ut_comment_field"))
        self.comment_edit.setMinimumHeight(110)
        feedback_card.layout().addWidget(self.comment_edit)
        fbtn = QHBoxLayout()
        self.add_btn = QPushButton(t("ut_add_feedback"))
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.clicked.connect(self._add_feedback)
        fbtn.addWidget(self.add_btn)
        self.delete_fb_btn = QPushButton(t("ut_delete_feedback"))
        self.delete_fb_btn.clicked.connect(self._delete_feedback)
        fbtn.addWidget(self.delete_fb_btn)
        self.resolve_btn = QPushButton(t("ut_mark_resolved"))
        self.resolve_btn.clicked.connect(self._mark_resolved)
        fbtn.addWidget(self.resolve_btn)
        fbtn.addStretch()
        feedback_card.layout().addLayout(fbtn)
        self._main_layout.addWidget(feedback_card)

    def _build_stats(self):
        """بطاقات المؤشرات"""

        # 3) المؤشرات
        stats_grid = QGridLayout()
        stats_grid.setSpacing(12)
        self.stat_score = self._make_stat_card(t("ut_overall_score"), "0/5", "#333")
        self.stat_count = self._make_stat_card(t("ut_total_feedback"), "0")
        self.stat_issues = self._make_stat_card(t("ut_open_issues"), "0", "#E74C3C")
        self.stat_enh = self._make_stat_card(t("ut_enhancements"), "0", "#2980B9")
        for i, stat in enumerate((self.stat_score, self.stat_count,
                                  self.stat_issues, self.stat_enh)):
            stats_grid.addWidget(stat, 0, i)
        self._main_layout.addLayout(stats_grid)

    def _build_table_card(self):
        """بطاقة جدول الملاحظات مع المرشحات"""

        # 4) جدول الملاحظات
        table_card = self._make_card("ut_feedback_card")
        filters = QHBoxLayout()
        filters.addWidget(QLabel(t("ut_filter_group")))
        self.filter_group = QComboBox()
        _fill_combo(self.filter_group, ("all",) + USER_GROUPS,
                    {k: ("ut_all" if k == "all" else _GROUP_KEYS[k]) for k in ("all",) + USER_GROUPS})
        self.filter_group.currentIndexChanged.connect(self._refresh_table)
        filters.addWidget(self.filter_group)
        filters.addWidget(QLabel(t("ut_filter_category")))
        self.filter_category = QComboBox()
        _fill_combo(self.filter_category, ("all",) + FEEDBACK_CATEGORIES,
                    {k: ("ut_all" if k == "all" else _CATEGORY_KEYS[k]) for k in ("all",) + FEEDBACK_CATEGORIES})
        self.filter_category.currentIndexChanged.connect(self._refresh_table)
        filters.addWidget(self.filter_category)
        filters.addWidget(QLabel(t("ut_filter_status")))
        self.filter_status = QComboBox()
        _fill_combo(self.filter_status, ("all",) + STATUSES,
                    {k: ("ut_all" if k == "all" else _STATUS_KEYS[k]) for k in ("all",) + STATUSES})
        self.filter_status.currentIndexChanged.connect(self._refresh_table)
        filters.addStretch()
        table_card.layout().addLayout(filters)
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            t("ut_col_date"), t("ut_col_group"), t("ut_col_scenario"),
            t("ut_col_category"), t("ut_col_rating"), t("ut_col_priority"),
            t("ut_col_status"), t("ut_col_title"), t("ut_col_comment"), "",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setWordWrap(True)
        self.table.setMinimumHeight(44 * 6 + 40)
        table_card.layout().addWidget(self.table)
        self._main_layout.addWidget(table_card)

    def _build_reports_card(self):
        """بطاقة التقارير والتصدير"""

        # 5) التقارير والتصدير
        report_card = self._make_card("ut_reports_card")
        rrow = QHBoxLayout()
        self.report_fb_btn = QPushButton(t("ut_report_feedback"))
        self.report_fb_btn.clicked.connect(self._show_feedback_report)
        rrow.addWidget(self.report_fb_btn)
        self.report_issue_btn = QPushButton(t("ut_report_issues"))
        self.report_issue_btn.clicked.connect(self._show_issue_list)
        rrow.addWidget(self.report_issue_btn)
        self.report_enh_btn = QPushButton(t("ut_report_enhancements"))
        self.report_enh_btn.clicked.connect(self._show_enhancements)
        rrow.addWidget(self.report_enh_btn)
        rrow.addStretch()
        self.export_json_btn = QPushButton(t("ut_export_json"))
        self.export_json_btn.clicked.connect(self._export_json)
        rrow.addWidget(self.export_json_btn)
        self.import_json_btn = QPushButton(t("ut_import_json"))
        self.import_json_btn.clicked.connect(self._import_json)
        rrow.addWidget(self.import_json_btn)
        self.export_excel_btn = QPushButton(t("ut_export_excel"))
        self.export_excel_btn.clicked.connect(self._export_excel)
        rrow.addWidget(self.export_excel_btn)
        self.export_pdf_btn = QPushButton(t("ut_export_pdf"))
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        rrow.addWidget(self.export_pdf_btn)
        self.export_csv_btn = QPushButton(t("ut_export_csv"))
        self.export_csv_btn.clicked.connect(self._export_csv)
        rrow.addWidget(self.export_csv_btn)
        report_card.layout().addLayout(rrow)
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setMinimumHeight(180)
        report_card.layout().addWidget(self.report_preview)
        self._main_layout.addWidget(report_card)

        self._main_layout.addStretch()

    # ===== التحديث =====

    def refresh(self):
        self._refresh_session_combo()
        if self._current_sid:
            self._refresh_all()

    def _refresh_session_combo(self):
        current = self._current_sid
        self.session_combo.blockSignals(True)
        self.session_combo.clear()
        for session in self._engine.list_sessions():
            label = f"{session['name']} — {t(_GROUP_KEYS[session['user_group']])}"
            self.session_combo.addItem(label, session["id"])
        self.session_combo.blockSignals(False)
        if current is not None:
            index = self.session_combo.findData(current)
            if index >= 0:
                self.session_combo.setCurrentIndex(index)
                self._current_sid = current
                return
        if self.session_combo.count():
            self._current_sid = self.session_combo.itemData(0)
            self.session_combo.setCurrentIndex(0)
        else:
            self._current_sid = None

    def _current_session(self):
        return self._engine.get_session(self._current_sid)

    def _on_session_changed(self, _index):
        self._current_sid = self.session_combo.currentData()
        self._refresh_all()

    def _refresh_all(self):
        session = self._current_session()
        if not session:
            self.table.setRowCount(0)
            self.report_preview.setPlainText(t("ut_no_session"))
            self._update_stats(None)
            return
        self._update_stats(session)
        self._refresh_table()
        self.report_preview.setPlainText(self._engine.summary_text(session["id"]))

    def _update_stats(self, session):
        score = self._engine.satisfaction_score(session["id"]) if session else None
        if score is None:
            self.stat_score.layout().itemAt(1).widget().setText("0/5")
            self.stat_score.layout().itemAt(1).widget().setStyleSheet("color: #333;")
            self.stat_count.layout().itemAt(1).widget().setText("0")
            self.stat_issues.layout().itemAt(1).widget().setText("0")
            self.stat_enh.layout().itemAt(1).widget().setText("0")
            return
        report = self._engine.feedback_report(session["id"])
        level_key = _LEVEL_KEYS.get(score["level"], "ut_level_poor")
        label = f"{score['overall']}/5  ({t(level_key)})"
        self.stat_score.layout().itemAt(1).widget().setText(label)
        self.stat_score.layout().itemAt(1).widget().setStyleSheet(
            f"color: {_LEVEL_COLORS.get(score['level'], '#333')};"
        )
        self.stat_count.layout().itemAt(1).widget().setText(str(score["count"]))
        self.stat_issues.layout().itemAt(1).widget().setText(str(report["open_issues"]))
        self.stat_enh.layout().itemAt(1).widget().setText(str(report["enhancement_requests"]))

    def _selected_feedback_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 9)
        return item.data(0x0100) if item else None

    def _refresh_table(self):
        session = self._current_session()
        if not session:
            self.table.setRowCount(0)
            return
        group = self.filter_group.currentData()
        category = self.filter_category.currentData()
        status = self.filter_status.currentData()
        items = self._engine.list_feedback(
            session["id"],
            category=None if category == "all" else category,
            user_group=None if group == "all" else group,
            status=None if status == "all" else status,
        )
        self.table.setRowCount(len(items))
        for r, item in enumerate(items):
            self.table.setItem(r, 0, QTableWidgetItem(item["created_at"]))
            self.table.setItem(r, 1, QTableWidgetItem(t(_GROUP_KEYS[item["user_group"]])))
            self.table.setItem(r, 2, QTableWidgetItem(t(_SCENARIO_KEYS[item["scenario"]])))
            self.table.setItem(r, 3, QTableWidgetItem(t(_CATEGORY_KEYS[item["category"]])))
            self.table.setItem(r, 4, QTableWidgetItem(str(item["rating"])))
            self.table.setItem(r, 5, QTableWidgetItem(t(_PRIORITY_KEYS[item["priority"]])))
            self.table.setItem(r, 6, QTableWidgetItem(t(_STATUS_KEYS[item["status"]])))
            self.table.setItem(r, 7, QTableWidgetItem(item["title"]))
            self.table.setItem(r, 8, QTableWidgetItem(item["comment"]))
            id_item = QTableWidgetItem("")
            id_item.setData(0x0100, item["id"])
            self.table.setItem(r, 9, id_item)

    # ===== الجلسات =====

    def _create_session(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, t("ut_title"), t("ut_session_name_required"))
            return
        try:
            session = self._engine.create_session(
                name=name,
                tester_name=self.tester_edit.text().strip(),
                user_group=self.group_combo.currentData(),
                scenario=self.scenario_combo.currentData(),
                environment=self.environment_edit.text().strip(),
            )
        except ValueError as e:
            QMessageBox.warning(self, t("ut_title"), str(e))
            return
        self.name_edit.clear()
        self._current_sid = session["id"]
        self._refresh_session_combo()
        self._refresh_all()
        self.statusBarMessage(t("ut_session_created"))

    def _delete_session(self):
        if self._current_sid is None:
            return
        reply = QMessageBox.question(
            self, t("ut_title"), t("ut_confirm_delete_session"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._engine.delete_session(self._current_sid)
        self._current_sid = None
        self._refresh_session_combo()
        self._refresh_all()

    def _load_demo(self):
        self._engine.build_demo_data()
        self._refresh_session_combo()
        if self.session_combo.count():
            self.session_combo.setCurrentIndex(0)
            self._current_sid = self.session_combo.itemData(0)
        self._refresh_all()
        self.statusBarMessage(t("ut_demo_loaded"))

    def _save_db(self):
        if self._current_sid is None:
            return
        if self._engine.save_session_db(self._current_sid):
            self.statusBarMessage(t("ut_session_saved"))
        else:
            QMessageBox.critical(self, t("ut_title"), t("ut_db_error"))

    def _load_db(self):
        try:
            ids = self._engine.list_session_ids_db()
        except Exception:
            ids = []
        if not ids:
            self.statusBarMessage(t("ut_db_empty"))
            return
        for entry in ids:
            self._engine.load_session_db(entry["id"])
        self._refresh_session_combo()
        if self.session_combo.count():
            self.session_combo.setCurrentIndex(0)
            self._current_sid = self.session_combo.itemData(0)
        self._refresh_all()
        self.statusBarMessage(t("ut_session_loaded"))

    # ===== الملاحظات =====

    def _add_feedback(self):
        session = self._current_session()
        if not session:
            QMessageBox.warning(self, t("ut_title"), t("ut_no_session"))
            return
        comment = self.comment_edit.toPlainText().strip()
        if not comment:
            QMessageBox.warning(self, t("ut_title"), t("ut_comment_field"))
            return
        try:
            self._engine.add_feedback(
                session["id"],
                category=self.category_combo.currentData(),
                comment=comment,
                rating=self.rating_spin.value(),
                priority=self.priority_combo.currentData(),
                title=self.title_edit.text().strip(),
                status=self.status_combo.currentData(),
            )
        except ValueError as e:
            QMessageBox.warning(self, t("ut_title"), str(e))
            return
        self.comment_edit.clear()
        self.title_edit.clear()
        self._refresh_all()
        self.statusBarMessage(t("ut_feedback_added"))

    def _delete_feedback(self):
        if self._current_sid is None:
            return
        feedback_id = self._selected_feedback_id()
        if not feedback_id:
            return
        if self._engine.delete_feedback(self._current_sid, feedback_id):
            self._refresh_all()
            self.statusBarMessage(t("ut_feedback_deleted"))

    def _mark_resolved(self):
        if self._current_sid is None:
            return
        feedback_id = self._selected_feedback_id()
        if not feedback_id:
            return
        self._engine.update_feedback(self._current_sid, feedback_id, status="resolved")
        self._refresh_all()
        self.statusBarMessage(t("ut_feedback_updated"))

    # ===== التقارير =====

    def _format_items(self, items, header_keys):
        if not items:
            return t("ut_report_empty")
        lines = [f"{t('ut_title')} — {header_keys}", "", "─" * 60]
        for item in items:
            lines.append(
                f"[{t(_CATEGORY_KEYS[item['category']])}/{t(_PRIORITY_KEYS[item['priority']])}"
                f"/{item['rating']}/5/{t(_STATUS_KEYS[item['status']])}] "
                f"{item['title'] or ''} — {item['comment']}"
            )
        return "\n".join(lines)

    def _show_feedback_report(self):
        session = self._current_session()
        if not session:
            return
        report = self._engine.feedback_report(session["id"])
        score = report["satisfaction"]
        lines = [
            f"{t('ut_title')} — {session['name']}",
            "",
            f"{t('ut_total_feedback')}: {report['total_feedback']}",
            f"{t('ut_overall_score')}: {score['overall']}/5 ({t(_LEVEL_KEYS.get(score['level'], 'ut_level_poor'))})",
            f"{t('ut_open_issues')}: {report['open_issues']}",
            f"{t('ut_enhancements')}: {report['enhancement_requests']}",
            "",
            f"{t('ut_count_by_category')}:",
        ]
        for category, count in report["counts_by_category"].items():
            lines.append(f"  • {t(_CATEGORY_KEYS[category])}: {count}")
        lines += ["", f"{t('ut_avg_by_category')}:"]
        for category, avg in report["avg_by_category"].items():
            lines.append(f"  • {t(_CATEGORY_KEYS[category])}: {avg}/5")
        self.report_preview.setPlainText("\n".join(lines))

    def _show_issue_list(self):
        session = self._current_session()
        if not session:
            return
        items = self._engine.issue_list(session["id"])
        self.report_preview.setPlainText(
            self._format_items(items, t("ut_report_issues"))
        )

    def _show_enhancements(self):
        session = self._current_session()
        if not session:
            return
        items = self._engine.enhancement_requests(session["id"])
        self.report_preview.setPlainText(
            self._format_items(items, t("ut_report_enhancements"))
        )

    # ===== التصدير/الاستيراد =====

    def _pick_save_path(self, caption, ext, filter_text):
        path, _ = QFileDialog.getSaveFileName(self, caption, "", filter_text)
        if not path:
            return None
        if not path.lower().endswith(ext):
            path += ext
        return path

    def _export_json(self):
        path = self._pick_save_path(t("ut_export_json"), ".json", "JSON (*.json)")
        if not path:
            return
        try:
            self._engine.export_json(path)
            self.statusBarMessage(f"{t('ut_exported')}: {path}")
        except Exception:
            QMessageBox.critical(self, t("ut_title"), t("ut_export_fail"))

    def _import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, t("ut_import_json"), "", "JSON (*.json)")
        if not path:
            return
        count = self._engine.import_json(path)
        self._refresh_session_combo()
        self._refresh_all()
        self.statusBarMessage(f"{t('ut_imported')}: {count}")

    def _export_excel(self):
        path = self._pick_save_path(t("ut_export_excel"), ".xlsx", "Excel (*.xlsx)")
        if not path:
            return
        ok = self._engine.export_excel(path)
        if ok:
            self.statusBarMessage(f"{t('ut_exported')}: {path}")
        else:
            QMessageBox.critical(self, t("ut_title"), t("ut_export_fail"))

    def _export_pdf(self):
        path = self._pick_save_path(t("ut_export_pdf"), ".pdf", "PDF (*.pdf)")
        if not path:
            return
        ok = self._engine.export_pdf(path)
        if ok:
            self.statusBarMessage(f"{t('ut_exported')}: {path}")
        else:
            QMessageBox.critical(self, t("ut_title"), t("ut_export_fail"))

    def _export_csv(self):
        path = self._pick_save_path(t("ut_export_csv"), ".csv", "CSV (*.csv)")
        if not path:
            return
        ok = self._engine.export_csv(path)
        if ok:
            self.statusBarMessage(f"{t('ut_exported')}: {path}")
        else:
            QMessageBox.critical(self, t("ut_title"), t("ut_export_fail"))

    def statusBarMessage(self, message):
        try:
            window = self.window()
            if window is not None and hasattr(window, "status_bar"):
                window.status_bar.showMessage(message, 5000)
        except Exception:
            pass
