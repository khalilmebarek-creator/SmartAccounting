# طبقة الرسوم البيانية المشتركة — pyqtgraph
# ============================
# تُعوّض matplotlib في كل الشاشات
# ============================

import math
import numpy as np

import pyqtgraph as pg
from pyqtgraph import PlotWidget, PlotDataItem, BarGraphItem, FillBetweenItem, InfiniteLine
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy, QGraphicsPathItem
from PyQt6.QtGui import QFont, QColor, QPainterPath, QPen, QBrush, QPainter
from PyQt6.QtCore import Qt, QRectF

from ui.app_state import ThemeColors


class PgChartWidget(QFrame):
    """كارت يحتوي على رسم بياني pyqtgraph"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground("transparent")
        self.plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot_widget.setAntialiasing(True)
        layout.addWidget(self.plot_widget)

        self.plot_item = self.plot_widget.getPlotItem()
        self._apply_theme()

        self.setLayout(layout)

    def _apply_theme(self):
        bg = ThemeColors.get("chart_bg")
        text_color = ThemeColors.get("chart_text")
        grid_color = ThemeColors.get("chart_grid")

        self.plot_widget.setBackground(bg)

        self.plot_item.getAxis("left").setPen(QPen(QColor(text_color)))
        self.plot_item.getAxis("bottom").setPen(QPen(QColor(text_color)))
        self.plot_item.getAxis("left").setTickPen(QPen(QColor(grid_color)))
        self.plot_item.getAxis("bottom").setTickPen(QPen(QColor(grid_color)))
        self.plot_item.showGrid(x=False, y=False)

        font = QFont("Segoe UI", 9)
        self.plot_item.getAxis("left").setTickFont(font)
        self.plot_item.getAxis("bottom").setTickFont(font)

    def clear_plot(self):
        self.plot_item.clear()

    def refresh_theme(self):
        self._apply_theme()


class PgPolarWidget(QFrame):
    """كارت يحتوي على رسم قطبي (radar)"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 350)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.setBackground("transparent")
        self.graphics_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.graphics_widget)

        self.view = self.graphics_widget.addViewBox()
        self.view.setAspectLocked(True)
        self.view.disableAutoRange()

        self.setLayout(layout)

    def clear_plot(self):
        self.view.clear()

    def set_range(self, r_max):
        self.view.setRange(xRange=(-r_max * 1.3, r_max * 1.3),
                           yRange=(-r_max * 1.3, r_max * 1.3))


class PgPieWidget(QFrame):
    """كارت يحتوي على رسم دائري مرسوم يدوياً"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.pie_canvas = PieCanvas()
        self.pie_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.pie_canvas)

        self.setLayout(layout)


class PieCanvas(QFrame):
    """لوحة رسم دائري مخصصة"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slices = []
        self._labels = []
        self._colors = []
        self._title = ""

    def set_pie_data(self, labels, values, colors):
        self._labels = labels
        self._slices = values
        self._colors = colors
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        center_x, center_y = w / 2, h / 2 + 10
        radius = min(w, h) * 0.35

        total = sum(self._slices) if self._slices else 1
        if total == 0:
            painter.end()
            return

        start_angle = 90 * 16
        for i, (val, color) in enumerate(zip(self._slices, self._colors)):
            span = int(val / total * 360 * 16)
            if span <= 0:
                continue
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(ThemeColors.get("chart_bg")), 2))
            painter.drawPie(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
                            start_angle, -span)
            start_angle -= span

        label_y = center_y + radius + 25
        text_color = ThemeColors.get("chart_text")
        painter.setPen(QPen(QColor(text_color)))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        x_offset = 20
        for i, (label, val) in enumerate(zip(self._labels, self._slices)):
            pct = val / total * 100 if total > 0 else 0
            color = self._colors[i] if i < len(self._colors) else text_color
            painter.setPen(QPen(QColor(color)))
            text = f"{label}: {pct:.1f}%"
            painter.drawText(x_offset, label_y + i * 18, text)

        painter.end()


def _text_color():
    return ThemeColors.get("chart_text")


def _edge_color():
    return ThemeColors.get("chart_edge")


