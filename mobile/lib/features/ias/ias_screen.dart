import 'package:flutter/material.dart';

import '../../core/app_state.dart';
import '../../core/i18n.dart';
import '../../data/snapshot_model.dart';

/// Compact IAS 1 summary read from the loaded snapshot (no new engine —
/// the desktop already computes the figures).
class IASScreen extends StatelessWidget {
  const IASScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    final lang = state.language;
    final snap = state.snapshot;

    if (snap == null) {
      return Center(child: Text(I18n.t(lang, 'empty_title')));
    }

    return ListView(
      padding: const EdgeInsets.only(top: 12, bottom: 24),
      children: [
        _Section(
          title: I18n.t(lang, 'ias_assets'),
          rows: _assets(snap, lang),
        ),
        _Section(
          title: I18n.t(lang, 'ias_liabilities'),
          rows: _liabilities(snap, lang),
        ),
        _Section(
          title: I18n.t(lang, 'ias_equity'),
          rows: _equity(snap, lang),
        ),
        _Section(
          title: I18n.t(lang, 'tab_ias'),
          rows: _income(snap, lang),
        ),
      ],
    );
  }

  List<(String, String)> _assets(SnapshotData snap, String lang) => [
        ('ias_assets', _money(snap.fin('current_assets'))),
        ('ias_total_assets', _money(snap.fin('total_assets'))),
      ].map((e) => (I18n.t(lang, e.$1), e.$2)).toList();

  List<(String, String)> _liabilities(SnapshotData snap, String lang) => [
        ('ias_liabilities', _money(snap.fin('current_liabilities'))),
        ('ias_total_liabilities', _money(snap.fin('total_liabilities'))),
      ].map((e) => (I18n.t(lang, e.$1), e.$2)).toList();

  List<(String, String)> _equity(SnapshotData snap, String lang) => [
        ('ias_total_equity', _money(snap.fin('equity'))),
      ].map((e) => (I18n.t(lang, e.$1), e.$2)).toList();

  List<(String, String)> _income(SnapshotData snap, String lang) => [
        ('ias_revenue', _money(snap.fin('revenue'))),
        ('ias_net_income', _money(snap.fin('net_income'))),
        ('ias_cash_ending', _money(snap.fin('cash'))),
      ].map((e) => (I18n.t(lang, e.$1), e.$2)).toList();

  String _money(double v) => v == 0 ? '—' : '${v.toStringAsFixed(2)} DA';
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.rows});

  final String title;
  final List<(String, String)> rows;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: theme.textTheme.titleSmall?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            ...rows.map((r) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(r.$1, style: theme.textTheme.bodyMedium),
                      Text(
                        r.$2,
                        style: theme.textTheme.bodyMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}
