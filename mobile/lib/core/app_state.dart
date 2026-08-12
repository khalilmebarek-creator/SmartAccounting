/// App-wide state exposed through an InheritedWidget (no external state
/// management): language, theme mode, and the currently loaded snapshot.
library;

import 'package:flutter/widgets.dart';

import '../data/snapshot_model.dart';
import 'app_logger.dart';

class AppState extends InheritedWidget {
  const AppState({
    super.key,
    required this.language,
    required this.darkMode,
    required this.snapshot,
    required this.prevSnapshot,
    required this.onLanguageChanged,
    required this.onThemeChanged,
    required this.onSnapshotLoaded,
    required this.onPrevSnapshotLoaded,
    required super.child,
  });

  final String language;
  final bool darkMode;
  final SnapshotData? snapshot;
  final SnapshotData? prevSnapshot;
  final ValueChanged<String> onLanguageChanged;
  final ValueChanged<bool> onThemeChanged;
  final ValueChanged<SnapshotData> onSnapshotLoaded;
  final ValueChanged<SnapshotData> onPrevSnapshotLoaded;

  bool get isRtl => language == 'ar';

  static AppState of(BuildContext context) {
    final state = context.dependOnInheritedWidgetOfExactType<AppState>();
    assert(state != null, 'AppState not found in widget tree');
    return state!;
  }

  @override
  bool updateShouldNotify(AppState oldWidget) =>
      language != oldWidget.language ||
      darkMode != oldWidget.darkMode ||
      snapshot != oldWidget.snapshot ||
      prevSnapshot != oldWidget.prevSnapshot;
}

/// Root controller owning the mutable state; rebuilds [AppState] on change.
class AppController extends StatefulWidget {
  const AppController({
    super.key,
    required this.initialLanguage,
    required this.child,
  });

  final String initialLanguage;
  final Widget child;

  @override
  State<AppController> createState() => _AppControllerState();
}

class _AppControllerState extends State<AppController> {
  late String _language;
  bool _darkMode = false;
  SnapshotData? _snapshot;
  SnapshotData? _prevSnapshot;

  @override
  void initState() {
    super.initState();
    _language = widget.initialLanguage;
    AppLogger.log.info('app', 'controller started (lang=$_language)');
  }

  void _setLanguage(String lang) {
    if (lang == _language) return;
    setState(() => _language = lang);
    AppLogger.log.info('app', 'language switched to $lang');
  }

  void _setTheme(bool dark) {
    if (dark == _darkMode) return;
    setState(() => _darkMode = dark);
    AppLogger.log.info('app', 'theme switched to ${dark ? 'dark' : 'light'}');
  }

  void _setSnapshot(SnapshotData snap) {
    setState(() {
      // In-session comparison: only shift when a current snapshot exists;
      // otherwise keep the prev snapshot restored from disk.
      if (_snapshot != null) _prevSnapshot = _snapshot;
      _snapshot = snap;
    });
    AppLogger.log.info(
        'app', 'snapshot loaded: ${snap.companyName} (fy ${snap.fiscalYear})');
  }

  void _setPrevSnapshot(SnapshotData snap) {
    setState(() => _prevSnapshot = snap);
    AppLogger.log.info('app', 'prev snapshot restored');
  }

  @override
  Widget build(BuildContext context) {
    return AppState(
      language: _language,
      darkMode: _darkMode,
      snapshot: _snapshot,
      prevSnapshot: _prevSnapshot,
      onLanguageChanged: _setLanguage,
      onThemeChanged: _setTheme,
      onSnapshotLoaded: _setSnapshot,
      onPrevSnapshotLoaded: _setPrevSnapshot,
      child: widget.child,
    );
  }
}