def _grid_color():
    return ThemeColors.get("chart_grid")


def _chart_bg():
    return ThemeColors.get("chart_bg")


def _hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mk_brush(color_str):
    r, g, b = _hex_to_rgb(color_str)
    return pg.mkBrush(r, g, b)


def _mk_pen(color_str, width=1):
    r, g, b = _hex_to_rgb(color_str)
    return pg.mkPen(r, g, b, width=width)


def _mk_text_item(text, x, y, color=None, size=9, bold=False, anchor=(0.5, 1.0)):
    c = color or _text_color()
    t = pg.TextItem(text, color=c, anchor=anchor)
    t.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    t.setPos(x, y)
    return t


def draw_bar(plot_item, labels, values, colors, title=None, bar_width=0.6):
    """رسم بياني شريطي عمودي"""
    plot_item.clear()
    n = len(values)
    x = np.arange(n)
    brushes = [_mk_brush(c) for c in colors]
    bg = BarGraphItem(x=x, height=values, width=bar_width, brushes=brushes)
    plot_item.addItem(bg)

    for i, val in enumerate(values):
        t = _mk_text_item(f"{val:.2f}", x[i], val + max(values) * 0.05 if max(values) > 0 else 0.1,
                          bold=True, size=9)
        plot_item.addItem(t)

    text_color = _text_color()
    tick_vals = list(range(n))
    tick_labels = [[(i, l) for i, l in enumerate(labels)]]
    plot_item.getAxis("bottom").setTicks(tick_labels)

    max_val = max(values) if values else 1
    plot_item.setYRange(0, max_val * 1.3)
    plot_item.showGrid(x=False, y=True, alpha=0.2)
    pg.setConfigOptions(antialias=True)


def draw_horizontal_bar(plot_item, labels, values, colors, title=None, bar_height=0.6):
    """رسم بياني شريطي أفقي"""
    plot_item.clear()
    n = len(values)
    y = np.arange(n)
    brushes = [_mk_brush(c) for c in colors]
    bg = BarGraphItem(y=y, x0=0, width=values, height=bar_height, brushes=brushes)
    plot_item.addItem(bg)

    for i, val in enumerate(values):
        t = _mk_text_item(f"{val:.2f}", val + max(values) * 0.03 if max(values) > 0 else 0.1, y[i],
                          bold=True, size=9)
        plot_item.addItem(t)

    tick_labels = [[(i, l) for i, l in enumerate(labels)]]
    plot_item.getAxis("left").setTicks(tick_labels)

    max_val = max(values) if values else 1
    plot_item.setXRange(0, max_val * 1.3)
    plot_item.showGrid(x=True, y=False, alpha=0.2)


def draw_grouped_bar(plot_item, groups, series_data, bar_width=0.8):
    """رسم بياني شريطي مُجمّع
    groups: ['Q1', 'Q2', ...]
    series_data: [{'label': 'Revenue', 'values': [...], 'color': '#3498DB'}, ...]
    """
    plot_item.clear()
    n = len(groups)
    n_series = len(series_data)
    group_width = bar_width
    bar_w = group_width / n_series

    for si, series in enumerate(series_data):
        offset = (si - n_series / 2 + 0.5) * bar_w
        x = np.arange(n) + offset
        brushes = [_mk_brush(series["color"])] * n
        bg = BarGraphItem(x=x, height=series["values"], width=bar_w * 0.9, brushes=brushes,
                          name=series.get("label", ""))
        plot_item.addItem(bg)

    tick_labels = [[(i, g) for i, g in enumerate(groups)]]
    plot_item.getAxis("bottom").setTicks(tick_labels)
    plot_item.showGrid(x=False, y=True, alpha=0.2)
    plot_item.addLegend(offset=(10, 10))


