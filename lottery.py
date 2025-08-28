import sys
import random
import time
import os
import math
import soundfile as sf
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout)
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen, QRegion,QMouseEvent,QIcon
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5 import uic
import ctypes
from ctypes import wintypes, windll, create_unicode_buffer
import json

STUDENT_LIST = [
    "张三", "李四", "王五", "赵六", "钱七"
]

def getDocPath(pathID=5):
    '''path=5: My Documents'''
    buf= create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(None, pathID, None, 0, buf)
    return buf.value
# os拼接路径
USER_RES = os.path.join(getDocPath() , "LingYun_Profile/")

# 保存学生名单到json
def save_student_list(student_list, file_path = os.path.join(USER_RES, "student_list.json")):
    global STUDENT_LIST
    STUDENT_LIST = student_list
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(student_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存学生名单失败: {str(e)}")

# 本地读取学生名单json
def load_student_list(file_path = USER_RES + "student_list.json"):
    import json
    if not os.path.exists(file_path):
        #print(f"学生名单文件不存在: {file_path}")
        save_student_list(STUDENT_LIST)
        return STUDENT_LIST
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            student_list = json.load(f)
        return student_list
    except Exception as e:
        #print(f"加载学生名单失败: {str(e)}")
        return STUDENT_LIST
    
STUDENT_LIST = load_student_list()


# 简化后的音频播放函数，直接播放无需线程
def play_sound(wav_file):
    """简单播放音频文件"""
    try:
        if not os.path.exists(wav_file):
            print(f"音频文件不存在: {wav_file}")
            return

        data, samplerate = sf.read(wav_file)
        sd.play(data, samplerate)
    except Exception as e:
        print(f"音频播放错误: {str(e)}")

class FloatWindow(QWidget):
    """置顶圆形悬浮窗（支持拖拽）"""
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()
        # 圆形的半径和中心
        self.radius = 40  # 80x80窗口的半径是40
        self.center = QPoint(40, 40)  # 中心坐标
        self.init_ui()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(80, 80)
        
        # 设置圆形掩码
        self.setMask(QRegion(0, 0, 80, 80, QRegion.Ellipse))
        
        # 设置初始位置
        self.move_to_bottom_right()
        
        # 设置透明度
        self.setWindowOpacity(0.4)

        # 悬浮窗文字
        self.label = QLabel("随机\n抽签", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        self.label.setStyleSheet("color: white;")
        self.label.setGeometry(0, 0, 80, 80)

        self.lottery_window = LotteryWindow()

        # 记录窗口位置
        self.old_pos = self.pos()


    def is_point_in_circle(self, point):
        """判断点是否在圆形区域内"""
        # 计算点到中心的距离
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        distance = math.sqrt(dx*dx + dy*dy)
        # 如果距离小于半径，则在圆内
        return distance <= self.radius

    def move_to_bottom_right(self):
        try:
            screen_geometry = QApplication.desktop().availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            x = max(0, screen_width - 80 - 300)
            y = max(0, screen_height - 80 - 300)
            self.move(x, y)
        except Exception as e:
            print(f"设置窗口位置错误: {e}")
            self.move(100, 100)
            print("使用 fallback 位置 (100, 100)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(30, 144, 255))  # 蓝色背景，确保可见
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(1, 1, 78, 78)

    def enterEvent(self, event):
        self.setWindowOpacity(0.8)
        event.accept()

    def leaveEvent(self, event):
        self.setWindowOpacity(0.4)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            new_pos = self.pos()

            self.dragging = False
            event.accept()
            # 单击打开抽签窗口
            if new_pos == self.old_pos:
                self.open_lottery_window()
            self.old_pos = new_pos

    def open_lottery_window(self):
        try:
            self.lottery_window.show()
        except Exception as e:
            print(f"打开抽签窗口错误: {e}")

    def handle_update(self, key, value=None):
        if key == "switch":
            if value:
                self.show()
            else:
                self.hide()
                self.lottery_window.hide()
        elif key == "pin":
            # 检查原来有没有显示
            flag = False
            if self.isVisible():
                flag = True
            if value:
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            if flag:
                self.show()

        elif key == "student_list":
            self.lottery_window.update_student_list()


class LotteryWindow(QWidget):
    """抽签主窗口"""
    def __init__(self):
        super().__init__()

        ICON_PATH = os.path.join("Resource", "ico", "LINGYUN.ico")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.running = False
   
        # 加载UI文件
        try:
            ui_path = os.path.join("Resource", "ui", "lottery_ui.ui")
            if not os.path.exists(ui_path):
                print(f"UI文件不存在: {ui_path}，使用备用界面")
                self.init_fallback_ui()
            else:
                uic.loadUi(ui_path, self)
                self.result_label = self.findChild(QLabel, "result_label")
                self.draw_btn = self.findChild(QPushButton, "draw_btn")
                self.init_ui()
        except Exception as e:
            print(f"加载UI文件失败: {e}，使用备用界面")
            self.init_fallback_ui()

    def update_student_list(self):
        global STUDENT_LIST
        self.people_list = STUDENT_LIST.copy()
        self.result_label.setText("看看是哪位同学中奖了")

    def init_fallback_ui(self):
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        
        self.result_label = QLabel("开始抽签")
        self.result_label.setFont(QFont("微软雅黑", 30, QFont.Bold))
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
        self.draw_btn = QPushButton("开始抽签")
        layout.addWidget(self.draw_btn)
        self.draw_btn.clicked.connect(self.start_lottery)
        self.init_ui()

    def init_ui(self):
        self.people_list = STUDENT_LIST.copy()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_name)
        self.is_animating = False
        self.start_time = 0
        self.total_duration = 2500

        self.setFixedSize(self.width(), self.height()); 

        if self.result_label:
            self.result_label.setFont(QFont("微软雅黑", 30, QFont.Bold))
            self.result_label.setAlignment(Qt.AlignCenter)
        
        if self.draw_btn:
            self.draw_btn.clicked.connect(self.start_lottery)
        

    def play_gear_sound(self):
        """播放齿轮音效"""
        try:
            wav_path = os.path.join("Resource", "gear_sound.wav")
            play_sound(wav_path)  # 直接调用简化的播放函数
        except Exception as e:
            print(f"播放音效失败: {e}")

    def start_lottery(self):
        if self.is_animating or not self.draw_btn or not self.result_label:
            return
        self.running = True
        self.play_gear_sound()  # 播放音效
        self.is_animating = True
        self.draw_btn.setText("抽签中...")
        self.draw_btn.setEnabled(False)
        self.start_time = time.time() * 1000
        self.animation_timer.setInterval(50)
        self.animation_timer.start()

    def update_name(self):
        if not self.result_label:
            self.animation_timer.stop()
            return
            
        current_time = time.time() * 1000
        elapsed = current_time - self.start_time
        
        random_name = random.choice(self.people_list)
        self.result_label.setText(random_name)
        
        progress = min(elapsed / self.total_duration, 1.0)
        interval = 50 + (450 * (progress ** 2))
        self.animation_timer.setInterval(int(interval))
        
        if elapsed >= self.total_duration:
            self.animation_timer.stop()
            self.is_animating = False
            if self.draw_btn:
                self.draw_btn.setEnabled(True)
                self.draw_btn.setText("开始抽签")
            self.running = False
                

    def closeEvent(self, event):
        # 忽略关闭事件，隐藏窗口
        event.ignore()
        if self.running:
            print("抽签进行中，无法关闭窗口")
            return
        self.draw_btn.setText("瞧一瞧是哪位幸运儿")
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 确保中文显示
    font = QFont("SimHei")
    app.setFont(font)
    

    
    # 创建并显示悬浮窗
    try:
        float_window = FloatWindow()
        float_window.show()
        float_window.raise_()  # 置顶显示
        float_window.activateWindow()  # 激活窗口
        
        # 进入应用主循环
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序运行错误: {e}")
        input("按回车键退出...")