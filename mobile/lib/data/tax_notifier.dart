/// Tax deadline notifications.
///
/// Pure planning logic (testable) + a thin flutter_local_notifications
/// wrapper. Platform calls are best-effort: scheduling failures are logged
/// and never crash the app.
library;

import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;

import '../core/app_logger.dart';

/// One planned notification.
class TaxNotification {
  const TaxNotification({
    required this.id,
    required this.when,
    required this.title,
    required this.body,
  });

  final int id;
  final DateTime when;
  final String title;
  final String body;
}

typedef NotificationTitleBuilder = String Function(String taxType, int daysLeft);
typedef NotificationBodyBuilder = String Function(String taxType, double amount);
typedef NotificationDueTitleBuilder = String Function(String taxType);

/// Pure planner: builds the notification list for a set of obligations.
/// An obligation is a map like
/// `{"tax_type": "TVA", "due_day": 20, "month": 8, "amount": 3958.33}`.
/// Two notifications per obligation:
///  - a reminder 3 days before the due day at 09:00
///  - a due-day alert on the payment date itself at 09:00
/// (each skipped when its moment is already in the past).
List<TaxNotification> buildNotificationPlan(
  List<dynamic> obligations, {
  DateTime? now,
  required NotificationTitleBuilder titleTemplate,
  required NotificationBodyBuilder bodyTemplate,
  NotificationDueTitleBuilder? dueTitleTemplate,
}) {
  final current = now ?? DateTime.now();
  final dueTitle = dueTitleTemplate ?? ((tax) => titleTemplate(tax, 0));
  final plan = <TaxNotification>[];

  for (final entry in obligations) {
    if (entry is! Map) continue;
    final taxType = (entry['tax_type'] ?? '').toString();
    final dueDay = entry['due_day'] is num
        ? (entry['due_day'] as num).toInt()
        : 20;
    final month = entry['month'] is num
        ? (entry['month'] as num).toInt()
        : current.month;
    final amount = entry['amount'] is num
        ? (entry['amount'] as num).toDouble()
        : 0.0;

    var year = current.year;
    var due = DateTime(year, month, dueDay);
    if (due.isBefore(current)) {
      due = DateTime(year + 1, month, dueDay);
    }

    final baseId = taxType.hashCode ^ (month * 31);

    // 1) تذكير قبل 3 أيام
    final fireAtBase = due.subtract(const Duration(days: 3));
    final fireAt = DateTime(fireAtBase.year, fireAtBase.month, fireAtBase.day, 9);
    if (!fireAt.isBefore(current)) {
      plan.add(TaxNotification(
        id: baseId,
        when: fireAt,
        title: titleTemplate(taxType, 3),
        body: bodyTemplate(taxType, amount),
      ));
    }

    // 2) تنبيه يوم الاستحقاق نفسه
    final dueAt = DateTime(due.year, due.month, due.day, 9);
    if (!dueAt.isBefore(current)) {
      plan.add(TaxNotification(
        id: baseId + 100000,
        when: dueAt,
        title: dueTitle(taxType),
        body: bodyTemplate(taxType, amount),
      ));
    }
  }
  return plan;
}

/// Thin wrapper over the platform notification plugin.
class TaxNotifier {
  TaxNotifier({FlutterLocalNotificationsPlugin? plugin})
      : _plugin = plugin ?? FlutterLocalNotificationsPlugin();

  final FlutterLocalNotificationsPlugin _plugin;
  bool _initialized = false;

  /// Platform init + Android notification channel + permission request.
  /// Call once at app start; safe to call repeatedly.
  Future<void> init() async {
    if (_initialized) return;
    try {
      tzdata.initializeTimeZones();
      const settings = InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
      );
      await _plugin.initialize(settings: settings);
      const channel = AndroidNotificationChannel(
        'tax_deadlines',
        'Tax deadlines',
        description: 'Tax calendar due dates',
        importance: Importance.high,
      );
      await _plugin
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);
      await _plugin
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.requestNotificationsPermission();
      _initialized = true;
      AppLogger.log.info('notifier', 'initialized');
    } catch (err) {
      AppLogger.log.warn('notifier', 'init failed: $err');
    }
  }

  /// Schedule one notification per planned item (best-effort).
  Future<void> scheduleAll(List<TaxNotification> plan) async {
    await init();
    for (final n in plan) {
      try {
        final when = tz.TZDateTime.from(n.when, tz.local);
        await _plugin.zonedSchedule(
          id: n.id,
          title: n.title,
          body: n.body,
          scheduledDate: when,
          notificationDetails: const NotificationDetails(
            android: AndroidNotificationDetails(
              'tax_deadlines',
              'Tax deadlines',
              importance: Importance.high,
              priority: Priority.high,
            ),
          ),
          androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
        );
      } catch (err) {
        AppLogger.log.warn('notifier', 'schedule failed for ${n.title}: $err');
      }
    }
    AppLogger.log.info('notifier', 'scheduled ${plan.length} notifications');
  }
}
