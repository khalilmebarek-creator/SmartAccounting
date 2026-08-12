import 'package:flutter/material.dart';

import '../../core/app_state.dart';
import '../../core/i18n.dart';
import '../../widgets/ratio_bar.dart';

/// Ordered ratio catalog aligned with the desktop engine keys. A ratio is
/// shown only when present in the loaded snapshot.
class RatioEntry {
  const RatioEntry(this.key, this.labelKey, this.barMax);
  final String key;
  final String labelKey;
  final double barMax;
}

const List<List<RatioEntry>> _catalog = [
  [
    RatioEntry('current_ratio', 'ratio_current_ratio', 3),
    RatioEntry('quick_ratio', 'ratio_quick_ratio', 2),
    RatioEntry('cash_ratio', 'ratio_cash_ratio', 1),
    RatioEntry('working_capital_ratio', 'ratio_working_capital_ratio', 2),
  ],
  [
    RatioEntry('gross_margin', 'ratio_gross_margin', 50),
    RatioEntry('net_profit_margin', 'ratio_net_profit_margin', 30),
    RatioEntry('operating_margin', 'ratio_operating_margin', 30),
    RatioEntry('roa', 'ratio_roa', 20),
    RatioEntry('roe', 'ratio_roe', 40),
    RatioEntry('return_on_capital', 'ratio_return_on_capital', 30),
  ],
  [
    RatioEntry('asset_turnover', 'ratio_asset_turnover', 3),
    RatioEntry('inventory_turnover', 'ratio_inventory_turnover', 12),
    RatioEntry('receivables_turnover', 'ratio_receivables_turnover', 12),
    RatioEntry('payables_turnover', 'ratio_payables_turnover', 12),
  ],
  [
    RatioEntry('debt_to_equity', 'ratio_debt_to_equity', 3),
    RatioEntry('debt_ratio', 'ratio_debt_ratio', 100),
    RatioEntry('interest_coverage', 'ratio_interest_coverage', 10),
  ],
  [
    RatioEntry('z_score', 'ratio_z_score', 4),
  ],
];

const List<String> _categoryKeys = [
  'cat_liquidity',
  'cat_profitability',
  'cat_efficiency',
  'cat_leverage',
  'ratio_z_score',
];

class RatiosScreen extends StatelessWidget {
  const RatiosScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    final lang = state.language;
    final snap = state.snapshot;

    if (snap == null) {
      return Center(child: Text(I18n.t(lang, 'empty_title')));
    }

    final children = <Widget>[];
    for (var i = 0; i < _catalog.length; i++) {
      final entries = _catalog[i]
          .where((e) => snap.ratios.containsKey(e.key))
          .toList();
      if (entries.isEmpty) continue;
      children.add(_CategoryHeader(label: I18n.t(lang, _categoryKeys[i])));
      children.addAll(entries.map((e) => RatioBar(
            label: I18n.t(lang, e.labelKey),
            value: snap.ratio(e.key),
            max: e.barMax,
          )));
    }
    if (children.isEmpty) {
      return Center(child: Text(I18n.t(lang, 'empty_title')));
    }

    return ListView(
      padding: const EdgeInsets.only(top: 12, bottom: 24),
      children: children,
    );
  }
}

class _CategoryHeader extends StatelessWidget {
  const _CategoryHeader({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Text(
        label,
        style: theme.textTheme.titleSmall?.copyWith(
          color: theme.colorScheme.primary,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
