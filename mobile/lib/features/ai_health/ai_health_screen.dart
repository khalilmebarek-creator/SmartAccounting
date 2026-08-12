import 'package:flutter/material.dart';

import '../../core/app_state.dart';
import '../../core/i18n.dart';
import '../../data/ai_health.dart';
import '../../widgets/risk_radar.dart';

class AIHealthScreen extends StatelessWidget {
  const AIHealthScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    final lang = state.language;
    final snap = state.snapshot;

    if (snap == null) {
      return Center(child: Text(I18n.t(lang, 'empty_title')));
    }

    final health = computeHealth(snap);
    final dims = <String, String>{
      'profitability': 'ai_dim_profitability',
      'liquidity': 'ai_dim_liquidity',
      'leverage': 'ai_dim_leverage',
      'efficiency': 'ai_dim_efficiency',
      'growth': 'ai_dim_growth',
      'stability': 'ai_dim_stability',
    };
    final risks = <String, String>{
      'liquidity_risk': 'ai_risk_liquidity',
      'leverage_risk': 'ai_risk_leverage',
      'profitability_risk': 'ai_risk_profitability',
      'efficiency_risk': 'ai_risk_efficiency',
      'growth_risk': 'ai_risk_growth',
      'solvency_risk': 'ai_risk_solvency',
    };

    return ListView(
      padding: const EdgeInsets.only(top: 12, bottom: 24),
      children: [
        _ScoreHeader(health: health, lang: lang),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(I18n.t(lang, 'health_score'),
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                ...dims.entries.map((e) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 110,
                            child: Text(I18n.t(lang, e.value)),
                          ),
                          Expanded(
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(6),
                              child: LinearProgressIndicator(
                                value: (health.breakdown[e.key] ?? 0) / _maxOf(e.key),
                                minHeight: 10,
                              ),
                            ),
                          ),
                          SizedBox(
                            width: 44,
                            child: Text(
                              (health.breakdown[e.key] ?? 0).toStringAsFixed(1),
                              textAlign: TextAlign.end,
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
        ),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text(I18n.t(lang, 'tab_ai'),
                    style: Theme.of(context).textTheme.titleMedium),
                RiskRadar(
                  values: [
                    health.riskRadar['liquidity_risk'] ?? 0,
                    health.riskRadar['leverage_risk'] ?? 0,
                    health.riskRadar['profitability_risk'] ?? 0,
                    health.riskRadar['efficiency_risk'] ?? 0,
                    health.riskRadar['growth_risk'] ?? 0,
                    health.riskRadar['solvency_risk'] ?? 0,
                  ],
                  labels: risks.entries
                      .map((e) => I18n.t(lang, e.value))
                      .toList(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  double _maxOf(String dim) => switch (dim) {
        'profitability' => 30,
        'liquidity' => 20,
        'leverage' => 15,
        'efficiency' => 15,
        _ => 10,
      };
}

class _ScoreHeader extends StatelessWidget {
  const _ScoreHeader({required this.health, required this.lang});

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
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
      child: Column(
        children: [
          Text(
            '${health.total.toStringAsFixed(0)}/100',
            style: theme.textTheme.displayMedium
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          Text(
            '${health.grade} · ${I18n.t(lang, gradeKey)}',
            style: theme.textTheme.titleMedium
                ?.copyWith(color: theme.colorScheme.primary),
          ),
        ],
      ),
    );
  }
}
