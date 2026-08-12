import 'package:flutter/material.dart';

import '../../core/app_state.dart';
import '../../core/i18n.dart';

class TaxCalendarScreen extends StatelessWidget {
  const TaxCalendarScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    final lang = state.language;
    final snap = state.snapshot;

    if (snap == null || snap.taxObligations.isEmpty) {
      return Center(child: Text(I18n.t(lang, 'tax_no_obligations')));
    }

    final items = snap.taxObligations
        .whereType<Map<String, dynamic>>()
        .toList();

    return ListView(
      padding: const EdgeInsets.only(top: 12, bottom: 24),
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
          child: Text(
            I18n.t(lang, 'tax_upcoming'),
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ),
        ...items.map((o) => _ObligationTile(obligation: o, lang: lang)),
      ],
    );
  }
}

class _ObligationTile extends StatelessWidget {
  const _ObligationTile({required this.obligation, required this.lang});

  final Map<String, dynamic> obligation;
  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final taxType = (obligation['tax_type'] ?? '').toString();
    final dueDay = obligation['due_day'] is num
        ? (obligation['due_day'] as num).toInt()
        : 20;
    final month = obligation['month'] is num
        ? (obligation['month'] as num).toInt()
        : 1;
    final amount = obligation['amount'] is num
        ? (obligation['amount'] as num).toDouble()
        : 0.0;

    final now = DateTime.now();
    final due = DateTime(now.year, month, dueDay);
    final delta = due.difference(DateTime(now.year, now.month, now.day)).inDays;
    final String when = delta >= 0
        ? I18n.format(I18n.t(lang, 'tax_days_left'), ['$delta'])
        : I18n.format(I18n.t(lang, 'tax_days_overdue'), ['${-delta}']);

    return Card(
      child: ListTile(
        leading: Icon(
          delta < 0 ? Icons.error_outline : Icons.event,
          color: delta < 0 ? theme.colorScheme.error : theme.colorScheme.primary,
        ),
        title: Text(taxType),
        subtitle: Text(when),
        trailing: Text(
          amount == 0 ? '—' : '${amount.toStringAsFixed(2)} DA',
          style: theme.textTheme.bodyMedium
              ?.copyWith(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
