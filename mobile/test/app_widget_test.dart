import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/app_logger.dart';
import 'package:smart_accounting_mobile/core/app_state.dart';
import 'package:smart_accounting_mobile/data/snapshot_model.dart';
import 'package:smart_accounting_mobile/main.dart';

Widget _harness(String lang) {
  return AppController(
    initialLanguage: lang,
    child: Builder(
      builder: (context) {
        final state = AppState.of(context);
        return MaterialApp(
          locale: Locale(state.language),
          theme: ThemeData(useMaterial3: true),
          home: const MainShell(),
        );
      },
    ),
  );
}

SnapshotData _demoSnapshot() => SnapshotData(
      companyName: 'Mobile Test Co',
      fiscalYear: 2024,
      financialData: const {
        'revenue': 250000.0,
        'net_income': 20000.0,
        'gross_profit': 50000.0,
        'operating_expenses': 25000.0,
        'current_assets': 150000.0,
        'total_assets': 600000.0,
        'current_liabilities': 60000.0,
        'total_liabilities': 220000.0,
        'equity': 380000.0,
        'cash': 12000.0,
      },
      ratios: const {
        'current_ratio': 2.5,
        'quick_ratio': 1.5,
        'cash_ratio': 0.2,
        'gross_margin': 20.0,
        'net_profit_margin': 8.0,
        'roe': 5.26,
        'debt_to_equity': 0.58,
        'z_score': 3.2,
      },
      taxObligations: const [
        {'tax_type': 'TVA', 'due_day': 20, 'month': 8, 'amount': 3958.33},
      ],
    );

void _load(AppState state, SnapshotData snap) {
  state.onSnapshotLoaded(snap);
}

void main() {
  AppLogger.log.autoFlush = false;

  testWidgets('renders empty state in arabic with RTL', (tester) async {
    await tester.pumpWidget(_harness('ar'));
    await tester.pumpAndSettle();

    expect(find.text('لا توجد بيانات بعد'), findsOneWidget);
    final direction = Directionality.of(
        tester.element(find.text('لا توجد بيانات بعد')));
    expect(direction, TextDirection.rtl);
  });

  testWidgets('empty state in english with LTR', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    expect(find.text('No data yet'), findsOneWidget);
  });

  testWidgets('all five tabs render', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    expect(find.text('Dashboard'), findsWidgets);
    expect(find.text('Ratios'), findsOneWidget);
    expect(find.text('AI Health'), findsOneWidget);
    expect(find.text('Tax'), findsOneWidget);
    expect(find.text('IAS'), findsOneWidget);
  });

  testWidgets('dashboard shows KPIs and company after load', (tester) async {
    await tester.pumpWidget(_harness('ar'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    expect(find.text('Mobile Test Co'), findsOneWidget);
    expect(find.text('الإيرادات'), findsWidgets);
  });

  testWidgets('ratios tab lists loaded ratio labels', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Ratios'));
    await tester.pumpAndSettle();

    expect(find.text('Current ratio'), findsOneWidget);
    expect(find.text('Return on equity'), findsOneWidget);
  });

  testWidgets('ai tab shows health score and radar', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    await tester.tap(find.text('AI Health'));
    await tester.pumpAndSettle();

    expect(find.textContaining('/100'), findsWidgets);
  });

  testWidgets('tax tab shows obligation', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Tax'));
    await tester.pumpAndSettle();

    expect(find.text('TVA'), findsOneWidget);
  });

  testWidgets('ias tab shows totals', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    await tester.tap(find.text('IAS'));
    await tester.pumpAndSettle();

    expect(find.text('Total assets'), findsOneWidget);
  });

  testWidgets('language switch rebuilds labels and flips direction',
      (tester) async {
    await tester.pumpWidget(_harness('ar'));
    await tester.pumpAndSettle();

    final state = AppState.of(tester.element(find.byType(MainShell)));
    state.onLanguageChanged('en');
    await tester.pumpAndSettle();

    expect(find.text('Dashboard'), findsWidgets);
    final direction = Directionality.of(
        tester.element(find.text('No data yet')));
    expect(direction, TextDirection.ltr);
  });

  testWidgets('theme toggle switches dark mode', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    var state = AppState.of(tester.element(find.byType(MainShell)));
    expect(state.darkMode, false);
    state.onThemeChanged(true);
    await tester.pumpAndSettle();
    state = AppState.of(tester.element(find.byType(MainShell)));
    expect(state.darkMode, true);
  });

  testWidgets('french empty state renders', (tester) async {
    await tester.pumpWidget(_harness('fr'));
    await tester.pumpAndSettle();
    expect(find.text('Aucune donnée'), findsOneWidget);
  });

  testWidgets('dashboard shows z-score card and trend chart after load',
      (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(find.text('Z-Score status'), 150);
    expect(find.text('Z-Score status'), findsOneWidget);
    expect(find.text('Revenue, expenses and profit'), findsOneWidget);
  });

  testWidgets('dashboard shows company information card', (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    final snap = SnapshotData(
      companyName: 'Mobile Test Co',
      fiscalYear: 2024,
      companyNif: '1234567890',
      companyRc: '01/00-123456',
      companyAddress: 'Test street',
      financialData: const {'revenue': 250000.0},
      ratios: const {'z_score': 3.2},
    );
    _load(AppState.of(tester.element(find.byType(MainShell))), snap);
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(find.text('Company information'), 150);
    expect(find.text('Company information'), findsOneWidget);
    await tester.tap(find.text('Company information'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text('1234567890'), 150);
    expect(find.text('1234567890'), findsOneWidget);
    expect(find.text('01/00-123456'), findsOneWidget);
  });

  testWidgets('kpi shows trend arrow when prev snapshot present',
      (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    final state = AppState.of(tester.element(find.byType(MainShell)));
    final prev = SnapshotData(
      companyName: 'Old',
      fiscalYear: 2023,
      financialData: const {'revenue': 200000.0},
      ratios: const {},
    );
    state.onPrevSnapshotLoaded(prev);
    await tester.pumpAndSettle();
    _load(state, _demoSnapshot());
    await tester.pumpAndSettle();

    expect(find.textContaining('▲'), findsWidgets);
    expect(find.textContaining('25.0%'), findsOneWidget);
  });

  testWidgets('ai health shows executive summary after load',
      (tester) async {
    await tester.pumpWidget(_harness('en'));
    await tester.pumpAndSettle();

    _load(AppState.of(tester.element(find.byType(MainShell))), _demoSnapshot());
    await tester.pumpAndSettle();

    await tester.tap(find.text('AI Health'));
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(find.text('📋 Executive summary'), 150);
    expect(find.text('📋 Executive summary'), findsOneWidget);
    expect(find.textContaining('Financial health score'), findsWidgets);
    await tester.scrollUntilVisible(find.text('💡 Strategic recommendations'), 150);
    expect(find.text('💡 Strategic recommendations'), findsOneWidget);
  });
}
