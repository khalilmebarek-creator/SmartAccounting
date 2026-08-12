import 'package:flutter/material.dart';

/// Compact three-bar chart (revenue / expenses / profit) drawn with
/// [CustomPainter] — no chart library.
class KpiTrendChart extends StatelessWidget {
  const KpiTrendChart({
    super.key,
    required this.labels,
    required this.values,
    required this.color,
  });

  final List<String> labels;
  final List<double> values;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SizedBox(
      height: 180,
      width: double.infinity,
      child: CustomPaint(
        painter: _BarPainter(
          labels: labels,
          values: values,
          barColor: color,
          axisColor: theme.colorScheme.outlineVariant,
          labelStyle: theme.textTheme.bodySmall!
              .copyWith(color: theme.colorScheme.onSurface),
          valueStyle: theme.textTheme.bodySmall!
              .copyWith(color: theme.colorScheme.onSurface),
        ),
      ),
    );
  }
}

class _BarPainter extends CustomPainter {
  _BarPainter({
    required this.labels,
    required this.values,
    required this.barColor,
    required this.axisColor,
    required this.labelStyle,
    required this.valueStyle,
  });

  final List<String> labels;
  final List<double> values;
  final Color barColor;
  final Color axisColor;
  final TextStyle labelStyle;
  final TextStyle valueStyle;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;
    final maxValue = values.fold<double>(0, (a, b) => a > b ? a : b);
    if (maxValue <= 0) return;
    const topPad = 22.0;
    const bottomPad = 34.0;
    final chartHeight = size.height - topPad - bottomPad;
    final slot = size.width / values.length;
    final barWidth = slot * 0.5;

    // Baseline.
    final baseY = size.height - bottomPad;
    canvas.drawLine(
      Offset(0, baseY),
      Offset(size.width, baseY),
      Paint()
        ..color = axisColor
        ..strokeWidth = 1,
    );

    String short(double v) => v >= 1000000
        ? '${(v / 1000000).toStringAsFixed(1)}M'
        : v.toStringAsFixed(0);

    for (var i = 0; i < values.length; i++) {
      final v = values[i];
      final barHeight = (v / maxValue) * chartHeight;
      final left = i * slot + (slot - barWidth) / 2;
      final rect = Rect.fromLTWH(left, baseY - barHeight, barWidth, barHeight);
      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(6)),
        Paint()..color = barColor,
      );

      final valueTp = TextPainter(
        text: TextSpan(text: short(v), style: valueStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      valueTp.paint(
        canvas,
        Offset(left + barWidth / 2 - valueTp.width / 2,
            baseY - barHeight - valueTp.height - 2),
      );

      final labelTp = TextPainter(
        text: TextSpan(text: labels[i], style: labelStyle),
        textDirection: TextDirection.ltr,
        maxLines: 1,
        ellipsis: '…',
      )..layout(maxWidth: slot);
      labelTp.paint(
        canvas,
        Offset(left + barWidth / 2 - labelTp.width / 2, baseY + 6),
      );
    }
  }

  @override
  bool shouldRepaint(_BarPainter old) =>
      old.values != values || old.labels != labels || old.barColor != barColor;
}
