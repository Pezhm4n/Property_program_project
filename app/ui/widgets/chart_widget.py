from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath

class SkeletonChart(QWidget):
    def __init__(self, chart_type="bar", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.data = []
        self.categories = []
        self.setMouseTracking(True)
        self.hovered_index = -1
        
    def set_data(self, data, categories=None):
        self.data = data
        if categories is not None:
            self.categories = categories
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        is_empty = not self.data or all(v == 0 for v in self.data)
        if is_empty:
            empty_text = "داده‌ای برای نمایش وجود ندارد."
            icon = "📊"
            
            # Draw Icon
            font_icon = self.font()
            font_icon.setPointSize(24)
            painter.setFont(font_icon)
            painter.setPen(QColor("#38bdf8"))
            painter.drawText(0, 0, width, height - 40, Qt.AlignmentFlag.AlignCenter, icon)
            
            # Draw Text
            painter.setFont(self.font())
            text_color = QColor("#64748b")
            painter.setPen(text_color)
            painter.drawText(0, 0, width, height + 40, Qt.AlignmentFlag.AlignCenter, empty_text)
            return
            
        # Background Grid Lines
        grid_pen = QPen(QColor("#334155") if self.palette().window().color().value() < 128 else QColor("#cbd5e1"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(1, 5):
            y = int(height * (i / 5))
            painter.drawLine(10, y, width - 10, y)
            
        if self.chart_type == "bar":
            self.draw_bar_chart(painter, width, height)
        elif self.chart_type == "line":
            self.draw_line_chart(painter, width, height)
            
    def draw_bar_chart(self, painter, width, height):
        if not self.data:
            return
            
        max_val = max(self.data) if self.data else 1
        if max_val == 0:
            max_val = 1
        num_bars = len(self.data)
        spacing = 15
        bar_width = (width - (spacing * (num_bars + 1))) / num_bars
        
        for i, val in enumerate(self.data):
            bar_height = (val / max_val) * (height - 60)
            x = spacing + i * (bar_width + spacing)
            y = height - bar_height - 30
            
            # Highlight if hovered
            is_hovered = (i == self.hovered_index)
            gradient = QLinearGradient(x, y, x, height - 30)
            if is_hovered:
                gradient.setColorAt(0.0, QColor("#fbbf24")) # Hover: Bright amber
                gradient.setColorAt(1.0, QColor("#d97706"))
            else:
                gradient.setColorAt(0.0, QColor("#38bdf8")) # Sleek Light Blue
                gradient.setColorAt(1.0, QColor("#0284c7")) # Deep Blue
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 6, 6)
            
            # Draw values above the bar
            text_color = QColor("#f59e0b") if is_hovered else QColor("#94a3b8")
            painter.setPen(text_color)
            val_str = str(val)
            text_rect = painter.fontMetrics().boundingRect(val_str)
            painter.drawText(int(x + (bar_width - text_rect.width()) / 2), int(y - 6), val_str)

            # Draw X-axis category label (month name)
            if self.categories and i < len(self.categories):
                cat_str = self.categories[i]
                painter.setPen(QColor("#64748b"))
                cat_rect = painter.fontMetrics().boundingRect(cat_str)
                painter.drawText(int(x + (bar_width - cat_rect.width()) / 2), int(height - 10), cat_str)
            
    def draw_line_chart(self, painter, width, height):
        if not self.data:
            return
            
        max_val = max(self.data) if self.data else 1
        if max_val == 0:
            max_val = 1
        num_points = len(self.data)
        spacing = (width - 40) / (num_points - 1) if num_points > 1 else width
        
        points = []
        for i, val in enumerate(self.data):
            x = 20 + i * spacing
            y = height - ((val / max_val) * (height - 60)) - 30
            points.append(QPointF(x, y))
            
        # Draw dynamic Bezier path
        path = QPainterPath()
        if points:
            path.moveTo(points[0])
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i+1]
                # Control points for smooth bezier spline
                cp1 = QPointF(p1.x() + spacing / 2.0, p1.y())
                cp2 = QPointF(p2.x() - spacing / 2.0, p2.y())
                path.cubicTo(cp1, cp2, p2)
                
            # Create a closed path to draw a gradient fill underneath the curve
            fill_path = QPainterPath(path)
            fill_path.lineTo(points[-1].x(), height - 30)
            fill_path.lineTo(points[0].x(), height - 30)
            fill_path.closeSubpath()
            
            # Gradient fill under line chart
            fill_gradient = QLinearGradient(0, 0, 0, height)
            fill_gradient.setColorAt(0.0, QColor(16, 185, 129, 80)) # Emerald translucent
            fill_gradient.setColorAt(1.0, QColor(16, 185, 129, 0)) # Emerald transparent
            painter.fillPath(fill_path, QBrush(fill_gradient))
            
            # Draw the main line path on top of the fill
            pen = QPen(QColor("#10B981"), 3, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawPath(path)
            
        # Draw points and values
        bg_val = self.palette().window().color().value()
        bg_color = QColor("#020617") if bg_val < 128 else QColor("#FFFFFF")
        for i, val in enumerate(self.data):
            pt = points[i]
            is_hovered = (i == self.hovered_index)
            
            # Draw point dot
            painter.setBrush(QBrush(QColor("#fbbf24") if is_hovered else bg_color))
            painter.setPen(QPen(QColor("#f59e0b") if is_hovered else QColor("#10B981"), 2.5))
            painter.drawEllipse(pt, 5.5 if is_hovered else 4.5, 5.5 if is_hovered else 4.5)
            
            # Draw value above dot
            painter.setPen(QColor("#f59e0b") if is_hovered else QColor("#94a3b8"))
            val_str = str(val)
            text_rect = painter.fontMetrics().boundingRect(val_str)
            painter.drawText(int(pt.x() - text_rect.width() / 2), int(pt.y() - 10), val_str)

            # Draw X-axis label
            if self.categories and i < len(self.categories):
                cat_str = self.categories[i]
                painter.setPen(QColor("#64748b"))
                cat_rect = painter.fontMetrics().boundingRect(cat_str)
                painter.drawText(int(pt.x() - cat_rect.width() / 2), int(height - 10), cat_str)

    def mouseMoveEvent(self, event):
        width = self.width()
        height = self.height()
        if not self.data:
            self.hovered_index = -1
            self.update()
            return
            
        pos = event.position()
        mx = pos.x()
        my = pos.y()
        
        num_items = len(self.data)
        new_hover = -1
        
        if self.chart_type == "bar":
            spacing = 15
            bar_width = (width - (spacing * (num_items + 1))) / num_items
            for i in range(num_items):
                x = spacing + i * (bar_width + spacing)
                if x <= mx <= x + bar_width:
                     new_hover = i
                     break
        elif self.chart_type == "line":
            spacing = (width - 40) / (num_items - 1) if num_items > 1 else width
            for i in range(num_items):
                px = 20 + i * spacing
                if abs(mx - px) <= 25:
                     new_hover = i
                     break
                     
        if new_hover != self.hovered_index:
             self.hovered_index = new_hover
             self.update()
             
             # Show native tooltip
             if self.hovered_index != -1 and self.hovered_index < len(self.data):
                 from PySide6.QtWidgets import QToolTip
                 val = self.data[self.hovered_index]
                 month_name = self.categories[self.hovered_index] if (self.categories and self.hovered_index < len(self.categories)) else f"ستون {self.hovered_index + 1}"
                 tooltip_txt = f"{month_name}: {val} مورد"
                 QToolTip.showText(event.globalPosition().toPoint(), tooltip_txt, self)

    def leaveEvent(self, event):
        self.hovered_index = -1
        self.update()
        super().leaveEvent(event)

class ChartWidget(QFrame):
    def __init__(self, title: str, chart_type="bar", parent=None):
        super().__init__(parent)
        self.setObjectName("ChartWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Title
        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("chartTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_title)
        
        # Skeleton Chart
        self.chart = SkeletonChart(chart_type)
        layout.addWidget(self.chart)
        
    def update_chart_data(self, data, categories=None):
        self.chart.set_data(data, categories)
