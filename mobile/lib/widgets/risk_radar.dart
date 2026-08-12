import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Radial risk radar (0-100 per axis, higher = worse). Drawn with
/// [CustomPainter] — no chart dependency.
class RiskRadar extends StatelessWidget {
  const RiskRadar({super.key, required this.values, required this.labels});

  final List<double> values;
  final List<String> labels;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SizedBox(
      height: 220,
      width: double.infinity,
      child: CustomPaint(
        painter: _RadarPainter(
          values: values,
          labels: labels,
          axisColor: theme.colorScheme.outlineVariant,
          fillColor: theme.colorScheme.error.withValues(alpha: 0.25),
          strokeColor: theme.colorScheme.error,
          labelStyle: theme.textTheme.bodySmall!
              .copyWith(color: theme.colorScheme.onSurface),
        ),
      ),
    );
  }
}

class _RadarPainter extends CustomPainter {
  _RadarPainter({
    required this.values,
    required this.labels,
    required this.axisColor,
    required this.fillColor,
    required this.strokeColor,
    required this.labelStyle,
  });

  final List<double> values;
  final List<String> labels;
  final Color axisColor;
  final Color fillColor;
  final Color strokeColor;
  final TextStyle labelStyle;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;
    final n = values.length;
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 28;

    double angleFor(int i) => -math.pi / 2 + 2 * math.pi * i / n;
    Offset pointAt(int i, double r) =>
        center + Offset(math.cos(angleFor(i)) * r, math.sin(angleFor(i)) * r);

    final gridPaint = Paint()
      ..color = axisColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // Grid rings 25/50/75/100%.
    for (final ring in [0.25, 0.5, 0.75, 1.0]) {
      final path = Path();
      for (var i = 0; i < n; i++) {
        final p = pointAt(i, radius * ring);
        if (i == 0) {
          path.moveTo(p.dx, p.dy);
        } else {
          path.lineTo(p.dx, p.dy);
        }
      }
      path.close();
      canvas.drawPath(path, gridPaint);
    }

    // Spokes.
    for (var i = 0; i < n; i++) {
      canvas.drawLine(center, pointAt(i, radius), gridPaint);
    }

    // Data polygon.
    final dataPath = Path();
    for (var i = 0; i < n; i++) {
      final v = values[i].clamp(0.0, 100.0) / 100.0;
      final p = pointAt(i, radius * v);
      if (i == 0) {
        dataPath.moveTo(p.dx, p.dy);
      } else {
        dataPath.lineTo(p.dx, p.dy);
      }
    }
    dataPath.close();
    canvas.drawPath(dataPath, Paint()..color = fillColor);
    canvas.drawPath(
      dataPath,
      Paint()
        ..color = strokeColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );

    // Labels.
    for (var i = 0; i < n; i++) {
      final tp = TextPainter(
        text: TextSpan(text: labels[i], style: labelStyle),
        textDirection: TextDirection.ltr,
        maxLines: 1,
        ellipsis: '…',
      )..layout(maxWidth: 90);
      final p = pointAt(i, radius + 16);
      tp.paint(
        canvas,
        Offset(p.dx - tp.width / 2, p.dy - tp.height / 2),
      );
    }
  }

  @override
  bool shouldRepaint(_RadarPainter old) =>
      old.values != values ||
      old.labels != labels ||
      old.strokeColor != strokeColor;
}
