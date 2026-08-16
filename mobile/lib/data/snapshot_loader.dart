/// Loads desktop snapshots (`smart_accounting_snapshot_*.json`) produced by
/// the Smart Accounting Platform cloud sync:
///
/// Wrapper:
///   {"app": "SmartAccounting", "format": 1, "encrypted": bool,
///    "checksum": sha256-hex of raw payload JSON,
///    "data": `<base64 SACF1>` or raw payload string}
///
/// Encrypted data is the SACF1 blob format from the desktop
/// `commercial/encryption` module:
///   MAGIC(5) | KDF_ID(1) | MEMORY_COST(4BE) | TIME_COST(4BE) | PARALLELISM(1)
///   | SALT_LEN(1) | NONCE_LEN(1) | SALT(16) | NONCE(12) | AES-256-GCM(CT||TAG)
///   with AAD = header + salt + nonce and an Argon2id-derived key.
library;

import 'dart:convert';
import 'dart:typed_data';

import 'package:crypto/crypto.dart' as sha;
import 'package:cryptography/cryptography.dart';

import '../core/app_logger.dart';
import 'snapshot_model.dart';

class SnapshotError implements Exception {
  SnapshotError(this.reason);
  final String reason;

  @override
  String toString() => 'SnapshotError($reason)';
}

class SnapshotLoader {
  SnapshotLoader();

  static const String _appId = 'SmartAccounting';
  static const int _headerSize = 17; // 5s B I I B B B (big-endian)

  /// Parse a snapshot file's full text into a typed [SnapshotData].
  /// [passphrase] is required only when the wrapper says `encrypted: true`.
  Future<SnapshotData> load(String fileText, {String? passphrase}) async {
    final Object? decoded;
    try {
      decoded = jsonDecode(fileText);
    } catch (err) {
      AppLogger.log.warn('loader', 'invalid JSON: $err');
      throw SnapshotError('invalid_json');
    }
    if (decoded is! Map<String, dynamic>) {
      throw SnapshotError('invalid_snapshot');
    }
    if (decoded['app'] != _appId) {
      AppLogger.log.warn('loader', 'app id mismatch: ${decoded['app']}');
      throw SnapshotError('invalid_snapshot');
    }

    final String rawPayload;
    if (decoded['encrypted'] == true) {
      if (passphrase == null || passphrase.isEmpty) {
        throw SnapshotError('passphrase_required');
      }
      final data = decoded['data'];
      if (data is! String) {
        throw SnapshotError('invalid_snapshot');
      }
      final clear = await _decryptSACF1(data, passphrase);
      rawPayload = utf8.decode(clear);
    } else {
      final data = decoded['data'];
      if (data is! String) {
        throw SnapshotError('invalid_snapshot');
      }
      rawPayload = data;
    }

    final expected = decoded['checksum'];
    if (expected is String && expected.isNotEmpty) {
      final actual = sha.sha256.convert(utf8.encode(rawPayload)).toString();
      if (actual != expected) {
        AppLogger.log.warn('loader', 'checksum mismatch');
        throw SnapshotError('checksum_mismatch');
      }
    }

    final Object? payload;
    try {
      payload = jsonDecode(rawPayload);
    } catch (err) {
      AppLogger.log.warn('loader', 'payload JSON broken: $err');
      throw SnapshotError('invalid_snapshot');
    }
    if (payload is! Map<String, dynamic>) {
      throw SnapshotError('invalid_snapshot');
    }
    AppLogger.log.info('loader', 'snapshot parsed (checksum ok)');
    return SnapshotData.fromPayload(payload);
  }

  /// Decrypt a base64 SACF1 blob with the given passphrase.
  Future<Uint8List> _decryptSACF1(String base64Blob, String passphrase) async {
    final Uint8List blob;
    try {
      blob = base64Decode(base64Blob);
    } catch (_) {
      throw SnapshotError('invalid_snapshot');
    }
    final parsed = parseSACF1(blob);
    try {
      final kdf = Argon2id(
        memory: parsed.memoryCost,
        iterations: parsed.timeCost,
        parallelism: parsed.parallelism,
        hashLength: 32,
      );
      final key = await kdf.deriveKey(
        secretKey: SecretKey(utf8.encode(passphrase)),
        nonce: parsed.salt,
      );
      final aes = AesGcm.with256bits();
      final clear = await aes.decrypt(
        SecretBox(
          parsed.ciphertext,
          nonce: parsed.nonce,
          mac: Mac(parsed.tag),
        ),
        secretKey: key,
        aad: parsed.aad,
      );
      return Uint8List.fromList(clear);
    } on SecretBoxAuthenticationError {
      AppLogger.log.warn('loader', 'decryption failed (wrong passphrase/tamper)');
      throw SnapshotError('decryption_failed');
    } catch (_) {
      AppLogger.log.warn('loader', 'decryption failed unexpectedly');
      throw SnapshotError('decryption_failed');
    }
  }

  /// Parse the SACF1 header + body layout. Exposed for unit tests.
  SACF1Parts parseSACF1(List<int> blob) {
    if (blob.length < _headerSize + 16 + 12 + 16) {
      throw SnapshotError('invalid_snapshot');
    }
    final bd = ByteData.sublistView(Uint8List.fromList(blob));
    final magic = String.fromCharCodes(blob.sublist(0, 5));
    if (magic != 'SACF1') {
      throw SnapshotError('invalid_snapshot');
    }
    final kdfId = bd.getUint8(5);
    if (kdfId != 1) {
      throw SnapshotError('unsupported_kdf');
    }
    final memoryCost = bd.getUint32(6, Endian.big);
    final timeCost = bd.getUint32(10, Endian.big);
    final parallelism = bd.getUint8(14);
    final saltLen = bd.getUint8(15);
    final nonceLen = bd.getUint8(16);
    if (saltLen != 16 || nonceLen != 12) {
      throw SnapshotError('invalid_snapshot');
    }
    final saltStart = _headerSize;
    final saltEnd = saltStart + saltLen;
    final nonceEnd = saltEnd + nonceLen;
    final salt = blob.sublist(saltStart, saltEnd);
    final nonce = blob.sublist(saltEnd, nonceEnd);
    final body = blob.sublist(nonceEnd);
    final ciphertext = Uint8List.sublistView(
        Uint8List.fromList(body), 0, body.length - 16);
    final tag = Uint8List.sublistView(
        Uint8List.fromList(body), body.length - 16);
    final aad = Uint8List.fromList(blob.sublist(0, nonceEnd));
    return SACF1Parts(
      memoryCost: memoryCost,
      timeCost: timeCost,
      parallelism: parallelism,
      salt: Uint8List.fromList(salt),
      nonce: Uint8List.fromList(nonce),
      ciphertext: ciphertext,
      tag: tag,
      aad: aad,
    );
  }
}

/// Structured SACF1 blob parts.
class SACF1Parts {
  SACF1Parts({
    required this.memoryCost,
    required this.timeCost,
    required this.parallelism,
    required this.salt,
    required this.nonce,
    required this.ciphertext,
    required this.tag,
    required this.aad,
  });

  final int memoryCost;
  final int timeCost;
  final int parallelism;
  final Uint8List salt;
  final Uint8List nonce;
  final Uint8List ciphertext;
  final Uint8List tag;
  final Uint8List aad;
}
