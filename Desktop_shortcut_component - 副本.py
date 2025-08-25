import sys, os, json, shutil, warnings, ctypes, winreg as reg
from ctypes import wintypes
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QDialog,QProgressBar,
                            QLabel, QPushButton, QScrollArea, QFileDialog, QMessageBox,QComboBox,QLineEdit,
                            QMenu, QAction, QInputDialog, QLayout, QGraphicsOpacityEffect, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QIcon, QPixmap, QConicalGradient, QLinearGradient, QPainter, QColor, QFont, QBrush, QPen, QPainterPath, QTransform
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QProcess, QSize, QByteArray, pyqtProperty, pyqtSignal, QTimer, QThread
import uuid
import subprocess
import re, time
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import ctypes
from ctypes import wintypes, Structure, POINTER, c_ulonglong, c_uint, c_int


HRESULT = ctypes.c_long

# save_shortcut_order
warnings.filterwarnings("ignore", category=DeprecationWarning) # 忽略警告
windll = ctypes.windll.LoadLibrary("shell32.dll")

def getDocPath(pathID=5):
    '''获取系统文件夹路径，pathID=5: 我的文档'''
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    windll.SHGetFolderPathW(None, pathID, None, 0, buf)
    return buf.value

# 定义路径
USER_RES = os.path.join(getDocPath(), "LingYun_Profile")
TEACHER_FILES = os.path.join(USER_RES, "教师文件")
CONFIG_PATH = os.path.join(USER_RES, "shortcut_config.json")

# 确保基础文件夹存在
os.makedirs(TEACHER_FILES, exist_ok=True)

# 默认九大学科
SUBJECTS = [
    "语文", "数学", "英语",
    "物理", "化学", "生物",
    "政治", "历史", "地理"
]

