# تصدير Plotly التفاعلي
# ====================

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json


def export_dashboard_html(file_path, charts_data):
    """
    charts_data: dict with keys:
      - ratios_bar: {'labels': list, 'values': list, 'colors': list}
      - profitability_pie: {'labels': list, 'values': list, 'colors': list}
      - dupont: {'labels': list, 'values': list, 'colors': list}
      - balance_pie: {'labels': list, 'values': list, 'colors': list}
      - expenses_pie: {'labels': list, 'values': list, 'colors': list}
      - radar: {'labels': list, 'values': list}
      - zscore: {'value': float, 'zones': list of (color, label, max_val)}
      - liquidity: {'labels': list, 'values': list, 'colors': list}
    """
    fig = make_subplots(
        rows=3, cols=3,
        specs=[
            [{"type": "bar"}, {"type": "pie"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "pie"}, {"type": "polar"}],
            [{"type": "indicator"}, {"type": "bar"}, None],
        ],
        subplot_titles=[
            "Financial Ratios", "Profitability", "DuPont Analysis",
            "Balance Sheet", "Expenses", "Radar",
            "Z-Score", "Liquidity", "",
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.08,
    )

    d = charts_data

    if "ratios_bar" in d:
        rb = d["ratios_bar"]
        fig.add_trace(go.Bar(
            x=rb["labels"], y=rb["values"],
            marker_color=rb["colors"], name="Ratios"
        ), row=1, col=1)

    if "profitability_pie" in d:
        pp = d["profitability_pie"]
        fig.add_trace(go.Pie(
            labels=pp["labels"], values=pp["values"],
            marker_colors=pp["colors"], name="Profitability"
        ), row=1, col=2)

    if "dupont" in d:
        dp = d["dupont"]
        fig.add_trace(go.Bar(
            x=dp["labels"], y=dp["values"],
            marker_color=dp["colors"], name="DuPont"
        ), row=1, col=3)

    if "balance_pie" in d:
        bp = d["balance_pie"]
        fig.add_trace(go.Pie(
            labels=bp["labels"], values=bp["values"],
            marker_colors=bp["colors"], name="Balance"
        ), row=2, col=1)

    if "expenses_pie" in d:
        ep = d["expenses_pie"]
        fig.add_trace(go.Pie(
            labels=ep["labels"], values=ep["values"],
            marker_colors=ep["colors"], name="Expenses"
        ), row=2, col=2)

    if "radar" in d:
        rd = d["radar"]
        fig.add_trace(go.Scatterpolar(
            r=rd["values"] + [rd["values"][0]],
            theta=rd["labels"] + [rd["labels"][0]],
            fill="toself", name="Radar"
        ), row=2, col=3)

    if "zscore" in d:
        zs = d["zscore"]
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=zs["value"],
            title={"text": "Z-Score"},
            gauge={
                "axis": {"range": [0, 5]},
                "bar": {"color": "#333"},
                "steps": [
                    {"range": [z[2] if len(z) > 2 else 0, z[3] if len(z) > 3 else 5],
                     "color": z[0]} for z in zs["zones"]
                ] if zs["zones"] else [],
            }
        ), row=3, col=1)

    if "liquidity" in d:
        lq = d["liquidity"]
        fig.add_trace(go.Bar(
            y=lq["labels"], x=lq["values"],
            orientation="h", marker_color=lq["colors"], name="Liquidity"
        ), row=3, col=2)

    fig.update_layout(
        height=1200, width=1400,
        title_text="Smart Accounting Dashboard",
        showlegend=False,
        template="plotly_white",
    )
    fig.write_html(file_path, include_plotlyjs=True, full_html=True)


def export_analysis_html(file_path, charts_data):
    """
    charts_data: dict with keys:
      - waterfall: {'labels': list, 'values': list}
      - trend: {'x': list, 'series': [{'name': str, 'y': list, 'color': str}]}
      - gauge: {'value': float, 'zones': list of (color, label)}
      - industry: {'groups': list, 'series': [{'name': str, 'values': list, 'color': str}]}
    """
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "waterfall"}, {"type": "scatter"}],
            [{"type": "indicator"}, {"type": "bar"}],
        ],
        subplot_titles=["DuPont Waterfall", "Trend", "ROE Gauge", "Industry Comparison"],
        vertical_spacing=0.12, horizontal_spacing=0.1,
    )
    d = charts_data

    if "waterfall" in d:
        wf = d["waterfall"]
        fig.add_trace(go.Waterfall(
            x=wf["labels"], y=wf["values"],
            measure=["absolute"] + ["relative"] * (len(wf["labels"]) - 2) + ["total"],
        ), row=1, col=1)

    if "trend" in d:
        tr = d["trend"]
        for s in tr["series"]:
            fig.add_trace(go.Scatter(
                x=tr["x"], y=s["y"], name=s["name"],
                line=dict(color=s["color"]), mode="lines+markers"
            ), row=1, col=2)

    if "gauge" in d:
        g = d["gauge"]
        fig.add_trace(go.Indicator(
            mode="gauge+number", value=g["value"],
            title={"text": "ROE %"},
            gauge={"axis": {"range": [0, 50]}, "bar": {"color": "#333"}},
        ), row=2, col=1)

    if "industry" in d:
        ind = d["industry"]
        for s in ind["series"]:
            fig.add_trace(go.Bar(
                x=ind["groups"], y=s["values"],
                name=s["name"], marker_color=s["color"]
            ), row=2, col=2)
        fig.update_layout(barmode="group")

    fig.update_layout(height=900, width=1200, title_text="DuPont Analysis", template="plotly_white")
    fig.write_html(file_path, include_plotlyjs=True, full_html=True)


