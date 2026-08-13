import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/app_logger.dart';
import 'package:smart_accounting_mobile/core/app_state.dart';
import 'package:smart_accounting_mobile/data/snapshot_model.dart';
import 'package:smart_accounting_mobile/features/ai_health/ai_health_screen.dart';
import 'package:smart_accounting_mobile/features/dashboard/dashboard_screen.dart';
import 'package:smart_accounting_mobile/features/ias/ias_screen.dart';
import 'package:smart_accounting_mobile/features/ratios/ratios_screen.dart';
import 'package:smart_accounting_mobile/features/tax_calendar/tax_calendar_screen.dart';

/// Golden screenshots for defense materials. Renders the five screens with
/// real Amiri Arabic glyphs (FontLoader) and a phone-like 360x780 viewport.
/// Run: flutter test --update-goldens test/screenshot_golden_test.dart
/// Output: test/goldens/*.png
Future<void> main() async {
  AppLogger.log.autoFlush = false;

  final regular = File('test/fixtures/fonts/Amiri-Regular.ttf')
      .readAsBytesSync()
      .buffer
      .asByteData();
  final bold = File('test/fixtures/fonts/Amiri-Bold.ttf')
      .readAsBytesSync()
      .buffer
      .asByteData();
  final loader = FontLoader('Amiri')
    ..addFont(Future.value(regular))
    ..addFont(Future.value(bold));
  await loader.load();

  testWidgets('screenshots', (tester) async {
    tester.view.physicalSize = const Size(1080, 2340);
    tester.view.devicePixelRatio = 3.0;
    addTearDown(tester.view.reset);

    Future<void> shot(Widget screen, String name) async {
      await tester.pumpWidget(_shell('ar', screen));
      await tester.pumpAndSettle();
      await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/$name.png'));
    }

    // Dashboard (full scroll top only — deterministic for goldens)
    await shot(const DashboardScreen(), 'dashboard_ar');
    await shot(const RatiosScreen(), 'ratios_ar');
    await shot(const AIHealthScreen(), 'ai_ar');
    await shot(TaxCalendarScreen(now: DateTime(2026, 8, 1)), 'tax_ar');
    await shot(const IASScreen(), 'ias_ar');
  });

  testWidgets('screenshots en', (tester) async {
    tester.view.physicalSize = const Size(1080, 2340);
    tester.view.devicePixelRatio = 3.0;
    addTearDown(tester.view.reset);

    Future<void> shot(Widget screen, String name) async {
      await tester.pumpWidget(_shell('en', screen));
      await tester.pumpAndSettle();
      await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/$name.png'));
    }

    await shot(const DashboardScreen(), 'dashboard_en');
    await shot(const RatiosScreen(), 'ratios_en');
    await shot(const AIHealthScreen(), 'ai_en');
    await shot(TaxCalendarScreen(now: DateTime(2026, 8, 1)), 'tax_en');
    await shot(const IASScreen(), 'ias_en');
  });
}

Widget _shell(String lang, Widget screen) {
  return AppController(
    initialLanguage: lang,
    child: _ShellHost(lang: lang, screen: screen),
  );
}

class _ShellHost extends StatefulWidget {
  const _ShellHost({required this.lang, required this.screen});

  final String lang;
  final Widget screen;

  @override
  State<_ShellHost> createState() => _ShellHostState();
}

class _ShellHostState extends State<_ShellHost> {
  bool _seeded = false;

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    if (!_seeded) {
      _seeded = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) state.onSnapshotLoaded(_demo());
      });
    }
    return Directionality(
      textDirection:
          widget.lang == 'ar' ? TextDirection.rtl : TextDirection.ltr,
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          fontFamily: 'Amiri',
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF3B82F6),
          ),
        ),
        home: Scaffold(body: widget.screen),
      ),
    );
  }
}

SnapshotData _demo() => SnapshotData(
      companyName: 'شركة الأمل للتجارة',
      companyNameFr: 'El Amel Trading Co',
      fiscalYear: 2024,
      companyNif: '098765432109876',
      companyRc: '16/00-0045678',
      companyLegalForm: 'SARL',
      companyAddress: 'حي النصر، الجزائر العاصمة',
      companyPhone: '+213 555 123 456',
      companyEmail: 'contact@elamel.dz',
      companyBank: 'BNA 0012345678',
      financialData: const {
        'revenue': 4500000.0,
        'net_income': 480000.0,
        'gross_profit': 1350000.0,
        'operating_expenses': 620000.0,
        'current_assets': 2100000.0,
        'total_assets': 7800000.0,
        'current_liabilities': 950000.0,
        'total_liabilities': 2900000.0,
        'equity': 4900000.0,
        'cash': 340000.0,
      },
      ratios: const {
        'current_ratio': 2.21,
        'quick_ratio': 1.6,
        'cash_ratio': 0.36,
        'gross_margin': 30.0,
        'net_profit_margin': 10.7,
        'operating_margin': 16.2,
        'roa': 6.2,
        'roe': 9.8,
        'return_on_capital': 8.5,
        'debt_to_equity': 0.59,
        'debt_ratio': 37.2,
        'interest_coverage': 7.4,
        'asset_turnover': 0.58,
        'inventory_turnover': 6.3,
        'receivables_turnover': 5.9,
        'payables_turnover': 7.1,
        'working_capital_ratio': 1.21,
        'z_score': 3.4,
      },
      taxObligations: const [
        {'tax_type': 'TVA', 'due_day': 20, 'month': 8, 'amount': 71250.0},
        {'tax_type': 'CNAS', 'due_day': 30, 'month': 8, 'amount': 24500.0},
        {'tax_type': 'IRG', 'due_day': 30, 'month': 8, 'amount': 18200.0},
      ],
    );
