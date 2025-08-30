import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QBrush, QLinearGradient
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve,QParallelAnimationGroup,QRectF

# closeEvent
class WaveAnimation(QWidget):
    def __init__(self, color="#3498db", duration=1500, start_delay=0, parent=None):
        # 确保QApplication实例存在
        self._app = QApplication.instance()
        if self._app is None:
            self._app = QApplication(sys.argv)
            self._owns_app = True
        else:
            self._owns_app = False
            
        super().__init__(parent)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._width = 0
        self._opacity = 0
        self.color = QColor(color)
        self.duration = duration
        
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.resize(self.screen_geometry.width(), self.screen_geometry.height())
        
        QTimer.singleShot(start_delay, self.showAnimation)
    
    @pyqtProperty(float)
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value):
        self._width = value
        self.update()
    
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()
    
    def showAnimation(self):
        """开始动画"""
        self.show()
        
        # 宽度动画
        self.width_animation = QPropertyAnimation(self, b'width')
        self.width_animation.setDuration(self.duration)
        self.width_animation.setStartValue(0)
        self.width_animation.setEndValue(self.screen_geometry.width())
        self.width_animation.setEasingCurve(QEasingCurve.OutQuart)

        
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b'opacity')
        self.opacity_animation.setDuration(self.duration)
        self.opacity_animation.setStartValue(1)
        self.opacity_animation.setKeyValueAt(0.9, 0.1)
        self.opacity_animation.setEndValue(0)
        
        # 动画组
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.width_animation)
        self.animation_group.addAnimation(self.opacity_animation)
        self.animation_group.finished.connect(self.close)
        self.animation_group.start()
    
    def paintEvent(self, event):
        """绘制海浪动画"""
        if self._opacity <= 0 or self._width <= 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self._opacity)
        
        pos_x = self.screen_geometry.width() - self._width
        
        gradient = QLinearGradient(pos_x, 0, pos_x + self._width, 0)
        gradient.setColorAt(0, QColor(self.color.red(), self.color.green(), self.color.blue(), 200))
        gradient.setColorAt(1, self.color)
        
        wave_rect = QRectF(
            pos_x, 
            0, 
            self._width, 
            self.screen_geometry.height()
        )
        painter.fillRect(wave_rect, QBrush(gradient))
    
    def closeEvent(self, event):
        """正确处理窗口关闭"""
        self.deleteLater()
        event.accept()
    
    def start(self, color=None, duration=None, start_delay=None):
        """启动动画并选择性进入应用程序事件循环"""
        if color is not None:
            self.color = QColor(color)
        if duration is not None:
            self.duration = duration
            if hasattr(self, 'width_animation'):
                self.width_animation.setDuration(duration)
                self.opacity_animation.setDuration(duration)
        if start_delay is not None:
            if not hasattr(self, 'width_animation'):
                if hasattr(self, '_start_timer'):
                    self._start_timer.stop()
                self._start_timer = QTimer.singleShot(start_delay, self.showAnimation)
        
        self.showAnimation()
        
        if self._owns_app:
            return self._app.exec_()
        else:
            #事件循环已在运行
            return None



if __name__ == "__main__":
    wave = WaveAnimation()
    sys.exit(wave.start())