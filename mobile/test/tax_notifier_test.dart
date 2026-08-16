import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/app_logger.dart';
import 'package:smart_accounting_mobile/data/tax_notifier.dart';

void main() {
  AppLogger.log.autoFlush = false;

  String title(String tax, int days) => '$tax in $days days';
  String dueTitle(String tax) => '$tax due today';
  String body(String tax, double amount) =>
      amount == 0 ? tax : '$tax: $amount';

  group('buildNotificationPlan', () {
    test('emits reminder (3 days before) AND due-day notification', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 20, 'month': 8, 'amount': 3958.33},
        ],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan.length, 2);
      expect(plan[0].when, DateTime(2026, 8, 17, 9));
      expect(plan[0].title, 'TVA in 3 days');
      expect(plan[1].when, DateTime(2026, 8, 20, 9));
      expect(plan[1].title, 'TVA due today');
    });

    test('reminder fires 09:00, due-day fires 09:00 on the due date', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'CNAS', 'due_day': 30, 'month': 8, 'amount': 10},
        ],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan[0].when, DateTime(2026, 8, 27, 9));
      expect(plan[1].when, DateTime(2026, 8, 30, 9));
    });

    test('rolls to next year when the due date already passed', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 5, 'month': 8, 'amount': 100},
        ],
        now: DateTime(2026, 8, 10),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan.length, 2);
      expect(plan[0].when, DateTime(2027, 8, 2, 9));
      expect(plan[1].when, DateTime(2027, 8, 5, 9));
    });

    test('reminder skipped when past but due-day still future fires', () {
      // due 5th; today 3rd → reminder (2nd) past, due-day (5th) future.
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 5, 'month': 8, 'amount': 100},
        ],
        now: DateTime(2026, 8, 3),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan.length, 1);
      expect(plan.single.title, 'TVA due today');
      expect(plan.single.when, DateTime(2026, 8, 5, 9));
    });

    test('fully passed window rolls to next year (both fire next year)', () {
      // due 5th; today 6th → the cycle rolls to next year by design.
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 5, 'month': 8, 'amount': 100},
        ],
        now: DateTime(2026, 8, 6),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan.length, 2);
      expect(plan[0].when, DateTime(2027, 8, 2, 9));
      expect(plan[1].when, DateTime(2027, 8, 5, 9));
    });

    test('handles multiple obligations with unique ids', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 20, 'month': 9, 'amount': 10},
          {'tax_type': 'CNAS', 'due_day': 30, 'month': 9, 'amount': 20},
        ],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan.length, 4);
      final ids = plan.map((n) => n.id).toSet();
      expect(ids.length, 4, reason: 'ids must be unique');
    });

    test('skips non-map entries safely', () {
      final plan = buildNotificationPlan(
        ['garbage', 42, null],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
        dueTitleTemplate: dueTitle,
      );
      expect(plan, isEmpty);
    });

    test('dueTitleTemplate defaults to titleTemplate with 0 days', () {
      final plan = buildNotificationPlan(
        [
          {'tax_type': 'TVA', 'due_day': 20, 'month': 8, 'amount': 10},
        ],
        now: DateTime(2026, 8, 1),
        titleTemplate: title,
        bodyTemplate: body,
      );
      expect(plan.length, 2);
      expect(plan[1].title, 'TVA in 0 days');
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
