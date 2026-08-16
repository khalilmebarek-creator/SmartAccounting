/// Local persistence:
///  - last loaded snapshot text cached as a file in the app documents dir
///  - language / theme preferences via shared_preferences
library;

import 'dart:io';

import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/app_logger.dart';

class LocalStore {
  LocalStore._();

  static const String _langKey = 'language';
  static const String _themeKey = 'dark_mode';
  static const String _cacheName = 'last_snapshot.json';
  static const String _prevCacheName = 'prev_snapshot.json';

  /// Persisted language, defaulting to `ar`.
  static Future<String> loadLanguage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_langKey) ?? 'ar';
    } catch (err) {
      AppLogger.log.warn('store', 'loadLanguage failed: $err');
      return 'ar';
    }
  }

  static Future<void> saveLanguage(String language) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_langKey, language);
    } catch (err) {
      AppLogger.log.warn('store', 'saveLanguage failed: $err');
    }
  }

  static Future<bool> loadDarkMode() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getBool(_themeKey) ?? false;
    } catch (err) {
      AppLogger.log.warn('store', 'loadDarkMode failed: $err');
      return false;
    }
  }

  static Future<void> saveDarkMode(bool dark) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_themeKey, dark);
    } catch (err) {
      AppLogger.log.warn('store', 'saveDarkMode failed: $err');
    }
  }

  /// Save the last snapshot text so the app reopens with data offline.
  /// The previous snapshot is shifted to the prev slot to enable
  /// period-over-period trend comparison.
  static Future<void> saveLastSnapshot(String fileText) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}${Platform.pathSeparator}$_cacheName');
      final prev = File('${dir.path}${Platform.pathSeparator}$_prevCacheName');
      if (await file.exists()) {
        await file.copy(prev.path);
      }
      await file.writeAsString(fileText, flush: true);
      AppLogger.log.info('store', 'snapshot cached');
    } catch (err) {
      AppLogger.log.warn('store', 'saveLastSnapshot failed: $err');
    }
  }

  /// Read the cached snapshot text, or null when absent/corrupt.
  static Future<String?> loadLastSnapshot() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}${Platform.pathSeparator}$_cacheName');
      if (!await file.exists()) return null;
      return await file.readAsString();
    } catch (err) {
      AppLogger.log.warn('store', 'loadLastSnapshot failed: $err');
      return null;
    }
  }

  /// Read the previous snapshot text (trend comparison), or null.
  static Future<String?> loadPrevSnapshot() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}${Platform.pathSeparator}$_prevCacheName');
      if (!await file.exists()) return null;
      return await file.readAsString();
    } catch (err) {
      AppLogger.log.warn('store', 'loadPrevSnapshot failed: $err');
      return null;
    }
  }
}
