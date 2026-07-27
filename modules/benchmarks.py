# المعايير المرجعية لقطاعات الأعمال الجزائرية
# ================================================

from typing import Dict, List, Optional, Tuple
from utils.app_logger import get_logger

logger = get_logger("benchmarks")

ALGERIAN_SECTORS = {
    "commercial": {
        "name_ar": "القطاع التجاري",
        "name_en": "Commercial / Trading",
        "name_fr": "Commerce",
        "description_ar": "تجارة الجملة والقطاعي",
        "benchmarks": {
            "current_ratio": {"min": 1.0, "avg": 1.8, "max": 3.0, "ideal": (1.5, 2.5)},
            "quick_ratio": {"min": 0.5, "avg": 1.0, "max": 2.0, "ideal": (0.8, 1.5)},
            "gross_profit_margin": {"min": 8, "avg": 18, "max": 35, "ideal": (15, 25)},
            "net_profit_margin": {"min": 1, "avg": 5, "max": 15, "ideal": (3, 10)},
            "roa": {"min": 2, "avg": 6, "max": 15, "ideal": (4, 10)},
            "roe": {"min": 5, "avg": 12, "max": 30, "ideal": (10, 20)},
            "debt_to_equity": {"min": 0.2, "avg": 1.0, "max": 3.0, "ideal": (0.5, 1.5)},
            "asset_turnover": {"min": 0.5, "avg": 1.2, "max": 3.0, "ideal": (1.0, 2.0)},
            "inventory_turnover": {"min": 3, "avg": 6, "max": 12, "ideal": (5, 9)},
            "receivable_turnover": {"min": 4, "avg": 8, "max": 15, "ideal": (6, 12)},
        }
    },
    "industrial": {
        "name_ar": "القطاع الصناعي",
        "name_en": "Industrial / Manufacturing",
        "name_fr": "Industrie",
        "description_ar": "التصنيع والإنتاج الصناعي",
        "benchmarks": {
            "current_ratio": {"min": 1.0, "avg": 1.5, "max": 2.5, "ideal": (1.2, 2.0)},
            "quick_ratio": {"min": 0.5, "avg": 0.8, "max": 1.5, "ideal": (0.6, 1.2)},
            "gross_profit_margin": {"min": 15, "avg": 25, "max": 45, "ideal": (20, 35)},
            "net_profit_margin": {"min": 2, "avg": 7, "max": 18, "ideal": (5, 12)},
            "roa": {"min": 3, "avg": 8, "max": 20, "ideal": (5, 12)},
            "roe": {"min": 5, "avg": 15, "max": 35, "ideal": (12, 25)},
            "debt_to_equity": {"min": 0.3, "avg": 1.2, "max": 3.5, "ideal": (0.6, 1.8)},
            "asset_turnover": {"min": 0.4, "avg": 0.9, "max": 2.0, "ideal": (0.6, 1.2)},
            "inventory_turnover": {"min": 2, "avg": 5, "max": 10, "ideal": (4, 7)},
            "receivable_turnover": {"min": 4, "avg": 7, "max": 12, "ideal": (5, 10)},
        }
    },
    "services": {
        "name_ar": "قطاع الخدمات",
        "name_en": "Services",
        "name_fr": "Services",
        "description_ar": "الخدمات التجارية والمهنية",
        "benchmarks": {
            "current_ratio": {"min": 1.0, "avg": 1.8, "max": 3.5, "ideal": (1.5, 2.5)},
            "quick_ratio": {"min": 0.8, "avg": 1.2, "max": 2.5, "ideal": (1.0, 1.8)},
            "gross_profit_margin": {"min": 25, "avg": 40, "max": 70, "ideal": (35, 55)},
            "net_profit_margin": {"min": 3, "avg": 10, "max": 25, "ideal": (8, 18)},
            "roa": {"min": 3, "avg": 10, "max": 25, "ideal": (8, 18)},
            "roe": {"min": 8, "avg": 18, "max": 40, "ideal": (15, 30)},
            "debt_to_equity": {"min": 0.1, "avg": 0.8, "max": 2.5, "ideal": (0.3, 1.2)},
            "asset_turnover": {"min": 0.5, "avg": 1.0, "max": 2.5, "ideal": (0.8, 1.5)},
            "inventory_turnover": {"min": 5, "avg": 10, "max": 20, "ideal": (8, 15)},
            "receivable_turnover": {"min": 5, "avg": 10, "max": 18, "ideal": (8, 14)},
        }
    },
    "construction": {
        "name_ar": "قطاع البناء والأشغال العمومية",
        "name_en": "Construction & Public Works",
        "name_fr": "BTP",
        "description_ar": "البناء والأشغال العمومية",
        "benchmarks": {
            "current_ratio": {"min": 0.8, "avg": 1.3, "max": 2.0, "ideal": (1.0, 1.8)},
            "quick_ratio": {"min": 0.4, "avg": 0.7, "max": 1.2, "ideal": (0.5, 1.0)},
            "gross_profit_margin": {"min": 10, "avg": 18, "max": 30, "ideal": (14, 22)},
            "net_profit_margin": {"min": 1, "avg": 4, "max": 10, "ideal": (3, 7)},
            "roa": {"min": 2, "avg": 5, "max": 12, "ideal": (3, 8)},
            "roe": {"min": 5, "avg": 10, "max": 25, "ideal": (8, 18)},
            "debt_to_equity": {"min": 0.5, "avg": 1.5, "max": 4.0, "ideal": (0.8, 2.0)},
            "asset_turnover": {"min": 0.4, "avg": 0.8, "max": 1.5, "ideal": (0.6, 1.0)},
            "inventory_turnover": {"min": 2, "avg": 4, "max": 8, "ideal": (3, 6)},
            "receivable_turnover": {"min": 3, "avg": 6, "max": 10, "ideal": (4, 8)},
        }
    },
    "agriculture": {
        "name_ar": "القطاع الفلاحي",
        "name_en": "Agriculture",
        "name_fr": "Agriculture",
        "description_ar": "الزراعة والثروة الحيوانية",
        "benchmarks": {
            "current_ratio": {"min": 0.8, "avg": 1.4, "max": 2.5, "ideal": (1.0, 2.0)},
            "quick_ratio": {"min": 0.3, "avg": 0.6, "max": 1.2, "ideal": (0.4, 0.9)},
            "gross_profit_margin": {"min": 15, "avg": 30, "max": 55, "ideal": (20, 40)},
            "net_profit_margin": {"min": -2, "avg": 5, "max": 15, "ideal": (3, 10)},
            "roa": {"min": 1, "avg": 5, "max": 12, "ideal": (3, 8)},
            "roe": {"min": 3, "avg": 10, "max": 25, "ideal": (7, 18)},
            "debt_to_equity": {"min": 0.3, "avg": 1.0, "max": 3.0, "ideal": (0.5, 1.5)},
            "asset_turnover": {"min": 0.3, "avg": 0.6, "max": 1.2, "ideal": (0.4, 0.8)},
            "inventory_turnover": {"min": 1, "avg": 3, "max": 6, "ideal": (2, 5)},
            "receivable_turnover": {"min": 3, "avg": 6, "max": 12, "ideal": (4, 9)},
        }
    },
    "transport": {
        "name_ar": "قطاع النقل والمواصلات",
        "name_en": "Transport & Logistics",
        "name_fr": "Transport & Logistique",
        "description_ar": "النقل البري والبحري والجوي",
        "benchmarks": {
            "current_ratio": {"min": 0.8, "avg": 1.3, "max": 2.0, "ideal": (1.0, 1.8)},
            "quick_ratio": {"min": 0.4, "avg": 0.7, "max": 1.2, "ideal": (0.5, 1.0)},
            "gross_profit_margin": {"min": 15, "avg": 25, "max": 40, "ideal": (20, 30)},
            "net_profit_margin": {"min": 1, "avg": 6, "max": 15, "ideal": (4, 10)},
            "roa": {"min": 2, "avg": 6, "max": 15, "ideal": (4, 10)},
            "roe": {"min": 5, "avg": 12, "max": 28, "ideal": (10, 20)},
            "debt_to_equity": {"min": 0.5, "avg": 1.5, "max": 3.5, "ideal": (0.8, 2.0)},
            "asset_turnover": {"min": 0.4, "avg": 0.8, "max": 1.5, "ideal": (0.6, 1.1)},
            "inventory_turnover": {"min": 3, "avg": 7, "max": 15, "ideal": (5, 10)},
            "receivable_turnover": {"min": 4, "avg": 8, "max": 14, "ideal": (6, 11)},
        }
    },
    "food": {
        "name_ar": "قطاع تجهيز المواد الغذائية",
        "name_en": "Food Processing",
        "name_fr": "Agroalimentaire",
        "description_ar": "صناعة وتجهيز المواد الغذائية",
        "benchmarks": {
            "current_ratio": {"min": 1.0, "avg": 1.6, "max": 2.8, "ideal": (1.3, 2.2)},
            "quick_ratio": {"min": 0.5, "avg": 0.9, "max": 1.8, "ideal": (0.7, 1.3)},
            "gross_profit_margin": {"min": 12, "avg": 22, "max": 40, "ideal": (18, 30)},
            "net_profit_margin": {"min": 1, "avg": 6, "max": 15, "ideal": (4, 10)},
            "roa": {"min": 3, "avg": 7, "max": 18, "ideal": (5, 12)},
            "roe": {"min": 5, "avg": 14, "max": 30, "ideal": (10, 22)},
            "debt_to_equity": {"min": 0.3, "avg": 1.0, "max": 2.5, "ideal": (0.5, 1.5)},
            "asset_turnover": {"min": 0.6, "avg": 1.1, "max": 2.0, "ideal": (0.8, 1.5)},
            "inventory_turnover": {"min": 4, "avg": 8, "max": 15, "ideal": (6, 12)},
            "receivable_turnover": {"min": 5, "avg": 9, "max": 15, "ideal": (7, 12)},
        }
    },
}


