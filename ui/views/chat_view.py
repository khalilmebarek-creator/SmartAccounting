# واجهة شات الذكاء الاصطناعي
# ============================

import html as html_mod
import json
import ssl
import time

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTextBrowser, QFrame,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import (QTextCursor)

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from utils.app_logger import get_logger

logger = get_logger("chat_view")

API_RATE_LIMIT_SECONDS = 2
MAX_MESSAGE_LENGTH = 2000


class AIWorker(QThread):
    """Worker لإرسال الطلبات في خيط منفصل"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, api_key, api_url, model):
        super().__init__()
        self.messages = messages
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def run(self):
        try:
            import urllib.request
            import urllib.error

            payload = json.dumps({
                "model": self.model,
                "messages": self.messages,
                "max_tokens": 1500,
                "temperature": 0.7,
            }).encode("utf-8")

            req = urllib.request.Request(
                self.api_url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )

            with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                self.response_received.emit(content)

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass
            self.error_occurred.emit(f"HTTP {e.code}: {e.reason}\n{body}")
        except Exception as e:
            self.error_occurred.emit(str(e))


class LocalFinancialAssistant:
    """مساعد مالي محلي — يعمل بدون إنترنت"""

    def __init__(self):
        self.lang = "ar"

    def respond(self, question):
        """الرد على سؤال مالي بناءً على البيانات المدخلة"""
        self.lang = state.language
        q = question.lower().strip()

        if not state.has_data():
            return self._msg("no_data")

        r = state.ratios
        d = state.financial_data

        if self._match(q, ["roe", "عائد", "حقوق الملكية", "return on equity"]):
            return self._roe_analysis(r)
        if self._match(q, ["roa", "عائد على الأصول", "return on assets"]):
            return self._roa_analysis(r)
        if self._match(q, ["سيولة", "current", "流动性", "liquidity", "流动比率"]):
            return self._liquidity_analysis(r)
        if self._match(q, ["ربحية", "profit", "margin", "هامش", "rentabilidad"]):
            return self._profitability_analysis(r, d)
        if self._match(q, ["دين", "debt", "leverag", "استدانة", "الرافعة"]):
            return self._debt_analysis(r, d)
        if self._match(q, ["تحليل", "analysis", "تحليل شامل", "ملخص", "summary", "overview"]):
            return self._full_analysis(r, d)
        if self._match(q, ["نصيحة", "advice", "تحسين", "improve", "توصية", "recommendation"]):
            return self._advice(r, d)
        if self._match(q, ["مقارنة", "compare", "مقارنة مع", "benchmark"]):
            return self._benchmark(r)
        if self._match(q, ["dupont", "ديبونت", "componen", "مكونات"]):
            return self._dupont_analysis()
        if self._match(q, ["margin", "هامش صافي", "net profit", "صافي الربح"]):
            return self._npm_analysis(r, d)
        if self._match(q, ["أصول", "assets", "ميزان", "balance"]):
            return self._balance_analysis(d)
        if self._match(q, ["مخزون", "inventory", "دوران المخزون"]):
            return self._inventory_analysis(r)
        if self._match(q, ["ذمم", "receivable", "مدينون"]):
            return self._receivables_analysis(r)

        return self._default_response(q)

    def _match(self, question, keywords):
        return any(kw in question for kw in keywords)

    def _fmt(self, val):
        if isinstance(val, (int, float)):
            return f"{val:,.2f}"
        return str(val)

    def _msg(self, key):
        msgs = {
            "no_data": {
                "ar": t("chat_offline_no_data"),
                "en": t("chat_offline_no_data_en")
            }
        }
        return msgs.get(key, {}).get(self.lang, msgs.get(key, {}).get("ar", ""))

    def _roe_analysis(self, r):
        roe = r.get("roe", 0)
        npm = r.get("net_profit_margin", 0)
        at = r.get("asset_turnover", 0)
        em = r.get("equity_multiplier", 0) or 0

        if self.lang == "ar":
            lines = [t("chat_offline_roe_title")]
            lines.append(f"🎯 ROE = {roe:.2f}%\n")

            if roe > 20:
                lines.append(t("chat_offline_roe_excellent"))
            elif roe > 10:
                lines.append(t("chat_offline_roe_good"))
            elif roe > 0:
                lines.append(t("chat_offline_roe_weak"))
            else:
                lines.append(t("chat_offline_roe_negative"))

            lines.append(f"\n{t('chat_offline_dupont_components')}:")
            lines.append(f"   • {t('chat_offline_npm_label')}: {npm:.2f}%")
            lines.append(f"   • {t('chat_offline_asset_turnover_label')}: {at:.2f}")
            if em:
                lines.append(f"   • Equity Multiplier: {em:.2f}")

            if npm < 10:
                lines.append(f"\n{t('chat_offline_npm_tip')}")
            if at < 1:
                lines.append(t("chat_offline_asset_turnover_tip"))

            return "\n".join(lines)
        else:
            lines = [f"📊 Return on Equity (ROE) Analysis\n"]
            lines.append(f"🎯 ROE = {roe:.2f}%\n")
            if roe > 20:
                lines.append("✅ Assessment: Excellent! Very high return indicating strong performance.")
            elif roe > 10:
                lines.append("⚠️ Assessment: Good. Acceptable return but can be improved.")
            elif roe > 0:
                lines.append("⚠️ Assessment: Weak. Low return needs improvement.")
            else:
                lines.append("❌ Assessment: Negative! The company is losing money.\n")
            lines.append(f"\n📐 DuPont Components:")
            lines.append(f"   • Net Profit Margin: {npm:.2f}%")
            lines.append(f"   • Asset Turnover: {at:.2f}")
            if em:
                lines.append(f"   • Equity Multiplier: {em:.2f}")
            return "\n".join(lines)

    def _roa_analysis(self, r):
        roa = r.get("roa", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_roa_title")]
            lines.append(f"🎯 ROA = {roa:.2f}%\n")
            if roa > 10:
                lines.append(t("chat_offline_roa_excellent"))
            elif roa > 5:
                lines.append(t("chat_offline_roa_good"))
            else:
                lines.append(t("chat_offline_roa_weak"))
            lines.append(f"\n{t('chat_offline_roa_note')}")
            return "\n".join(lines)
        else:
            lines = [f"📊 Return on Assets (ROA) Analysis\n"]
            lines.append(f"🎯 ROA = {roa:.2f}%\n")
            if roa > 10:
                lines.append("✅ Excellent! Company uses assets efficiently.")
            elif roa > 5:
                lines.append("⚠️ Good — room for improvement in asset utilization.")
            else:
                lines.append("❌ Weak — assets aren't generating sufficient returns.")
            return "\n".join(lines)

    def _liquidity_analysis(self, r):
        cr = r.get("current_ratio", 0)
        qr = r.get("quick_ratio", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_liquidity_title")]
            lines.append(f"📊 {t('chat_offline_current_ratio_label')}: {cr:.2f}")
            lines.append(f"📊 {t('chat_offline_quick_ratio_label')}: {qr:.2f}\n")
            if cr > 2:
                lines.append(t("chat_offline_liquidity_excellent"))
            elif cr > 1:
                lines.append(t("chat_offline_liquidity_acceptable"))
            else:
                lines.append(t("chat_offline_liquidity_danger"))
            if qr < 1:
                lines.append(f"\n{t('chat_offline_quick_ratio_tip')}")
            return "\n".join(lines)
        else:
            lines = [f"💧 Liquidity Analysis\n"]
            lines.append(f"📊 Current Ratio: {cr:.2f}")
            lines.append(f"📊 Quick Ratio: {qr:.2f}\n")
            if cr > 2:
                lines.append("✅ Excellent liquidity — company can easily meet obligations.")
            elif cr > 1:
                lines.append("⚠️ Acceptable — but caution needed for potential shortfalls.")
            else:
                lines.append("❌ Danger! Low liquidity — company may struggle to pay debts.")
            return "\n".join(lines)

    def _profitability_analysis(self, r, d):
        gpm = r.get("gross_profit_margin", 0)
        npm = r.get("net_profit_margin", 0)
        rev = d.get("revenue", 0)
        cogs = d.get("cost_of_goods_sold", 0)
        ni = d.get("net_income", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_profit_title")]
            lines.append(f"📊 {t('chat_offline_gpm_label')}: {gpm:.2f}%")
            lines.append(f"📊 {t('chat_offline_npm_label')}: {npm:.2f}%")
            lines.append(f"💰 {t('chat_offline_revenue_label')}: {self._fmt(rev)}")
            lines.append(f"📦 {t('chat_offline_cogs_label')}: {self._fmt(cogs)}")
            lines.append(f"💵 {t('chat_offline_net_income_label')}: {self._fmt(ni)}\n")
            if gpm > 50:
                lines.append(t("chat_offline_gpm_excellent"))
            elif gpm > 30:
                lines.append(t("chat_offline_gpm_acceptable"))
            else:
                lines.append(t("chat_offline_gpm_low"))
            if npm < 10:
                lines.append(f"\n{t('chat_offline_profit_tip')}")
            return "\n".join(lines)
        else:
            lines = [f"💰 Profitability Analysis\n"]
            lines.append(f"📊 Gross Margin: {gpm:.2f}%")
            lines.append(f"📊 Net Margin: {npm:.2f}%\n")
            if gpm > 50:
                lines.append("✅ Excellent gross margin — pricing is strong.")
            elif gpm > 30:
                lines.append("⚠️ Acceptable — room to reduce costs.")
            else:
                lines.append("❌ Low margin — costs are high relative to revenue.")
            return "\n".join(lines)

    def _debt_analysis(self, r, d):
        de = r.get("debt_to_equity", 0)
        dr = r.get("debt_ratio", 0)
        tl = d.get("total_liabilities", 0)
        eq = d.get("equity", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_debt_title")]
            lines.append(f"📊 {t('chat_offline_de_label')}: {de:.2f}")
            lines.append(f"📊 {t('chat_offline_debt_ratio_label')}: {dr:.2f}%")
            lines.append(f"💳 {t('chat_offline_liabilities_label')}: {self._fmt(tl)}")
            lines.append(f"💰 {t('chat_offline_equity_label')}: {self._fmt(eq)}\n")
            if de < 1:
                lines.append(t("chat_offline_debt_low"))
            elif de < 2:
                lines.append(t("chat_offline_debt_moderate"))
            else:
                lines.append(t("chat_offline_debt_high"))
            return "\n".join(lines)
        else:
            lines = [f"📊 Debt Analysis\n"]
            lines.append(f"📊 Debt/Equity: {de:.2f}")
            lines.append(f"📊 Debt Ratio: {dr:.2f}%\n")
            if de < 1:
                lines.append("✅ Low debt — company relies on equity financing.")
            elif de < 2:
                lines.append("⚠️ Moderate debt — monitor closely.")
            else:
                lines.append("❌ High debt — company faces financing risks.")
            return "\n".join(lines)

    def _full_analysis(self, r, d):
        if self.lang == "ar":
            lines = [t("chat_offline_full_title").format(name=state.company_name)]
            lines.append(f"📅 {t('chat_offline_fiscal_year')}: {state.fiscal_year}\n")
            lines.append(f"{'='*45}\n")
            lines.append(f"💰 {t('chat_offline_revenue_label')}: {self._fmt(d.get('revenue', 0))}")
            lines.append(f"💵 {t('chat_offline_net_income_label')}: {self._fmt(d.get('net_income', 0))}")
            lines.append(f"🏦 {t('chat_offline_assets_label')}: {self._fmt(d.get('total_assets', 0))}")
            lines.append(f"💳 {t('chat_offline_liabilities_label')}: {self._fmt(d.get('total_liabilities', 0))}")
            lines.append(f"💰 {t('chat_offline_equity_label')}: {self._fmt(d.get('equity', 0))}\n")
            lines.append(f"📈 {t('chat_offline_key_ratios_label')}:")
            lines.append(f"   • ROE: {r.get('roe', 0):.2f}%")
            lines.append(f"   • ROA: {r.get('roa', 0):.2f}%")
            lines.append(f"   • {t('chat_offline_current_ratio_label')}: {r.get('current_ratio', 0):.2f}")
            lines.append(f"   • {t('chat_offline_npm_label')}: {r.get('net_profit_margin', 0):.2f}%")
            lines.append(f"   • {t('chat_offline_de_label')}: {r.get('debt_to_equity', 0):.2f}")
            lines.append(f"\n{t('chat_offline_full_hint')}")
            return "\n".join(lines)
        else:
            lines = [f"📊 Full Financial Analysis for '{state.company_name}'\n"]
            lines.append(f"📅 Fiscal Year: {state.fiscal_year}\n")
            lines.append(f"💰 Revenue: {self._fmt(d.get('revenue', 0))}")
            lines.append(f"💵 Net Income: {self._fmt(d.get('net_income', 0))}")
            lines.append(f"🏦 Total Assets: {self._fmt(d.get('total_assets', 0))}")
            lines.append(f"💳 Total Liabilities: {self._fmt(d.get('total_liabilities', 0))}")
            lines.append(f"💰 Equity: {self._fmt(d.get('equity', 0))}\n")
            lines.append(f"📈 Key Ratios:")
            lines.append(f"   • ROE: {r.get('roe', 0):.2f}%")
            lines.append(f"   • ROA: {r.get('roa', 0):.2f}%")
            lines.append(f"   • Current Ratio: {r.get('current_ratio', 0):.2f}")
            lines.append(f"   • Net Margin: {r.get('net_profit_margin', 0):.2f}%")
            lines.append(f"   • Debt/Equity: {r.get('debt_to_equity', 0):.2f}")
            lines.append(f"\n💡 Ask me about any specific ratio for more detail!")
            return "\n".join(lines)

    def _advice(self, r, d):
        roe = r.get("roe", 0)
        cr = r.get("current_ratio", 0)
        npm = r.get("net_profit_margin", 0)
        de = r.get("debt_to_equity", 0)
        tips = []
        if self.lang == "ar":
            lines = [t("chat_offline_advice_title").format(name=state.company_name)]
            if npm < 10:
                lines.append(t("chat_offline_advice_npm_title"))
                lines.append(f"   • {t('chat_offline_advice_npm_tip1')}")
                lines.append(f"   • {t('chat_offline_advice_npm_tip2')}\n")
            if cr < 1.5:
                lines.append(t("chat_offline_advice_liquidity_title"))
                lines.append(f"   • {t('chat_offline_advice_liquidity_tip1')}")
                lines.append(f"   • {t('chat_offline_advice_liquidity_tip2')}\n")
            if de > 2:
                lines.append(t("chat_offline_advice_debt_title"))
                lines.append(f"   • {t('chat_offline_advice_debt_tip1')}")
                lines.append(f"   • {t('chat_offline_advice_debt_tip2')}\n")
            if roe < 10:
                lines.append(t("chat_offline_advice_roe_title"))
                lines.append(f"   • {t('chat_offline_advice_roe_tip1')}")
                lines.append(f"   • {t('chat_offline_advice_roe_tip2')}\n")
            if not tips and len(lines) == 1:
                lines.append(t("chat_offline_advice_good"))
            return "\n".join(lines) if len(lines) > 1 else lines[0] + f"\n{t('chat_offline_advice_good')}"
        else:
            lines = [f"💡 Financial Advice for '{state.company_name}'\n"]
            if npm < 10:
                lines.append("1️⃣ Improve Net Profit Margin:")
                lines.append("   • Cut unnecessary costs")
                lines.append("   • Review pricing strategy\n")
            if cr < 1.5:
                lines.append("2️⃣ Improve Liquidity:")
                lines.append("   • Increase current assets")
                lines.append("   • Reduce current liabilities\n")
            if de > 2:
                lines.append("3️⃣ Reduce Debt:")
                lines.append("   • Improve financing structure")
                lines.append("   • Focus on generating profits to pay debts\n")
            if roe < 10:
                lines.append("4️⃣ Improve ROE:")
                lines.append("   • Increase net income")
                lines.append("   • Improve asset efficiency\n")
            if len(lines) == 1:
                lines.append("✅ Overall performance is good! Keep it up.")
            return "\n".join(lines)

    def _benchmark(self, r):
        if self.lang == "ar":
            lines = [t("chat_offline_benchmark_title")]
            cr = r.get("current_ratio", 0)
            npm = r.get("net_profit_margin", 0)
            roe = r.get("roe", 0)
            de = r.get("debt_to_equity", 0)
            lines.append(f"{t('chat_offline_current_ratio_label')}: {cr:.2f} ({t('chat_offline_benchmark')}: 1.5-2.0)")
            lines.append(f"  {t('chat_offline_benchmark_good') if 1.5 <= cr <= 3 else t('chat_offline_benchmark_outside')}\n")
            lines.append(f"{t('chat_offline_npm_label')}: {npm:.2f}% ({t('chat_offline_benchmark')}: 10-20%)")
            lines.append(f"  {t('chat_offline_benchmark_good') if 10 <= npm <= 30 else t('chat_offline_benchmark_outside')}\n")
            lines.append(f"ROE: {roe:.2f}% ({t('chat_offline_benchmark')}: 15-25%)")
            lines.append(f"  {t('chat_offline_benchmark_good') if 15 <= roe <= 30 else t('chat_offline_benchmark_outside')}\n")
            lines.append(f"{t('chat_offline_de_label')}: {de:.2f} ({t('chat_offline_benchmark')}: 0.5-1.5)")
            lines.append(f"  {t('chat_offline_benchmark_good') if 0.5 <= de <= 2 else t('chat_offline_benchmark_outside')}")
            return "\n".join(lines)
        else:
            lines = [f"📊 Benchmark Comparison\n"]
            cr = r.get("current_ratio", 0)
            npm = r.get("net_profit_margin", 0)
            roe = r.get("roe", 0)
            de = r.get("debt_to_equity", 0)
            lines.append(f"Current Ratio: {cr:.2f} (Benchmark: 1.5-2.0)")
            lines.append(f"  {'✅ Good' if 1.5 <= cr <= 3 else '⚠️ Outside benchmark'}\n")
            lines.append(f"Net Margin: {npm:.2f}% (Benchmark: 10-20%)")
            lines.append(f"  {'✅ Good' if 10 <= npm <= 30 else '⚠️ Outside benchmark'}\n")
            lines.append(f"ROE: {roe:.2f}% (Benchmark: 15-25%)")
            lines.append(f"  {'✅ Good' if 15 <= roe <= 30 else '⚠️ Outside benchmark'}\n")
            lines.append(f"Debt/Equity: {de:.2f} (Benchmark: 0.5-1.5)")
            lines.append(f"  {'✅ Good' if 0.5 <= de <= 2 else '⚠️ Outside benchmark'}")
            return "\n".join(lines)

    def _dupont_analysis(self):
        dp = state.dupont
        if not dp:
            if self.lang == "ar":
                return t("chat_offline_dupont_no_data")
            return "⚠️ No DuPont data available. Calculate ratios first."

        if self.lang == "ar":
            lines = [t("chat_offline_dupont_title")]
            lines.append(f"📐 {t('chat_offline_dupont_formula')}")
            lines.append(f"🎯 {dp.get('roe', 0):.2f}% = {dp.get('net_profit_margin', 0):.2f}% × {dp.get('asset_turnover', 0):.2f} × {dp.get('equity_multiplier', 0):.2f}\n")
            lines.append(f"💡 {t('chat_offline_dupont_biggest')}:")
            components = [
                (t("chat_offline_npm_label"), dp.get('net_profit_margin', 0)),
                (t("chat_offline_asset_turnover_label"), dp.get('asset_turnover', 0)),
                (t("chat_offline_equity_multiplier_label"), dp.get('equity_multiplier', 0)),
            ]
            biggest = max(components, key=lambda x: x[1])
            lines.append(f"   → {biggest[0]} = {biggest[1]:.2f}")
            return "\n".join(lines)
        else:
            lines = [f"🔄 Detailed DuPont Analysis\n"]
            lines.append(f"📐 ROE = NPM × Asset Turnover × Equity Multiplier")
            lines.append(f"🎯 {dp.get('roe', 0):.2f}% = {dp.get('net_profit_margin', 0):.2f}% × {dp.get('asset_turnover', 0):.2f} × {dp.get('equity_multiplier', 0):.2f}")
            return "\n".join(lines)

    def _npm_analysis(self, r, d):
        npm = r.get("net_profit_margin", 0)
        rev = d.get("revenue", 0)
        ni = d.get("net_income", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_npm_title")]
            lines.append(f"📊 {t('chat_offline_margin_label')}: {npm:.2f}%")
            lines.append(f"💰 {t('chat_offline_revenue_label')}: {self._fmt(rev)}")
            lines.append(f"💵 {t('chat_offline_net_income_label')}: {self._fmt(ni)}\n")
            if npm > 20:
                lines.append(t("chat_offline_npm_excellent"))
            elif npm > 10:
                lines.append(t("chat_offline_npm_good"))
            else:
                lines.append(t("chat_offline_npm_low"))
            return "\n".join(lines)
        else:
            lines = [f"💰 Net Profit Margin Analysis\n"]
            lines.append(f"📊 Margin: {npm:.2f}%")
            lines.append(f"💰 Revenue: {self._fmt(rev)}")
            lines.append(f"💵 Net Income: {self._fmt(ni)}\n")
            if npm > 20:
                lines.append("✅ Excellent! Company retains over 20% as net profit.")
            elif npm > 10:
                lines.append("⚠️ Good — but room to improve efficiency.")
            else:
                lines.append("❌ Low — operating costs consume too much revenue.")
            return "\n".join(lines)

    def _balance_analysis(self, d):
        ta = d.get("total_assets", 0)
        tl = d.get("total_liabilities", 0)
        eq = d.get("equity", 0)
        ratio = (tl / ta * 100) if ta > 0 else 0
        if self.lang == "ar":
            lines = [t("chat_offline_balance_title")]
            lines.append(f"🏦 {t('chat_offline_total_assets_label')}: {self._fmt(ta)}")
            lines.append(f"💳 {t('chat_offline_liabilities_label')}: {self._fmt(tl)} ({ratio:.1f}%)")
            lines.append(f"💰 {t('chat_offline_equity_label')}: {self._fmt(eq)} ({100-ratio:.1f}%)\n")
            if ratio < 50:
                lines.append(t("chat_offline_balance_healthy"))
            elif ratio < 70:
                lines.append(t("chat_offline_balance_moderate"))
            else:
                lines.append(t("chat_offline_balance_high"))
            return "\n".join(lines)
        else:
            lines = [f"🏦 Balance Sheet Analysis\n"]
            lines.append(f"🏦 Total Assets: {self._fmt(ta)}")
            lines.append(f"💳 Liabilities: {self._fmt(tl)} ({ratio:.1f}%)")
            lines.append(f"💰 Equity: {self._fmt(eq)} ({100-ratio:.1f}%)\n")
            if ratio < 50:
                lines.append("✅ Healthy financing structure — equity is dominant.")
            else:
                lines.append("⚠️ High liability ratio — monitor closely.")
            return "\n".join(lines)

    def _inventory_analysis(self, r):
        it = r.get("inventory_turnover", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_inventory_title")]
            lines.append(f"📊 {t('chat_offline_inventory_turnover_label')}: {it:.2f}\n")
            if it > 8:
                lines.append(t("chat_offline_inventory_excellent"))
            elif it > 4:
                lines.append(t("chat_offline_inventory_acceptable"))
            else:
                lines.append(t("chat_offline_inventory_slow"))
            return "\n".join(lines)
        else:
            lines = [f"📦 Inventory Analysis\n"]
            lines.append(f"📊 Inventory Turnover: {it:.2f}\n")
            if it > 8:
                lines.append("✅ Excellent turnover — inventory sells quickly.")
            elif it > 4:
                lines.append("⚠️ Acceptable — room to improve inventory management.")
            else:
                lines.append("❌ Slow turnover — excess stagnant inventory.")
            return "\n".join(lines)

    def _receivables_analysis(self, r):
        rt = r.get("receivables_turnover", 0)
        dso = r.get("days_sales_outstanding", 0)
        if self.lang == "ar":
            lines = [t("chat_offline_receivables_title")]
            lines.append(f"📊 {t('chat_offline_receivables_turnover_label')}: {rt:.2f}")
            lines.append(f"📅 {t('chat_offline_dso_label')}: {dso:.0f} {t('chat_offline_days')}\n")
            if dso < 30:
                lines.append(t("chat_offline_receivables_excellent"))
            elif dso < 60:
                lines.append(t("chat_offline_receivables_acceptable"))
            else:
                lines.append(t("chat_offline_receivables_slow"))
            return "\n".join(lines)
        else:
            lines = [f"📋 Receivables Analysis\n"]
            lines.append(f"📊 Receivables Turnover: {rt:.2f}")
            lines.append(f"📅 Days Sales Outstanding: {dso:.0f} days\n")
            if dso < 30:
                lines.append("✅ Excellent collection — customers pay quickly.")
            elif dso < 60:
                lines.append("⚠️ Acceptable — monitor for delays.")
            else:
                lines.append("❌ Slow collection — risk of bad debts.")
            return "\n".join(lines)

    def _default_response(self, q):
        if self.lang == "ar":
            return t("chat_offline_default")
        else:
            return (
                "🤖 I'm your Financial Assistant!\n\n"
                "I can help you with:\n"
                "• ROE and ROA analysis\n"
                "• Liquidity assessment\n"
                "• Profitability analysis\n"
                "• Debt review\n"
                "• DuPont analysis\n"
                "• Financial advice\n"
                "• Benchmark comparison\n"
                "• Full analysis\n\n"
                "💡 Try asking: 'analyze ratios' or 'give advice' or 'what is ROE?'"
            )


class ChatView(QWidget):
    """واجهة شات الذكاء الاصطناعي — يعمل بدون إنترنت"""

    def __init__(self):
        super().__init__()
        self.messages = state.load_chat_history()
        self.worker = None
        self.local_assistant = LocalFinancialAssistant()
        self._last_api_call = 0.0
        self.setup_ui()
        self._restore_history()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel(t("chat_title"))
        title.setObjectName("headerTitle")
        main_layout.addWidget(title)

        subtitle = QLabel(t("chat_subtitle"))
        subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(subtitle)

        # === Mode indicator ===
        self.mode_label = QLabel()
        self.mode_label.setObjectName("modeLabel")
        self._update_mode_label()
        main_layout.addWidget(self.mode_label)

        # === Chat History ===
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', 'Tahoma', sans-serif;
                font-size: 10.5pt;
                line-height: 1.6;
            }
        """)
        main_layout.addWidget(self.chat_display, 1)

        self._add_system_message(t("chat_welcome"))

        # === Input Area ===
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(t("chat_placeholder"))
        self.input_field.setMaximumHeight(80)
        self.input_field.setAcceptRichText(False)
        self.input_field.installEventFilter(self)
        input_layout.addWidget(self.input_field, 1)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)

        self.send_btn = QPushButton(t("chat_send"))
        self.send_btn.setObjectName("primaryBtn")
        self.send_btn.setMinimumHeight(40)
        self.send_btn.clicked.connect(self.send_message)
        btn_col.addWidget(self.send_btn)

        self.clear_btn = QPushButton(t("chat_clear"))
        self.clear_btn.setObjectName("dangerBtn")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_chat)
        btn_col.addWidget(self.clear_btn)

        input_layout.addLayout(btn_col)
        input_frame.setLayout(input_layout)
        main_layout.addWidget(input_frame)

        self.setLayout(main_layout)

    def _update_mode_label(self):
        if state.api_key:
            self.mode_label.setText(t("chat_mode_online"))
            self.mode_label.setProperty("mode", "online")
        else:
            self.mode_label.setText(t("chat_mode_offline"))
            self.mode_label.setProperty("mode", "offline")
        self.mode_label.style().unpolish(self.mode_label)
        self.mode_label.style().polish(self.mode_label)

    def eventFilter(self, obj, event):
        if obj == self.input_field and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        if len(text) > MAX_MESSAGE_LENGTH:
            self._add_system_message("Message too long. Maximum 2000 characters.")
            return

        self._add_user_message(text)
        self.input_field.clear()

        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳ ...")

        if state.api_key:
            now = time.time()
            elapsed = now - self._last_api_call
            if elapsed < API_RATE_LIMIT_SECONDS:
                self._add_system_message(t("chat_rate_limit"))
                self.send_btn.setEnabled(True)
                self.send_btn.setText(t("chat_send"))
                return
            self._last_api_call = now
            self._send_online(text)
        else:
            self._send_offline(text)
            self._add_system_message(t("chat_offline_mode"))

    def _send_offline(self, text):
        """رد محلي بدون إنترنت"""
        response = self.local_assistant.respond(text)
        self._add_ai_message(response)
        self.messages.append({"role": "user", "content": text})
        self.messages.append({"role": "assistant", "content": response})
        self._save_history()
        self.send_btn.setEnabled(True)
        self.send_btn.setText(t("chat_send"))

    def _send_online(self, text):
        """إرسال عبر OpenAI API"""
        if hasattr(self, 'worker') and self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(2000)
        system_prompt = self._build_system_prompt()
        self.messages.append({"role": "user", "content": text})
        api_messages = [{"role": "system", "content": system_prompt}] + self.messages[-20:]
        self.worker = AIWorker(api_messages, state.api_key, state.api_url, state.model)
        self.worker.response_received.connect(self._on_response)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_response(self, content):
        self._add_ai_message(content)
        self.messages.append({"role": "assistant", "content": content})
        self._save_history()
        self.send_btn.setEnabled(True)
        self.send_btn.setText(t("chat_send"))

    def _on_error(self, error):
        self._add_system_message(t("chat_error_prefix") + " " + error)
        self.send_btn.setEnabled(True)
        self.send_btn.setText(t("chat_send"))

    def _build_system_prompt(self):
        lang = state.language
        if lang == "ar":
            base = (
                "أنت مساعد مالي محاسبي ذكي. تتحدث العربية بطلاقة. "
                "أنت متخصص في التحليل المالي والمراجعية والمحاسبة. "
                "أجب بإجابات مختصرة ومفيدة مع ذكر الأرقام والنسب إن أمكن. "
                "إذا كان المستخدم يسألك عن شيء غير مالي، أجب بإيجاز ثم أعد التوجيه للتحليل المالي."
            )
        else:
            base = (
                "You are a smart financial accounting assistant. You speak English fluently. "
                "You specialize in financial analysis, auditing, and accounting. "
                "Answer concisely and helpfully, mentioning numbers and ratios when possible. "
                "If the user asks about something non-financial, answer briefly then redirect to financial analysis."
            )

        if state.has_data():
            if state.language == "ar":
                data_summary = (
                    f"\n\nالبيانات المالية الحالية للشركة '{state.company_name}' (السنة {state.fiscal_year}):\n"
                    f"- الأصول: {state.financial_data.get('total_assets', 0):,.0f}\n"
                    f"- الالتزامات: {state.financial_data.get('total_liabilities', 0):,.0f}\n"
                    f"- حقوق الملكية: {state.financial_data.get('equity', 0):,.0f}\n"
                    f"- الإيرادات: {state.financial_data.get('revenue', 0):,.0f}\n"
                    f"- صافي الربح: {state.financial_data.get('net_income', 0):,.0f}\n"
                    f"- ROE: {state.ratios.get('roe', 0):.2f}%\n"
                    f"- ROA: {state.ratios.get('roa', 0):.2f}%\n"
                    f"- نسبة السيولة الحالية: {state.ratios.get('current_ratio', 0):.2f}\n"
                    f"- هامش صافي الربح: {state.ratios.get('net_profit_margin', 0):.2f}%\n"
                    f"- نسبة الدين إلى حقوق الملكية: {state.ratios.get('debt_to_equity', 0):.2f}\n"
                )
            else:
                data_summary = (
                    f"\n\nCurrent financial data for '{state.company_name}' (Year {state.fiscal_year}):\n"
                    f"- Total Assets: {state.financial_data.get('total_assets', 0):,.0f}\n"
                    f"- Total Liabilities: {state.financial_data.get('total_liabilities', 0):,.0f}\n"
                    f"- Equity: {state.financial_data.get('equity', 0):,.0f}\n"
                    f"- Revenue: {state.financial_data.get('revenue', 0):,.0f}\n"
                    f"- Net Income: {state.financial_data.get('net_income', 0):,.0f}\n"
                    f"- ROE: {state.ratios.get('roe', 0):.2f}%\n"
                    f"- ROA: {state.ratios.get('roa', 0):.2f}%\n"
                    f"- Current Ratio: {state.ratios.get('current_ratio', 0):.2f}\n"
                    f"- Net Profit Margin: {state.ratios.get('net_profit_margin', 0):.2f}%\n"
                    f"- Debt to Equity: {state.ratios.get('debt_to_equity', 0):.2f}\n"
                )
            base += data_summary

        return base

    def _add_user_message(self, text):
        safe = html_mod.escape(text)
        if state.theme == 'dark':
            user_bg_css = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0052D4, stop:1 #4361EE);"
        else:
            user_bg_css = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0052D4, stop:1 #4361EE);"
        html = f"""
        <div style="margin: 8px 0; text-align: right;">
            <div style="{user_bg_css}
                color: white; padding: 12px 16px; border-radius: 12px 12px 2px 12px;
                display: inline-block; max-width: 75%; font-size: 10.5pt;">
                {safe}
            </div>
            <div style="color: {ThemeColors.get('text_muted')}; font-size: 8pt; margin-top: 2px;">{t("chat_user_label")}</div>
        </div>
        """
        self.chat_display.append(html)
        self._scroll_to_bottom()

    def _add_ai_message(self, text):
        formatted = html_mod.escape(text).replace("\n", "<br>")
        if state.theme == 'dark':
            ai_bg, ai_color = '#2A2A3C', '#E0E0E0'
        else:
            ai_bg, ai_color = '#F0F0F0', '#333333'
        html = f"""
        <div style="margin: 8px 0;">
            <div style="background: {ai_bg}; color: {ai_color}; padding: 12px 16px;
                border-radius: 12px 12px 12px 2px; display: inline-block;
                max-width: 75%; font-size: 10.5pt;">
                {formatted}
            </div>
            <div style="color: {ThemeColors.get('text_muted')}; font-size: 8pt; margin-top: 2px;">{t("chat_ai_label")}</div>
        </div>
        """
        self.chat_display.append(html)
        self._scroll_to_bottom()

    def _add_system_message(self, text):
        safe = html_mod.escape(text)
        if state.theme == 'dark':
            sys_bg, sys_color, sys_border = '#3A3000', '#FFD966', '#665C00'
        else:
            sys_bg, sys_color, sys_border = '#FFF3CD', '#856404', '#FFEAA7'
        html = f"""
        <div style="margin: 10px 0; text-align: center;">
            <div style="background: {sys_bg}; color: {sys_color}; padding: 10px 16px;
                border-radius: 8px; display: inline-block; font-size: 10pt;
                border: 1px solid {sys_border};">
                {safe}
            </div>
        </div>
        """
        self.chat_display.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)

    def _restore_history(self):
        for msg in self.messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                self._add_user_message(content)
            elif role == "assistant":
                self._add_ai_message(content)

    def _save_history(self):
        state.save_chat_history(self.messages)

    def clear_chat(self):
        self.messages.clear()
        self.chat_display.clear()
        self._add_system_message(t("chat_welcome"))
        self._save_history()

    def retranslate(self):
        self._update_mode_label()

    def closeEvent(self, event):
        """تنظيف AIWorker عند إغلاق الواجهة"""
        if self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(3000)
            self.worker.deleteLater()
            self.worker = None
        event.accept()

    def deleteLater(self):
        """تنظيف عند الحذف"""
        if self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(3000)
            self.worker.deleteLater()
            self.worker = None
        super().deleteLater()
