import sys
import random
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel)
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import (QPixmap, QPainter, QPen, QColor, QFont, QBrush,
                         QImage, QRadialGradient, QGuiApplication,QFontDatabase)

class LineParticle:
    """线条状粒子，从中心向外扩散，模拟时间穿梭效果"""
    def __init__(self, center_x, center_y, screen_width, screen_height):
        self.center = QPointF(center_x, center_y)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(10, 30)  # 速度范围
        
        # 线条长度和粗细
        self.length = random.uniform(30, 70)  # 线条长度
        self.thickness = random.uniform(0.2, 2)  # 线条粗细
        
        # 随机颜色（冷色调为主）
        hue = random.uniform(180, 300)  # 蓝到紫的色调
        self.color = QColor.fromHsvF(hue/360, 0.7, 0.9, 0.8)
        
        # 生命周期控制
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        
        # 初始位置在中心
        self.pos = QPointF(center_x, center_y)
        
    def update(self):
        """更新粒子状态"""

        # 沿角度移动
        self.pos += QPointF(math.cos(self.angle), math.sin(self.angle)) * self.speed
        
        # 减少生命周期
        self.life = max(0, self.life - self.decay)
        self.color.setAlphaF(self.life)
        
    def is_alive(self):
        """检查粒子是否存活"""
        return self.life > 0
    
    def draw(self, painter):
        """绘制线条状粒子"""
        painter.setPen(QPen(self.color, self.thickness))
        end_point = QPointF(
            self.pos.x() - math.cos(self.angle) * self.length,
            self.pos.y() - math.sin(self.angle) * self.length
        )
        painter.drawLine(self.pos, end_point)

class Nebula:
    """星云类，支持颜色变化和缓慢移动HSV"""
    def __init__(self, size, center=None):
        self.size = size
        if center == True:  # 固定在中心
            screen = QGuiApplication.primaryScreen()
            screen_geometry = screen.geometry()
            w_width = screen_geometry.width()  # 屏幕宽度
            w_height = screen_geometry.height()  # 屏幕高度
            self.center = QPointF(w_width // 2, w_height // 2)
            self.fixed = True

        else:  # 随机位置
            self.center = QPointF(
                random.randint(0, size.width()),
                random.randint(0, size.height())
            )
            self.fixed = False
        self.radius = random.randint(300, 600)
        
        # 初始颜色
        self.hue = random.randint(180, 240)  # 蓝色调
        self.saturation = random.randint(50, 80)
        self.value = 255
        self.alpha = random.randint(50, 100)
        
        # 移动和颜色变化参数
        self.dx = random.uniform(-5, 5)  # 水平移动速度
        self.dy = random.uniform(-5, 5)  # 垂直移动速度
        self.hue_change = random.uniform(-1, 1)  # 色调变化速度
        
    def update(self):
        """更新星云状态（位置和颜色）"""
        if not self.fixed:  # 仅在非固定模式下移动
            # 移动
            self.center.setX(self.center.x() + self.dx)
            self.center.setY(self.center.y() + self.dy)
            
            # 边界检查
            if self.center.x() < -self.radius:
                self.center.setX(self.size.width() + self.radius)
            elif self.center.x() > self.size.width() + self.radius:
                self.center.setX(-self.radius)
                
            if self.center.y() < -self.radius:
                self.center.setY(self.size.height() + self.radius)
            elif self.center.y() > self.size.height() + self.radius:
                self.center.setY(-self.radius)
        
        # 颜色变化（所有模式都变化）
        self.hue = (self.hue + self.hue_change) % 360
        
    def draw(self, painter):
        """绘制星云"""
        gradient = QRadialGradient(self.center, self.radius)
        
        # 基于当前hue生成颜色
        color1 = QColor.fromHsv(
            int(self.hue), 
            self.saturation,
            self.value,
            self.alpha
        )
        color2 = QColor(0, 0, 0, 0)  # 透明边缘
        
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(
            self.center.x() - self.radius,
            self.center.y() - self.radius,
            2 * self.radius,
            2 * self.radius
        ))

