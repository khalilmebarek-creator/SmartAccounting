import 'package:flutter/material.dart';

import '../../core/app_state.dart';
import '../../core/i18n.dart';
import '../../data/ai_health.dart';
import '../../data/snapshot_model.dart';
import '../../widgets/kpi_card.dart';

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
              ),
              KpiCard(
                label: I18n.t(lang, 'kpi_net_income'),
                value: _money(snap.fin('net_income')),
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
              ),
              KpiCard(
                label: I18n.t(lang, 'kpi_operating_expenses'),
                value: _money(snap.fin('operating_expenses')),
              ),
            ],
          ),
        ),
        _HealthCard(health: health, lang: lang),
      ],
    );
  }

  String _money(double v) =>
      v == 0 ? '—' : '${v.toStringAsFixed(0)} DA';
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
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Column(
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
              ],
            ),
            const Spacer(),
            Text(
              '${health.grade} · ${I18n.t(lang, gradeKey)}',
              style: theme.textTheme.titleMedium
                  ?.copyWith(color: theme.colorScheme.primary),
            ),
          ],
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
