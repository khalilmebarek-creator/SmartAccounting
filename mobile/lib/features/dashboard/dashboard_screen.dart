import 'package:flutter/material.dart';

import '../../core/app_state.dart';
import '../../core/i18n.dart';
import '../../data/ai_health.dart';
import '../../data/snapshot_model.dart';
import '../../widgets/kpi_card.dart';
import '../../widgets/kpi_trend_chart.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    final lang = state.language;
    final snap = state.snapshot;

    if (snap == null) {
      return _EmptyState(lang: lang);
    }

    final health = computeHealth(snap);
    final prev = state.prevSnapshot;
    return ListView(
      padding: const EdgeInsets.only(top: 12, bottom: 24),
      children: [
        _CompanyHeader(snap: snap, lang: lang),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Row(
            children: [
              KpiCard(
                label: I18n.t(lang, 'kpi_revenue'),
                value: _money(snap.fin('revenue')),
                delta: _delta(snap.fin('revenue'), prev?.fin('revenue')),
              ),
              KpiCard(
                label: I18n.t(lang, 'kpi_net_income'),
                value: _money(snap.fin('net_income')),
                delta: _delta(snap.fin('net_income'), prev?.fin('net_income')),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Row(
            children: [
              KpiCard(
                label: I18n.t(lang, 'kpi_gross_profit'),
                value: _money(snap.fin('gross_profit')),
                delta:
                    _delta(snap.fin('gross_profit'), prev?.fin('gross_profit')),
              ),
              KpiCard(
                label: I18n.t(lang, 'kpi_operating_expenses'),
                value: _money(snap.fin('operating_expenses')),
                delta: _delta(snap.fin('operating_expenses'),
                    prev?.fin('operating_expenses')),
              ),
            ],
          ),
        ),
        _TrendChartCard(snap: snap, lang: lang),
        Row(
          children: [
            _HealthCard(health: health, lang: lang),
            _ZScoreCard(snap: snap, lang: lang),
          ],
        ),
        _CompanyInfoCard(snap: snap, lang: lang),
      ],
    );
  }

  double? _delta(double current, double? previous) {
    if (previous == null || previous == 0) return null;
    return (current - previous) / previous.abs() * 100;
  }

  String _money(double v) => v == 0 ? '—' : '${v.toStringAsFixed(0)} DA';
}

class _TrendChartCard extends StatelessWidget {
  const _TrendChartCard({required this.snap, required this.lang});

  final SnapshotData snap;
  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(I18n.t(lang, 'kpi_chart'),
                style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            KpiTrendChart(
              labels: [
                I18n.t(lang, 'kpi_revenue'),
                I18n.t(lang, 'kpi_operating_expenses'),
                I18n.t(lang, 'kpi_gross_profit'),
              ],
              values: [
                snap.fin('revenue'),
                snap.fin('operating_expenses'),
                snap.fin('gross_profit'),
              ],
              color: theme.colorScheme.primary,
            ),
          ],
        ),
      ),
    );
  }
}

class _ZScoreCard extends StatelessWidget {
  const _ZScoreCard({required this.snap, required this.lang});

  final SnapshotData snap;
  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final zs = snap.ratio('z_score');
    final String statusKey;
    final Color statusColor;
    if (zs >= 3) {
      statusKey = 'z_safe_status';
      statusColor = const Color(0xFF22C55E);
    } else if (zs >= 1.8) {
      statusKey = 'z_grey_status';
      statusColor = const Color(0xFFF59E0B);
    } else {
      statusKey = 'z_danger_status';
      statusColor = const Color(0xFFEF4444);
    }
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(I18n.t(lang, 'z_status'),
                  style: theme.textTheme.titleMedium),
              const SizedBox(height: 8),
              Text(
                zs == 0 ? '—' : zs.toStringAsFixed(2),
                style: theme.textTheme.headlineMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                I18n.t(lang, statusKey),
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: statusColor, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CompanyInfoCard extends StatelessWidget {
  const _CompanyInfoCard({required this.snap, required this.lang});

  final SnapshotData snap;
  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final rows = <(String, String)>[
      (I18n.t(lang, 'company_nif'), snap.companyNif),
      (I18n.t(lang, 'company_rc'), snap.companyRc),
      (I18n.t(lang, 'company_legal_form'), snap.companyLegalForm),
      (I18n.t(lang, 'company_address'), snap.companyAddress),
      (I18n.t(lang, 'company_phone'), snap.companyPhone),
      (I18n.t(lang, 'company_email'), snap.companyEmail),
      (I18n.t(lang, 'company_bank'), snap.companyBank),
    ].where((r) => r.$2.isNotEmpty).toList();

    if (rows.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Theme(
        data: theme.copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          title: Text(I18n.t(lang, 'company_info'),
              style: theme.textTheme.titleMedium),
          childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          expandedCrossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final (label, value) in rows)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 150,
                      child: Text(
                        label,
                        style: theme.textTheme.bodySmall
                            ?.copyWith(color: theme.colorScheme.outline),
                      ),
                    ),
                    Expanded(
                      child: Text(value, style: theme.textTheme.bodyMedium),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _CompanyHeader extends StatelessWidget {
  const _CompanyHeader({required this.snap, required this.lang});

  final SnapshotData snap;
  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            snap.displayName(lang),
            style: theme.textTheme.titleLarge
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            '${I18n.t(lang, 'fiscal_year')}: ${snap.fiscalYear}',
            style: theme.textTheme.bodySmall
                ?.copyWith(color: theme.colorScheme.outline),
          ),
        ],
      ),
    );
  }
}

class _HealthCard extends StatelessWidget {
  const _HealthCard({required this.health, required this.lang});

  final HealthResult health;
  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final gradeKey = switch (health.grade) {
      'A' => 'grade_excellent',
      'B' => 'grade_good',
      'C' => 'grade_fair',
      'D' => 'grade_poor',
      _ => 'grade_critical',
    };
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(I18n.t(lang, 'health_score'),
                  style: theme.textTheme.titleMedium),
              const SizedBox(height: 6),
              Text(
                '${health.total.toStringAsFixed(0)}/100',
                style: theme.textTheme.headlineMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              Text(
                '${health.grade} · ${I18n.t(lang, gradeKey)}',
                style: theme.textTheme.bodyMedium
                    ?.copyWith(color: theme.colorScheme.primary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.lang});

  final String lang;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cloud_download_outlined,
              size: 64, color: theme.colorScheme.outline),
          const SizedBox(height: 16),
          Text(
            I18n.t(lang, 'empty_title'),
            style: theme.textTheme.titleLarge
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            I18n.t(lang, 'empty_body'),
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium
                ?.copyWith(color: theme.colorScheme.outline),
          ),
        ],
      ),
    );
  }
}
