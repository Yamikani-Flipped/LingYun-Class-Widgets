from PyQt5.QtCore import Qt,QRectF,QTimer
from PyQt5.QtGui import QPainterPath, QRegion,QGuiApplication,QFont,QColor
from PyQt5.QtWidgets import QApplication, QWidget,QLabel
from PyQt5 import uic

from datetime import datetime
from qfluentwidgets import TitleLabel,ProgressBar,Theme

#桌面组件
class Desktop_Component(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    def initUI(self):
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度
        self.move(display_x-260,12)

        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)# 使背景透明

        self.uic_ui()
        timer = QTimer(self)
        timer.timeout.connect(self.updateCountdown)
        timer.start(1000)
    def setRoundedCorners(self, radius):
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())  # 使用QRectF而不是QRect
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    def uic_ui(self):
        self.classes = uic.loadUi("Resource/ui/class_mini2.ui",self)
        self.classes.setObjectName("classes")

        self.TitleLabel = self.findChild(TitleLabel,"lingyun_class")

        self.lingyun_Title = self.findChild(QLabel,"lingyun_Title")
        self.lingyun_class = self.findChild(TitleLabel,"lingyun_class")

        self.lingyun_Title_2 = self.findChild(QLabel,"lingyun_Title_2")
        self.lingyun_down = self.findChild(TitleLabel,"lingyun_down")
        self.lingyun_Bar = self.findChild(ProgressBar,"lingyun_Bar")
        self.lingyun_Bar.setRange(0, 100)
        self.lingyun_Bar.setCustomBarColor(QColor(0, 0, 255), QColor(255, 255, 255))

        self.todayclass_Title = self.findChild(QLabel,"todayclass_Title")
        self.Widgets_ORD = self.findChild(QLabel,"class_ORD")
        self.Widgets = self.findChild(QLabel,"class_widget")
        
        self.lingyun_background = self.findChild(QLabel,"lingyun_background")
        self.lingyun_background_2 = self.findChild(QLabel,"lingyun_background_2")
        self.todayclass_background = self.findChild(QLabel,"todayclass_background")
        self.todayclass_background.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(0, 225, 245, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 8px""")

        self.TOPIC()

        result = self.get_current_time_period(class_time)
        if result == None:
            self.TitleLabel.setText("暂无课程")
        else:
            self.TitleLabel.setText(result)

        self.generate_timetable()

        font = QFont("MiSans Demibold", 16)
        self.Widgets_ORD.setFont(font)
        self.Widgets_ORD.setIndent(8)
        self.Widgets.setFont(font)
        self.Widgets.setIndent(8)
        font = QFont("MiSans Demibold",21)
        font.setWeight(QFont.Bold)
        self.lingyun_down.setFont(font)

        
        self.class_i = ""
        self.class_ORD_i = ""
        for j in range(len(self.done_class)):
            i = self.done_class[j]
            ORDs = self.done_class_ORD[j]
            if len(i) > 0:
                self.class_i = self.class_i + i + "\n"
                self.class_ORD_i = self.class_ORD_i + ORDs + "\n"
        self.Widgets_ORD.setText(self.class_ORD_i)
        self.Widgets.setText(self.class_i)

        # 定时器更新颜色
        self.cols = [0,0,1,0]
        self.col = ["220","70","0","60"]
        self.up_col = QTimer(self)
        self.up_col.timeout.connect(self.update_color)
        self.up_col.start(10)
    def generate_timetable(self):
        global class_table,class_time,class_ORD_Filtration
        current_day = datetime.now().strftime("%w") # 获取当前星期
        current_day = "1"
        self.done_class = [] # 初始化课程列表和时间列表
        self.done_class_ORD = []
        courses = class_table.get(current_day, []) # 获取当前星期的课程
        for course_block in courses:
            for period, classes in course_block.items():
                self.done_class_ORD.append(period)# 添加时间段标识
                self.done_class.append("——") # 在 self.done_class 中添加空格以表示时间段标识
                section_counter = 1  # 初始化节数计数器
                for i, cls in enumerate(classes): # 遍历该时间段的课程
                    class_time_slot = class_time[period][i]
                    if class_time_slot in class_ORD_Filtration:
                        # 如果时间段被过滤，则用空格代替
                        self.done_class.append(cls)
                        self.done_class_ORD.append("")
                    else:
                        # 否则添加课程名称和“第x节”标识
                        self.done_class.append(cls)
                        #if len(classes) > 1:
                        self.done_class_ORD.append(f"第{section_counter}节")
                        section_counter += 1  # 增加节数计数器
    def get_current_time_period(self, class_time):
        now = datetime.now().strftime("%H:%M")
        week = datetime.now().strftime("%w")
        week = "1"
        # 遍历所有时间段
        for period, times in class_time.items():
            for index, time_range in enumerate(times):
                start_time, end_time = map(lambda x: datetime.strptime(x, "%H:%M").time(), time_range.split('-'))
                current_time = datetime.strptime(now, "%H:%M").time()
                # 检查当前时间是否在时间段内  
                if start_time <= current_time <= end_time:
                    for item in class_table[week]:
                        if period in item:
                            try:
                                return item[period][index]
                            except:
                                return None
        return None # 如果没有找到匹配的时间段，返回None
    def update_color(self):
        self.todayclass_background.setStyleSheet(f"""background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[0]}, 150, 255, 255), stop:1 rgba({self.col[2]}, 200, 255, 255));border-radius: 10px""")
        for i in range(4):
            if self.cols[i] == 0:
                if self.col[i] == "1":
                    self.cols[i] = 1
                self.col[i] = str(int(self.col[i])-1)
            else:
                if self.col[i] == "254":
                    self.cols[i] = 0
                self.col[i] = str(int(self.col[i])+1)
    def TOPIC(self):
        if theme == "light":
            self.lingyun_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.todayclass_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")

            self.lingyun_class.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.lingyun_down.setStyleSheet("color: rgba(0, 0, 0, 255)")



            self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
        elif theme == "dark":
            self.lingyun_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.todayclass_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")

            self.Widgets_ORD.setStyleSheet("line-height: 100px;color: rgba(255, 255, 255, 255)")
            self.Widgets.setStyleSheet("color: rgba(255, 255, 255, 255)")

            self.lingyun_class.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.lingyun_down.setStyleSheet("color: rgba(255, 255, 255, 255)")

            self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")  
    def Countdown(self):#弃用
        now = datetime.now().strftime("%H:%M:%S")
        nows = datetime.now()
        week = datetime.now().strftime("%w")
        # 遍历所有时间段
        for period, times in class_time.items():
            for index, time_range in enumerate(times):
                start_time, end_time = map(lambda x: datetime.strptime(x, "%H:%M").time(), time_range.split('-'))
                current_time = datetime.strptime(now, "%H:%M:%S").time()
                # 将当前时间和结束时间转换为包含当前日期的datetime对象
                current_datetime = datetime.combine(nows.date(), nows.time())
                end_datetime = datetime.combine(nows.date(), end_time)
                # 检查当前时间是否在时间段内
                if start_time <= current_time <= end_time:
                    remaining_time = end_datetime - current_datetime
                    print(remaining_time)
                    # 提取分钟和秒数
                    minutes = remaining_time.seconds // 60
                    seconds = remaining_time.seconds % 60
                    print(minutes)
                    # 格式化输出
                    down_time = f"{minutes:02}:{seconds:02}"
                    break
        self.lingyun_down.setText(down_time)
    def updateCountdown(self):
        now = datetime.now()
        nows = datetime.now()
        self.remaining_minutes = 00
        self.remaining_seconds = 00
        self.remaining_percentage = 0
        for period, times in class_time.items():
            for index, time_range in enumerate(times):
                start_time_str, end_time_str = time_range.split('-')
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
                
                current_time = now.time()
                
                # 将当前时间和结束时间转换为包含当前日期的datetime对象
                current_datetime = datetime.combine(nows.date(), current_time)
                end_datetime = datetime.combine(nows.date(), end_time)
                
                # 检查当前时间是否在时间段内
                if start_time <= current_time <= end_time:
                    remaining_time = end_datetime - current_datetime
                    self.remaining_minutes = remaining_time.seconds // 60
                    self.remaining_seconds = remaining_time.seconds % 60
                    # 计算总时间（秒）
                    total_time_seconds = (datetime.combine(now.date(), end_time) - datetime.combine(now.date(), start_time)).total_seconds()
                    # 计算剩余时间的百分比
                    self.remaining_percentage = (remaining_time.total_seconds() / total_time_seconds) * 100
                    break
        # 更新标签显示
        self.lingyun_down.setText(f"{self.remaining_minutes:02}:{self.remaining_seconds:02}")
        self.lingyun_Bar.setVal(self.remaining_percentage)

        

if 1==0:
    theme = "dark"
else:
    theme = "light"
class_table = {
    "1": [
        {"上午": ["早读", "英语", "地理", "语文", "数学"]},
        {"下午": ["历史", "化学", "体育"]},
        {"晚上": ["自习"]}
    ],
    "2": [
        {"上午": ["早读", "化学", "语文", "物理", "英语"]},
        {"下午": ["美术", "数学", "生物"]},
        {"晚上": ["自习"]}
    ],
    "3": [
        {"上午": ["早读", "语文", "语文", "数学", "数学"]},
        {"下午": ["政治", "生物", "英语"]},
        {"晚上": ["自习"]}
    ],
    "4": [
        {"上午": ["数学", "政治", "英语", "地理", "语文"]},
        {"下午": ["化学", "物理", "数学"]},
        {"晚上": ["自习"]}
    ],
    "5": [
        {"上午": ["早读", "英语", "物理", "数学", "历史"]},
        {"下午": ["体育", "语文", "音乐"]},
        {"晚上": ["自习"]}
    ],
    "6": [
        {"上午": []},
        {"下午": []},
        {"晚上": ["自习"]}
    ],
    "7": [
        {"上午": ["早读", "历史", "物理", "政治", "化学"]},
        {"下午": ["地理", "生物", "生物"]},
        {"晚上": ["自习"]}
    ]
}   
class_time = {
    "上午": ["7:20-8:00","08:00-8:45", "08:55-9:40","10:10-10:55","11:10-11:50"],
    "下午": ["13:10-14:50", "15:05-15:45","15:50-16:35"],
    "晚上": ["18:30-20:30"]
}
class_ORD_Filtration = ["7:20-8:00"]



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    demo = Desktop_Component()
    demo.show()
    sys.exit(app.exec_())