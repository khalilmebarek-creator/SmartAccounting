"""Login and Registration screen."""

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QMessageBox, QStackedWidget, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ui.resources.i18n import t
from ui.app_state import ThemeColors
from ui.login_session import save_login_email, load_login_email
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
        layout.addRow(t("pwd_old"), old_pass)

        new_pass = QLineEdit()
        new_pass.setEchoMode(QLineEdit.Password)
        new_pass.setMinimumHeight(34)
        layout.addRow(t("pwd_new"), new_pass)

        confirm_pass = QLineEdit()
        confirm_pass.setEchoMode(QLineEdit.Password)
        confirm_pass.setMinimumHeight(34)
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
        self._login_pass_label = QLabel(t("login_password"))
        self.login_password.returnPressed.connect(self.do_login)
        form.addRow(self._login_pass_label, self.login_password)

        layout.addLayout(form)

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
        self.register_link.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(self.register_link)

        self.forgot_link = QPushButton(t("login_forgot_password"))
        self.forgot_link.setFlat(True)
        self.forgot_link.setStyleSheet(f"color: {ThemeColors.get('warning')}; border: none;")
        self.forgot_link.setCursor(Qt.PointingHandCursor)
        self.forgot_link.clicked.connect(self._show_forgot_password)
        self.forgot_link.setVisible(False)
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
        self._reg_pass_label = QLabel(t("login_password"))
        form.addRow(self._reg_pass_label, self.reg_password)

        layout.addLayout(form)

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
        self.back_link.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(self.back_link)

        page.setLayout(layout)
        return page

    def do_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text()
        if not email or not password:
            self.login_error.setText(t("login_empty_fields"))
            return
        ok, error_code, extra = user_manager.login(email, password)
        if ok:
            self.login_error.setText("")
            save_login_email(email)
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
            self.stack.setCurrentIndex(0)
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

    def _show_forgot_password(self):
        from PyQt5.QtWidgets import QInputDialog, QLineEdit
        email, ok1 = QInputDialog.getText(
            self, t("login_forgot_password"), t("login_email"),
            QLineEdit.Normal
        )
        if not ok1 or not email.strip():
            return
        new_pass, ok2 = QInputDialog.getText(
            self, t("login_forgot_password"), t("login_password"),
            QLineEdit.Password
        )
        if not ok2 or not new_pass:
            return
        success, error_code = user_manager.reset_password_by_email(email.strip(), new_pass)
        if success:
            QMessageBox.information(self, t("success"), t("login_forgot_success"))
        else:
            msg = t(error_code) if t(error_code) != error_code else error_code
            QMessageBox.warning(self, t("error"), msg)
