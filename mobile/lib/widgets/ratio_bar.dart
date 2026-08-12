import 'package:flutter/material.dart';

class RatioBar extends StatelessWidget {
  const RatioBar({
    super.key,
    required this.label,
    required this.value,
    required this.max,
  });

  final String label;
  final double value;
  final double max;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final fraction = (max <= 0 ? 0.0 : (value / max)).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(label, style: theme.textTheme.bodyMedium),
          ),
          Expanded(
            flex: 2,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: fraction,
                minHeight: 10,
                backgroundColor: theme.colorScheme.surfaceContainerHighest,
              ),
            ),
          ),
          SizedBox(
            width: 76,
            child: Text(
              value.toStringAsFixed(2),
              textAlign: TextAlign.end,
              style: theme.textTheme.bodyMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }
}
