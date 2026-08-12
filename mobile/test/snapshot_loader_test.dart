import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/app_logger.dart';
import 'package:smart_accounting_mobile/data/snapshot_loader.dart';

/// Real cross-platform fixtures produced by the desktop Python engine
/// (tools/gen_mobile_fixtures.py) — including a genuine SACF1 blob.
String _fixture(String name) =>
    File('test/fixtures/$name').readAsStringSync();

void main() {
  AppLogger.log.autoFlush = false;
  final loader = SnapshotLoader();

  group('plain (unencrypted) snapshot', () {
    test('loads and parses payload fields', () async {
      final snap = await loader.load(_fixture('demo_snapshot_plain.json'));
      expect(snap.companyName, 'Mobile Test Co');
      expect(snap.fiscalYear, 2024);
      expect(snap.fin('revenue'), 250000.0);
      expect(snap.ratio('current_ratio'), 2.5);
      expect(snap.taxObligations.length, 2);
    });

    test('rejects non-SmartAccounting app id', () async {
      final text = _fixture('demo_snapshot_plain.json');
      final map = jsonDecode(text) as Map<String, dynamic>;
      map['app'] = 'OtherApp';
      expect(
        () => loader.load(jsonEncode(map)),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'invalid_snapshot')),
      );
    });

    test('rejects broken json', () async {
      expect(
        () => loader.load('{not json'),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'invalid_json')),
      );
    });

    test('rejects checksum mismatch', () async {
      final text = _fixture('demo_snapshot_plain.json');
      final map = jsonDecode(text) as Map<String, dynamic>;
      map['checksum'] = 'deadbeef';
      expect(
        () => loader.load(jsonEncode(map)),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'checksum_mismatch')),
      );
    });
  });

  group('encrypted snapshot (desktop SACF1)', () {
    test('decrypts with correct passphrase', () async {
      final snap =
          await loader.load(_fixture('demo_snapshot_encrypted.json'),
              passphrase: 'test-pass');
      expect(snap.companyName, 'Mobile Test Co');
      expect(snap.fin('net_income'), 20000.0);
    });

    test('requires passphrase for encrypted wrapper', () async {
      expect(
        () => loader.load(_fixture('demo_snapshot_encrypted.json')),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'passphrase_required')),
      );
    });

    test('wrong passphrase fails with decryption_failed', () async {
      expect(
        () => loader.load(_fixture('demo_snapshot_encrypted.json'),
            passphrase: 'wrong-pass'),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'decryption_failed')),
      );
    });

    test('tampered ciphertext fails with decryption_failed', () async {
      final text = _fixture('demo_snapshot_encrypted.json');
      final map = jsonDecode(text) as Map<String, dynamic>;
      final blob = base64Decode(map['data'] as String);
      blob[blob.length - 1] ^= 0xFF; // flip last byte (inside tag)
      map['data'] = base64Encode(blob);
      expect(
        () => loader.load(jsonEncode(map), passphrase: 'test-pass'),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'decryption_failed')),
      );
    });
  });

  group('SACF1 header parsing', () {
    test('rejects short blob', () {
      expect(
        () => loader.parseSACF1([1, 2, 3]),
        throwsA(isA<SnapshotError>()),
      );
    });

    test('rejects wrong magic', () {
      final blob = Uint8List.fromList(List.filled(64, 0));
      blob.setAll(0, utf8.encode('BAD12'));
      expect(
        () => loader.parseSACF1(blob),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'invalid_snapshot')),
      );
    });

    test('rejects unsupported KDF id', () {
      final blob = Uint8List.fromList(List.filled(64, 0));
      blob.setAll(0, utf8.encode('SACF1'));
      blob[5] = 9; // unknown KDF
      expect(
        () => loader.parseSACF1(blob),
        throwsA(isA<SnapshotError>()
            .having((e) => e.reason, 'reason', 'unsupported_kdf')),
      );
    });

    test('parses a valid desktop header layout', () {
      // Minimal valid blob: header + salt16 + nonce12 + 16 dummy bytes.
      final blob = Uint8List.fromList(List.filled(17 + 16 + 12 + 16, 0));
      blob.setAll(0, utf8.encode('SACF1'));
      blob[5] = 1; // argon2id
      blob[6] = 0x00; // memory cost = 65536 (0x00010000)
      blob[7] = 0x01;
      blob[8] = 0x00;
      blob[9] = 0x00;
      blob[10] = 0x00; // time cost = 3
      blob[11] = 0x00;
      blob[12] = 0x00;
      blob[13] = 0x03;
      blob[14] = 0x01; // parallelism
      blob[15] = 0x10; // salt len 16
      blob[16] = 0x0C; // nonce len 12
      final parts = loader.parseSACF1(blob);
      expect(parts.memoryCost, 65536);
      expect(parts.timeCost, 3);
      expect(parts.parallelism, 1);
      expect(parts.salt.length, 16);
      expect(parts.nonce.length, 12);
      expect(parts.aad.length, 17 + 16 + 12);
    });
  });
}
