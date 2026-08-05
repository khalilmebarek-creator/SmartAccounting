# -*- coding: utf-8 -*-
# Module 3: Tier enforcement (live feature gates) — tests
# ========================================================
# بوابات feature_enabled مفعّلة فعلياً عند نقاط دخول الميزات في الواجهات.

from datetime import date
import sys
from unittest import mock

import pytest

from commercial import entitlement
from commercial.entitlement import current_tier, feature_allowed, required_tier
from commercial.licensing.activation import LicenseStore
from commercial.licensing.expiry import expiry_from_today
from commercial.licensing.license import (
    encode_key,
    generate_keypair,
    load_private_key,
    load_public_key,
)
from commercial.licensing.tier import Tier

TEST_HWID = "aa" * 32


@pytest.fixture(scope="module")
def keypair():
    private_pem, public_pem = generate_keypair()
    return load_private_key(private_pem), load_public_key(public_pem)


@pytest.fixture(scope="module")
def qapp():
    """تطبيق Qt واحد للاختبارات الواجهية (sys.argv ضروري — درس Module 1)."""
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    app.processEvents()


def _key_for(tier: Tier, private, days=30):
    payload = {
        "tier": tier.value,
        "licensee": "Tester",
        "exp": expiry_from_today(days),
        "hwid": TEST_HWID,
        "iss": date.today().isoformat(),
        "uid": "test-uid",
    }
    return encode_key(payload, private)


def _store_for(tmp_path, keypair, tier: Tier):
    private, public = keypair
    store = LicenseStore(
        path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID
    )
    store.save(_key_for(tier, private))
    return store


def _corrupt_store(tmp_path, public):
    path = tmp_path / "license.dat"
    path.write_text("garbage-not-a-key", encoding="utf-8")
    return LicenseStore(path=str(path), public_key=public, hardware_id=TEST_HWID)


# ------------------------------------------------------------- core


def test_default_tier_is_free():
    entitlement.reset()
    assert current_tier() == Tier.FREE


def test_tier_from_license(tmp_path, keypair):
    entitlement.set_store(_store_for(tmp_path, keypair, Tier.PRO))
    assert current_tier() == Tier.PRO


def test_corrupt_license_is_free(tmp_path, keypair):
    _, public = keypair
    entitlement.set_store(_corrupt_store(tmp_path, public))
    assert current_tier() == Tier.FREE


def test_reset_restores_default(tmp_path, keypair):
    entitlement.set_store(_store_for(tmp_path, keypair, Tier.ENTERPRISE))
    entitlement.reset()
    assert current_tier() == Tier.FREE


def test_feature_allowed_matrix_free():
    entitlement.reset()
    assert not feature_allowed("cloud_sync")
    assert not feature_allowed("multi_device")
    assert not feature_allowed("ai_unlimited")
    assert not feature_allowed("api_access")
    assert not feature_allowed("audit_trail")
    assert feature_allowed("unknown_feature")


def test_feature_allowed_pro(tmp_path, keypair):
    entitlement.set_store(_store_for(tmp_path, keypair, Tier.PRO))
    assert feature_allowed("cloud_sync")
    assert feature_allowed("multi_device")
    assert not feature_allowed("ai_unlimited")


def test_feature_allowed_enterprise(tmp_path, keypair):
    entitlement.set_store(_store_for(tmp_path, keypair, Tier.ENTERPRISE))
    assert feature_allowed("ai_unlimited")
    assert feature_allowed("api_access")
    assert feature_allowed("audit_trail")


def test_required_tier_mapping():
    assert required_tier("cloud_sync") == Tier.PRO
    assert required_tier("ai_unlimited") == Tier.ENTERPRISE
    assert required_tier("unknown") is None


@pytest.fixture(autouse=True)
def _reset_entitlement(qapp):
    yield
    entitlement.reset()


# ------------------------------------------------------- cloud sync gate (PRO)


def _make_cloud_view(qapp):
    from ui.views.cloud_sync_view import CloudSyncView

    return CloudSyncView()


def test_push_blocked_on_free(qapp):
    view = _make_cloud_view(qapp)
    view._engine.push = mock.Mock(side_effect=AssertionError("gated!"))
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information") as info:
        view._do_push(None)
    info.assert_called_once()
    view._engine.push.assert_not_called()


def test_pull_blocked_on_free(qapp):
    view = _make_cloud_view(qapp)
    view._engine.pull = mock.Mock(side_effect=AssertionError("gated!"))
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information"):
        view._pull()
    view._engine.pull.assert_not_called()


def test_push_allowed_on_pro(tmp_path, keypair, qapp):
    entitlement.set_store(_store_for(tmp_path, keypair, Tier.PRO))
    view = _make_cloud_view(qapp)
    view._engine.push = mock.Mock(return_value=[])
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information"):
        view._do_push(None)
    view._engine.push.assert_called_once()


def test_backup_local_stays_free(qapp):
    """النسخ الاحتياطي المحلي غير مقفل (ليس مزامنة سحابية)."""
    view = _make_cloud_view(qapp)
    view._engine.backup_local = mock.Mock(
        return_value={"path": "x", "size": 1, "timestamp": 0}
    )
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information"):
        view._backup_local()
    view._engine.backup_local.assert_called_once()


# ---------------------------------------------- ai_unlimited gate (ENTERPRISE)


def test_ai_months_6_removed_on_free(qapp):
    from ui.views.ai_insights_view import AIInsightsView

    view = AIInsightsView()
    items = [view.months_combo.itemText(i) for i in range(view.months_combo.count())]
    assert "6" not in items
    assert view.months_combo.currentText() == "3"


def test_ai_months_6_present_on_enterprise(tmp_path, keypair, qapp):
    from ui.views.ai_insights_view import AIInsightsView

    entitlement.set_store(_store_for(tmp_path, keypair, Tier.ENTERPRISE))
    view = AIInsightsView()
    items = [view.months_combo.itemText(i) for i in range(view.months_combo.count())]
    assert "6" in items


def test_ai_export_blocked_on_free(qapp):
    from ui.views.ai_insights_view import AIInsightsView

    view = AIInsightsView()
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information"), mock.patch(
        "ui.views.ai_insights_view.QFileDialog.getSaveFileName",
        side_effect=AssertionError("dialog opened!"),
    ):
        view._export_pdf()
        view._export_excel()


def test_ai_export_allowed_on_enterprise(tmp_path, keypair, qapp):
    from ui.views.ai_insights_view import AIInsightsView

    entitlement.set_store(_store_for(tmp_path, keypair, Tier.ENTERPRISE))
    view = AIInsightsView()
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information"), mock.patch(
        "PyQt5.QtWidgets.QMessageBox.warning"
    ), mock.patch(
        "ui.views.ai_insights_view.QFileDialog.getSaveFileName",
        return_value=("", ""),
    ), mock.patch("PyQt5.QtWidgets.QMessageBox.critical"):
        view._export_pdf()
        view._export_excel()


def test_ai_retranslate_keeps_gate(qapp):
    from ui.views.ai_insights_view import AIInsightsView

    view = AIInsightsView()
    with mock.patch("PyQt5.QtWidgets.QMessageBox.information"):
        view.retranslate()
    items = [view.months_combo.itemText(i) for i in range(view.months_combo.count())]
    assert "6" not in items