def draw_line(plot_item, x_data, y_series, labels=None, colors=None, fill=False, fill_alpha=50):
    """رسم بياني خطي"""
    plot_item.clear()
    if not isinstance(y_series[0], (list, tuple)):
        y_series = [y_series]
        labels = [labels] if labels else [None]
        colors = [colors] if colors else [None]

    for i, ys in enumerate(y_series):
        color = colors[i] if colors and i < len(colors) else "#3498DB"
        pen = _mk_pen(color, width=2)
        label = labels[i] if labels and i < len(labels) else None
        item = PlotDataItem(x_data, ys, pen=pen, name=label)
        if fill and i == 0:
            item.setFillBrush(_mk_brush(color))
            item.setFillLevel(0)
            item.setBrush(pg.mkBrush(*_hex_to_rgb(color), fill_alpha))
        plot_item.addItem(item)

    plot_item.showGrid(x=True, y=True, alpha=0.2)
    if labels and any(labels):
        plot_item.addLegend(offset=(10, 10))


def draw_area(plot_item, x_data, y_series, labels=None, colors=None):
    """رسم بياني مساحي"""
    plot_item.clear()
    if not isinstance(y_series[0], (list, tuple)):
        y_series = [y_series]
        labels = [labels] if labels else [None]
        colors = [colors] if colors else [None]

    for i, ys in enumerate(y_series):
        color = colors[i] if colors and i < len(colors) else "#3498DB"
        pen = _mk_pen(color, width=2)
        label = labels[i] if labels and i < len(labels) else None
        item = PlotDataItem(x_data, ys, pen=pen, name=label)
        r, g, b = _hex_to_rgb(color)
        item.setBrush(pg.mkBrush(r, g, b, 60))
        item.setFillLevel(0)
        plot_item.addItem(item)

    plot_item.showGrid(x=True, y=True, alpha=0.2)
    if labels and any(labels):
        plot_item.addLegend(offset=(10, 10))


def draw_waterfall(plot_item, labels, values, colors=None):
    """رسم بياني شلالي"""
    plot_item.clear()
    n = len(values)
    x = np.arange(n)

    cum = [0]
    for v in values[:-1]:
        cum.append(cum[-1] + v)

    bottoms = []
    heights = []
    bar_colors = []
    for i, val in enumerate(values):
        if i == n - 1:
            bottoms.append(0)
            heights.append(val)
            bar_colors.append(colors[i] if colors else "#3498DB")
        elif val >= 0:
            bottoms.append(cum[i])
            heights.append(val)
            bar_colors.append(colors[i] if colors else "#2ECC71")
        else:
            bottoms.append(cum[i] + val)
            heights.append(abs(val))
            bar_colors.append(colors[i] if colors else "#E74C3C")

    brushes = [_mk_brush(c) for c in bar_colors]
    bg = BarGraphItem(x=x, height=heights, y0=bottoms, width=0.6, brushes=brushes)
    plot_item.addItem(bg)

    for i in range(n):
        y_pos = bottoms[i] + heights[i] + max(abs(v) for v in values) * 0.05
        t = _mk_text_item(f"{values[i]:.2f}", x[i], y_pos, bold=True, size=9)
        plot_item.addItem(t)

    tick_labels = [[(i, l) for i, l in enumerate(labels)]]
    plot_item.getAxis("bottom").setTicks(tick_labels)

    all_vals = bottoms + [b + h for b, h in zip(bottoms, heights)]
    low = min(min(bottoms), 0)
    high = max(all_vals) if all_vals else 1
    padding = max(abs(high - low) * 0.15, 0.5)
    plot_item.setYRange(low - padding, high + padding)
    plot_item.showGrid(x=False, y=True, alpha=0.2)


def draw_pie_widget(pie_widget, labels, values, colors):
    """رسم بياني دائري"""
    pie_widget.pie_canvas.set_pie_data(labels, values, colors)


