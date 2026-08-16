import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:file_picker/file_picker.dart';

import 'core/app_logger.dart';
import 'core/app_state.dart';
import 'core/i18n.dart';
import 'core/theme.dart';
import 'data/local_store.dart';
import 'data/snapshot_loader.dart';
import 'data/tax_notifier.dart';
import 'features/ai_health/ai_health_screen.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/ias/ias_screen.dart';
import 'features/ratios/ratios_screen.dart';
import 'features/tax_calendar/tax_calendar_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SmartAccountingApp());
}

class SmartAccountingApp extends StatefulWidget {
  const SmartAccountingApp({super.key});

  @override
  State<SmartAccountingApp> createState() => _SmartAccountingAppState();
}

class _SmartAccountingAppState extends State<SmartAccountingApp> {
  String? _initialLanguage;
  bool? _initialDarkMode;
  String? _cachedSnapshot;
  String? _prevSnapshot;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final lang = await LocalStore.loadLanguage();
    final dark = await LocalStore.loadDarkMode();
    final cached = await LocalStore.loadLastSnapshot();
    final prev = await LocalStore.loadPrevSnapshot();
    AppLogger.log.info('app',
        'bootstrap lang=$lang dark=$dark cached=${cached != null} prev=${prev != null}');
    if (!mounted) return;
    setState(() {
      _initialLanguage = lang;
      _initialDarkMode = dark;
      _cachedSnapshot = cached;
      _prevSnapshot = prev;
    });
  }

  @override
  Widget build(BuildContext context) {
    final lang = _initialLanguage;
    if (lang == null) {
      return const MaterialApp(
        home: Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }
    return AppController(
      initialLanguage: lang,
      child: _ThemedApp(
        initialDark: _initialDarkMode ?? false,
        cachedSnapshot: _cachedSnapshot,
        prevSnapshot: _prevSnapshot,
      ),
    );
  }
}

/// Reads [AppState] for live language/theme values; applies the theme and
/// localizations delegates.
class _ThemedApp extends StatefulWidget {
  const _ThemedApp({
    required this.initialDark,
    required this.cachedSnapshot,
    required this.prevSnapshot,
  });

  final bool initialDark;
  final String? cachedSnapshot;
  final String? prevSnapshot;

  @override
  State<_ThemedApp> createState() => _ThemedAppState();
}

