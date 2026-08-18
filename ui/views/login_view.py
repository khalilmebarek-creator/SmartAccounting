"""Login and Registration screen."""

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QStackedWidget,
    QFormLayout, QToolButton, QCheckBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon

from ui.resources.i18n import t
from ui.app_state import ThemeColors
from ui.login_session import load_login_email, save_login_session
from modules.user_manager import user_manager


class PasswordChangeDialog(QMessageBox):
    """Forced password change on first login."""

    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("pwd_change_title"))
        self.setIcon(QMessageBox.Warning)
        self.setText(t("pwd_change_msg"))
        self.username = username

    @staticmethod
    def prompt(parent, username):
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox
        dlg = QDialog(parent)
        dlg.setWindowTitle(t("pwd_change_title"))
        layout = QFormLayout()

        old_pass = QLineEdit()
        old_pass.setEchoMode(QLineEdit.Password)
        old_pass.setMinimumHeight(34)
        old_pass.setLayoutDirection(Qt.LeftToRight)
        layout.addRow(t("pwd_old"), old_pass)

        new_pass = QLineEdit()
        new_pass.setEchoMode(QLineEdit.Password)
        new_pass.setMinimumHeight(34)
        new_pass.setLayoutDirection(Qt.LeftToRight)
        layout.addRow(t("pwd_new"), new_pass)

        confirm_pass = QLineEdit()
        confirm_pass.setEchoMode(QLineEdit.Password)
        confirm_pass.setMinimumHeight(34)
        confirm_pass.setLayoutDirection(Qt.LeftToRight)
        layout.addRow(t("pwd_confirm"), confirm_pass)

        error_label = QLabel("")
        error_label.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 12px;")
        error_label.setWordWrap(True)
        layout.addRow(error_label)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addRow(btns)

        dlg.setLayout(layout)
        dlg.setMinimumWidth(380)

        while True:
            if dlg.exec_() != QDialog.Accepted:
                return False
            old = old_pass.text()
            new = new_pass.text()
            confirm = confirm_pass.text()
            if not old or not new:
                error_label.setText(t("pwd_empty"))
                continue
            if new != confirm:
                error_label.setText(t("pwd_mismatch"))
                continue
            ok, err = user_manager.change_password(username, old, new)
            if ok:
                return True
            error_label.setText(t(err) if t(err) != err else err)


