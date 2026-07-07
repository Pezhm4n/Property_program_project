from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath

class SkeletonChart(QWidget):
    def __init__(self, chart_type="bar", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.data = []
        self.categories = {}
        
    def set_data(self, data, categories=None):
        self.data = data
        if categories:
            self.categories = categories
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
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
            self.data = [10, 15, 8, 12, 20, 25] # default mock
            
        max_val = max(self.data) if self.data else 1
        if max_val == 0:
            max_val = 1
        num_bars = len(self.data)
        spacing = 15
        bar_width = (width - (spacing * (num_bars + 1))) / num_bars
        
        for i, val in enumerate(self.data):
            bar_height = (val / max_val) * (height - 40)
            x = spacing + i * (bar_width + spacing)
            y = height - bar_height - 20
            
            # Gradient fill for bar
            gradient = QLinearGradient(x, y, x, height - 20)
            gradient.setColorAt(0.0, QColor("#38bdf8")) # Sleek Light Blue
            gradient.setColorAt(1.0, QColor("#0284c7")) # Deep Blue
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 6, 6)
            
            # Draw values
            text_color = QColor("#f8fafc") if self.palette().window().color().value() < 128 else QColor("#0f172a")
            painter.setPen(text_color)
            painter.drawText(x + (bar_width / 4), height - 5, f"{val}")
            
    def draw_line_chart(self, painter, width, height):
        if not self.data:
            self.data = [5, 12, 15, 8, 10, 18] # default mock
            
        max_val = max(self.data) if self.data else 1
        if max_val == 0:
            max_val = 1
        num_points = len(self.data)
        spacing = width / (num_points - 1) if num_points > 1 else width
        
        points = []
        for i, val in enumerate(self.data):
            x = i * spacing
            y = height - ((val / max_val) * (height - 40)) - 20
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
            fill_path.lineTo(points[-1].x(), height - 20)
            fill_path.lineTo(points[0].x(), height - 20)
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
            
        # Draw points with a themed hollow center
        bg_val = self.palette().window().color().value()
        bg_color = QColor("#020617") if bg_val < 128 else QColor("#FFFFFF")
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#10B981"), 2.5))
        for pt in points:
            painter.drawEllipse(pt, 4.5, 4.5)

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
        
    def update_chart_data(self, data):
        self.chart.set_data(data)
