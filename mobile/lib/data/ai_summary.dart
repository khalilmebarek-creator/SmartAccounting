/// Executive summary + strategic recommendations — mirrors the desktop
/// `modules/ai_platform.py` rules exactly (same thresholds, same Arabic
/// wording) so mobile and desktop show identical conclusions.
library;

import '../core/i18n.dart';
import 'ai_health.dart';
import 'snapshot_model.dart';

class Recommendation {
  const Recommendation({
    required this.priority,
    required this.actionKey,
    required this.impactKey,
  });

  final String priority;
  final String actionKey;
  final String impactKey;
}

/// Renders a recommendation action in the requested language.
String renderAction(Recommendation rec, String lang) =>
    I18n.t(lang, rec.actionKey);

/// Renders a recommendation impact in the requested language.
String renderImpact(Recommendation rec, String lang) =>
    I18n.t(lang, rec.impactKey);

List<String> executiveSummary(
    SnapshotData snap, HealthResult health, String lang) {
  final roe = snap.ratio('roe');
  final cr = snap.ratio('current_ratio');
  final de = snap.ratio('debt_to_equity');
  final zs = snap.ratio('z_score');
  final rev = snap.fin('revenue');
  final ni = snap.fin('net_income');
  final oe = snap.fin('operating_expenses');

  String one(double v) => v.toStringAsFixed(1);
  String two(double v) => v.toStringAsFixed(2);

  final points = <String>[];
  points.add(I18n.formatMap(I18n.t(lang, 'sum_health'), {
    'n': health.total.toStringAsFixed(1),
    'g': health.grade,
  }));

  if (roe > 20) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_roe_strong'), {'n': one(roe)}));
  } else if (roe > 10) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_roe_ok'), {'n': one(roe)}));
  } else {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_roe_weak'), {'n': one(roe)}));
  }

  if (cr >= 2) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_cr_good'), {'n': one(cr)}));
  } else if (cr >= 1) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_cr_tight'), {'n': one(cr)}));
  } else {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_cr_danger'), {'n': one(cr)}));
  }

  if (de <= 1) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_de_ok'), {'n': two(de)}));
  } else if (de <= 2) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_de_mid'), {'n': two(de)}));
  } else {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_de_high'), {'n': two(de)}));
  }

  if (zs >= 3) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_zs_safe'), {'n': two(zs)}));
  } else if (zs >= 1.8) {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_zs_grey'), {'n': two(zs)}));
  } else {
    points.add(I18n.formatMap(I18n.t(lang, 'sum_zs_danger'), {'n': two(zs)}));
  }

  if (ni > 0 && oe > 0) {
    final margin = rev > 0 ? ni / rev * 100 : 0.0;
    points.add(I18n.formatMap(
        I18n.t(lang, margin > 10 ? 'sum_margin_above' : 'sum_margin_below'),
        {'n': one(margin)}));
  }

  return points;
}

List<Recommendation> strategicRecommendations(SnapshotData snap) {
  final recs = <Recommendation>[];
  final cr = snap.ratio('current_ratio');
  final de = snap.ratio('debt_to_equity');
  final roe = snap.ratio('roe');
  final zs = snap.ratio('z_score');
  final invTurn = snap.ratio('inventory_turnover');

  if (cr < 1.5) {
    recs.add(const Recommendation(
        priority: 'high',
        actionKey: 'rec_liquidity_action',
        impactKey: 'rec_liquidity_impact'));
  }
  if (de > 2) {
    recs.add(const Recommendation(
        priority: 'high',
        actionKey: 'rec_debt_action',
        impactKey: 'rec_debt_impact'));
  }
  if (zs < 2.5) {
    recs.add(const Recommendation(
        priority: 'high',
        actionKey: 'rec_structure_action',
        impactKey: 'rec_structure_impact'));
  }
  if (roe < 10) {
    recs.add(const Recommendation(
        priority: 'medium',
        actionKey: 'rec_profit_action',
        impactKey: 'rec_profit_impact'));
  }
  if (invTurn < 4) {
    recs.add(const Recommendation(
        priority: 'medium',
        actionKey: 'rec_inventory_action',
        impactKey: 'rec_inventory_impact'));
  }
  if (recs.isEmpty) {
    recs.add(const Recommendation(
        priority: 'low',
        actionKey: 'rec_stable_action',
        impactKey: 'rec_stable_impact'));
  }
  return recs;
}
