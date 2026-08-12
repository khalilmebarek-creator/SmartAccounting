/// Non-blocking logger: fixed-size in-memory ring buffer; file flush happens
/// on a background isolate so the UI thread never waits on disk I/O.
library;

import 'dart:async';
import 'dart:collection';
import 'dart:developer' as developer;
import 'dart:io';
import 'dart:isolate';

enum LogLevel { debug, info, warn, error }

/// Emit a single formatted log line like `2026-08-12T16:03:00  INFO  core  message`.
String _formatLine(DateTime ts, LogLevel level, String scope, String message) {
  String two(int v) => v.toString().padLeft(2, '0');
  final stamp =
      '${ts.year}-${two(ts.month)}-${two(ts.day)}T${two(ts.hour)}:${two(ts.minute)}:${two(ts.second)}';
  return '$stamp  ${level.name.toUpperCase().padRight(5)}  $scope  $message';
}

/// Logger singleton: `AppLogger.log.info('loader', 'msg')`.
class AppLogger {
  AppLogger._();

  static final AppLogger log = AppLogger._();

  final Queue<String> _buffer = Queue<String>();
  static const int _maxEntries = 500;
  final List<String Function(String)> _sinks = [];
  bool _flushScheduled = false;

  /// Minimum level actually emitted; anything below is dropped.
  LogLevel minLevel = LogLevel.debug;

  /// Auto file-flush scheduling; tests set this false to avoid pending
  /// timers in the widget-test harness.
  bool autoFlush = true;

  void _emit(LogLevel level, String scope, String message) {
    if (level.index < minLevel.index) return;
    final line = _formatLine(DateTime.now(), level, scope, message);
    if (_buffer.length >= _maxEntries) _buffer.removeFirst();
    _buffer.add(line);
    for (final sink in _sinks) {
      sink(line);
    }
    _scheduleFlush();
  }

  void debug(String scope, String message) => _emit(LogLevel.debug, scope, message);
  void info(String scope, String message) => _emit(LogLevel.info, scope, message);
  void warn(String scope, String message) => _emit(LogLevel.warn, scope, message);
  void error(String scope, String message) => _emit(LogLevel.error, scope, message);

  /// Attach an in-process sink (used by tests and debug UI).
  void addSink(String Function(String) sink) => _sinks.add(sink);
  void removeSink(String Function(String) sink) => _sinks.remove(sink);

  List<String> recentLines() => List.unmodifiable(_buffer);

  /// Schedule a file flush on a background isolate (coalesced, at most one
  /// pending flush at a time). Safe to call from the UI thread.
  void _scheduleFlush() {
    if (!autoFlush || _flushScheduled) return;
    _flushScheduled = true;
    unawaited(Future(() async {
      await Future<void>.delayed(const Duration(milliseconds: 400));
      final lines = recentLines();
      await flushToFile(lines);
      _flushScheduled = false;
    }));
  }

  /// Flush the given lines to the app documents dir. Runs in a separate
  /// isolate via [Isolate.run] so file I/O never blocks the UI isolate.
  static Future<void> flushToFile(List<String> lines, {String? directory}) async {
    if (lines.isEmpty) return;
    try {
      await Isolate.run(() async {
        final dir = directory ??
            Directory.systemTemp.path; // tests pass an explicit dir
        final file = File('$dir${Platform.pathSeparator}smartaccounting_mobile.log');
        final sink = file.openWrite(mode: FileMode.append);
        for (final line in lines) {
          sink.writeln(line);
        }
        await sink.flush();
        await sink.close();
      });
    } catch (err) {
      // Logging must never crash the app; a failed flush is best-effort.
      developer.log('AppLogger.flushToFile failed: $err',
          name: 'AppLogger', level: 1000);
    }
  }
}
