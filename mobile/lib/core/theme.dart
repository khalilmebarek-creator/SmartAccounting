/// Material 3 theme for light and dark mode. RTL direction is driven by
/// [Directionality] set in `main.dart` from the selected language.
library;

import 'package:flutter/material.dart';

class AppTheme {
  AppTheme._();

  static const Color primary = Color(0xFF3B82F6);
  static const Color primaryDark = Color(0xFF90CAF9);

  static ThemeData light() => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: primary),
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.symmetric(vertical: 6, horizontal: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
            side: BorderSide(color: Color(0xFFE2E8F0)),
          ),
          color: Colors.white,
        ),
      );

  static ThemeData dark() => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primaryDark,
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF121212),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.symmetric(vertical: 6, horizontal: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
            side: BorderSide(color: Color(0x14FFFFFF)),
          ),
          color: Color(0xFF1E1E1E),
        ),
      );
}
