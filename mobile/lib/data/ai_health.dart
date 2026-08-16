/// Financial health score — mirrors the desktop `modules/ai_platform.py`
/// formulas exactly so mobile and desktop show identical numbers.
library;

import 'snapshot_model.dart';

double _cap(double v, double lo, double hi) =>
    v < lo ? lo : (v > hi ? hi : v);

class HealthResult {
  HealthResult({
    required this.total,
    required this.grade,
    required this.breakdown,
    required this.riskRadar,
  });

  final double total;
  final String grade;
  final Map<String, double> breakdown;
  final Map<String, double> riskRadar;
}

HealthResult computeHealth(SnapshotData snap) {
  final roe = snap.ratio('roe');
  final npm = snap.ratio('net_profit_margin');
  final cr = snap.ratio('current_ratio');
  final qr = snap.ratio('quick_ratio');
  final de = snap.ratio('debt_to_equity');
  final dar = snap.ratio('debt_ratio');
  final invTurn = snap.ratio('inventory_turnover');
  final arTurn = snap.ratio('receivables_turnover');
  final zs = snap.ratio('z_score');
  final gp = snap.fin('gross_profit');
  final rev = snap.fin('revenue');
  final ni = snap.fin('net_income');

  // 1. profitability (30)
  final profitability = _cap(
      (_cap(roe, 0, 40) / 40) * 15 + (_cap(npm, 0, 30) / 30) * 15, 0, 30);
  // 2. liquidity (20)
  final liquidity = _cap(
      (_cap(cr, 0, 3) / 3) * 10 + (_cap(qr, 0, 2) / 2) * 10, 0, 20);
  // 3. leverage (15)
  final leverage = _cap(
      15 - (_cap(de, 0, 3) / 3) * 8 - (_cap(dar, 0, 1) / 1) * 7, 0, 15);
  // 4. efficiency (15)
  final efficiency = _cap(
      (_cap(invTurn, 0, 12) / 12) * 7 + (_cap(arTurn, 0, 12) / 12) * 8, 0, 15);
  // 5. growth (10)
  final gpm = rev > 0 ? gp / rev * 100 : 0.0;
  final nim = rev > 0 ? ni / rev * 100 : 0.0;
  final growth =
      _cap((_cap(gpm, 0, 50) / 50) * 5 + (_cap(nim, 0, 20) / 20) * 5, 0, 10);
  // 6. stability (10) — Z-Score
  final stability = _cap(_cap(zs, 0, 4) / 4 * 10, 0, 10);

  final total = profitability +
      liquidity +
      leverage +
      efficiency +
      growth +
      stability;

  return HealthResult(
    total: double.parse(total.toStringAsFixed(1)),
    grade: _grade(total),
    breakdown: {
      'profitability': _r(profitability),
      'liquidity': _r(liquidity),
      'leverage': _r(leverage),
      'efficiency': _r(efficiency),
      'growth': _r(growth),
      'stability': _r(stability),
    },
    riskRadar: {
      'liquidity_risk': _r(_cap(100 - (cr / 2) * 100, 0, 100)),
      'leverage_risk': _r(_cap((de / 3) * 100, 0, 100)),
      'profitability_risk': _r(_cap(100 - (roe / 30) * 100, 0, 100)),
      'efficiency_risk': _r(_cap(100 - (invTurn / 8) * 100, 0, 100)),
      'growth_risk': _r(_cap(100 - (npm / 20) * 100, 0, 100)),
      'solvency_risk': _r(_cap((1 - _cap(zs, 0, 3) / 3) * 100, 0, 100)),
    },
  );
}

double _r(double v) => double.parse(v.toStringAsFixed(1));

String _grade(double total) {
  if (total >= 80) return 'A';
  if (total >= 60) return 'B';
  if (total >= 40) return 'C';
  if (total >= 20) return 'D';
  return 'E';
}