class ShortcutItem(QWidget):
    """单个快捷方式项（支持文件夹、EXE、UWP应用和分割线）"""
    def __init__(self, name, path, is_exe=False, is_uwp=False, icon_path=None, is_separator=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.path = path
        self.is_exe = is_exe  # 标识是否为EXE文件
        self.is_uwp = is_uwp  # 标识是否为UWP应用
        self.icon_path = icon_path  # 自定义图标路径
        self.is_separator = is_separator  # 标识是否为分割线
        self.icon_size = 64  # 图标尺寸
        self.max_text_length = 16  # 最大文字长度
        self.parent_widget = parent  # 保存父窗口引用
        self.setAcceptDrops(True)

        self.initUI()
        
    def initUI(self):
        if self.is_separator:
            # 分割线的UI
            self.separator_label = QLabel(self)
            self.separator_label.setMinimumHeight(100)

            self.setFixedWidth(2)
            
            self.separator_label.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 0.4);
                }
                QWidget::hover {
                    background-color: rgba(255, 255, 255, 0.9);
                }
            """)
            return

        
        self.setWindowIcon(QIcon(f'{USER_RES}/ico/LINGYUN.ico'))

        # 布局 - 垂直布局，确保图标和文字在项内居中
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # 图标 - 带大圆角
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(self.icon_size, self.icon_size)
        self.updateIcon()
        
        # 文字 - 限制长度
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setFixedWidth(self.icon_size)
        self.text_label.setWordWrap(True)
        font_family = read_from_registry("dsc_Typeface")
        font_size = read_from_registry("dsc_Typeface_size")
        if font_family == '':
            font_family = "微软雅黑"
        self.text_label.setFont(QFont(font_family, int(font_size), QFont.Bold))

        self.tip_label = QLabel("正在\n打开\n稍安勿躁", self)
        tip_font = QFont("微软雅黑", 25, QFont.Bold)
        self.tip_label.setFont(tip_font)
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setFixedSize(63, 85)
        self.tip_label.move((self.width() - 100) // 2, 0)
        self.tip_label.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 50, 50, 200);
                color: white;
                border-radius: 8px;
                font-size: 12px;
            }
        """)
        self.tip_label.hide()
        
        # 设置提示标签的透明度属性
        self.tip_label.setGraphicsEffect(QGraphicsOpacityEffect(self.tip_label))
        self.tip_label.graphicsEffect().setOpacity(1.0)
            
        # 处理名称
        display_name = self.name
        if len(display_name) > self.max_text_length:
            display_name = display_name[:self.max_text_length] + "..."
            
        self.text_label.setText(display_name)
        self.text_label.setStyleSheet("""
                                      color: white; 
                                      font-size: 13px;
                                      """)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.Style_str = """
            QWidget {
                border-radius: 12px;
                padding: 2px;
                background-color: transparent;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QWidget[dragOver="true"] {
                background-color: rgba(100, 200, 100, 0.3);
                border: 2px dashed #64C864;
            }                           
            QInputDialog {
                background-color: #f0f0f0;
            }
            QLabel { /* 输入框的提示文本 */
                color: #333;
                font-size: 14px;
            }
            QLineEdit { /* 输入框本身 */
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QPushButton { /* 对话框按钮 */
                background-color: #DCDCDC;
                color: black;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c8c8c8;
            }
            QPushButton:pressed {
                background-color: #D2D2D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QMessageBox {
                background-color: #000000;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
            QMessageBox:hover {
                background-color: #000000;
            }
            QMessageBox QLabel:hover {
                background-color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #525252; /* 按钮背景 */
                color: white; /* 按钮文本颜色 */
                border-radius: 6px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background-color: #666666; /* 按钮悬停效果 */
            }
        """
        self.setStyleSheet(self.Style_str)
        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        
    def updateIcon(self):
        """更新图标显示，完整显示内容并保留圆角"""
        try:
            # 定义内边距，确保图标内容不被圆角切割
            padding = 4  # 边距值，可根据需要调整
            draw_size = self.icon_size - padding * 2  # 实际绘制尺寸（减去两边边距）
            
            # 优先使用自定义图标
            if self.icon_path and os.path.exists(self.icon_path):
                # 缩放图标时考虑边距，确保内容完整
                pixmap = QPixmap(self.icon_path).scaled(
                    draw_size, draw_size, 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                
                # 创建带大圆角的图标
                rounded_pixmap = QPixmap(self.icon_size, self.icon_size)
                rounded_pixmap.fill(Qt.transparent)
                painter = QPainter(rounded_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # 创建圆角路径（整个图标区域）
                path = QPainterPath()
                path.addRoundedRect(0, 0, self.icon_size, self.icon_size, 12, 12)
                painter.setClipPath(path)
                
                # 在边距内绘制图标，避免被圆角切割
                x = (self.icon_size - pixmap.width()) // 2
                y = (self.icon_size - pixmap.height()) // 2
                painter.drawPixmap(x, y, pixmap)
                
                painter.end()
                self.icon_label.setPixmap(rounded_pixmap)
                return
                
            # 使用系统默认图标
            if self.is_exe:
                icon = QIcon.fromTheme("application-x-executable", QIcon())
            else:
                icon = QIcon.fromTheme("folder", QIcon())
                
            if icon.isNull():
                # 使用SVG作为默认图标（替代手绘图标）
                if not self.is_exe:
                    # 文件夹SVG代码
                    folder_svg = '''<svg t="1755498896615" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7432" width="200" height="200">
                    <path d="M510.4 243.2c8 27.2 33.6 44.8 60.8 44.8h259.2c0-35.2-28.8-64-64-64H504l6.4 19.2zM484.8 160h281.6c70.4 0 128 57.6 128 128v25.6c30.4 24 51.2 60.8 51.2 102.4v384c0 70.4-57.6 128-128 128H208c-70.4 0-128-57.6-128-128V224c0-70.4 57.6-128 128-128h164.8c46.4 0 89.6 25.6 112 64z m-112 0H208c-35.2 0-64 28.8-64 64v576c0 35.2 28.8 64 64 64h608c35.2 0 64-28.8 64-64V416c0-35.2-28.8-64-64-64H574.4c-56 0-105.6-36.8-121.6-89.6l-19.2-57.6c-8-27.2-32-44.8-60.8-44.8zM272 704h256c17.6 0 32 14.4 32 32s-14.4 32-32 32H272c-17.6 0-32-14.4-32-32s14.4-32 32-32z" fill="#ffffff" p-id="7433">
                    </path></svg>'''
                    
                    # 处理SVG尺寸以匹配绘制区域
                    processed_svg = folder_svg.replace(
                        'width="200" height="200"', 
                        f'width="{draw_size}" height="{draw_size}"'
                    )
                    
                    # 从SVG代码创建图标
                    svg_bytes = QByteArray(processed_svg.encode('utf-8'))
                    pixmap = QPixmap()
                    pixmap.loadFromData(svg_bytes)
                    icon = QIcon(pixmap)
                else:
                    # 保留原有的EXE默认图标绘制逻辑
                    pixmap = QPixmap(draw_size, draw_size)
                    color = QColor(70, 130, 180)
                    pixmap.fill(color)
                    
                    painter = QPainter(pixmap)
                    painter.setPen(QPen(QColor(255, 255, 255), 2))
                    painter.drawRect(5, 5, draw_size-10, draw_size-10)
                    painter.drawLine(7, draw_size//2, draw_size-7, draw_size//2)
                    painter.end()
                    icon = QIcon(pixmap)
                
            # 为系统图标添加大圆角（带边距）
            pixmap = icon.pixmap(draw_size, draw_size)
            rounded_pixmap = QPixmap(self.icon_size, self.icon_size)
            rounded_pixmap.fill(Qt.transparent)
            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 创建圆角路径
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.icon_size, self.icon_size, 12, 12)
            painter.setClipPath(path)
            
            # 在边距内绘制图标
            x = (self.icon_size - pixmap.width()) // 2
            y = (self.icon_size - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
            
            painter.end()
            self.icon_label.setPixmap(rounded_pixmap)
            
        except Exception as e:
            print(f"更新图标出错: {e}")
            # 出错时使用默认图标（带边距）
            pixmap = QPixmap(draw_size, draw_size)
            pixmap.fill(QColor(100, 100, 100, 128))
            
            rounded_pixmap = QPixmap(self.icon_size, self.icon_size)
            rounded_pixmap.fill(Qt.transparent)
            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.icon_size, self.icon_size, 12, 12)
            painter.setClipPath(path)
            
            x = (self.icon_size - pixmap.width()) // 2
            y = (self.icon_size - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
            
            painter.end()
            self.icon_label.setPixmap(rounded_pixmap)
        
    def showContextMenu(self, position):
        """显示右键菜单 - 如果是分割线则显示不同的菜单"""
        if self.is_separator:
            self.showSeparatorContextMenu(position)
        else:
            self.showNormalContextMenu(position)
    
    def showSeparatorContextMenu(self, position):
        """分割线的右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border-radius: 12px;
                padding: 5px 0;
                font-size: 12px;
            }
            QMenu::item {
                padding: 5px 20px;
                margin: 2px 5px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #525252;
            }
        """)
        
        # 删除分割线动作
        delete_action = QAction("删除分割线", self)
        delete_action.triggered.connect(self.deleteSeparator)
        
        menu.addAction(delete_action)
        menu.exec_(self.mapToGlobal(position))

    def showNormalContextMenu(self, position):
        """普通快捷方式的右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border-radius: 12px;
                padding: 5px 0;
                font-size: 12px;
            }
            QMenu::item {
                padding: 5px 20px;
                margin: 2px 5px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #525252;
            }
        """)
        
        # 打开动作
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.openTarget)
        
        # 重命名动作
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(self.renameTarget)
        
        # 更改图标动作
        change_icon_action = QAction("更改图标", self)
        change_icon_action.triggered.connect(self.changeIcon)
        
        # 分隔线
        menu.addSeparator()
        
        # 在左侧添加分割线
        add_separator_left = QAction("在左侧添加分割线", self)
        add_separator_left.triggered.connect(lambda: self.addSeparator("left"))
        
        # 在右侧添加分割线
        add_separator_right = QAction("在右侧添加分割线", self)
        add_separator_right.triggered.connect(lambda: self.addSeparator("right"))
        
        menu.addSeparator()
        
        # 删除动作
        delete_action = QAction("删除快捷方式", self)
        delete_action.triggered.connect(self.deleteShortcut)
        
        # 添加动作到菜单
        menu.addAction(open_action)
        menu.addAction(rename_action)
        menu.addAction(change_icon_action)
        menu.addSeparator()
        menu.addAction(add_separator_left)
        menu.addAction(add_separator_right)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def openTarget(self):
        """打开目标（文件夹、EXE、UWP应用、快捷方式或系统特殊文件夹）"""
        try:
            if self.is_uwp:
                # 启动UWP应用
                self.showOpeningTip()
                self.launchUwpApp(self.path)
                return
                
            # 检查是否是系统特殊文件夹（CLSID路径）
            if self.path.startswith("::{"):
                self.showOpeningTip()
                # 使用explorer打开特殊文件夹
                subprocess.Popen(f'explorer.exe "{self.path}"', shell=True)
                return
                
            # 对于常规路径，检查是否存在
            if not os.path.exists(self.path) and not self.is_uwp:
                QMessageBox.warning(self, "不存在", f"'{self.path}' 不存在")
                return
                
            if sys.platform.startswith('win32'):
                # Windows系统
                self.showOpeningTip()

                if self.is_exe:
                    # 启动EXE或快捷方式
                    if self.path.endswith('.url'):
                        # 处理.url快捷方式
                        self.openUrlShortcut(self.path)
                    else:
                        # 启动EXE文件
                        subprocess.Popen([self.path] + [])
                else:
                    # 打开文件夹
                    QProcess.startDetached('explorer.exe', [self.path])
            else:
                # 非Windows系统
                if self.is_exe:
                    subprocess.Popen([self.path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(['xdg-open', self.path])
        except Exception as e:
            QMessageBox.warning(
                self, "打开失败", 
                f"无法打开\n错误: {str(e)}"
            )

    def openUrlShortcut(self, url_path):
        """打开.url快捷方式"""
        try:
            # 读取.url文件内容获取URL
            with open(url_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找URL
            
            url_match = re.search(r'URL=(.*)', content)
            if url_match:
                url = url_match.group(1)
                # 使用默认浏览器打开URL
                QProcess.startDetached('cmd', ['/c', 'start', url])
            else:
                QMessageBox.warning(self, "打开失败", "无法解析快捷方式文件")
                
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开快捷方式: {str(e)}")

    def launchUwpApp(self, app_id):
        """启动UWP应用"""
        try:
            # 方法1: 使用 explorer shell 命令
            command = f'explorer shell:appsFolder\\{app_id}'
            result = subprocess.Popen(command, shell=True)
            
            # 方法2: 如果上面方法失败，使用 PowerShell 启动
            if result.returncode != 0:
                ps_command = f"Start-Process shell:appsFolder\\{app_id}"
                subprocess.run(["powershell", "-Command", ps_command], shell=True)
                
        except Exception as e:
            QMessageBox.warning(
                self, "启动失败", 
                f"无法启动UWP应用\n错误: {str(e)}"
            )

    def renameTarget(self):
        """重命名"""
        old_name = self.name
        new_name, ok = QInputDialog.getText(
            self, "重命名", "请输入新名称:", 
            text=self.name
        )
        
        if ok and new_name and new_name != self.name:
            # 更新显示名称
            self.name = new_name
            display_name = new_name
            if len(display_name) > self.max_text_length:
                display_name = display_name[:self.max_text_length] + "..."
            self.text_label.setText(display_name)

            # 通知父窗口更新数据
            if hasattr(self.parent_widget, 'updateShortcutName'):
                self.parent_widget.updateShortcutName(self, new_name)
    
    def changeIcon(self):
        """更改图标"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "",
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.ico);;所有文件 (*)",
            options=options
        )
        
        if file_path:
            # 保存图标路径
            self.icon_path = file_path
            # 更新显示
            self.updateIcon()
            
            # 通知父窗口更新数据
            if hasattr(self.parent_widget, 'updateShortcutIcon'):
                self.parent_widget.updateShortcutIcon(self, file_path)
    
    def deleteShortcut(self):
        """删除快捷方式"""
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除 '{self.name}' 的快捷方式吗?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 通知父窗口删除
            if hasattr(self.parent_widget, 'removeShortcut'):
                self.parent_widget.removeShortcut(self)
    
    def mouseDoubleClickEvent(self, event):
        """双击打开目标 - 分割线不响应双击"""

        if not self.is_separator and event.button() == Qt.LeftButton:
            self.openTarget()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if self.is_separator and event.button() == Qt.RightButton:
            self.showSeparatorContextMenu(event.pos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def addSeparator(self, position):
        """添加快捷方式分割线"""
        if hasattr(self.parent_widget, 'addSeparator'):
            self.parent_widget.addSeparator(self, position)
    
    def deleteSeparator(self):
        """删除分割线"""
        if hasattr(self.parent_widget, 'removeShortcut'):
            self.parent_widget.removeShortcut(self)

    def hideTipWithAnimation(self):
        """使用透明度动画隐藏提示"""
        self.animation = QPropertyAnimation(self.tip_label.graphicsEffect(), b"opacity")
        self.animation.setDuration(100)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: self.tip_label.hide())
        self.animation.start()

    def showOpeningTip(self):
        """显示'正在打开'提示并启动消失动画"""
        # 显示提示
        self.tip_label.raise_()
        self.tip_label.show()
        self.tip_label.graphicsEffect().setOpacity(1.0)
        
        # 3秒后启动消失动画
        QTimer.singleShot(3000, self.hideTipWithAnimation)


    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        
        if event.mimeData().hasUrls() and not self.is_separator:
            event.acceptProposedAction()

            # 使用QPalette动态改变背景色
            palette = self.palette()
            palette.setColor(self.backgroundRole(), QColor(100, 200, 100, 76))  # 30% 透明度
            self.setPalette(palette)
            self.setAutoFillBackground(True)
            # 设置边框样式
            self.setStyleSheet("border: 2px dashed #64C864; border-radius: 12px;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 恢复原始样式
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))  # 透明
        self.setPalette(palette)
        self.setAutoFillBackground(False)
        self.setStyleSheet(f"""{self.Style_str}
            border: none; border-radius: 12px;""")

    def dropEvent(self, event):
        """拖拽释放事件"""
        # 恢复原始样式
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))  # 透明
        self.setPalette(palette)
        self.setAutoFillBackground(False)
        self.setStyleSheet(f"""{self.Style_str}
            border: none; border-radius: 12px;""")
        if not event.mimeData().hasUrls() or self.is_separator:
            return
            
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.handleDroppedFile(file_path)
            
    def handleDroppedFile(self, file_path):
        """处理拖拽的文件"""
        try:
            if self.is_uwp:
                # UWP应用：直接打开，不处理文件
                self.openTarget()
                return
                
            if self.is_exe:
                # EXE应用：打开应用并传递文件路径作为参数
                self.launchExeWithFile(file_path)
            else:
                # 文件夹：复制文件到目标文件夹
                self.copyFileToFolder(file_path)
                
        except Exception as e:
            QMessageBox.warning(self, "操作失败", f"无法处理文件: {str(e)}")
            
    def launchExeWithFile(self, file_path):
        """启动EXE并传递文件路径"""
        try:
            if sys.platform.startswith('win32'):
                # 对于Windows系统
                if self.path.endswith('.url'):
                    # 处理.url快捷方式（不支持传递参数）
                    self.openUrlShortcut(self.path)
                else:
                    # 启动EXE并传递文件路径作为参数
                    subprocess.Popen([self.path, file_path])
            else:
                # 非Windows系统
                subprocess.Popen([self.path, file_path])
                
        except Exception as e:
            QMessageBox.warning(self, "启动失败", f"无法启动应用程序: {str(e)}")
            
    def copyFileToFolder2(self, file_path):
        """复制文件到目标文件夹"""
        try:
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "文件不存在", "拖拽的文件不存在")
                return
                
            target_path = os.path.join(self.path, os.path.basename(file_path))
            
            # 如果目标文件已存在，询问是否覆盖
            if os.path.exists(target_path):
                reply = QMessageBox.question(
                    self, "文件已存在", 
                    f"'{os.path.basename(file_path)}' 已存在，是否覆盖?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # 执行复制操作
            if os.path.isdir(file_path):
                # 复制文件夹
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(file_path, target_path)
            else:
                # 复制文件
                shutil.copy2(file_path, target_path)
                
            QMessageBox.information(self, "成功", "文件已复制到目标文件夹")
            
        except Exception as e:
            QMessageBox.warning(self, "复制失败", f"无法复制文件: {str(e)}")

    def copyFileToFolder(self, file_path):
        """复制文件到目标文件夹"""
        try:
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "文件不存在", "拖拽的文件不存在")
                return
                
            # 检查目标文件是否已存在
            target_name = os.path.basename(file_path)
            target_path = os.path.join(self.path, target_name)
            
            if os.path.exists(target_path):
                reply = QMessageBox.question(
                    self, "文件已存在", 
                    f"'{target_name}' 已存在，是否覆盖?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # 创建并显示进度窗口
            self.progress_window = CopyProgressWidget(file_path, self.path)
            self.progress_window.show()
            
            # 连接完成信号
            if hasattr(self.progress_window, 'copy_thread'):
                self.progress_window.copy_thread.finished.connect(
                    lambda success, msg: self.onCopyFinished(success, msg, target_name)
                )
                
        except Exception as e:
            QMessageBox.warning(self, "复制失败", f"无法复制文件: {str(e)}")
    
    def onCopyFinished(self, success, error_message, file_name):
        """复制完成回调"""
        if success:
            # 可以在这里添加复制成功后的操作
            pass
        elif error_message and error_message != "操作已取消":
            QMessageBox.warning(self, "复制失败", f"复制 '{file_name}' 失败: {error_message}")

class ScrollArea(QScrollArea):
    """自定义滚动区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setStyleSheet("background: transparent; border: none;")
        
        # 内部容器
        self.container = QWidget()
        self.container.setLayout(QHBoxLayout())
        self.container.layout().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 左对齐
        self.container.layout().setSpacing(10)  # 项之间的间距
        self.container.setStyleSheet("background: transparent;")
        self.setWidget(self.container)
        
        # 滑动相关变量
        self.dragging = False
        self.last_pos = QPoint()
        self.scroll_speed = 20
        
    def addShortcut(self, shortcut):
        """添加快捷方式"""
        self.container.layout().addWidget(shortcut)
        
    def removeShortcut(self, shortcut, remove=True):
        """移除快捷方式"""
        self.container.layout().removeWidget(shortcut)
        if remove:
            shortcut.deleteLater()
        
    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        delta = event.angleDelta().y()
        if delta > 0:
            # 向上滚动，向左移动
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - self.scroll_speed
            )
        else:
            # 向下滚动，向右移动
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + self.scroll_speed
            )
        event.accept()
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """鼠标移动事件（支持拖动滑动）"""
        if self.dragging:
            delta = self.last_pos - event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + delta.x()
            )
            self.last_pos = event.pos()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)

