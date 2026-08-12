import 'package:flutter/material.dart';

class KpiCard extends StatelessWidget {
  const KpiCard({
    super.key,
    required this.label,
    required this.value,
    this.delta,
  });

  final String label;
  final String value;

  /// Percent change vs previous snapshot; null hides the trend arrow.
  final double? delta;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final Widget? trend;
    if (delta != null) {
      final up = delta! >= 0;
      final arrow = up ? '▲' : '▼';
      final color = up ? const Color(0xFF22C55E) : const Color(0xFFEF4444);
      trend = Text(
        '$arrow ${delta!.abs().toStringAsFixed(1)}%',
        style: theme.textTheme.bodySmall
            ?.copyWith(color: color, fontWeight: FontWeight.bold),
      );
    } else {
      trend = null;
    }
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: theme.colorScheme.outline),
              ),
              const SizedBox(height: 6),
              Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              if (trend != null) ...[const SizedBox(height: 4), trend],
            ],
          ),
        ),
      ),
    );
  }
}