class LoginView(QWidget):
    """شاشة تسجيل الدخول"""

    login_success = pyqtSignal()

    _ERR_I18N = {
        "err_email_not_found": "login_error_email_not_found",
        "err_wrong_password": "login_error_wrong_password",
        "err_locked": "login_error_locked",
        "err_empty_fields": "login_error_empty_fields",
        "err_invalid_email": "login_error_invalid_email",
        "err_email_exists": "login_error_email_exists",
        "err_password_short": "login_error_err_password_short",
        "err_password_no_upper": "login_error_err_password_no_upper",
        "err_password_no_lower": "login_error_err_password_no_lower",
        "err_password_no_digit": "login_error_err_password_no_digit",
        "err_password_no_special": "login_error_err_password_no_special",
    }

    def __init__(self):
        super().__init__()
        self._had_login_error = False
        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout()
        outer.setAlignment(Qt.AlignCenter)

        container = QWidget()
        container.setMaximumWidth(500)
        container.setMinimumWidth(400)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)

        import os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base, 'resources', 'app_icon_hq.png')
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base, 'resources', 'app_icon.ico')
        if os.path.exists(icon_path):
            logo = QLabel()
            pixmap = QPixmap(icon_path)
            logo.setPixmap(pixmap.scaled(QSize(120, 120), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(logo)

        title = QLabel(t("login_title"))
        title.setObjectName("headerTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("", 20, QFont.Bold))
        container_layout.addWidget(title)
        self._title_label = title

        subtitle = QLabel(t("login_subtitle"))
        subtitle.setObjectName("headerSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(subtitle)
        self._subtitle_label = subtitle

        self.stack = QStackedWidget()

        self.stack.addWidget(self._build_login_page())
        self.stack.addWidget(self._build_register_page())
        self.stack.addWidget(self._build_forgot_page_1())
        self.stack.addWidget(self._build_forgot_page_2())
        self.stack.addWidget(self._build_forgot_page_3())

        container_layout.addWidget(self.stack)

        container.setLayout(container_layout)
        outer.addWidget(container)
        outer.addStretch()
        self.setLayout(outer)

    def _build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(0, 20, 0, 0)

        form = QFormLayout()
        form.setSpacing(15)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText(t("login_email_ph"))
        self.login_email.setMinimumHeight(38)
        saved_email = load_login_email()
        if saved_email:
            self.login_email.setText(saved_email)
        self._login_email_label = QLabel(t("login_email"))
        form.addRow(self._login_email_label, self.login_email)

        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText(t("login_password"))
        self.login_password.setMinimumHeight(38)
        self.login_password.setLayoutDirection(Qt.LeftToRight)
        self._login_pass_label = QLabel(t("login_password"))
        self.login_password.returnPressed.connect(self.do_login)

        pass_layout = QHBoxLayout()
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(5)
        pass_layout.addWidget(self.login_password)
        self._pwd_toggle_btn = QToolButton()
        self._pwd_toggle_btn.setText("👁")
        self._pwd_toggle_btn.setCheckable(True)
        self._pwd_toggle_btn.setFixedWidth(36)
        self._pwd_toggle_btn.setMinimumHeight(38)
        self._pwd_toggle_btn.clicked.connect(self._toggle_login_password)
        pass_layout.addWidget(self._pwd_toggle_btn)
        form.addRow(self._login_pass_label, pass_layout)

        layout.addLayout(form)

        self.login_remember = QCheckBox(t("login_remember_me"))
        self.login_remember.setMinimumHeight(32)
        layout.addWidget(self.login_remember)

        self.login_error = QLabel("")
        self.login_error.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
        self.login_error.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.login_error)

        self.login_btn = QPushButton(t("login_btn"))
        self.login_btn.setObjectName("primaryBtn")
        self.login_btn.setMinimumHeight(44)
        self.login_btn.clicked.connect(self.do_login)
        layout.addWidget(self.login_btn)

        self.register_link = QPushButton(t("login_register_link"))
        self.register_link.setFlat(True)
        self.register_link.setStyleSheet(f"color: {ThemeColors.get('info')}; border: none;")
        self.register_link.setCursor(Qt.PointingHandCursor)
        self.register_link.clicked.connect(self._go_to_register)
        layout.addWidget(self.register_link)

        self.forgot_link = QPushButton(t("login_forgot_password"))
        self.forgot_link.setFlat(True)
        self.forgot_link.setStyleSheet(f"color: {ThemeColors.get('warning')}; border: none;")
        self.forgot_link.setCursor(Qt.PointingHandCursor)
        self.forgot_link.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        layout.addWidget(self.forgot_link)

        page.setLayout(layout)
        return page

    def _build_register_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(0, 20, 0, 0)

        form = QFormLayout()
        form.setSpacing(15)

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText(t("login_reg_email_ph"))
        self.reg_email.setMinimumHeight(38)
        self._reg_email_label = QLabel(t("login_email"))
        form.addRow(self._reg_email_label, self.reg_email)

        self.reg_display = QLineEdit()
        self.reg_display.setPlaceholderText(t("login_reg_display_ph"))
        self.reg_display.setMinimumHeight(38)
        self._reg_display_label = QLabel(t("login_reg_display"))
        form.addRow(self._reg_display_label, self.reg_display)

        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setPlaceholderText(t("login_reg_password_ph"))
        self.reg_password.setMinimumHeight(38)
        self.reg_password.setLayoutDirection(Qt.LeftToRight)
        self._reg_pass_label = QLabel(t("login_password"))
        form.addRow(self._reg_pass_label, self.reg_password)

        layout.addLayout(form)

        self.reg_remember = QCheckBox(t("login_remember_me"))
        self.reg_remember.setMinimumHeight(32)
        layout.addWidget(self.reg_remember)

        self.reg_error = QLabel("")
        self.reg_error.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
        self.reg_error.setWordWrap(True)
        self.reg_error.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.reg_error)

        self.reg_btn = QPushButton(t("login_register_btn"))
        self.reg_btn.setObjectName("primaryBtn")
        self.reg_btn.setMinimumHeight(44)
        self.reg_btn.clicked.connect(self.do_register)
        layout.addWidget(self.reg_btn)

        self.back_link = QPushButton(t("login_back"))
        self.back_link.setFlat(True)
        self.back_link.setStyleSheet(f"color: {ThemeColors.get('info')}; border: none;")
        self.back_link.setCursor(Qt.PointingHandCursor)
        self.back_link.clicked.connect(self._go_to_login_from_register)
        layout.addWidget(self.back_link)

        page.setLayout(layout)
        return page

    def _build_forgot_page_1(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(0, 20, 0, 0)

        lbl = QLabel(t("forgot_step1_title"))
        lbl.setObjectName("sectionTitle")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        desc = QLabel(t("forgot_step1_desc"))
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.forgot_email = QLineEdit()
        self.forgot_email.setPlaceholderText(t("login_email_ph"))
        self.forgot_email.setMinimumHeight(38)
        layout.addWidget(self.forgot_email)

        self.forgot_error1 = QLabel("")
        self.forgot_error1.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
        self.forgot_error1.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.forgot_error1)

        self.forgot_send_btn = QPushButton(t("forgot_send_code"))
        self.forgot_send_btn.setObjectName("primaryBtn")
        self.forgot_send_btn.setMinimumHeight(44)
        self.forgot_send_btn.clicked.connect(self._forgot_step1_submit)
        layout.addWidget(self.forgot_send_btn)

        back = QPushButton(t("login_back"))
        back.setFlat(True)
        back.setStyleSheet(f"color: {ThemeColors.get('info')}; border: none;")
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back)

        page.setLayout(layout)
        return page

    def _build_forgot_page_2(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(0, 20, 0, 0)

        lbl = QLabel(t("forgot_step2_title"))
        lbl.setObjectName("sectionTitle")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        self.forgot_code_display = QLabel("")
        self.forgot_code_display.setAlignment(Qt.AlignCenter)
        self.forgot_code_display.setFont(QFont("", 16, QFont.Bold))
        self.forgot_code_display.setStyleSheet(
            f"color: {ThemeColors.get('info')}; font-size: 20px; "
            f"background: rgba(0,210,255,0.08); border-radius: 8px; padding: 12px;"
        )
        layout.addWidget(self.forgot_code_display)

        self.forgot_token = QLineEdit()
        self.forgot_token.setPlaceholderText(t("forgot_enter_code"))
        self.forgot_token.setMinimumHeight(38)
        layout.addWidget(self.forgot_token)

        self.forgot_new_pass = QLineEdit()
        self.forgot_new_pass.setEchoMode(QLineEdit.Password)
        self.forgot_new_pass.setPlaceholderText(t("forgot_new_password"))
        self.forgot_new_pass.setMinimumHeight(38)
        self.forgot_new_pass.setLayoutDirection(Qt.LeftToRight)
        layout.addWidget(self.forgot_new_pass)

        self.forgot_confirm = QLineEdit()
        self.forgot_confirm.setEchoMode(QLineEdit.Password)
        self.forgot_confirm.setPlaceholderText(t("forgot_confirm_password"))
        self.forgot_confirm.setMinimumHeight(38)
        self.forgot_confirm.setLayoutDirection(Qt.LeftToRight)
        layout.addWidget(self.forgot_confirm)

        self.forgot_error2 = QLabel("")
        self.forgot_error2.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
        self.forgot_error2.setAlignment(Qt.AlignCenter)
        self.forgot_error2.setWordWrap(True)
        layout.addWidget(self.forgot_error2)

        self.forgot_reset_btn = QPushButton(t("forgot_reset_btn"))
        self.forgot_reset_btn.setObjectName("primaryBtn")
        self.forgot_reset_btn.setMinimumHeight(44)
        self.forgot_reset_btn.clicked.connect(self._forgot_step2_submit)
        layout.addWidget(self.forgot_reset_btn)

        back = QPushButton(t("login_back"))
        back.setFlat(True)
        back.setStyleSheet(f"color: {ThemeColors.get('info')}; border: none;")
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        layout.addWidget(back)

        page.setLayout(layout)
        return page

    def _build_forgot_page_3(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(0, 20, 0, 0)

        lbl = QLabel(t("forgot_step3_title"))
        lbl.setObjectName("sectionTitle")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        done = QLabel(t("forgot_step3_desc"))
        done.setAlignment(Qt.AlignCenter)
        done.setWordWrap(True)
        layout.addWidget(done)

        ok_btn = QPushButton(t("login_btn"))
        ok_btn.setObjectName("primaryBtn")
        ok_btn.setMinimumHeight(44)
        ok_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(ok_btn)

        page.setLayout(layout)
        return page

    def _forgot_step1_submit(self):
        email = self.forgot_email.text().strip()
        if not email:
            self.forgot_error1.setText(t("login_empty_fields"))
            return
        ok, data = user_manager.request_password_reset(email)
        if ok:
            self._reset_email = email
            self.forgot_code_display.setText(data["token"])
            self.forgot_token.clear()
            self.forgot_new_pass.clear()
            self.forgot_confirm.clear()
            self.forgot_error2.setText("")
            self.stack.setCurrentIndex(3)
        else:
            i18n_key = self._ERR_I18N.get(data, data)
            self.forgot_error1.setText(t(i18n_key) if t(i18n_key) != i18n_key else data)

    def _forgot_step2_submit(self):
        token = self.forgot_token.text().strip()
        new_pass = self.forgot_new_pass.text()
        confirm = self.forgot_confirm.text()

        if not token or not new_pass or not confirm:
            self.forgot_error2.setText(t("login_empty_fields"))
            return
        if new_pass != confirm:
            self.forgot_error2.setText(t("forgot_password_mismatch"))
            return

        ok, error_code = user_manager.confirm_password_reset(self._reset_email, token, new_pass)
        if ok:
            self.stack.setCurrentIndex(4)
            self.forgot_email.clear()
        else:
            i18n_key = self._ERR_I18N.get(error_code, error_code)
            msg = t(i18n_key) if t(i18n_key) != i18n_key else error_code
            self.forgot_error2.setText(msg)

    def _toggle_login_password(self, checked):
        if checked:
            self.login_password.setEchoMode(QLineEdit.Normal)
            self._pwd_toggle_btn.setText("🙈")
        else:
            self.login_password.setEchoMode(QLineEdit.Password)
            self._pwd_toggle_btn.setText("👁")

    def _go_to_register(self):
        self.login_email.setEnabled(True)
        self.stack.setCurrentIndex(1)

    def _go_to_login_from_register(self):
        self.login_email.setEnabled(True)
        self.login_remember.setChecked(self.reg_remember.isChecked())
        self.stack.setCurrentIndex(0)

    def do_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text()
        if not email or not password:
            self.login_error.setText(t("login_empty_fields"))
            return
        ok, error_code, extra = user_manager.login(email, password)
        if ok:
            self.login_error.setText("")
            save_login_session(email, password, self.login_remember.isChecked())
            self.login_password.clear()
            self._had_login_error = False
            self.forgot_link.setVisible(False)
            if user_manager.needs_password_change():
                current_user = user_manager.get_current_user()
                if current_user:
                    result = PasswordChangeDialog.prompt(self, current_user["username"])
                    if not result:
                        user_manager.logout()
                        self.login_error.setText(t("pwd_change_required"))
                        self.login_error.setStyleSheet(f"color: {ThemeColors.get('warning')}; font-size: 13px;")
                        return
            self.login_error.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
            self.login_success.emit()
        else:
            i18n_key = self._ERR_I18N.get(error_code, error_code)
            msg = t(i18n_key)
            if extra:
                for k, v in extra.items():
                    msg = msg.replace(f"{{{k}}}", str(v))
            self.login_error.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
            self.login_error.setText(msg)
            self._had_login_error = True
            self.forgot_link.setVisible(True)

    def do_register(self):
        email = self.reg_email.text().strip()
        display = self.reg_display.text().strip()
        password = self.reg_password.text()
        if not email or not password:
            self.reg_error.setText(t("login_empty_fields"))
            return
        ok, error_code = user_manager.register(email, password, display)
        if ok:
            self.reg_error.setText("")
            self.reg_email.clear()
            self.reg_display.clear()
            self.reg_password.clear()
            self.login_remember.setChecked(self.reg_remember.isChecked())
            self.stack.setCurrentIndex(0)
            self.login_email.setText(email)
            self.login_email.setEnabled(False)
            self.login_password.setFocus()
            self.login_password.clear()
            self.login_error.setText(t("login_register_success"))
            self.login_error.setStyleSheet(f"color: {ThemeColors.get('success')}; font-size: 13px;")
        else:
            i18n_key = self._ERR_I18N.get(error_code, error_code)
            msg = t(i18n_key)
            self.reg_error.setText(msg)

    def retranslate(self):
        if hasattr(self, '_title_label'):
            self._title_label.setText(t("login_title"))
        if hasattr(self, '_subtitle_label'):
            self._subtitle_label.setText(t("login_subtitle"))
        if hasattr(self, '_login_email_label'):
            self._login_email_label.setText(t("login_email"))
        if hasattr(self, '_login_pass_label'):
            self._login_pass_label.setText(t("login_password"))
        if hasattr(self, 'login_email'):
            self.login_email.setPlaceholderText(t("login_email_ph"))
        if hasattr(self, 'login_password'):
            self.login_password.setPlaceholderText(t("login_password"))
        if hasattr(self, 'login_btn'):
            self.login_btn.setText(t("login_btn"))
        if hasattr(self, 'login_remember'):
            self.login_remember.setText(t("login_remember_me"))
        if hasattr(self, 'reg_remember'):
            self.reg_remember.setText(t("login_remember_me"))
        if hasattr(self, 'register_link'):
            self.register_link.setText(t("login_register_link"))
        if hasattr(self, 'forgot_link'):
            self.forgot_link.setText(t("login_forgot_password"))
        if hasattr(self, '_reg_email_label'):
            self._reg_email_label.setText(t("login_email"))
        if hasattr(self, '_reg_display_label'):
            self._reg_display_label.setText(t("login_reg_display"))
        if hasattr(self, '_reg_pass_label'):
            self._reg_pass_label.setText(t("login_password"))
        if hasattr(self, 'reg_email'):
            self.reg_email.setPlaceholderText(t("login_reg_email_ph"))
        if hasattr(self, 'reg_display'):
            self.reg_display.setPlaceholderText(t("login_reg_display_ph"))
        if hasattr(self, 'reg_password'):
            self.reg_password.setPlaceholderText(t("login_reg_password_ph"))
        if hasattr(self, 'reg_btn'):
            self.reg_btn.setText(t("login_register_btn"))
        if hasattr(self, 'back_link'):
            self.back_link.setText(t("login_back"))