def draw_radar(polar_widget, labels, values, colors_list=None, legend_labels=None):
    """رسم بياني قطبي (radar)"""
    polar_widget.clear_plot()

    n = len(labels)
    if n == 0:
        return

    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r_max = max(max(values_list) for values_list in values) if values else 100
    if r_max == 0:
        r_max = 100

    grid_rings = 5
    for ring in range(1, grid_rings + 1):
        r = r_max * ring / grid_rings
        ring_points_x = [r * math.cos(a) for a in np.linspace(0, 2 * np.pi, 100)]
        ring_points_y = [r * math.sin(a) for a in np.linspace(0, 2 * np.pi, 100)]
        pen = pg.mkPen(100, 100, 100, 80, style=Qt.PenStyle.DashLine)
        polar_widget.view.addItem(PlotDataItem(ring_points_x, ring_points_y, pen=pen))

    for a in angles:
        line_x = [0, r_max * 1.1 * math.cos(a)]
        line_y = [0, r_max * 1.1 * math.sin(a)]
        pen = pg.mkPen(100, 100, 100, 60, style=Qt.PenStyle.DashLine)
        polar_widget.view.addItem(PlotDataItem(line_x, line_y, pen=pen))

    text_color = _text_color()
    for i, label in enumerate(labels):
        tx = r_max * 1.2 * math.cos(angles[i])
        ty = r_max * 1.2 * math.sin(angles[i])
        t = pg.TextItem(label, color=text_color, anchor=(0.5, 0.5))
        t.setFont(QFont("Segoe UI", 8))
        t.setPos(tx, ty)
        polar_widget.view.addItem(t)

    default_colors = ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12"]
    for vi, vals in enumerate(values):
        color = colors_list[vi] if colors_list and vi < len(colors_list) else default_colors[vi % len(default_colors)]
        pts_x = [vals[i] * math.cos(angles[i]) for i in range(n)]
        pts_y = [vals[i] * math.sin(angles[i]) for i in range(n)]
        pts_x.append(pts_x[0])
        pts_y.append(pts_y[0])

        r, g, b = _hex_to_rgb(color)
        fill_pen = pg.mkPen(r, g, b, width=2)
        fill_brush = pg.mkBrush(r, g, b, 40)
        curve = PlotDataItem(pts_x, pts_y, pen=fill_pen, name="")
        polar_widget.view.addItem(curve)

        fill_path = QPainterPath()
        fill_path.moveTo(pts_x[0], pts_y[0])
        for px, py in zip(pts_x[1:], pts_y[1:]):
            fill_path.lineTo(px, py)
        fill_path.closeSubpath()

        fill_item = QGraphicsPathItem(fill_path)
        fill_item.setBrush(fill_brush)
        fill_item.setPen(QPen(Qt.PenStyle.NoPen))
        polar_widget.view.addItem(fill_item)

    polar_widget.set_range(r_max * 1.3)


def draw_gauge(plot_item, value, zones, max_val=100, label=""):
    """رسم بياني مقياس أفقي مع مناطق ألوان"""
    plot_item.clear()

    zone_width = max_val / len(zones)
    for i, (zone_color, zone_label) in enumerate(zones):
        bg = BarGraphItem(
            y=0, x0=i * zone_width, width=zone_width, height=0.5,
            brush=_mk_brush(zone_color)
        )
        plot_item.addItem(bg)

    pen = _mk_pen("#FFFFFF", width=3)
    indicator = InfiniteLine(pos=(min(max(value, 0), max_val), 0), angle=90, pen=pen)
    plot_item.addItem(indicator)

    t = _mk_text_item(f"{value:.2f}", min(max(value, 0), max_val), 0.4,
                      color="#FFFFFF", bold=True, size=11, anchor=(0.5, 1.0))
    plot_item.addItem(t)

    plot_item.setYRange(-0.5, 1.0)
    plot_item.setXRange(-max_val * 0.05, max_val * 1.05)
    plot_item.hideAxis("left")
    plot_item.hideAxis("bottom")
    plot_item.hideButtons()


def draw_stacked_bar(plot_item, groups, series_data, bar_width=0.8):
    """رسم بياني شريطي مكدّس"""
    plot_item.clear()
    n = len(groups)
    bottom = np.zeros(n)

    for series in series_data:
        color = series.get("color", "#3498DB")
        values = series.get("values", [0] * n)
        bg = BarGraphItem(x=np.arange(n), y0=bottom, height=values,
                          width=bar_width, brush=_mk_brush(color),
                          name=series.get("label", ""))
        plot_item.addItem(bg)
        bottom += np.array(values)

    tick_labels = [[(i, g) for i, g in enumerate(groups)]]
    plot_item.getAxis("bottom").setTicks(tick_labels)
    plot_item.showGrid(x=False, y=True, alpha=0.2)
    plot_item.addLegend(offset=(10, 10))