class _ThemedAppState extends State<_ThemedApp> {
  bool _restored = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_restored && widget.cachedSnapshot != null) {
      _restored = true;
      final state = AppState.of(context);
      _restoreAll(state);
    }
  }

  Future<void> _restoreAll(AppState state) async {
    // Prev first, then current: the current restore must not shift away
    // the disk-restored prev (shift only happens when a current exists).
    if (widget.prevSnapshot != null && state.prevSnapshot == null) {
      await _restorePrev(widget.prevSnapshot!, state);
    }
    if (state.snapshot == null) {
      await _restoreCached(widget.cachedSnapshot!, state);
    }
  }

  Future<void> _restorePrev(String text, AppState state) async {
    final loader = SnapshotLoader();
    try {
      final snap = await loader.load(text);
      if (mounted) state.onPrevSnapshotLoaded(snap);
    } catch (err) {
      AppLogger.log.warn('app', 'prev snapshot unusable: $err');
    }
  }

  Future<void> _restoreCached(String text, AppState state) async {
    final loader = SnapshotLoader();
    try {
      final snap = await loader.load(text);
      if (mounted) state.onSnapshotLoaded(snap);
    } catch (err) {
      AppLogger.log.warn('app', 'cached snapshot unusable: $err');
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    return MaterialApp(
      title: I18n.t(state.language, 'app_title'),
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: state.darkMode ? ThemeMode.dark : ThemeMode.light,
      locale: Locale(state.language),
      supportedLocales: const [Locale('ar'), Locale('en'), Locale('fr')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      home: const MainShell(),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _tab = 0;

  static const List<Widget> _screens = [
    DashboardScreen(),
    RatiosScreen(),
    AIHealthScreen(),
    TaxCalendarScreen(),
    IASScreen(),
  ];

  Future<void> _scheduleTaxNotifications(AppState state, String lang) async {
    final snap = state.snapshot;
    if (snap == null || snap.taxObligations.isEmpty) return;
    final notifier = TaxNotifier();
    final plan = buildNotificationPlan(
      snap.taxObligations,
      titleTemplate: (taxType, daysLeft) =>
          '$taxType — ${I18n.format(I18n.t(lang, 'tax_days_left'), ['$daysLeft'])}',
      dueTitleTemplate: (taxType) =>
          I18n.formatMap(I18n.t(lang, 'tax_due_today'), {'n': taxType}),
      bodyTemplate: (taxType, amount) => amount == 0
          ? taxType
          : '$taxType: ${amount.toStringAsFixed(2)} DA',
    );
    await notifier.scheduleAll(plan);
  }

  Future<void> _loadFile(AppState state, String lang) async {
    // withData=true: cloud providers (Gmail/Drive) expose content URIs that
    // cannot be read via dart:io — requesting bytes avoids path issues.
    final result = await FilePicker.pickFiles(withData: true);
    if (result == null || result.files.isEmpty) return;
    final file = result.files.single;

    String fileText;
    try {
      final bytes = file.bytes;
      if (bytes != null && bytes.isNotEmpty) {
        fileText = utf8.decode(bytes);
      } else {
        final path = file.path;
        if (path == null) {
          AppLogger.log.warn('loader', 'picked file has no path and no bytes');
          if (mounted) _toast(context, I18n.t(lang, 'load_fail'));
          return;
        }
        fileText = await _readFile(path);
      }
      AppLogger.log.info('loader', 'picked file ${file.name}');
    } catch (err) {
      AppLogger.log.warn('loader', 'read failed: $err');
      if (mounted) _toast(context, I18n.t(lang, 'load_fail'));
      return;
    }

    final loader = SnapshotLoader();
    try {
      final snap = await loader.load(fileText);
      state.onSnapshotLoaded(snap);
      await LocalStore.saveLastSnapshot(fileText);
      if (mounted) _toast(context, I18n.t(lang, 'load_success'));
      await _scheduleTaxNotifications(state, lang);
    } on SnapshotError catch (err) {
      if (err.reason == 'passphrase_required') {
        if (!mounted) return;
        final pass = await _askPassword(context, lang);
        if (pass == null) return;
        try {
          final snap = await loader.load(fileText, passphrase: pass);
          state.onSnapshotLoaded(snap);
          await LocalStore.saveLastSnapshot(fileText);
          if (mounted) _toast(context, I18n.t(lang, 'load_success'));
          await _scheduleTaxNotifications(state, lang);
          return;
        } on SnapshotError {
          if (mounted) _toast(context, I18n.t(lang, 'password_error'));
          return;
        }
      }
      final message = switch (err.reason) {
        'invalid_json' || 'invalid_snapshot' => I18n.t(lang, 'load_invalid'),
        'decryption_failed' => I18n.t(lang, 'password_error'),
        _ => I18n.t(lang, 'load_fail'),
      };
      if (mounted) _toast(context, message);
    } catch (err) {
      AppLogger.log.error('loader', 'unexpected: $err');
      if (mounted) _toast(context, I18n.t(lang, 'load_fail'));
    }
  }

  Future<String?> _askPassword(BuildContext context, String lang) {
    final controller = TextEditingController();
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(I18n.t(lang, 'load_encrypted')),
        content: TextField(
          controller: controller,
          obscureText: true,
          decoration: InputDecoration(hintText: I18n.t(lang, 'password_hint')),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(I18n.t(lang, 'btn_cancel')),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(controller.text),
            child: Text(I18n.t(lang, 'btn_ok')),
          ),
        ],
      ),
    );
  }

  Future<String> _readFile(String path) async {
    final bytes = await File(path).readAsBytes();
    return utf8.decode(bytes);
  }

  void _toast(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), duration: const Duration(seconds: 2)),
    );
  }

  void _switchLanguage(AppState state, String lang) {
    state.onLanguageChanged(lang);
    LocalStore.saveLanguage(lang);
  }

  void _toggleTheme(AppState state) {
    final next = !state.darkMode;
    state.onThemeChanged(next);
    LocalStore.saveDarkMode(next);
  }

  @override
  Widget build(BuildContext context) {
    final state = AppState.of(context);
    final lang = state.language;
    return Directionality(
      textDirection: state.isRtl ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(I18n.t(lang, 'app_title')),
          actions: [
            IconButton(
              tooltip: I18n.t(lang, 'load_file'),
              icon: const Icon(Icons.folder_open),
              onPressed: () => _loadFile(state, lang),
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.language),
              onSelected: (l) => _switchLanguage(state, l),
              itemBuilder: (_) => const [
                PopupMenuItem(value: 'ar', child: Text('العربية')),
                PopupMenuItem(value: 'en', child: Text('English')),
                PopupMenuItem(value: 'fr', child: Text('Français')),
              ],
            ),
            IconButton(
              tooltip: state.darkMode ? 'Light' : 'Dark',
              icon: Icon(state.darkMode ? Icons.light_mode : Icons.dark_mode),
              onPressed: () => _toggleTheme(state),
            ),
          ],
        ),
        body: IndexedStack(index: _tab, children: _screens),
        bottomNavigationBar: NavigationBar(
          selectedIndex: _tab,
          onDestinationSelected: (i) => setState(() => _tab = i),
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.dashboard_outlined),
              selectedIcon: const Icon(Icons.dashboard),
              label: I18n.t(lang, 'tab_dashboard'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.percent_outlined),
              selectedIcon: const Icon(Icons.percent),
              label: I18n.t(lang, 'tab_ratios'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.monitor_heart_outlined),
              selectedIcon: const Icon(Icons.monitor_heart),
              label: I18n.t(lang, 'tab_ai'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.event_note_outlined),
              selectedIcon: const Icon(Icons.event_note),
              label: I18n.t(lang, 'tab_tax'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.description_outlined),
              selectedIcon: const Icon(Icons.description),
              label: I18n.t(lang, 'tab_ias'),
            ),
          ],
        ),
      ),
    );
  }
}
