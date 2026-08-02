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