class CountdownWindow(QMainWindow):
    """全屏倒计时窗口（带线条粒子和动态星云）"""
    def __init__(self, parent=None, countdown=11,RES = "Resource/",font=''):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.RES = RES
        self.fonts = font
        self.screen_size = None
        self.particles = []
        self.countdown = countdown
        self.final_second = False
        self.fade_out = False
        self.fade_opacity = 1.0
        self.fade_step = 3 / 30  # 0.8秒内完成渐隐 (30fps)

        # 星空背景和星云
        self.star_background = None
        self.nebulas = []
        self.fixed_nebula = None
        
        # 倒计时标签
        self.label = QLabel(str(self.countdown), self)
        
        self.setup_label(self.fonts)

        # 计时器
        self.particle_timer = QTimer(self, interval=30, timeout=self.update_particles)
        self.countdown_timer = QTimer(self, interval=1000, timeout=self.update_countdown)
        self.fade_timer = QTimer(self, interval=30, timeout=self.update_fade)

    def setup_label(self,font):
        font = QFont(self.font_files(f"{self.RES}MiSans-Bold.ttf",font))
        font.setPointSize(min(self.width(), self.height()) // 5)
        font.setWeight(QFont.Bold)
        #font.setFamily("MiSans")

        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        self.label.setGeometry(self.rect())

    def font_files(self,file,font_name):
        # 加载字体文件
        #global da tas
        font = font_name
        if font_name == "":
            font_id = QFontDatabase.addApplicationFont(file)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font = font_families[0]
                else:
                    font = "微软雅黑"
            else:
                font = "微软雅黑"
        return font

    def start_countdown(self):
        """初始化窗口和粒子系统"""
        self.showFullScreen()
        self.update_screen_size()
        self.center = self.screen_size.width()//2, self.screen_size.height()//2
        
        # 生成星空背景和星云
        self.create_star_background()
        self.create_nebulas()
        self.fixed_nebula = Nebula(self.screen_size, center=True)  # 确保固定在中心
        
        # 生成初始粒子
        self.generate_particles(100)
        self.particle_timer.start()
        self.countdown_timer.start()
        
    def update_screen_size(self):
        """更新屏幕尺寸"""
        self.screen_size = self.size()
        self.setup_label(self.fonts)

    def resizeEvent(self, event):
        """窗口大小改变时更新尺寸"""
        super().resizeEvent(event)
        self.update_screen_size()
        if self.screen_size:
            self.center = self.screen_size.width()//2, self.screen_size.height()//2
            # 窗口大小变化时重新生成背景和星云
            self.create_star_background()
            self.create_nebulas()
            self.fixed_nebula = Nebula(self.screen_size, center=True)
        
    def generate_particles(self, count):
        """生成指定数量的粒子"""
        if not self.screen_size:
            return
            
        for _ in range(count):
            particle = LineParticle(*self.center, self.screen_size.width(), self.screen_size.height())
            self.particles.append(particle)
        
    def update_countdown(self):
        """更新倒计时显示"""
        self.countdown -= 1
        self.label.setText(str(self.countdown))
        if self.countdown == 0:
            self.countdown_timer.stop()
            self.final_second = True
            QTimer.singleShot(200, self.start_fade_out)
        
    def update_particles(self):
        """更新粒子和星云状态"""
        # 更新粒子
        self.particles = [p for p in self.particles if p.is_alive()]
        
        if not self.final_second and len(self.particles) < 100:
            self.generate_particles(1)
        
        for p in self.particles:
            p.update()
            
        # 更新星云
        for nebula in self.nebulas:
            nebula.update()
            
        self.update()  # 触发重绘
        
    def paintEvent(self, event):
        """绘制背景、粒子、星云和倒计时"""
        if not self.screen_size:
            self.update_screen_size()
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制全屏黑色背景
        painter.fillRect(self.rect(), Qt.black)
        
        # 设置全局透明度
        painter.setOpacity(self.fade_opacity)
        
        # 绘制星空背景
        if self.star_background:
            painter.drawPixmap(0, 0, self.star_background.scaled(self.size()))
        
        # 绘制星云（在粒子之下）
        for nebula in self.nebulas:
            nebula.draw(painter)
            
        # 绘制固定星云（在粒子之上，但在倒计时之下）
        if self.fixed_nebula:
            self.fixed_nebula.draw(painter)
            
        # 绘制粒子
        for p in self.particles:
            p.draw(painter)
            
        # 绘制倒计时标签
        self.label.setStyleSheet(f"color: rgba(255, 255, 255, {int(self.fade_opacity * 255)});")
        
    def create_star_background(self):
        """创建星空背景"""
        if not self.screen_size:
            return
            
        width, height = self.screen_size.width(), self.screen_size.height()
        img = QImage(width, height, QImage.Format_RGB32)
        img.fill(Qt.black)
        painter = QPainter(img)
        
        # 绘制星星
        for _ in range(800):
            brightness = random.randint(100, 255)
            star_size = random.randint(1, 3)  # 避免变量名冲突
            color = QColor(brightness, brightness, brightness, brightness)
            painter.setPen(QPen(color, star_size))
            painter.drawPoint(random.randint(0, width), random.randint(0, height))
            
        # 添加一些彩色星星
        for _ in range(100):
            hue = random.randint(0, 360)
            brightness = random.randint(150, 255)
            star_size = random.randint(2, 4)
            color = QColor.fromHsv(hue, 200, brightness, brightness // 2)
            painter.setPen(QPen(color, star_size))
            painter.drawPoint(random.randint(0, width), random.randint(0, height))
        
        painter.end()
        self.star_background = QPixmap.fromImage(img)
        
    def create_nebulas(self):
        """创建星云"""
        if not self.screen_size:
            return
        self.nebulas = []
        for _ in range(5):  # 创建5个星云
            nebula = Nebula(self.screen_size)
            self.nebulas.append(nebula)

    def start_fade_out(self):
        """开始渐隐过程"""
        self.fade_out = True
        self.fade_timer.start()

    def update_fade(self):
        """更新渐隐状态"""
        if self.fade_out:
            self.fade_opacity -= self.fade_step
            
            # 确保渐变完成后再关闭
            if self.fade_opacity <= 0:
                self.fade_opacity = 0
                self.fade_timer.stop()
                self.close()
            else:
                self.update()  # 触发重绘

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CountdownWindow()
    window.start_countdown()
    sys.exit(app.exec_())