def export_scenarios_html(file_path, charts_data):
    """
    charts_data: dict with keys:
      - line: {'x': list, 'series': [{'name': str, 'y': list, 'color': str}]}
      - bar: {'groups': list, 'series': [{'name': str, 'values': list, 'color': str}]}
      - area: {'x': list, 'series': [{'name': str, 'y': list, 'color': str}]}
      - tornado: {'labels': list, 'low': list, 'high': list, 'base': float}
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Scenario Lines", "Scenario Comparison", "Revenue & Income", "Tornado Sensitivity"],
        vertical_spacing=0.12, horizontal_spacing=0.1,
    )
    d = charts_data

    if "line" in d:
        ln = d["line"]
        for s in ln["series"]:
            fig.add_trace(go.Scatter(
                x=ln["x"], y=s["y"], name=s["name"],
                line=dict(color=s["color"]), mode="lines+markers"
            ), row=1, col=1)

    if "bar" in d:
        br = d["bar"]
        for s in br["series"]:
            fig.add_trace(go.Bar(
                x=br["groups"], y=s["values"],
                name=s["name"], marker_color=s["color"]
            ), row=1, col=2)
        fig.update_layout(barmode="group")

    if "area" in d:
        ar = d["area"]
        for s in ar["series"]:
            fig.add_trace(go.Scatter(
                x=ar["x"], y=s["y"], name=s["name"],
                fill="tozeroy", line=dict(color=s["color"])
            ), row=2, col=1)

    if "tornado" in d:
        tn = d["tornado"]
        low_vals = [-v for v in tn["low"]]
        fig.add_trace(go.Bar(
            y=tn["labels"], x=low_vals, orientation="h",
            name="Low", marker_color="#E74C3C"
        ), row=2, col=2)
        fig.add_trace(go.Bar(
            y=tn["labels"], x=tn["high"], orientation="h",
            name="High", marker_color="#2ECC71"
        ), row=2, col=2)

    fig.update_layout(height=900, width=1200, title_text="Scenario Analysis", template="plotly_white")
    fig.write_html(file_path, include_plotlyjs=True, full_html=True)


def export_benchmarks_html(file_path, charts_data):
    """
    charts_data: dict with keys:
      - radar: {'labels': list, 'series': [{'name': str, 'values': list, 'color': str}]}
      - bar: {'labels': list, 'values': list, 'colors': list}
      - trend: {'x': list, 'series': [{'name': str, 'y': list, 'color': str}]}
    """
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{"type": "polar"}, {"type": "bar"}, {"type": "scatter"}]],
        subplot_titles=["Radar", "Score Bar", "Trend"],
    )
    d = charts_data

    if "radar" in d:
        rd = d["radar"]
        for s in rd["series"]:
            fig.add_trace(go.Scatterpolar(
                r=s["values"] + [s["values"][0]],
                theta=rd["labels"] + [rd["labels"][0]],
                fill="toself", name=s["name"],
                line=dict(color=s["color"])
            ), row=1, col=1)

    if "bar" in d:
        br = d["bar"]
        fig.add_trace(go.Bar(
            y=br["labels"], x=br["values"],
            orientation="h", marker_color=br["colors"], name="Scores"
        ), row=1, col=2)

    if "trend" in d:
        tr = d["trend"]
        for s in tr["series"]:
            fig.add_trace(go.Scatter(
                x=tr["x"], y=s["y"], name=s["name"],
                line=dict(color=s["color"]), mode="lines+markers"
            ), row=1, col=3)

    fig.update_layout(height=500, width=1500, title_text="Benchmarks", template="plotly_white")
    fig.write_html(file_path, include_plotlyjs=True, full_html=True)
