from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QListWidget, QListWidgetItem,
                            QPushButton, QScrollArea, QApplication, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent, QTimer, QByteArray
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) # 忽略警告

class HorizontalSortWidget(QWidget):
    """完整的横向排序控件，包含所有必要方法"""
    orderChanged = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        # 主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        
        # 滚动区域设置
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置固定高度
        self.scroll_area.setMaximumHeight(80)
        self.scroll_area.setMinimumHeight(60)
        
        # 使用现代风格的滚动条
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QScrollBar:horizontal {
                height: 12px;
                background: #f0f0f0;
                border: none;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 6px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: none;
            }
        """)
        
        # 内容容器
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.list_layout = QHBoxLayout(self.container)
        self.list_layout.setContentsMargins(5, 5, 5, 5)
        self.list_layout.setSpacing(5)
        
        # 列表控件
        self.list_widget = QListWidget()
        self.list_widget.setFlow(QListWidget.LeftToRight)
        self.list_widget.setWrapping(False)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # 设置列表控件高度
        self.list_widget.setFixedHeight(60)
        
        # 去掉选中项目的虚线框
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 4px;
                margin: 0;
                outline: none;  /* 去掉焦点边框 */
            }
            QListWidget::item {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px 14px;
                margin: 2px;
                color: #1a1a1a;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QListWidget::item:hover {
                background: #f1f3f5;
                border-color: #d0d7dc;
            }
            QListWidget::item:selected {
                background: #e6f4ff;
                border: 1px solid #99ccf3;
                color: #004b8d;
            }
            QListWidget::item:selected:hover {
                background: #d1eaff;
                border-color: #80b9e6;
            }
            QListWidget::item:focus {
                border: none;  /* 去掉焦点边框 */
                outline: none; /* 去掉虚线框 */
            }
        """)
        
        # 去掉项目的焦点虚线框
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        
        self.list_layout.addWidget(self.list_widget)
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area, 1)
        
        # 控制按钮
        self.btn_layout = QVBoxLayout()
        self.btn_layout.setContentsMargins(0, 0, 5, 0)
        self.btn_layout.setSpacing(5)
        
        self.btn_left = self._create_button("arrow-left", "左", self.moveLeft)
        self.btn_right = self._create_button("arrow-right", "右", self.moveRight)
        
        self.btn_layout.addWidget(self.btn_left)
        self.btn_layout.addWidget(self.btn_right)
        self.btn_layout.addStretch()
        self.main_layout.addLayout(self.btn_layout)
        
        # 连接信号
        self.list_widget.model().rowsMoved.connect(self.emitOrderChanged)
        
        # 调整滚动条的步进值，使其滑动更平滑
        scroll_bar = self.scroll_area.horizontalScrollBar()
        scroll_bar.setSingleStep(10)
        scroll_bar.setPageStep(50)
        
    def _svg_to_icon(self, svg_code):
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        svg_bytes = QByteArray(svg_code.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)

    def _create_button(self, icon_name, tooltip, slot):
        btn = QPushButton()
        
        if icon_name == "arrow-left":
            svg_code = """
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            """
        else:
            svg_code = """
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            """
            
        btn.setIcon(self._svg_to_icon(svg_code))
        btn.setToolTip(tooltip)
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #f5f5f5;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
            QPushButton:focus {
                outline: none;  /* 去掉按钮的焦点边框 */
            }
        """)
        btn.clicked.connect(slot)
        return btn
        
    def moveLeft(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)
            self.emitOrderChanged()
            
    def moveRight(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1 and current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)
            self.emitOrderChanged()
            
    def addItems(self, items):
        self.list_widget.clear()
        for item in items:
            self.addItem(item)
            
    def addItem(self, text):
        item = QListWidgetItem(text)
        width = max(len(text) * 9 + 50, 60)
        item.setSizeHint(QSize(width, 40))
        self.list_widget.addItem(item)
        
    def getItems(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
    
    def emitOrderChanged(self):
        self.orderChanged.emit(self.getItems())
        
    def clear(self):
        self.list_widget.clear()
        
    def setItemStyle(self, style_sheet):
        self.list_widget.setStyleSheet(style_sheet)

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    
    sorter = HorizontalSortWidget()
    sorter.addItems([
        "项目1", 
        "中等长度项目", 
        "这是一个非常长的项目名称", 
        "短", 
        "另一个项目",
        "最后一个项目",
        "第七个项目",
        "第八个项目",
        "第九个项目"
    ])
    
    layout.addWidget(sorter)
    window.setGeometry(300, 300, 400, 120)
    window.show()
    
    sys.exit(app.exec_())