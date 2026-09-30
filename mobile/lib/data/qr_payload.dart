/// Decodes a desktop QR payload (gzip + base64 URL-safe) into [SnapshotData].
///
/// The desktop `modules/qr_transfer.py` encodes the snapshot as:
///   json → gzip.compress → base64.urlsafe_b64encode
/// This module reverses that chain.
library;

import 'dart:convert';
import 'dart:io';

import 'snapshot_model.dart';

class QrPayloadError implements Exception {
  QrPayloadError(this.reason);
  final String reason;

  @override
  String toString() => 'QrPayloadError($reason)';
}

/// Decode the text of a scanned QR code into a typed snapshot.
SnapshotData decodeQrSnapshot(String qrText) {
  try {
    final compressed = base64Url.decode(qrText.trim());
    final raw = gzip.decode(compressed);
    final decoded = jsonDecode(utf8.decode(raw));
    if (decoded is! Map<String, dynamic>) {
      throw QrPayloadError('invalid_qr');
    }
    return SnapshotData.fromPayload(decoded);
  } on QrPayloadError {
    rethrow;
  } catch (_) {
    throw QrPayloadError('invalid_qr');
  }
}