class ShortcutManager(QWidget):
    """快捷方式管理器主窗口"""
    # 可配置变量
    DEFAULT_WIDTH_RATIO = 0.5  # 默认宽度为屏幕的一半
    MAX_SHORTCUTS = 20  # 最大快捷方式数量
    CORNER_RADIUS = 30  # 窗口大圆角
    update_signal = pyqtSignal(dict)  # 接收外部更新指令
    position_changed = pyqtSignal(int, int)
    
    # 光环样式常量
    STYLE_FULL_COLOR_RING = 0
    STYLE_TOP_BOTTOM_GRADIENT = 1
    STYLE_DOUBLE_LAYER_RING = 2
    
    def __init__(self, initial_params=None, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self.opacity = float(read_from_registry("dsc_tran")) / 100
        self.shortcuts = []  # 存储所有快捷方式

        hex_color = read_from_registry("dsc_Color").lstrip('#')
        self.R = int(hex_color[0:2], 16)
        self.G = int(hex_color[2:4], 16)
        self.B = int(hex_color[4:6], 16)

        # 设置图标
        self.setWindowIcon(QIcon(f'{USER_RES}/ico/LINGYUN.ico'))

        self.initUI()
        self.loadExistingItems()  # 加载已存在的项目

        self.setAcceptDrops(False)

        self.update_signal.connect(self.handle_update)
        
        if self.read_from_registry("dsc_lock") == "True":
            self.locked = True
        else:
            self.locked = False

        # 记录上一次位置
        self.last_pos = self.pos()
        # 定时器用于检测变化是否结束
        self.change_timer = QTimer(self)
        self.change_timer.setSingleShot(True)  # 单次触发
        self.change_timer.setInterval(300)  # 300ms无变化视为结束
        self.change_timer.timeout.connect(self._on_position_stable)

        # 光环相关属性
        self._angle = 0
        self._sub_angle = 0
        self._style = self.STYLE_FULL_COLOR_RING

        halo_switch = read_from_registry("dsc_halo_switch")
        if halo_switch == "True":
            self.is_running = True
            self.is_enabled = True
        else:
            self.is_running = False
            self.is_enabled = False

        # 初始化光环动画
        self.init_glow_animation()
        
    def initUI(self):
        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnBottomHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)



        # 防止乱码
        # get_all_applist_thread = threading.Thread(target=get_all_apps)
        # get_all_applist_thread.start()
        
        # 创建主布局容器
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)

        main_layout.setContentsMargins(10, 0, 0, 0)  # 去除布局边距

        main_layout.setSizeConstraint(QLayout.SetNoConstraint)  # 取消布局尺寸约束

        self.setMinimumWidth(0)  # 允许窗口缩放到任意小宽度
        self.setMinimumSize(0, self.minimumHeight())  # 只限制最小高度
        
        # 滚动区域 - 主要内容区
        self.scroll_area = ScrollArea()
        main_layout.addWidget(self.scroll_area, 1)
        
        # 右侧细长的收起按钮
        svg_code = '''<svg t="1755498412657" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4111" width="200" height="200"><path d="M593.95 770.426c2.908-4.234 4.614-9.38 4.614-14.892s-1.706-10.66-4.614-14.923L431.085 577c-10.322-10.325-10.322-27.044 0-37.382l158.6-159.118c5.377-4.843 8.773-11.818 8.773-19.614 0-14.602-11.833-26.433-26.434-26.433-5.954 0-11.42 1.98-15.836 5.299l-5.3 5.3L375.02 520.937c-20.65 20.647-20.65 54.114 0 74.763l177.557 177.591 1.81 1.795c4.692 4.264 10.904 6.885 17.741 6.885 9.06-0.002 17.054-4.571 21.82-11.545z" fill="#ffffff" p-id="4112"></path></svg>'''
        # 创建带SVG的旋转按钮
        self.toggle_button = RotatableSvgButton(svg_code)
        self.toggle_button.setFixedSize(30, 100)
        self.toggle_button.setStyleSheet("""                        
            QPushButton {
                background-color: rgba(255, 255, 255, 0.0);
                border-radius: 12px;
                color: white;
                margin-left: 5px;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.toggle_button.clicked.connect(self.toggleExpand)
        self.toggle_button.setToolTip("点击收起/展开快捷方式列表")
        self.toggle_button.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时的手型
        if read_from_registry("dsc_put") == "False":
            self.toggle_button.hide()
        # 设置主窗口布局
        window_layout = QHBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 10, 0)
        window_layout.addWidget(main_container)
        
        # 设置初始位置和大小
        self.setInitialGeometry()
        
        # 创建右键菜单（用于添加新项）
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMainContextMenu)

        window_layout.addWidget(self.toggle_button)

        self.setStyleSheet("""
            QInputDialog {
                background-color: #f0f0f0;
            }
            QLabel { /* 输入框的提示文本 */
                color: #333;
                font-size: 14px;
            }
            QLineEdit { /* 输入框本身 */
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QPushButton { /* 对话框按钮 */
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QMessageBox {
                background-color: #000000;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
            QMessageBox:hover {
                background-color: #000000;
            }
            QMessageBox QLabel:hover {
                background-color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #525252; /* 按钮背景 */
                color: white; /* 按钮文本颜色 */
                border-radius: 6px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background-color: #666666; /* 按钮悬停效果 */
            }
        """)
        
        # 窗口拖动相关
        self.dragging = False
        self.drag_start_pos = QPoint()

    def moveEvent(self, event):
        """窗口移动事件（位置变化时触发）"""
        current_pos = self.pos()
        
        # 位置确实发生了变化
        if current_pos != self.last_pos:
            self.last_pos = current_pos
            # 重启定时器（如果300ms内再次移动则重新计时）
            self.change_timer.start()
            
        super().moveEvent(event)
        
    def _on_position_stable(self):
        """位置稳定后发送通知"""
        x, y = self.pos().x(), self.pos().y()
        self.position_changed.emit(x, y)
        # 可以在这里同时更新注册表
        self._update_position_to_registry(x, y)
        
    def _update_position_to_registry(self, x, y):
        """将位置更新到注册表（如果需要）"""
        try:
            import winreg as reg
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
            reg.SetValueEx(registry_key, "dsc_x", 0, reg.REG_SZ, str(x))
            reg.SetValueEx(registry_key, "dsc_y", 0, reg.REG_SZ, str(y))
            reg.CloseKey(registry_key)
        except Exception as e:
            print(f"更新位置到注册表失败: {e}")

    def read_from_registry(self, value_name):
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes', 0, reg.KEY_QUERY_VALUE) as key:
                value, regtype = reg.QueryValueEx(key, value_name)
                return value
        except FileNotFoundError:
            return None
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取注册表失败：{e}')
            return None

    def handle_update(self, param, value = None):
        """处理外部更新指令"""
        # 更新参数
        #self.params.update(params)
        
        # 根据参数执行相应更新
        '''
        if 'icons' in params:
            self.update_icons(params['icons'])
        if 'width' in params:
            self.resize(params['width'], self.height())
        if 'visibility' in params:
            self.setVisible(params['visibility'])
        '''

        if param == 'default_xy':
            x = (screen_width - width) // 2
            y = screen_height - height - 20
            self.setGeometry(x, y, self.width(), self.height())

        if param == 'switch':
            if value == 'True':
                self.show()
            else:
                self.hide()
        
        if param == 'lock':
            if value == 'True':
                self.locked = True
            else:
                self.locked = False
        
        if param == 'Typeface':
            # 更新字体
            self.setFont(value)
            
            for shortcut in self.shortcuts:
                try:
                    shortcut.text_label.setFont(QFont(value.family(), value.pointSize(), QFont.Bold))
                except:pass
        if param == 'default_font':
            # 更新默认字体
            font_family = read_from_registry("dsc_Typeface")
            font_size = read_from_registry("dsc_Typeface_size")
            if font_family == '':
                font_family = "微软雅黑"
            
                for shortcut in self.shortcuts:
                    try:
                        shortcut.text_label.setFont(QFont(font_family, int(font_size), QFont.Bold))
                    except:pass
        if param == "put":
            if read_from_registry("dsc_put") == "True":
                self.toggle_button.show()
            else:
                self.toggle_button.hide()
   
                if self.is_expanded == False:
                    self.toggleExpand()
        
        if param == "color":
            # 更新颜色
            hex_color = value.lstrip('#')
            # 解析RR、GG、BB分量
            self.R = int(hex_color[0:2], 16)
            self.G = int(hex_color[2:4], 16)
            self.B = int(hex_color[4:6], 16)
            self.update()

        if param == "tran":
            # 更新透明度
            self.opacity = float(value) / 100
            self.update()

        if param == "halo":
            if value == "True":
                self.is_running = True
                self.is_enabled = True                
                self.main_animation.start()
                self.sub_animation.start()
                self.update()

            else:
                self.main_animation.stop()
                self.sub_animation.stop()
                self.is_running = False
                self.is_enabled = False
                self.update()
        
        if param == "length":
            self.resize(int(value), self.height())
            self.original_width = int(value)


    def update_icons(self, icon_data):
        """更新图标（示例方法）"""
        # 根据传入的图标数据更新界面
        # ...
        
    def get_current_state(self):
        """获取当前状态（供外部查询）"""
        # 生成带临时编号的快捷方式信息列表
        shortcut_info = []
        for idx, shortcut in enumerate(self.shortcuts):
            shortcut_info.append({
                'temp_id': idx,  # 临时编号，用于排序后定位
                'name': shortcut.name,
                'path': shortcut.path,
                'is_exe': shortcut.is_exe
            })
        return {
            'width': self.width(),
            'is_expanded': self.is_expanded,
            'visible': self.isVisible(),
            'shortcuts': shortcut_info,  # 返回带临时编号的信息列表
            # 其他需要暴露的状态
        }
    
    def updateShortcutIcon(self, shortcut, icon_path):
        """更新快捷方式图标路径"""
        # 可以在这里添加保存图标路径到配置文件的逻辑
        pass

    def sort_shortcuts(self, sorted_temp_ids):
        """根据排序后的临时编号列表重新排列快捷方式"""
        try:
            # 验证输入有效性
            if not isinstance(sorted_temp_ids, list):
                raise ValueError("排序信息必须是列表类型")
            
            # 确保每个快捷方式都有唯一的temp_id属性
            for idx, shortcut in enumerate(self.shortcuts):
                if not hasattr(shortcut, 'temp_id'):
                    shortcut.temp_id = idx  # 首次初始化

            # 基于快捷方式自身的temp_id创建映射，而非依赖列表索引
            temp_id_map = {shortcut.temp_id: shortcut for shortcut in self.shortcuts}
            
            # 验证输入的临时编号是否存在
            valid_ids = []
            invalid_ids = []
            for tid in sorted_temp_ids:
                if tid in temp_id_map:
                    valid_ids.append(tid)
                else:
                    invalid_ids.append(tid)
            
            if invalid_ids:
                print(f"警告：存在无效的临时编号 {invalid_ids}")
            
            # 按输入顺序排列有效项
            sorted_shortcuts = [temp_id_map[tid] for tid in valid_ids]
            
            # 处理未在排序中的项目（保持原有顺序）
            existing_tids = set(valid_ids)
            remaining_shortcuts = [
                s for s in self.shortcuts 
                if s.temp_id not in existing_tids
            ]
            
            final_shortcuts = sorted_shortcuts + remaining_shortcuts
            
            # 清空布局（可靠方式）
            layout = self.scroll_area.container.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            
            # 更新并重新添加
            self.shortcuts = final_shortcuts
            for shortcut in self.shortcuts:
                layout.addWidget(shortcut)
            
            # 输出最终排序结果
            # final_order = {s.name: i for i, s in enumerate(self.shortcuts)}

            save_shortcut_order(self.shortcuts)

            return True
            
        except Exception as e:
            QMessageBox.warning(
                self, "排序失败", 
                f"无法完成排序\n错误: {str(e)}"
            )
            return False

    def setInitialGeometry(self):
        """设置初始位置和大小"""
        global screen_height, screen_width, width, height
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # 默认宽度为屏幕一半

        width = self.read_from_registry('dsc_length')
        if width == "None":
            width = int(screen_width * self.DEFAULT_WIDTH_RATIO)  
        else:
            width = int(width)
        # 高度固定
        height = 120
        
        x = int(self.read_from_registry('dsc_x'))
        y = int(self.read_from_registry('dsc_y'))

        # 设置位置（底部居中）
        if x is None or y is None or x < 0 or y < 0:
            x = (screen_width - width) // 2
            y = screen_height - height - 20
        
        self.setGeometry(x, y, width, height)
        self.original_geometry = self.geometry()
        self.original_width = width  # 保存原始宽度
        
    def loadExistingItems(self):
        """加载已存在的项目，支持分割线和系统快捷方式"""
        config = load_shortcut_order()
        config_shortcuts = []
        existing_items = []

        # 从配置文件加载
        if config:
            valid_shortcuts = []
            for item in config:
                if item.get("is_separator", False):
                    # 加载分割线
                    separator = ShortcutItem("separator", "", is_separator=True, parent=self)
                    valid_shortcuts.append(separator)
                    continue
                    
                if item["name"] == "__teacher_file__":
                    continue
                    
                path = item["path"]
                config_shortcuts.append(path)
                
                # 处理系统快捷方式
                if item.get("is_system", False):
                    shortcut = SystemShortcutItem(
                        item["name"], path, 
                        parent=self
                    )
                    valid_shortcuts.append(shortcut)
                    continue
                    
                # 处理UWP应用
                if item.get("is_uwp", False):
                    shortcut = ShortcutItem(
                        item["name"], path, 
                        is_exe=False, is_uwp=True,
                        icon_path=item.get("icon_path"),
                        parent=self
                    )
                    valid_shortcuts.append(shortcut)
                    continue

                # 处理文件夹（不存在则创建）
                if not item["is_exe"]:
                    if not os.path.exists(path):
                        os.makedirs(path, exist_ok=True)
                    shortcut = ShortcutItem(
                        item["name"], path, 
                        is_exe=False, 
                        icon_path=item.get("icon_path"),
                        parent=self
                    )
                    valid_shortcuts.append(shortcut)
                # 处理EXE（不存在则跳过）
                else:
                    if os.path.exists(path) and (path.endswith('.exe') or path.endswith('.EXE')):
                        shortcut = ShortcutItem(
                            item["name"], path, 
                            is_exe=True, 
                            icon_path=item.get("icon_path"),
                            parent=self
                        )
                        valid_shortcuts.append(shortcut)
            
            self.shortcuts = valid_shortcuts
            existing_items = valid_shortcuts
            for s in self.shortcuts:
                self.scroll_area.addShortcut(s)
        else:
            self.shortcuts = []
            config_shortcuts = []
            existing_items = []

            # 确保默认学科文件夹存在并添加
            for subject in SUBJECTS:
                subject_path = os.path.join(TEACHER_FILES, subject)  # 使用全局变量
                os.makedirs(subject_path, exist_ok=True)
                
                # 检查是否已添加，避免重复
                if not any(s.path == subject_path for s in self.shortcuts):
                    shortcut = ShortcutItem(subject, subject_path, is_exe=False, parent=self)
                    self.shortcuts.append(shortcut)
                    self.scroll_area.addShortcut(shortcut)
                    config_shortcuts.append(subject_path)
                    existing_items.append(shortcut)  # 保存为ShortcutItem对象

        # 扫描本地教师文件夹，检测新增文件夹
        new_items = []  # 存储新增的ShortcutItem对象
        if os.path.exists(TEACHER_FILES):  # 使用全局变量
            for item in os.listdir(TEACHER_FILES):
                item_path = os.path.join(TEACHER_FILES, item)
                # 只处理文件夹，且不在配置中，且不是默认学科
                if (os.path.isdir(item_path) and 
                    item not in SUBJECTS and 
                    item_path not in config_shortcuts):
                    
                    # 直接创建ShortcutItem对象，而非字典
                    new_shortcut = ShortcutItem(
                        item, item_path,
                        is_exe=False,
                        icon_path=None,  # 可根据需要设置默认图标
                        parent=self
                    )
                    new_items.append(new_shortcut)

        # 添加新增文件夹并更新配置
        if new_items:
            print(f"发现 {len(new_items)} 个新增文件夹，已自动添加")
            
            # 添加到界面
            for shortcut in new_items:
                self.shortcuts.append(shortcut)
                self.scroll_area.addShortcut(shortcut)
            
            # 更新配置文件：合并原有ShortcutItem和新增ShortcutItem
            updated_items = existing_items + new_items  # 都是ShortcutItem对象
            save_shortcut_order(updated_items)  # 现在传入的是对象列表，可正常访问s.name

    def showMainContextMenu(self, position):
        """主窗口右键菜单，用于添加新项和移动文件夹"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border-radius: 12px;
                padding: 5px 0;
                font-size: 12px;
            }
            QMenu::item {
                padding: 5px 20px;
                margin: 2px 5px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #525252;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444444;
                margin: 5px 10px;
            }
        """)

        # 添加应用程序快捷方式（新增）
        add_app_action = QAction("添加本机已安装的UWP应用程序", self)
        add_app_action.triggered.connect(self.addNewAppShortcut)
        
        # 添加文件夹快捷方式
        add_folder_action = QAction("添加文件夹快捷方式", self)
        add_folder_action.triggered.connect(self.addNewFolderShortcut)
        
        # 添加EXE快捷方式
        add_exe_action = QAction("添加EXE快捷方式", self)
        add_exe_action.triggered.connect(self.addNewExeShortcut)

        # 添加系统快捷方式子菜单
        add_system_menu = QMenu("添加系统快捷方式", self)
        add_system_menu.setStyleSheet(menu.styleSheet())
        
        # 系统快捷方式选项
        computer_action = QAction("此电脑", self)
        computer_action.triggered.connect(lambda: self.addSystemShortcut("此电脑", "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}"))
        
        recycle_action = QAction("回收站", self)
        recycle_action.triggered.connect(lambda: self.addSystemShortcut("回收站", "::{645FF040-5081-101B-9F08-00AA002F954E}"))
        
        control_panel_action = QAction("控制面板", self)
        control_panel_action.triggered.connect(lambda: self.addSystemShortcut("控制面板", "::{26EE0668-A00A-44D7-9371-BEB064C98683}"))
        
        network_action = QAction("网络", self)
        network_action.triggered.connect(lambda: self.addSystemShortcut("网络", "::{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}"))
        
        desktop_action = QAction("桌面", self)
        desktop_action.triggered.connect(lambda: self.addSystemShortcut("桌面", "::{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}"))
        
        # 添加到系统菜单
        add_system_menu.addAction(computer_action)
        add_system_menu.addAction(recycle_action)
        add_system_menu.addAction(control_panel_action)
        add_system_menu.addAction(network_action)
        add_system_menu.addAction(desktop_action)
        
        # 分隔线
        menu.addSeparator()
        
        # 移动教师文件夹
        move_folder_action = QAction("移动教师文件文件夹", self)
        move_folder_action.triggered.connect(self.changeTeacherFilesPath)
        
        # 添加动作到菜单
        menu.addAction(add_app_action)
        menu.addAction(add_folder_action)
        menu.addAction(add_exe_action)
        menu.addMenu(add_system_menu)
        menu.addSeparator()
        menu.addAction(move_folder_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def addSeparator(self, shortcut, position):
        """在指定快捷方式的上方或下方添加分割线"""
        index = self.shortcuts.index(shortcut)

        if position == "left":
            insert_index = index
        else:  # "right"
            insert_index = index + 1
        if insert_index == 0 or insert_index == len(self.shortcuts):
            QMessageBox.warning(self, "警告", "无法在此处添加分割线")
            return     

        if self.shortcuts[insert_index - 1].is_separator or self.shortcuts[insert_index].is_separator:
            QMessageBox.warning(self, "警告", "已有分割线")
            return
           
        separator = ShortcutItem("separator", "", is_separator=True, parent=self)
        self.shortcuts.insert(insert_index, separator)
        
        # 更新界面
        layout = self.scroll_area.container.layout()
        layout.insertWidget(insert_index, separator)
        
        save_shortcut_order(self.shortcuts)
    
    def removeShortcut(self, shortcut):
        """移除快捷方式或分割线"""
        if shortcut in self.shortcuts:
            # 从列表中移除
            self.shortcuts.remove(shortcut)
            # 从界面中移除
            self.scroll_area.removeShortcut(shortcut)

            save_shortcut_order(self.shortcuts)
            
            # 如果是文件夹快捷方式，询问是否删除实际文件夹
            if not shortcut.is_exe and not shortcut.is_uwp and not shortcut.is_separator:
                reply = QMessageBox.question(
                    self, "删除文件夹", 
                    f"是否同时删除实际文件夹 '{shortcut.path}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        if os.path.exists(shortcut.path):
                            shutil.rmtree(shortcut.path)
                    except Exception as e:
                        QMessageBox.warning(
                            self, "删除失败", 
                            f"无法删除文件夹\n错误: {str(e)}"
                        )

    def addNewFolderShortcut(self,filename=None):
        """添加新的文件夹快捷方式"""
        # 检查是否已达到最大数量
        if len(self.shortcuts) >= self.MAX_SHORTCUTS:
            QMessageBox.information(self, "已达上限", f"最多只能添加 {self.MAX_SHORTCUTS} 个快捷方式")
            return
            
        # 获取文件夹名称
        if filename == None or filename == False:
            name, ok = QInputDialog.getText(self, "新建文件夹快捷方式", "请输入文件夹名称:")
            if not ok or not name:
                return
        else:
            name = filename

        if any(s.name == name for s in self.shortcuts):
            reply = QMessageBox.question(
                self, "名字重复", 
                f"名称为 '{name}' 的文件夹已经存在",
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
        # 创建新文件夹
        new_path = os.path.join(TEACHER_FILES, name)
        try:
            os.makedirs(new_path, exist_ok=True)
            
            # 创建并添加快捷方式
            shortcut = ShortcutItem(name, new_path, is_exe=False, parent=self)
            self.shortcuts.append(shortcut)
            self.scroll_area.addShortcut(shortcut)
            
        except Exception as e:
            QMessageBox.warning(
                self, "创建失败", 
                f"无法创建文件夹\n错误: {str(e)}"
            )

        save_shortcut_order(self.shortcuts)
    
    def addNewExeShortcut(self, exe_path=None, icon_path=None, name=None):
        """添加新的EXE快捷方式，要求用户提供图标"""
        # 检查是否已达到最大数量
        if len(self.shortcuts) >= self.MAX_SHORTCUTS:
            QMessageBox.information(self, "已达上限", f"最多只能添加 {self.MAX_SHORTCUTS} 个快捷方式")
            return
        
        options = QFileDialog.Options() if (exe_path is None or icon_path is None or name is None) else None
        
        # 选择EXE文件
        if exe_path is None or exe_path == False:
            exe_path, _ = QFileDialog.getOpenFileName(
                self, "选择EXE文件", "",
                "可执行文件 (*.exe);;所有文件 (*)",
                options=options
            )
            
            if not exe_path or not os.path.isfile(exe_path) or not (exe_path.lower().endswith('.exe') or exe_path.lower().endswith('.EXE')):

                QMessageBox.warning(self, "无效选择", "请选择有效的EXE文件")
                return
        
        # 获取显示名称
        if name is None:
            default_name = os.path.splitext(os.path.basename(exe_path))[0]
            name, ok = QInputDialog.getText(
                self, "EXE快捷方式名称", "请输入显示名称:",
                text=default_name
            )
            if not ok or not name:
                return
        
        copy_Icon = False 
        # 创建临时图标目录（如果不存在）
        temp_dir = os.path.join(USER_RES, "temp_icons")
        os.makedirs(temp_dir, exist_ok=True)
        temp_icon_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.ico")

        if extract_icon_with_key(exe_path,1,temp_icon_path):
            icon_path = temp_icon_path
            copy_Icon = True
        else:
            copy_Icon = False
            # 要求用户提供图标     
            if icon_path is None:
                QMessageBox.information(self, "选择图标", "请为该EXE文件选择一个图标")
                icon_path, _ = QFileDialog.getOpenFileName(
                    self, "选择图标文件", "",
                    "图像文件 (*.png *.jpg *.jpeg *.bmp *.ico);;所有文件 (*)",
                    options=options
                )
                
                if not icon_path or not os.path.isfile(icon_path):
                    QMessageBox.warning(self, "无效图标", "请选择有效的图像文件作为图标")
                    return
        
        if not copy_Icon:
            final_icon_path = self.copy_icon_to_temp(icon_path)
        else:
            final_icon_path = temp_icon_path
        
        # 如果是ICO文件，额外处理提取最佳质量图标
        if icon_path.lower().endswith('.ico'):
            final_icon_path = self.extract_good_icon(icon_path, temp_icon_path)

        # 创建并添加快捷方式
        shortcut = ShortcutItem(name, exe_path, is_exe=True, icon_path=final_icon_path, parent=self)
        self.shortcuts.append(shortcut)
        self.scroll_area.addShortcut(shortcut)

        save_shortcut_order(self.shortcuts)

    def addNewAppShortcut(self):
        """添加新的应用程序快捷方式（支持UWP和桌面应用）"""
        if len(self.shortcuts) >= self.MAX_SHORTCUTS:
            QMessageBox.information(self, "已达上限", f"最多只能添加 {self.MAX_SHORTCUTS} 个快捷方式")
            return
        
        # 获取所有应用
        all_apps = get_all_apps()
        if not all_apps:
            QMessageBox.information(self, "提示", "未找到可用的应用程序")
            return
        
        # 创建选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择应用程序")
        dialog.setFixedSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 筛选选项
        filter_layout = QHBoxLayout()
        filter_label = QLabel("筛选类型:(暂仅可选择UWP应用)")
        filter_combo = QComboBox()
        #filter_combo.addItem("所有应用", "all")
        filter_combo.addItem("UWP应用", "uwp")
        #filter_combo.addItem("桌面应用", "desktop")
        #filter_combo.addItem("快捷方式", "shortcut")
        filter_combo.setCurrentIndex(0)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(filter_combo)
        layout.addLayout(filter_layout)
        
        # 搜索框
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("搜索应用...")
        layout.addWidget(search_edit)
        
        # 应用列表
        list_widget = QListWidget()
        layout.addWidget(list_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        def update_app_list():
            """更新应用列表"""
            list_widget.clear()
            filter_type = filter_combo.currentData()
            search_text = search_edit.text().lower()
            
            for app in all_apps:
                if (filter_type == "all" or app['type'] == filter_type) and \
                search_text in app['name'].lower():
                    item = QListWidgetItem(app['name'])
                    item.setData(Qt.UserRole, app)
                    
                    # 显示应用类型
                    type_text = ""
                    if app['type'] == "uwp":
                        type_text = " (UWP应用)"
                    elif app['type'] == "desktop":
                        type_text = " (exe桌面应用)"
                    elif app['type'] == "shortcut":
                        type_text = " (快捷方式)"
                    
                    item.setText(app['name'] + type_text)
                    list_widget.addItem(item)
        
        # 连接信号
        filter_combo.currentIndexChanged.connect(update_app_list)
        search_edit.textChanged.connect(update_app_list)
        
        # 初始更新
        update_app_list()
        
        if dialog.exec_() == QDialog.Accepted:
            selected_item = list_widget.currentItem()
            if selected_item:
                app_data = selected_item.data(Qt.UserRole)
                
                app_name = app_data['name']
                app_id = app_data['app_id']
                app_type = app_data['type']



                # 让用户选择图标文件
                options = QFileDialog.Options()
                icon_path, _ = QFileDialog.getOpenFileName(
                    self, f"选择 {app_name} 的图标文件", "",
                    "图像文件 (*.png *.jpg *.jpeg *.bmp *.ico);;所有文件 (*)",
                    options=options
                )
                
                if not icon_path or not os.path.isfile(icon_path):
                    QMessageBox.warning(self, "无效图标", "请选择有效的图像文件作为图标")
                    return
                
                temp_dir = os.path.join(USER_RES, "temp_icons")
                os.makedirs(temp_dir, exist_ok=True)
                    

                # 复制图标到临时目录
                final_icon_path = self.copy_icon_to_temp(icon_path)

                if icon_path.lower().endswith('.ico'):
                    try:
                        icon = QIcon(final_icon_path)
                        if not icon.isNull():
                            available_sizes = icon.availableSizes()
                            if available_sizes:
                                best_size = max(available_sizes, key=lambda s: s.width() * s.height())
                                pixmap = icon.pixmap(best_size)
                                png_filename = f"{uuid.uuid4().hex}.png"
                                png_icon_path = os.path.join(temp_dir, png_filename)
                                if pixmap.save(png_icon_path, "PNG"):
                                    final_icon_path = png_icon_path
                                    #print(f"已提取最佳ICO图标到: {png_icon_path}")
                        
                    except Exception as e:
                        pass
                        #print(f"处理ICO文件失败: {e}, 使用复制后的ICO文件")

                
                # 创建并添加快捷方式
                if app_type == "uwp":
                    # UWP 应用
                    shortcut = ShortcutItem(
                        app_name, app_id, 
                        is_exe=False, is_uwp=True,
                        icon_path=final_icon_path, 
                        parent=self
                    )
                else:
                    # 桌面应用或快捷方式
                    shortcut = ShortcutItem(
                        app_name, app_id, 
                        is_exe=True, is_uwp=False,
                        icon_path=final_icon_path, 
                        parent=self
                    )
                
                self.shortcuts.append(shortcut)
                self.scroll_area.addShortcut(shortcut)
                
                save_shortcut_order(self.shortcuts)

    def addSystemShortcut(self, name, path):
        """添加系统快捷方式"""
        if len(self.shortcuts) >= self.MAX_SHORTCUTS:
            QMessageBox.information(self, "已达上限", f"最多只能添加 {self.MAX_SHORTCUTS} 个快捷方式")
            return
        
        # 检查是否已存在
        if any(s.path == path for s in self.shortcuts):
            QMessageBox.information(self, "已存在", f"'{name}' 快捷方式已存在")
            return
        
        # 创建系统快捷方式
        shortcut = SystemShortcutItem(name, path, parent=self)
        self.shortcuts.append(shortcut)
        self.scroll_area.addShortcut(shortcut)
        
        # 保存配置
        save_shortcut_order(self.shortcuts)

    def copy_icon_to_temp(self, original_icon_path):
        """复制图标文件到临时目录"""
        try:
            # 创建临时目录
            temp_dir = os.path.join(USER_RES, "temp_icons")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 获取文件扩展名
            file_extension = os.path.splitext(original_icon_path)[1].lower()
            
            # 生成唯一的文件名
            temp_filename = f"{uuid.uuid4().hex}{file_extension}"
            temp_icon_path = os.path.join(temp_dir, temp_filename)
            
            # 复制文件
            shutil.copy2(original_icon_path, temp_icon_path)
            
            #print(f"图标已复制到: {temp_icon_path}")
            return temp_icon_path
            
        except Exception as e:
            #print(f"复制图标失败: {e}")
            return original_icon_path  # 如果复制失败，返回原始路径

    def extract_good_icon(self, icon_path, temp_icon_path):
        try:
            # 使用Qt加载ICO文件，它会自动选择最佳尺寸
            icon = QIcon(icon_path)
            if not icon.isNull():
                # 获取可用尺寸并选择最大的
                available_sizes = icon.availableSizes()
                if available_sizes:
                    best_size = max(available_sizes, key=lambda s: s.width() * s.height())
                    pixmap = icon.pixmap(best_size)
                    # 生成PNG格式的临时文件名
                    png_filename = f"{uuid.uuid4().hex}.png"
                    temp_dir = os.path.join(USER_RES, "temp_icons")
                    png_icon_path = os.path.join(temp_dir, png_filename)
                    # 保存为PNG
                    if pixmap.save(png_icon_path, "PNG"):
                        icon_path = png_icon_path
                        #print(f"已提取最佳ICO图标到: {png_icon_path}")
                    # 删除原有的ICO文件
                    if os.path.exists(temp_icon_path):
                        os.remove(temp_icon_path)
                    return icon_path
            
        except Exception as e:
            return icon_path  # 如果处理失败，返回原始路径

    def changeTeacherFilesPath(self):
        """更改教师文件文件夹位置"""
        global TEACHER_FILES
        
        # 选择新位置
        new_path = QFileDialog.getExistingDirectory(
            self, "选择新的教师文件文件夹位置", TEACHER_FILES
        )
        
        if not new_path or new_path == TEACHER_FILES:
            return
            
        # 确认迁移
        reply = QMessageBox.question(
            self, "确认迁移", 
            f"确定要将教师文件文件夹从\n{TEACHER_FILES}\n迁移到\n{new_path}吗?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if os.path.exists(TEACHER_FILES):
                progress_dialog = ProgressDialog(TEACHER_FILES, new_path, self)
                progress_dialog.start_move()
                result = progress_dialog.exec_()

                if result == QDialog.Accepted:
                    # 更新全局变量
                    TEACHER_FILES = new_path
                    
                    # 更新配置文件中的路径
                    self.updateConfigAfterMigration(new_path)
                    
                    # 更新快捷方式路径
                    for shortcut in self.shortcuts:
                        if not shortcut.is_exe:
                            shortcut.path = os.path.normpath(os.path.join(TEACHER_FILES, shortcut.name))
                            print(f"更新快捷方式: {shortcut.name} -> {shortcut.path}")
            else:
                QMessageBox.warning(self, "迁移失败", "当前教师文件文件夹不存在，无法迁移")

    def updateConfigAfterMigration(self, new_path):
        """迁移完成后更新配置文件"""
        try:
            # 读取当前配置
            config = load_shortcut_order()
            if not config:
                return
            for item in config:
                if item["name"] == "__teacher_file__":
                    item["path"] = new_path.replace("/", "\\")
                    continue
                if not item["is_exe"]:
                    # 替换路径前缀
                    item["path"] = (f"{new_path}/{item['name']}").replace("/", "\\")
            # 保存更新后的配置
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"更新配置文件失败: {e}")
            QMessageBox.warning(
                self, "配置更新失败", 
                f"文件夹迁移成功，但配置文件更新失败: {str(e)}"
            )         

    def updateShortcutName(self, shortcut, new_name):
        """更新快捷方式名称"""
        # 找到索引
        if shortcut in self.shortcuts:
            # 更新名称
            old_path = shortcut.path
            parent_dir = os.path.dirname(old_path)
            new_path = os.path.join(parent_dir, new_name)
            
            if not shortcut.is_exe:
                try:
                    if os.path.exists(old_path) and not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        shortcut.path = new_path
                except Exception as e:
                    QMessageBox.warning(
                        self, "重命名失败", 
                        f"无法重命名文件夹\n错误: {str(e)}"
                    )
                    # 恢复显示名称
                    shortcut.name = os.path.basename(old_path)
                    shortcut.text_label.setText(shortcut.name)
            else:
                shortcut.name = new_name
            
            # 保存更新后的配置到文件
            save_shortcut_order(self.shortcuts)
    
    def toggleExpand(self):
        """切换展开/收起状态"""
        if self.is_expanded:
            # 收起动画 - 只保留按钮宽度
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(300)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.setStartValue(self.geometry())

   
            end_geometry = self.geometry()
            # 直接设置为按钮宽度（例如24px + 左右各2px边距 = 28px）
            end_geometry.setWidth(40)
            # 强制应用，忽略布局约束
            self.animation.setEndValue(end_geometry)

            # 更改按钮图标
            self.toggle_button.setIcon(QIcon.fromTheme("chevron-right"))
        else:
            # 展开动画 - 恢复原始宽度
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(300)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.setStartValue(self.geometry())
            
            # 恢复原始宽度
            end_geometry = self.geometry()
            end_geometry.setWidth(self.original_width)
            self.animation.setEndValue(end_geometry)
            
            # 更改按钮图标
            self.toggle_button.setIcon(QIcon.fromTheme("chevron-left"))
        
        self.animation.start()
        self.toggle_button.toggleRotation()
        self.is_expanded = not self.is_expanded
    
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if self.locked:
            event.ignore()  # 如果锁定，忽略拖动事件            
            self.dragging = False

        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_pos)
            # 更新原始几何信息（用于展开/收起）
            if self.is_expanded:
                self.original_geometry = self.geometry()
                self.original_width = self.geometry().width()
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""

        self.dragging = False

    # -------------------------- 光环动画初始化 --------------------------
    def init_glow_animation(self):
        # 主角度动画
        self.main_animation = QPropertyAnimation(self, b"angle")
        self.main_animation.setStartValue(0)
        self.main_animation.setEndValue(360)
        self.main_animation.setDuration(8000)
        self.main_animation.setLoopCount(-1)
        self.main_animation.start()

        # 副角度动画（双层光环用）
        self.sub_animation = QPropertyAnimation(self, b"sub_angle")
        self.sub_animation.setStartValue(0)
        self.sub_animation.setEndValue(360)
        self.sub_animation.setDuration(6000)
        self.sub_animation.setLoopCount(-1)
        self.sub_animation.start()

    # -------------------------- 光环属性与绘制 --------------------------
    @pyqtProperty(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if self.is_running and self.is_enabled:  # 仅在启用且运行时更新
            self._angle = value
            self.update()

    @pyqtProperty(int)
    def sub_angle(self):
        return self._sub_angle

    @sub_angle.setter
    def sub_angle(self, value):
        if self.is_running and self.is_enabled:  # 仅在启用且运行时更新
            self._sub_angle = value
            self.update()

    def paintEvent(self, event):
        # 1. 绘制你的原有亚克力效果（完全保留你的代码）
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        rect = self.rect()
        
        # 亚克力效果实现
        brush = QBrush(QColor(self.R, self.G, self.B, int(255 * self.opacity)))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)
        
        # 绘制轻微的高光效果模拟亚克力
        half_height = int(rect.height() / 3)
        highlight = QBrush(QColor(255, 255, 255, int(20 * self.opacity)))
        painter.setBrush(highlight)
        painter.drawRoundedRect(rect.adjusted(0, 0, 0, -half_height), 
                               self.CORNER_RADIUS, self.CORNER_RADIUS)

        # 2. 绘制光环（仅在运行状态）
        if not self.is_enabled:
            return  # 禁用时完全不绘制光环
        
        if not self.is_running:
            return
        
        # 光环绘制区域（向内缩进，不覆盖亚克力主体）
        glow_rect = rect.adjusted(5, 5, -5, -5)
        
        # 根据样式绘制光环
        if self._style == self.STYLE_FULL_COLOR_RING:
            self._draw_full_ring(painter, glow_rect)
        elif self._style == self.STYLE_TOP_BOTTOM_GRADIENT:
            self._draw_top_bottom(painter, glow_rect)
        elif self._style == self.STYLE_DOUBLE_LAYER_RING:
            self._draw_double_ring(painter, glow_rect)

    # 样式1：全环绕光环
    def _draw_full_ring(self, painter, rect):
        gradient = QConicalGradient(rect.center(), self._angle)
        self._add_rainbow_colors(gradient)
        painter.setPen(QPen(gradient, 10))  # 光环粗细
        painter.drawRoundedRect(rect, self.CORNER_RADIUS-5, self.CORNER_RADIUS-5)

    # 样式2：上下边缘光环
    def _draw_top_bottom(self, painter, rect):
        # 顶部光环
        top_grad = QLinearGradient(rect.left(), 0, rect.right(), 0)
        top_grad.setColorAt(0, QColor(255, 0, 0, 200))
        top_grad.setColorAt(1, QColor(0, 0, 255, 200))
        painter.setPen(QPen(top_grad, 8))
        painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())

        # 底部光环
        bottom_grad = QLinearGradient(rect.right(), 0, rect.left(), 0)
        bottom_grad.setColorAt(0, QColor(255, 0, 0, 200))
        bottom_grad.setColorAt(1, QColor(0, 0, 255, 200))
        painter.setPen(QPen(bottom_grad, 8))
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())

    # 样式3：双层光环
    def _draw_double_ring(self, painter, rect, radius=7):
        # 外层
        outer_grad = QConicalGradient(rect.center(), self._angle)
        self._add_rainbow_colors(outer_grad, 200)
        painter.setPen(QPen(outer_grad, 6))
        painter.drawRoundedRect(rect, radius, radius)

        # 内层
        inner_rect = rect.adjusted(8, 8, -8, -8)
        inner_grad = QConicalGradient(inner_rect.center(), self._sub_angle)
        self._add_rainbow_colors(inner_grad, 180)
        painter.setPen(QPen(inner_grad, 4))
        painter.drawRoundedRect(inner_rect, radius-2, radius-2)

    # 辅助：添加彩虹色
    def _add_rainbow_colors(self, gradient, alpha=220):
        colors = [
            (0.0, QColor(255, 0, 0, alpha)),
            (0.2, QColor(255, 165, 0, alpha)),
            (0.4, QColor(255, 255, 0, alpha)),
            (0.6, QColor(0, 255, 0, alpha)),
            (0.8, QColor(0, 0, 255, alpha)),
            (1.0, QColor(128, 0, 128, alpha))
        ]
        for pos, color in colors:
            gradient.setColorAt(pos, color)

    # -------------------------- 光环控制方法 --------------------------
    def toggle_glow(self):
        # 暂停/恢复光环
        self.is_running = not self.is_running
        if self.is_running:
            self.main_animation.start()
            self.sub_animation.start()
            self.toggle_btn.setText("暂停光环")
        else:
            self.main_animation.stop()
            self.sub_animation.stop()
            self.toggle_btn.setText("恢复光环")
        self.update()

    def switch_style(self):
        # 切换光环样式（循环切换）
        self._style = (self._style + 1) % 3
        self.update()

    # 新增：禁用/启用光环（完全隐藏）
    def toggle_enable(self):
        self.is_enabled = not self.is_enabled
        if self.is_enabled:
            # 启用时恢复动画和按钮状态
            self.is_running = True
            self.main_animation.start()
            self.sub_animation.start()
            self.enable_btn.setText("禁用光环")
            self.toggle_btn.setText("暂停光环")
            self.toggle_btn.setEnabled(True)
            self.style_btn.setEnabled(True)
        else:
            # 禁用时停止动画并隐藏
            self.is_running = False
            self.main_animation.stop()
            self.sub_animation.stop()
            self.enable_btn.setText("启用光环")
            self.toggle_btn.setEnabled(False)  # 禁用时暂停按钮失效
            self.style_btn.setEnabled(False)   # 禁用时样式按钮失效
        self.update()  # 触发重绘（隐藏光环）

class RotatableSvgButton(QPushButton):
    """带SVG旋转动画的按钮（修复初始大小问题）"""
    def __init__(self, svg_code, parent=None):
        super().__init__(parent)
        self.svg_code = svg_code
        self._rotation = 0  # 根据需要调整初始角度
        self.is_expanded = True
        
        # 明确设置图标尺寸
        self.icon_size = QSize(24, 24)  # 统一尺寸
        self.setIconSize(self.icon_size)
        
        # 加载并调整SVG大小
        self.setIcon(self.getSvgIcon())
        
        # 创建动画
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(300)

    @pyqtProperty(int)
    def rotation(self):
        return self._rotation
        
    @rotation.setter
    def rotation(self, angle):
        self._rotation = angle
        transform = QTransform().rotate(angle)
        # 始终使用相同尺寸
        pixmap = self.getSvgIcon().pixmap(self.icon_size)
        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.setIcon(QIcon(rotated_pixmap))

    def getSvgIcon(self):
        """确保SVG按指定尺寸正确渲染"""
        # 处理SVG代码，确保viewBox正确
        processed_svg = self.svg_code.replace(
            'width="200" height="200"', 
            f'width="{self.icon_size.width()}" height="{self.icon_size.height()}"'
        )
        
        svg_bytes = QByteArray(processed_svg.encode('utf-8'))
        pixmap = QPixmap()
        # 强制按指定尺寸加载
        pixmap.loadFromData(svg_bytes)
        if not pixmap.isNull():
            # 确保尺寸一致
            pixmap = pixmap.scaled(
                self.icon_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
        return QIcon(pixmap)
    
    def toggleRotation(self):
        if self.is_expanded:
            self.animation.setStartValue(0)
            self.animation.setEndValue(180)
        else:
            self.animation.setStartValue(180)
            self.animation.setEndValue(0)
        self.animation.start()
        self.is_expanded = not self.is_expanded

class MoveWorker(QThread):
    """移动文件工作线程（复制阶段）"""
    progress_updated = pyqtSignal(int)  # 进度更新信号
    finished = pyqtSignal(bool, list)   # 完成信号(是否成功, 错误文件列表)
    total_files = pyqtSignal(int)       # 总文件数信号

    def __init__(self, src, dst):
        super().__init__()
        self.src = src
        self.dst = dst
        self.aborted = False
        self.error_files = []

    def run(self):
        try:
            # 计算总文件数
            total = 0
            for root, _, files in os.walk(self.src):
                total += len(files)
            self.total_files.emit(total)

            # 复制文件
            copied = 0
            for root, dirs, files in os.walk(self.src):
                # 创建目标目录
                rel_path = os.path.relpath(root, self.src)
                dst_dir = os.path.join(self.dst, rel_path)
                os.makedirs(dst_dir, exist_ok=True)

                # 复制文件
                for file in files:
                    if self.aborted:
                        return
                    
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_dir, file)
                    
                    try:
                        shutil.copy2(src_file, dst_file)  # 保留元数据的复制
                        copied += 1
                        progress = int((copied / total) * 100)
                        self.progress_updated.emit(progress)
                        # 避免进度条更新过快
                        QTimer.singleShot(10, lambda: None)
                    except Exception as e:
                        self.error_files.append(f"{src_file}: {str(e)}")

            self.finished.emit(True, self.error_files)
        except Exception as e:
            self.error_files.append(f"整体错误: {str(e)}")
            self.finished.emit(False, self.error_files)

    def abort(self):
        self.aborted = True

class DeleteWorker(QThread):
    """删除源文件工作线程"""
    progress_updated = pyqtSignal(int)  # 进度更新信号
    finished = pyqtSignal(list)         # 完成信号(错误文件列表)
    total_files = pyqtSignal(int)       # 总文件数信号

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.aborted = False
        self.error_files = []

    def run(self):
        try:
            # 计算总文件数
            total = 0
            for root, _, files in os.walk(self.path):
                total += len(files)
            self.total_files.emit(total)

            # 删除文件
            deleted = 0
            # 先删除文件
            for root, _, files in os.walk(self.path, topdown=False):
                for file in files:
                    if self.aborted:
                        return
                    
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted += 1
                        progress = int((deleted / total) * 100)
                        self.progress_updated.emit(progress)
                        QTimer.singleShot(10, lambda: None)
                    except Exception as e:
                        self.error_files.append(f"{file_path}: {str(e)}")

            # 再删除空目录
            for root, dirs, _ in os.walk(self.path, topdown=False):
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                    except:
                        pass  # 目录非空时忽略

            self.finished.emit(self.error_files)
        except Exception as e:
            self.error_files.append(f"删除错误: {str(e)}")
            self.finished.emit(self.error_files)

    def abort(self):
        self.aborted = True

class ProgressDialog(QDialog):
    """进度条对话框"""
    def __init__(self, src, dst, parent=None):
        super().__init__(parent)
        self.src = src
        self.dst = dst
        self.parent = parent
        self.move_worker = None
        self.delete_worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("处理中")
        self.setFixedSize(400, 150)
        self.setWindowModality(Qt.ApplicationModal)  # 模态窗口，阻止父窗口操作

        # 布局
        layout = QVBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("准备开始复制文件...")
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        btn_layout.addWidget(self.cancel_btn)
        
        # 完成按钮（初始禁用）
        self.finish_btn = QPushButton("完成")
        self.finish_btn.setEnabled(False)
        self.finish_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.finish_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_move(self):
        """开始移动文件（先复制）"""
        self.move_worker = MoveWorker(self.src, self.dst)
        self.move_worker.total_files.connect(self.on_total_files)
        self.move_worker.progress_updated.connect(self.progress_bar.setValue)
        self.move_worker.finished.connect(self.on_move_finished)
        self.move_worker.start()

    def on_total_files(self, total):
        """更新总文件数显示"""
        self.status_label.setText(f"正在复制文件 (0/{total})...")

    def on_move_finished(self, success, errors):
        """复制完成后处理"""
        if not success:
            QMessageBox.error(self, "复制失败", "\n".join(errors))
            self.finish_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            return

        # 复制完成，开始删除源文件
        self.status_label.setText("准备删除源文件...")
        self.progress_bar.setValue(0)
        
        self.delete_worker = DeleteWorker(self.src)
        self.delete_worker.total_files.connect(self.on_delete_total)
        self.delete_worker.progress_updated.connect(self.progress_bar.setValue)
        self.delete_worker.finished.connect(self.on_delete_finished)
        self.delete_worker.start()

    def on_delete_total(self, total):
        """更新删除文件总数显示"""
        self.status_label.setText(f"正在删除源文件 (0/{total})...")

    def on_delete_finished(self, errors):
        """删除完成后处理"""
        self.progress_bar.setValue(100)
        self.status_label.setText("处理完成")
        self.finish_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # 显示删除错误（如果有）
        if errors:
            msg = "部分文件无法删除（可能正在使用）：\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... 还有 {len(errors)-5} 个文件"
            QMessageBox.warning(self, "删除提示", msg)

    def cancel_operation(self):
        """取消操作"""
        if self.move_worker and self.move_worker.isRunning():
            self.move_worker.abort()
            self.move_worker.wait()
        if self.delete_worker and self.delete_worker.isRunning():
            self.delete_worker.abort()
            self.delete_worker.wait()
        self.reject()

class CopyProgressWidget(QWidget):
    """简洁的复制进度窗口"""
    def __init__(self, source_path, target_dir, parent=None):
        super().__init__(parent)
        self.source_path = source_path
        self.target_dir = target_dir
        self.total_size = 0
        self.copied_size = 0
        self.is_cancelled = False
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("正在复制")
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 第一排：加粗加大标题
        title_label = QLabel("正在复制")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 第二排：复制路径信息
        path_label = QLabel(f'从 "{os.path.basename(self.source_path)}" 复制到 "{os.path.basename(self.target_dir)}"')
        path_label.setWordWrap(True)
        main_layout.addWidget(path_label)
        
        # 第三排：进度条（使用系统原生样式）
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # 第四排：速度和剩余时间（居右显示）
        info_layout = QHBoxLayout()
        info_layout.addStretch()  # 左侧弹簧，使内容居右
        
        self.info_label = QLabel("速度: ... | 剩余时间: ...")
        self.info_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.info_label)
        
        main_layout.addLayout(info_layout)
        
        # 第五排：取消按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 左侧弹簧，使按钮居右
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self.cancelCopy)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 启动复制线程
        self.startCopy()
        
    def startCopy(self):
        """启动复制线程"""
        self.copy_thread = CopyThread(self.source_path, self.target_dir)
        self.copy_thread.progress_updated.connect(self.updateProgress)
        self.copy_thread.speed_updated.connect(self.updateSpeed)
        self.copy_thread.finished.connect(self.onCopyFinished)
        self.copy_thread.start()
        
    def updateProgress(self, copied, total, percentage):
        """更新进度"""
        self.copied_size = copied
        self.total_size = total
        self.progress_bar.setValue(percentage)
        
    def updateSpeed(self, speed_mb, remaining_sec):
        """更新速度和剩余时间"""
        speed_text = f"{speed_mb:.1f} MB/s" if speed_mb > 0 else "0 MB/s"
        
        if remaining_sec > 3600:
            remaining_text = f"{remaining_sec // 3600}小时{(remaining_sec % 3600) // 60}分"
        elif remaining_sec > 60:
            remaining_text = f"{remaining_sec // 60}分{remaining_sec % 60}秒"
        else:
            remaining_text = f"{remaining_sec}秒"
            
        self.info_label.setText(f"速度: {speed_text} | 剩余时间: {remaining_text}")
        
    def onCopyFinished(self, success, error_message):
        """复制完成"""
        if success:
            # 复制成功，更新状态
            self.info_label.setText("复制完成")
            self.progress_bar.setValue(100)
            self.cancel_button.setText("关闭")
            
            # 3秒后自动关闭
            QTimer.singleShot(1000, self.hide)
        else:
            if not self.is_cancelled:
                self.info_label.setText(f"复制失败: {error_message}")
                self.cancel_button.setText("关闭")
                
    def cancelCopy(self):
        """取消复制"""
        if hasattr(self, 'copy_thread') and self.copy_thread.isRunning():
            self.is_cancelled = True
            self.copy_thread.stop()
            self.info_label.setText("正在取消...")
        else:
            self.hide()

            
    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'copy_thread') and self.copy_thread.isRunning():
            self.cancelCopy()
            event.ignore()
        else:
            event.accept()

class CopyThread(QThread):
    """复制线程"""
    progress_updated = pyqtSignal(int, int, int)  # copied, total, percentage
    speed_updated = pyqtSignal(float, int)        # speed_mb, remaining_sec
    finished = pyqtSignal(bool, str)              # success, error_message
    
    def __init__(self, source_path, target_dir):
        super().__init__()
        self.source_path = source_path
        self.target_dir = target_dir
        self.is_running = True
        
    def run(self):
        try:
            # 计算总大小
            total_size = self.calculateTotalSize(self.source_path)
            if total_size == 0:
                self.finished.emit(False, "文件大小为0")
                return
                
            copied_size = 0
            start_time = time.time()
            
            if os.path.isdir(self.source_path):
                # 复制文件夹 - 修复路径处理
                target_path = os.path.join(self.target_dir, os.path.basename(self.source_path))
                copied_size = self.copyDirectory(self.source_path, target_path, 
                                               copied_size, total_size, start_time)
            else:
                # 复制单个文件
                target_file = os.path.join(self.target_dir, os.path.basename(self.source_path))
                copied_size = self.copySingleFile(self.source_path, target_file, 
                                                copied_size, total_size, start_time)
            
            if self.is_running:
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, "操作已取消")
                
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def calculateTotalSize(self, path):
        """计算总大小"""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            else:
                total_size = 0
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if not self.is_running:
                            return total_size
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                return total_size
        except:
            return 0
            
    def copyDirectory(self, source_dir, target_dir, current_copied, total_size, start_time):
        """复制目录 - 修复版本"""
        copied = current_copied
        
        # 创建目标目录（保持源文件夹结构）
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制源目录下的所有内容到目标目录
        for item in os.listdir(source_dir):
            if not self.is_running:
                break
                
            source_item = os.path.join(source_dir, item)
            target_item = os.path.join(target_dir, item)
            
            if os.path.isdir(source_item):
                # 递归复制子目录
                copied = self.copyDirectory(source_item, target_item, copied, total_size, start_time)
            else:
                # 复制文件
                copied += self.copySingleFile(source_item, target_item, copied, total_size, start_time)
                
        return copied
        
    def copySingleFile(self, source_file, target_file, current_copied, total_size, start_time):
        """复制单个文件"""
        try:
            file_size = os.path.getsize(source_file)
            chunk_size = 64 * 1024  # 64KB chunks
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            with open(source_file, 'rb') as src, open(target_file, 'wb') as dst:
                bytes_copied = 0
                last_update_time = start_time
                
                while bytes_copied < file_size and self.is_running:
                    chunk = src.read(min(chunk_size, file_size - bytes_copied))
                    if not chunk:
                        break
                        
                    dst.write(chunk)
                    bytes_copied += len(chunk)
                    
                    # 更新进度
                    current_time = time.time()
                    if current_time - last_update_time > 0.1:  # 每100ms更新一次
                        total_copied = current_copied + bytes_copied
                        percentage = min(100, int((total_copied / total_size) * 100))
                        
                        elapsed = current_time - start_time
                        if elapsed > 0:
                            speed = total_copied / elapsed / (1024 * 1024)  # MB/s
                            remaining = (total_size - total_copied) / (speed * 1024 * 1024) if speed > 0 else 0
                            
                            self.progress_updated.emit(total_copied, total_size, percentage)
                            self.speed_updated.emit(speed, int(remaining))
                        
                        last_update_time = current_time
                        QApplication.processEvents()
                    
            return bytes_copied
            
        except Exception as e:
            raise Exception(f"复制文件失败: {str(e)}")
            
    def stop(self):
        """停止复制"""
        self.is_running = False

class SystemShortcutItem(ShortcutItem):
    """系统特殊文件夹快捷方式（支持特殊右键菜单）"""
    icon_manager = None
    def __init__(self, name, path, parent=None):
        super().__init__(name, path, is_exe=False, is_uwp=False, parent=parent)
        self.is_system = True
        self.system_type = self.getSystemType(name)
        
    def getSystemType(self, name):
        """根据名称确定系统类型"""
        if name == "此电脑":
            return "computer"
        elif name == "回收站":
            return "recycle"
        elif name == "控制面板":
            return "control_panel"
        elif name == "网络":
            return "network"
        elif name == "桌面":
            return "desktop"
        return "general"
    
    def showContextMenu(self, position):
        """显示系统特殊右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border-radius: 12px;
                padding: 5px 0;
                font-size: 12px;
            }
            QMenu::item {
                padding: 5px 20px;
                margin: 2px 5px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #525252;
            }
        """)
        
        # 通用操作
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.openTarget)
        
        # 根据系统类型添加特殊操作
        if self.system_type == "computer":
            manage_action = QAction("管理", self)
            manage_action.triggered.connect(self.openComputerManage)
            
            properties_action = QAction("属性", self)
            properties_action.triggered.connect(self.openComputerProperties)
            
            menu.addAction(open_action)
            menu.addAction(manage_action)
            menu.addAction(properties_action)
            
        elif self.system_type == "recycle":
            # 检查回收站是否为空
            is_empty = self.isRecycleBinEmpty()
            
            if not is_empty:
                empty_action = QAction("清空回收站", self)
                empty_action.triggered.connect(self.emptyRecycleBin)
                menu.addAction(empty_action)
            else:
                empty_action = QAction("清空回收站(空)", self)
                empty_action.setEnabled(False)  # 禁用菜单项
                menu.addAction(empty_action)
            
            properties_action = QAction("属性", self)
            properties_action.triggered.connect(self.openRecycleProperties)
            
            menu.addAction(open_action)
            menu.addAction(empty_action)
            menu.addAction(properties_action)
            
        elif self.system_type == "control_panel":
            menu.addAction(open_action)
            
        else:
            menu.addAction(open_action)
        
        menu.addSeparator()
        
        # 删除动作
        delete_action = QAction("删除快捷方式", self)
        delete_action.triggered.connect(self.deleteShortcut)
        
        menu.addAction(delete_action)
        
        menu.exec_(self.mapToGlobal(position))

    def isRecycleBinEmpty(self):
        """检查回收站是否为空 - 修复版本"""
        try:
            # 定义SHQUERYRBINFO结构体
            class SHQUERYRBINFO(Structure):
                _fields_ = [
                    ("cbSize", c_uint),
                    ("i64Size", c_ulonglong),
                    ("i64NumItems", c_ulonglong)
                ]
            
            # 定义函数原型
            SHQueryRecycleBin = ctypes.windll.shell32.SHQueryRecycleBinW
            SHQueryRecycleBin.argtypes = [wintypes.LPCWSTR, POINTER(SHQUERYRBINFO)]
            SHQueryRecycleBin.restype = HRESULT
            
            # 初始化结构体
            info = SHQUERYRBINFO()
            info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
            
            # 调用函数
            result = SHQueryRecycleBin(None, ctypes.byref(info))
            
            # 检查结果 (S_OK = 0)
            if result == 0:  # S_OK
                return info.i64NumItems == 0
            else:
                # 如果API调用失败，使用备用方法
                return self.isRecycleBinEmptyFallback()
                
        except Exception as e:
            print(f"回收站检查API失败: {e}")
            # 使用备用方法
            return self.isRecycleBinEmptyFallback()
    
    def isRecycleBinEmptyFallback(self):
        """备用方法：检查回收站是否为空"""
        try:
            # 获取系统驱动器
            system_drive = os.environ.get('SystemDrive', 'C:')
            recycle_bin_path = os.path.join(system_drive, '$Recycle.Bin')
            
            if not os.path.exists(recycle_bin_path):
                return True
                
            # 检查回收站目录中的用户文件夹
            for item in os.listdir(recycle_bin_path):
                item_path = os.path.join(recycle_bin_path, item)
                if os.path.isdir(item_path) and not item.startswith('S-1-5-18'):
                    # 检查用户回收站文件夹是否为空
                    try:
                        user_items = os.listdir(item_path)
                        # 排除系统文件
                        user_files = [f for f in user_items if not f.startswith('$')]
                        if user_files:
                            return False
                    except PermissionError:
                        # 如果没有权限访问某些文件夹，假设不为空
                        return False
                        
            return True
            
        except Exception as e:
            print(f"备用回收站检查失败: {e}")
            return True  # 默认认为为空

    def openComputerManage(self):
        """打开计算机管理"""
        try:
            subprocess.Popen("compmgmt.msc", shell=True)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开计算机管理: {str(e)}")
    
    def openComputerProperties(self):
        """打开计算机属性"""
        try:
            subprocess.Popen("sysdm.cpl", shell=True)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开系统属性: {str(e)}")
    
    def emptyRecycleBin(self):
        """清空回收站"""
        #reply = QMessageBox.question(
        #    self, "确认清空", 
        #    "确定要清空回收站吗?此操作无法撤销。",
        #    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        #)
        
        #if reply == QMessageBox.Yes:
        try:
            # 使用SHEmptyRecycleBin函数清空回收站
            from ctypes import windll
            windll.shell32.SHEmptyRecycleBinW(None, None, 0)
            #QMessageBox.information(self, "成功", "回收站已清空")
        except Exception as e:
            QMessageBox.warning(self, "清空失败", f"无法清空回收站: {str(e)}")
    
    def openRecycleProperties(self):
        """打开回收站属性"""
        try:
            # 通过回收站的CLSID打开属性
            subprocess.Popen('rundll32.exe shell32.dll,Control_RunDLL ::{645FF040-5081-101B-9F08-00AA002F954E}', shell=True)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开回收站属性: {str(e)}")




def read_from_registry(value_name):
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes', 0, reg.KEY_QUERY_VALUE) as key:
            value, regtype = reg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        return None
    except Exception as e:
        QMessageBox.critical(None, '错误', f'读取注册表失败：{e}')
        return None

def save_shortcut_order(shortcuts):
    """保存快捷方式顺序到配置文件，支持分割线、UWP应用和系统快捷方式"""
    config = []
    seen_paths = set()
    config.append({
        "name": "__teacher_file__",
        "path": TEACHER_FILES,
    })
    for s in shortcuts:
        if s.is_separator:
            # 保存分割线
            config.append({
                "name": "__separator__",
                "path": "",
                "is_exe": False,
                "is_uwp": False,
                "is_separator": True,
                "is_system": False
            })
        elif not s.path:  # 跳过路径为空的无效项
            continue
        elif s.path not in seen_paths:
            seen_paths.add(s.path)
            teacher_file = False if (s.is_exe or s.is_uwp or hasattr(s, 'is_system')) else True
            
            item_config = {
                "name": s.name,
                "path": s.path,
                "is_exe": s.is_exe,
                "is_uwp": s.is_uwp,
                "icon_path": s.icon_path,
                "teacher_file": teacher_file,
                "is_separator": False,
                "is_system": hasattr(s, 'is_system') and s.is_system
            }
            
            config.append(item_config)

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_shortcut_order():
    """从配置文件加载快捷方式顺序，支持分割线和UWP应用"""
    if not os.path.exists(CONFIG_PATH):
        return None
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 向后兼容：确保旧配置有is_uwp字段
            for item in config:
                if 'is_uwp' not in item:
                    item['is_uwp'] = False
                    
            return config
    except:
        return None


def get_all_apps():
    """获取计算机上所有安装的应用程序（兼容非UTF-8编码输出）"""
    try:
        cmd = [
            'powershell', 
            '-Command', 
            # 移除chcp命令，避免额外输出干扰
            '$OutputEncoding = [System.Text.Encoding]::UTF8; '
            'Get-StartApps | ConvertTo-Json -Depth 10'  # 增加Depth确保复杂结构被完整序列化
        ]
        
        # 关键修改：先以字节流读取（text=False），避免自动解码导致的错误
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=False,  # 不自动解码，获取原始字节流
            timeout=30,
            # 仅Windows需要隐藏窗口
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith('win32') else 0
        )
        
        if result.returncode != 0:
            # 错误输出也可能存在编码问题，用replace策略处理
            stderr = result.stderr.decode('utf-8', errors='replace')
            print(f"执行PowerShell命令失败: {stderr}")
            return []
        
        # 处理标准输出：尝试多种编码解码，优先UTF-8，失败则用gbk（Windows常见编码）
        stdout_bytes = result.stdout
        stdout = None
        # 尝试解码顺序：UTF-8 -> GBK -> Latin-1（最后保底）
        for encoding in ['utf-8', 'gbk', 'latin-1']:
            try:
                stdout = stdout_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if not stdout or not stdout.strip():
            print("PowerShell命令没有输出或输出为空")
            return []
        
        # 解析JSON
        apps = []
        try:
            data = json.loads(stdout)
            if isinstance(data, dict):
                apps = [data]
            elif isinstance(data, list):
                apps = data
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始输出（前500字符）: {stdout[:500]}")
            return []
        
        # 过滤和分类应用（保持原有逻辑）
        categorized_apps = []
        for app in apps:
            if not isinstance(app, dict):
                continue
                
            name = app.get('Name', '').strip()
            app_id = app.get('AppID', '').strip()
            
            if not name or not app_id:
                continue
                
            app_type = "unknown"
            icon_path = None
            
            if "!" in app_id:
                app_type = "uwp"
            elif app_id.endswith('.exe') or '\\' in app_id:
                app_type = "desktop"
                if os.path.exists(app_id):
                    icon_path = app_id
            elif app_id.endswith(('.url', '.lnk')):
                app_type = "shortcut"
            
            categorized_apps.append({
                'name': name,
                'app_id': app_id,
                'type': app_type,
                'icon_path': icon_path
            })
        
        return categorized_apps
        
    except subprocess.TimeoutExpired:
        print("获取应用列表超时")
        return []
    except Exception as e:
        print(f"获取应用列表失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_apps_by_type(app_type=None):
    """按类型获取应用列表"""
    all_apps = get_all_apps()
    if app_type:
        return [app for app in all_apps if app['type'] == app_type]
    return all_apps


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False
    


def extract_icon_with_key(file_path, icon_index, output_path):
    exe_path = r"Resource\tool\Extract.exe"
    # 调用程序（stdout=subprocess.PIPE捕获输出，stderr=subprocess.STDOUT合并错误输出）
    result = subprocess.run(
        [exe_path, file_path, str(icon_index), output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True  # 输出转为字符串
    )
    
    # 返回值说明：
    # result.returncode：程序退出码（0表示成功，其他为错误）
    # result.stdout：程序输出的文本内容
    return {
        "success": result.returncode == 0,
        "return_code": result.returncode,
        "output": result.stdout
    }


ds_config = load_shortcut_order()
if ds_config != None:
    for item in ds_config:
        if item["name"] == "__teacher_file__":
            TEACHER_FILES = item['path']
            break
    
    

if __name__ == "__main__":
    # 确保中文显示正常

    font = QFont("微软雅黑")
    
    app = QApplication(sys.argv)
    app.setFont(font)
    
    # 设置全局样式
    #app.setStyle("Fusion")


    manager = ShortcutManager()
    manager.show()

    sys.exit(app.exec_())
    