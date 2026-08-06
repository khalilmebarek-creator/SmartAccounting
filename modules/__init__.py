# Modules Package
# ================

_LAZY_IMPORTS = {
    "CalculationEngine": ("modules.calculations", "CalculationEngine"),
    "DataValidator": ("modules.validation", "DataValidator"),
    "FinancialAnalyzer": ("modules.analysis", "FinancialAnalyzer"),
    "AuditEngine": ("modules.audit", "AuditEngine"),
    "ReportGenerator": ("modules.reporting", "ReportGenerator"),
    "DataImporter": ("modules.data_import", "DataImporter"),
    "TaxEngine": ("modules.tax", "TaxEngine"),
    "FinancialForecaster": ("modules.forecasting", "FinancialForecaster"),
    "BudgetPlanner": ("modules.budget", "BudgetPlanner"),
    "CostCenterAnalyzer": ("modules.cost_center", "CostCenterAnalyzer"),
    "BreakEvenAnalyzer": ("modules.breakeven", "BreakEvenAnalyzer"),
    "ReportTemplates": ("modules.report_templates", "ReportTemplates"),
    "report_templates": ("modules.report_templates", "report_templates"),
    "ScheduledBackup": ("modules.scheduled_backup", "ScheduledBackup"),
    "scheduled_backup": ("modules.scheduled_backup", "scheduled_backup"),
    "LedgerBook": ("modules.ledger", "LedgerBook"),
    "ledger_book": ("modules.ledger", "ledger_book"),
    "PartnerManager": ("modules.partners", "PartnerManager"),
    "partner_manager": ("modules.partners", "partner_manager"),
    "InvoiceManager": ("modules.invoicing", "InvoiceManager"),
    "invoice_manager": ("modules.invoicing", "invoice_manager"),
    "InventoryManager": ("modules.inventory", "InventoryManager"),
    "inventory_manager": ("modules.inventory", "inventory_manager"),
    "PayrollEngine": ("modules.payroll", "PayrollEngine"),
    "payroll_engine": ("modules.payroll", "payroll_engine"),
    "compute_irg": ("modules.payroll", "compute_irg"),
    "compute_salary": ("modules.payroll", "compute_salary"),
    "BudgetManager": ("modules.budgeting", "BudgetManager"),
    "budget_manager": ("modules.budgeting", "budget_manager"),
    "ProcurementManager": ("modules.procurement", "ProcurementManager"),
    "procurement_manager": ("modules.procurement", "procurement_manager"),
    "EInvoiceManager": ("modules.einvoicing", "EInvoiceManager"),
    "einvoice_manager": ("modules.einvoicing", "einvoice_manager"),
    "IFRSReporter": ("modules.ifrs_reporting", "IFRSReporter"),
    "BankSimulator": ("modules.bank_api", "BankSimulator"),
    "BankReconciler": ("modules.bank_api", "BankReconciler"),
    "MLForecaster": ("modules.ml_insights", "MLForecaster"),
    "AnomalyDetector": ("modules.ml_insights", "AnomalyDetector"),
    "RiskScorer": ("modules.ml_insights", "RiskScorer"),
    "AIPlatform": ("modules.ai_platform", "AIPlatform"),
}

__all__ = [
    'CalculationEngine',
    'DataValidator',
    'FinancialAnalyzer',
    'AuditEngine',
    'ReportGenerator',
    'DataImporter',
    'TaxEngine',
    'FinancialForecaster',
    'BudgetPlanner',
    'CostCenterAnalyzer',
    'BreakEvenAnalyzer',
    'ReportTemplates',
    'report_templates',
    'ScheduledBackup',
    'scheduled_backup',
    'LedgerBook',
    'ledger_book',
    'PartnerManager',
    'partner_manager',
    'InvoiceManager',
    'invoice_manager',
    'InventoryManager',
    'inventory_manager',
    'PayrollEngine',
    'payroll_engine',
    'compute_irg',
    'compute_salary',
    'BudgetManager',
    'budget_manager',
    'ProcurementManager',
    'procurement_manager',
    'EInvoiceManager',
    'einvoice_manager',
    'IFRSReporter',
    'BankSimulator',
    'BankReconciler',
    'MLForecaster',
    'AnomalyDetector',
    'RiskScorer',
    'AIPlatform',
]


def __getattr__(name):
    """تحميل كسول لوحدات modules الثقيلة (تحسين زمن الإقلاع والذاكرة)"""
    if name in _LAZY_IMPORTS:
        from importlib import import_module
        module_name, attr = _LAZY_IMPORTS[name]
        module = import_module(module_name)
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
