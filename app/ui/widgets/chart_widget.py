from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

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
        grid_pen = QPen(QColor("#3F3F46"), 1, Qt.PenStyle.DashLine)
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
            gradient.setColorAt(0.0, QColor("#3B82F6")) # Sleek Blue
            gradient.setColorAt(1.0, QColor("#1D4ED8"))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 4, 4)
            
            # Draw values
            painter.setPen(QColor("#D4D4D8"))
            painter.drawText(x, height - 5, f"{val}")
            
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
            
        # Draw line path
        pen = QPen(QColor("#10B981"), 3, Qt.PenStyle.SolidLine) # Green
        painter.setPen(pen)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i+1])
            
        # Draw points
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#10B981"), 2))
        for pt in points:
            painter.drawEllipse(pt, 4, 4)

class ChartWidget(QFrame):
    def __init__(self, title: str, chart_type="bar", parent=None):
        super().__init__(parent)
        self.setObjectName("ChartWidget")
        self.setStyleSheet("""
            #ChartWidget {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; margin-bottom: 8px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_title)
        
        # Skeleton Chart
        self.chart = SkeletonChart(chart_type)
        layout.addWidget(self.chart)
        
    def update_chart_data(self, data):
        self.chart.set_data(data)
