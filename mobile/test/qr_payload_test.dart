import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/app_logger.dart';
import 'package:smart_accounting_mobile/data/qr_payload.dart';

String _fixture(String name) => File('test/fixtures/$name').readAsStringSync();

void main() {
  AppLogger.log.autoFlush = false;

  group('qr_payload', () {
    test('decodes a real desktop QR payload from fixtures', () {
      final qr = _fixture('demo_snapshot_qr.txt').trim();
      final snap = decodeQrSnapshot(qr);
      expect(snap.companyName, 'Mobile Test Co');
      expect(snap.fiscalYear, 2024);
      expect(snap.fin('revenue'), 250000.0);
      expect(snap.ratio('current_ratio'), 2.5);
      expect(snap.taxObligations.length, 2);
    });

    test('rejects garbage text', () {
      expect(
        () => decodeQrSnapshot('not a qr payload at all'),
        throwsA(isA<QrPayloadError>()
            .having((e) => e.reason, 'reason', 'invalid_qr')),
      );
    });

    test('rejects valid base64 that is not gzip', () {
      // base64 of plain text compresses differently — this must fail to
      // decode as a payload rather than crash.
      final notGzip =
          'dGhpcyBpcyBwbGFpbiBqc29uIHRleHQgbm90IGd6aXAgY29tcHJlc3NlZA==';
      expect(
        () => decodeQrSnapshot(notGzip),
        throwsA(isA<QrPayloadError>()),
      );
    });
  });
}