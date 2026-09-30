# نقل البيانات عبر رمز QR (Desktop → Mobile)
# ==========================================
# يضغط الـ snapshot المالي (gzip) ثم يرمّزه Base64 ثم يولّد صورة QR.
# الجوال يمسح الـ QR ويفك الضغط والترميز ليستورد نفس البيانات.

import base64
import gzip
import io
import json

from ui.app_state import state


def build_payload():
    """التقاط الحالة الكاملة (نفس payload المزامنة السحابية)."""
    from modules.cloud_sync import _build_payload
    return _build_payload(state)


def encode_payload(payload) -> str:
    """payload → (json + gzip + base64 URL-safe) سلسلة نصية قصيرة للـ QR."""
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def decode_payload(encoded: str) -> dict:
    """عكس encode_payload: سلسلة base64 → payload dict أصلي."""
    compressed = base64.urlsafe_b64decode(encoded.encode("ascii"))
    raw = gzip.decompress(compressed)
    return json.loads(raw.decode("utf-8"))


def make_qr_image(encoded: str, box_size=8, border=4):
    """توليد صورة QR (PIL Image) من السلسلة المرمّزة."""
    import qrcode

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(encoded)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def make_qr_png(encoded: str, box_size=8, border=4) -> bytes:
    """صورة QR كبايتات PNG (للعرض أو الحفظ)."""
    img = make_qr_image(encoded, box_size=box_size, border=border)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
