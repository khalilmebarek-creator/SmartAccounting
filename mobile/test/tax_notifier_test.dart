import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/app_logger.dart';
import 'package:smart_accounting_mobile/data/tax_notifier.dart';

void main() {
  AppLogger.log.autoFlush = false;

  String title(String tax, int days) => '$tax in $days days';
  String body(String tax, double amount) =>
      amount == 0 ? tax : '$tax: $amount';

  group('buildNotificationPlan', () {
    test('plans a notification 3 days before the due day at 09:00', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 20, 'month': 8, 'amount': 3958.33},
        ],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
      );
      expect(plan.length, 1);
      expect(plan.single.when, DateTime(2026, 8, 17, 9));
      expect(plan.single.title, 'TVA in 3 days');
      expect(plan.single.body, 'TVA: 3958.33');
    });

    test('rolls to next year when the due date already passed', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 5, 'month': 8, 'amount': 100},
        ],
        now: DateTime(2026, 8, 10),
        titleTemplate: title,
        bodyTemplate: body,
      );
      expect(plan.length, 1);
      expect(plan.single.when, DateTime(2027, 8, 2, 9));
    });

    test('skips obligations whose fire time is already in the past', () {
      // due day 5 → fire day 2; today is the 3rd → past → skipped.
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 5, 'month': 8, 'amount': 100},
        ],
        now: DateTime(2026, 8, 3),
        titleTemplate: title,
        bodyTemplate: body,
      );
      expect(plan, isEmpty);
    });

    test('handles multiple obligations with stable ids', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 20, 'month': 9, 'amount': 10},
          {'tax_type': 'CNAS', 'due_day': 30, 'month': 9, 'amount': 20},
        ],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
      );
      expect(plan.length, 2);
      final ids = plan.map((n) => n.id).toSet();
      expect(ids.length, 2, reason: 'ids must be unique');
    });

    test('skips non-map entries safely', () {
      final plan = buildNotificationPlan(
        ['garbage', 42, null],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
      );
      expect(plan, isEmpty);
    });
  });

  group('TaxNotifier', () {
    test('scheduleAll is best-effort and never throws', () async {
      final notifier = TaxNotifier();
      await notifier.scheduleAll([
        TaxNotification(id: 1, when: _dummyDate(), title: 'T', body: 'B'),
      ]);
      // No exception = pass (platform channel simply isn't available in tests).
    });

    test('init is safe without platform channels', () async {
      final notifier = TaxNotifier();
      await notifier.init();
    });
  });
}

DateTime _dummyDate() => DateTime(2026, 9, 1, 9);
