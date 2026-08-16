/// Typed view over a desktop snapshot payload (same keys the desktop
/// `state` exports: company fields, financial_data, ratios, tax fields).
library;

class SnapshotData {
  SnapshotData({
    required this.companyName,
    this.companyNameFr = '',
    this.fiscalYear = 0,
    this.companyNif = '',
    this.companyRc = '',
    this.companyLegalForm = '',
    this.companyAddress = '',
    this.companyPhone = '',
    this.companyEmail = '',
    this.companyBank = '',
    required this.financialData,
    required this.ratios,
    this.taxObligations = const [],
  });

  final String companyName;
  final String companyNameFr;
  final int fiscalYear;
  final String companyNif;
  final String companyRc;
  final String companyLegalForm;
  final String companyAddress;
  final String companyPhone;
  final String companyEmail;
  final String companyBank;
  final Map<String, dynamic> financialData;
  final Map<String, dynamic> ratios;
  final List<dynamic> taxObligations;

  String displayName(String language) =>
      language == 'fr' && companyNameFr.isNotEmpty ? companyNameFr : companyName;

  double fin(String key) {
    final v = financialData[key];
    if (v is num) return v.toDouble();
    return 0.0;
  }

  double ratio(String key) {
    final v = ratios[key];
    if (v is num) return v.toDouble();
    return 0.0;
  }

  factory SnapshotData.fromPayload(Map<String, dynamic> payload) {
    final fin = payload['financial_data'];
    final ratios = payload['ratios'];
    final obligations = payload['tax_obligations'];
    return SnapshotData(
      companyName: (payload['company_name'] ?? '').toString(),
      companyNameFr: (payload['company_name_fr'] ?? '').toString(),
      fiscalYear: (payload['fiscal_year'] is num)
          ? (payload['fiscal_year'] as num).toInt()
          : 0,
      companyNif: (payload['company_nif'] ?? '').toString(),
      companyRc: (payload['company_rc'] ?? '').toString(),
      companyLegalForm: (payload['company_legal_form'] ?? '').toString(),
      companyAddress: (payload['company_address'] ?? '').toString(),
      companyPhone: (payload['company_phone'] ?? '').toString(),
      companyEmail: (payload['company_email'] ?? '').toString(),
      companyBank: (payload['company_bank_account'] ?? '').toString(),
      financialData: fin is Map<String, dynamic>
          ? fin
          : <String, dynamic>{},
      ratios: ratios is Map<String, dynamic> ? ratios : <String, dynamic>{},
      taxObligations:
          obligations is List ? List<dynamic>.unmodifiable(obligations) : const [],
    );
  }
}