class BenchmarkAnalyzer:
    """محلل المعايير المرجعية لقطاعات الأعمال الجزائرية"""

    def __init__(self):
        self.sectors = ALGERIAN_SECTORS

    def get_sectors_list(self) -> List[Dict]:
        """قائمة القطاعات المتاحة"""
        result = []
        for code, info in self.sectors.items():
            result.append({
                "code": code,
                "name_ar": info["name_ar"],
                "name_en": info["name_en"],
                "name_fr": info.get("name_fr", info["name_en"]),
                "description_ar": info["description_ar"],
            })
        return result

    def compare_with_sector(self, company_ratios: Dict[str, float],
                            sector_code: str) -> Dict:
        """مقارنة أداء الشركة مع معايير القطاع"""
        if sector_code not in self.sectors:
            return {"error": f"Sector '{sector_code}' not found"}

        sector = self.sectors[sector_code]
        benchmarks = sector["benchmarks"]
        comparison = {}
        overall_score = 0
        count = 0

        for ratio_name, value in company_ratios.items():
            if ratio_name not in benchmarks:
                continue

            bm = benchmarks[ratio_name]
            ideal_min, ideal_max = bm["ideal"]
            min_val, avg_val, max_val = bm["min"], bm["avg"], bm["max"]

            if value is None:
                continue

            status = "excellent"
            if value < min_val:
                status = "critical"
                score = 0
            elif value < ideal_min:
                status = "below"
                score = 50
            elif value <= ideal_max:
                status = "good"
                score = 90
            elif value <= max_val:
                status = "above"
                score = 70
            else:
                status = "excellent"
                score = 100

            if ratio_name in ("debt_to_equity",):
                if value < min_val:
                    status = "excellent"
                    score = 95
                elif value <= ideal_max:
                    status = "good"
                    score = 90
                elif value <= max_val:
                    status = "above"
                    score = 60
                else:
                    status = "critical"
                    score = 20

            overall_score += score
            count += 1

            comparison[ratio_name] = {
                "company_value": round(value, 4),
                "sector_min": min_val,
                "sector_avg": avg_val,
                "sector_max": max_val,
                "ideal_range": f"{ideal_min} - {ideal_max}",
                "status": status,
                "score": score,
                "deviation": round(value - avg_val, 4),
            }

        return {
            "sector": sector["name_en"],
            "sector_ar": sector["name_ar"],
            "ratios": comparison,
            "overall_score": round(overall_score / max(count, 1), 1),
            "rating": self._get_rating(overall_score / max(count, 1)),
        }

    def _get_rating(self, score: float) -> Dict[str, str]:
        """تصنيف الأداء"""
        if score >= 85:
            return {"ar": "ممتاز", "en": "Excellent", "color": "#27AE60"}
        elif score >= 70:
            return {"ar": "جيد جداً", "en": "Very Good", "color": "#2ECC71"}
        elif score >= 55:
            return {"ar": "جيد", "en": "Good", "color": "#F39C12"}
        elif score >= 40:
            return {"ar": "مقبول", "en": "Average", "color": "#E67E22"}
        else:
            return {"ar": "ضعيف", "en": "Poor", "color": "#E74C3C"}

    def get_radar_data(self, company_ratios: Dict[str, float],
                       sector_code: str) -> Dict:
        """بيانات للرسم البياني الراداري"""
        if sector_code not in self.sectors:
            return {"labels": [], "company": [], "sector_avg": [], "sector_max": []}

        benchmarks = self.sectors[sector_code]["benchmarks"]
        labels = []
        company_vals = []
        sector_avg_vals = []
        sector_max_vals = []

        ratio_display = {
            "current_ratio": "Liquidity",
            "gross_profit_margin": "Gross Margin",
            "net_profit_margin": "Net Margin",
            "roa": "ROA",
            "roe": "ROE",
            "asset_turnover": "Asset Turnover",
            "debt_to_equity": "D/E Ratio",
            "inventory_turnover": "Inv. Turnover",
        }

        for ratio_name, display_name in ratio_display.items():
            if ratio_name in benchmarks and ratio_name in company_ratios:
                bm = benchmarks[ratio_name]
                val = company_ratios.get(ratio_name, 0)
                max_val = bm["max"]
                if max_val <= 0:
                    max_val = 1

                labels.append(display_name)
                company_vals.append(round(min(val / max_val * 100, 100), 1))
                sector_avg_vals.append(round(bm["avg"] / max_val * 100, 1))
                sector_max_vals.append(round(100, 1))

        return {
            "labels": labels,
            "company": company_vals,
            "sector_avg": sector_avg_vals,
            "sector_max": sector_max_vals,
        }

    def suggest_improvements(self, company_ratios: Dict[str, float],
                              sector_code: str) -> List[Dict]:
        """اقتراحات لتحسين الأداء"""
        if sector_code not in self.sectors:
            return []

        benchmarks = self.sectors[sector_code]["benchmarks"]
        suggestions = []

        suggestions_map = {
            "current_ratio": {
                "ar": {
                    "below": "زيادة الأصول المتداولة أو تقليل الخصوم المتداولة لتحسين السيولة",
                    "above": "ال/assets المتداولة مرتفعة - يمكن استخدام الأموال الزائدة للاستثمار",
                },
                "en": {
                    "below": "Increase current assets or reduce current liabilities to improve liquidity",
                    "above": "High current assets - consider investing excess funds for better returns",
                },
            },
            "net_profit_margin": {
                "ar": {
                    "below": "تحسين هامش الربح عبر تخفيض التكاليف أو رفع الأسعار",
                    "above": "هامش صافي الربح ممتاز - حافظ على هذا الأداء",
                },
                "en": {
                    "below": "Improve profit margin by reducing costs or optimizing pricing",
                    "above": "Excellent profit margin - maintain this performance level",
                },
            },
            "debt_to_equity": {
                "ar": {
                    "below": "النسبة ممتازة - الدين منخفض نسبياً",
                    "above": "تخفيض الدين لتحسين المرونة المالية والثقة لدى الدائنين",
                },
                "en": {
                    "below": "Good ratio - debt is relatively low",
                    "above": "Reduce debt to improve financial flexibility and creditor confidence",
                },
            },
            "roa": {
                "ar": {
                    "below": "تحسين كفاءة استخدام الأصول لتوليد أرباح أكبر",
                    "above": "استخدام الأصول بكفاءة عالية - أداء ممتاز",
                },
                "en": {
                    "below": "Improve asset utilization to generate higher returns",
                    "above": "Efficient asset usage - excellent performance",
                },
            },
            "roe": {
                "ar": {
                    "below": "تحسين العائد على حقوق الملكية عبر زيادة الأرباح المحتجزة أو تقليل التمويل بالدين",
                    "above": "عائد ممتاز على حقوق الملكية",
                },
                "en": {
                    "below": "Improve ROE through retained earnings growth or optimal leverage",
                    "above": "Excellent return on equity",
                },
            },
        }

        for ratio_name, company_val in company_ratios.items():
            if ratio_name not in benchmarks or ratio_name not in suggestions_map:
                continue

            bm = benchmarks[ratio_name]
            ideal_min, ideal_max = bm["ideal"]

            if company_val < ideal_min:
                severity = "critical" if company_val < bm["min"] else "warning"
                suggestions.append({
                    "ratio": ratio_name,
                    "status": "below",
                    "severity": severity,
                    "message_ar": suggestions_map[ratio_name]["ar"]["below"],
                    "message_en": suggestions_map[ratio_name]["en"]["below"],
                    "company_value": round(company_val, 4),
                    "target_range": f"{ideal_min} - {ideal_max}",
                })
            elif company_val > ideal_max:
                suggestions.append({
                    "ratio": ratio_name,
                    "status": "above",
                    "severity": "info",
                    "message_ar": suggestions_map[ratio_name]["ar"]["above"],
                    "message_en": suggestions_map[ratio_name]["en"]["above"],
                    "company_value": round(company_val, 4),
                    "target_range": f"{ideal_min} - {ideal_max}",
                })

        suggestions.sort(key=lambda x: 0 if x["severity"] == "critical" else 1 if x["severity"] == "warning" else 2)
        return suggestions


benchmark_analyzer = BenchmarkAnalyzer()
