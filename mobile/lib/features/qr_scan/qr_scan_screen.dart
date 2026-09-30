/// Full-screen QR scanner: reads a desktop QR code and returns a decoded
/// [SnapshotData] via `Navigator.pop`.
library;

import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../../core/i18n.dart';
import '../../data/qr_payload.dart';
import '../../data/snapshot_model.dart';

class QrScanScreen extends StatefulWidget {
  const QrScanScreen({super.key, required this.lang});

  final String lang;

  @override
  State<QrScanScreen> createState() => _QrScanScreenState();
}

class _QrScanScreenState extends State<QrScanScreen> {
  final MobileScannerController _controller = MobileScannerController();
  bool _handled = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_handled || !mounted) return;
    final barcode = capture.barcodes.isEmpty ? null : capture.barcodes.first;
    final text = barcode?.rawValue;
    if (text == null || text.isEmpty) return;

    try {
      final snap = decodeQrSnapshot(text);
      _handled = true;
      Navigator.of(context).pop(snap);
    } on QrPayloadError {
      _handled = false;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(I18n.t(widget.lang, 'qr_invalid')),
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(I18n.t(widget.lang, 'qr_scan_title'))),
      body: Stack(
        fit: StackFit.expand,
        children: [
          MobileScanner(controller: _controller, onDetect: _onDetect),
          Center(
            child: IgnorePointer(
              child: Container(
                width: 260,
                height: 260,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.white, width: 3),
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
