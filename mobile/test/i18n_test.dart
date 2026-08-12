import 'package:flutter_test/flutter_test.dart';
import 'package:smart_accounting_mobile/core/i18n.dart';

void main() {
  group('I18n language tables', () {
    test('all three languages have identical key sets', () {
      expect(I18n.en.keys.toSet(), equals(I18n.ar.keys.toSet()));
      expect(I18n.fr.keys.toSet(), equals(I18n.ar.keys.toSet()));
    });

    test('translate returns per-language strings', () {
      expect(I18n.t('ar', 'tab_dashboard'), 'لوحة القيادة');
      expect(I18n.t('en', 'tab_dashboard'), 'Dashboard');
      expect(I18n.t('fr', 'tab_dashboard'), 'Tableau de bord');
    });

    test('unknown key falls back to arabic then to the key itself', () {
      expect(I18n.t('ar', 'nope_missing'), 'nope_missing');
    });

    test('unknown language falls back to arabic', () {
      expect(I18n.t('xx', 'tab_ratios'), I18n.t('ar', 'tab_ratios'));
    });

    test('format replaces {n} placeholder', () {
      expect(I18n.format(I18n.t('en', 'tax_days_left'), ['7']), '7 days left');
    });

    test('format without values leaves placeholder intact', () {
      expect(I18n.format('abc {n} def', []), 'abc {n} def');
    });

    test('supportedLanguages lists ar en fr', () {
      expect(I18n.supportedLanguages, ['ar', 'en', 'fr']);
    });
  });
}
