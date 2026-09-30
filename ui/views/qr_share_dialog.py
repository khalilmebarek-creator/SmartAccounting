# نافذة مشاركة البيانات عبر رمز QR (Desktop → Mobile)
# ===================================================

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage

from ui.resources.i18n import t
from modules import qr_transfer


class QrShareDialog(QDialog):
    """يعرض رمز QR يحتوي snapshot البيانات المالية مضغوطاً لنقله للجوال."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._encoded = None
        self.setWindowTitle(t("qr_title"))
        self.setMinimumSize(460, 560)
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.info_label = QLabel(t("qr_info"))
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(340, 340)
        layout.addWidget(self.qr_label)

        self.size_label = QLabel("")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.size_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QPushButton(t("qr_save_png"))
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._save_png)
        btn_row.addWidget(self.save_btn)
        self.close_btn = QPushButton(t("guide_close"))
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.close_btn)
        layout.addLayout(btn_row)

    def refresh(self):
        try:
            payload = qr_transfer.build_payload()
            self._encoded = qr_transfer.encode_payload(payload)
        except Exception as e:
            self.qr_label.setText(t("qr_error"))
            self.size_label.setText(str(e))
            return

        try:
            png = qr_transfer.make_qr_png(self._encoded, box_size=8, border=4)
            image = QImage.fromData(png, "PNG")
            pixmap = QPixmap.fromImage(image)
            scaled = pixmap.scaled(
                340, 340,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.qr_label.setPixmap(scaled)
        except Exception as e:
            self.qr_label.setText(t("qr_too_large"))
            self.size_label.setText(str(e))
            return

        self.size_label.setText(
            f"{t('qr_size')}: {len(self._encoded)} {t('qr_chars')}"
        )

    def _save_png(self):
        if not self._encoded:
            return
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, t("qr_save_png"), "smart_accounting_qr.png", "PNG (*.png)"
        )
        if not path:
            return
        try:
            png = qr_transfer.make_qr_png(self._encoded, box_size=10, border=4)
            with open(path, "wb") as f:
                f.write(png)
            QMessageBox.information(self, t("success"), f"✅ {path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))
