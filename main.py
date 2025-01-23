import sys, os, logging, winreg as reg,webbrowser, warnings, json,threading
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime,timedelta
from playsound import playsound
from qfluentwidgets import (
    FluentWindow, FluentIcon,FluentWindow, SubtitleLabel,Slider,Action,SystemTrayMenu, 
    PushButton, SwitchButton,SpinBox,NavigationItemPosition,InfoBarIcon,TeachingTip
    ,BodyLabel,TransparentToolButton,PrimaryToolButton,TransparentPushButton,
    StyleSheetBase, Theme, qconfig,ToolButton,FluentWindow, SystemThemeListener, isDarkTheme,themeColor,setThemeColor
    ,setTheme,toggleTheme,SmoothScrollArea,TitleLabel,ProgressBar,TableWidget,StrongBodyLabel,MessageBox
    ,Dialog
)
from qframelesswindow.utils import getSystemAccentColor
#未取项SpinBox
"""Theme, setTheme,ToolButton, ListWidget, ComboBox, CaptionLabel, LineEdit, 
PrimaryPushButton, TableWidget, Flyout, InfoBarIcon,FlyoutAnimationType, 
MessageBox,CalendarPicker, BodyLabel, ColorDialog, isDarkTheme, TimeEdit, EditableComboBox, MessageBoxBase,
SearchLineEdit,  PlainTextEdit, ToolTipFilter, ToolTipPosition, RadioButton, HyperlinkLabel,
PrimaryDropDownPushButton,  RoundMenu, CardWidget, ImageLabel, StrongBodyLabel,
TransparentDropDownToolButton,  SmoothScrollArea,ColorPickerButton,NavigationItemPosition, """


warnings.filterwarnings("ignore", category=DeprecationWarning) # 忽略警告
Version = '1.4.6'
# 获取当前完整路径,获取当前文件名（os.path.basename(sys.argv[0])获得的是exe名字）
script_dir = sys.argv[0].replace(os.path.basename(sys.argv[0]),"")
script_full_path = sys.argv[0]
os.chdir(script_dir)# 切换工作目录，不切换执行.exe的目录还是cmd的路径

#初始化程序整体
class Initialization():
    def __init__(self):
        global theme_manager,theme,clock,tops,warn
        #初始化数据
        self.get_datas()
        #初始化主题管理器
        theme_manager = ThemeManager()
        theme_manager.toggleTheme(Theme.AUTO)
        theme = "dark" if isDarkTheme() else "light"
        
        tops = SystemTrayMenus()
        tops.create_tray_icon()


        # 创建桌面组件
        
        self.DP_Comonent = Desktop_Component()
        warn = class_warn()

        # 连接Sender对象的自定义信号到Receiver对象的槽函数
        theme_manager.customSignal.connect(self.DP_Comonent.TOPIC)

        # 创建桌面时钟
        clock = TransparentClock(datas)
        #clock.resize(int(datas['width']), int(datas['height']))  # 设置窗口大小
        clock.move(int(datas['x']), int(datas['y']))  # 设置窗口位置
        #clock.setAttribute(Qt.WA_TransparentForMouseEvents)

        

        
        #显示时钟和桌面组件
        clock.show()
        self.DP_Comonent.show()
        
        

             
    def get_datas(self):
        global class_table,class_time,class_ORD_Filtration,datas,lists
        # 默认课程表和时间
        default_class_table = {
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
                {"上午": ["", "", "", "", ""]},
                {"下午": ["", "", ""]},
                {"晚上": ["自习"]}
            ],
            "7": [
                {"上午": ["早读", "历史", "物理", "政治", "化学"]},
                {"下午": ["地理", "生物", "生物"]},
                {"晚上": ["自习"]}
            ]
        }   
        default_class_time = {
            "上午": ["7:20-8:00","08:00-8:45", "08:55-9:40","10:10-10:55","11:10-11:50"],
            "下午": ["14:10-14:44", "15:05-15:45","15:50-16:35"],
            "晚上": ["18:30-20:30"]
        }
        default_class_ORD_Filtration = ["7:20-8:00"]

        # 尝试从文件加载数据，如果文件不存在则使用默认值
        class_table = self.load_from_json('class_table.json', default_class_table)
        class_time = self.load_from_json('class_time.json', default_class_time)
        class_ORD_Filtration = self.load_from_json('class_ORD_Filtration.json', default_class_ORD_Filtration)


        # 默认数据时钟数据
        data = {'comboBox': '桌面',
                'x' : '700',
                'y' : '100',
                'width' : '200',
                'height' : '100',
                'fontSize' : '72',
                'textColor' : 'white',
                'fontname' : '微软雅黑',
                'update' : '100',
                'Penetrate' : 'True',
                }
        datas = {}
        for key in data:
            default_value = data[key]
            registry_value = self.read_from_registry(key, default_value)
            if registry_value is not None:
                datas[key] = registry_value
        lists = {'sets':False,'black':False,'black_notime':False,'black_f':data['comboBox'],'close_sets':False,"widgets_on":False,"down":False}

    def white_Widgets(self):
        # 保存课程表和时间到文件
        try:
            self.save_to_json(class_table, 'class_table.json')
            self.save_to_json(class_time, 'class_time.json')
            self.save_to_json(class_ORD_Filtration, 'class_ORD_Filtration.json')
            self.DP_Comonent.update_Widgets()
            return None
        except Exception as e:
            return e

    def save_to_json(self, data, filename):
        directory = 'Resource\\json'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_json(self, filename, default_data):
        directory = 'Resource\\json'
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 如果文件不存在，返回默认数据并可能保存默认数据到文件
            self.save_to_json(default_data, filename)
            return default_data

    # 写入注册表
    def write_to_registry(self, value_name, value_data):
        try:
            # 尝试创建或打开注册表键
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
            # 设置值
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_SZ, value_data)
            # 如果需要，可以在这里添加成功消息
            # QMessageBox.information(self, '成功', '写入注册表成功！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'写入注册表失败：{e}')
        finally:
            # 关闭注册表键
            if 'registry_key' in locals():
                reg.CloseKey(registry_key)
    
    # 读注册表
    def read_from_registry(self, value_name, default_value=None):
        try:
            # 打开注册表键
            with reg.OpenKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes', 0, reg.KEY_QUERY_VALUE) as key:
                # 查询注册表值
                value, regtype = reg.QueryValueEx(key, value_name)
                #QMessageBox.information(self, '成功', f'读取注册表成功：{value}')
                # 返回读取到的值
                return value
        except FileNotFoundError:
            # 如果找不到文件，即注册表项不存在
            if default_value is not None:
                # 写入默认值到注册表
                self.write_to_registry(value_name, default_value)
                # 返回默认值
                return default_value
            else:
                # 弹出警告框，提示注册表项不存在且未提供默认值
                QMessageBox.warning(self, '警告', '注册表项不存在，且未提供默认值。')
                # 返回None
                return None
        except Exception as e:
            # 捕获其他异常
            QMessageBox.critical(self, '错误', f'读取注册表失败：{e}')
            # 返回None
            return None

    # 检测系统深色模式（注册表方法，目前没用）
    def check_dark_mode(self):
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path)
            apps_use_light_theme, _ = reg.QueryValueEx(key, 'AppsUseLightTheme')
            reg.CloseKey(key)
            if apps_use_light_theme == 0:
                return "dark"
            else:
                return "light"
        except Exception as e:
            QMessageBox.warning(None, '警告', f'读取系统主题程序错误：{str(e)}\n将使用浅色模式。')
            return "light"
# 时钟类
class TransparentClock(QMainWindow):
    def __init__(self, datas):
        super().__init__()
        
        # 设置窗口属性
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint )
        
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 为了使窗口置顶，我们还需要设置这个属性
        if datas['comboBox'] == "置顶":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 鼠标穿透
        if datas['Penetrate'] == 'True':
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
 

        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局和标签
        layout = QVBoxLayout()
        self.time_label = QLabel('00:00:00', alignment=Qt.AlignCenter)
        self.time_label.setAlignment(Qt.AlignLeft)
        
        # 设置字体，大小，并加粗
        font = QFont(datas['fontname'], int(datas['fontSize']), QFont.Bold)  # 这里将字体权重设置为Bold
        self.time_label.setFont(font)
        
        # 设置文本颜色为白色
        color_value = datas['textColor']  # 获取颜色值
        self.time_label.setStyleSheet(f'color: {color_value};')
        
        layout.addWidget(self.time_label)
        central_widget.setLayout(layout)

        
        # 定时器更新时钟
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(int(datas['update']))
    
    def update_time(self):
        global datas,lists
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        self.time_label.setText(time_str)

    def update_settings(self,choose):
        #实时更新
        if choose == "fontSize" or choose == "fontname": 
            self.time_label.setFont(QFont(datas['fontname'], int(datas['fontSize']), QFont.Bold))
        elif choose == "textColor":
            color_value = datas['textColor']
            self.time_label.setStyleSheet(f'color: {color_value};')
        elif choose == "update":
            self.timer.stop()
            self.timer.start(int(datas['update']))
        elif choose == "x" or choose == "y":
            #clock.resize(int(datas['width']), int(datas['height']))  
            clock.move(int(datas['x']), int(datas['y']))  
        elif choose == "comboBox":
            # 保存当前的窗口标志
            current_flags = self.windowHandle().flags()
            logger = logging.getLogger(__name__)
            logger.debug(current_flags & Qt.WindowStaysOnTopHint)
            if (current_flags & Qt.WindowStaysOnTopHint) == Qt.WindowStaysOnTopHint:
                logger.debug("取消钉住")
                # 清除置顶标志，但保留无边框标志
                self.windowHandle().setFlags(current_flags & ~Qt.WindowStaysOnTopHint)
            else:
                logger.debug("钉住")
                # 设置置顶标志，并保留无边框标志
                self.windowHandle().setFlags(current_flags | Qt.WindowStaysOnTopHint)
            self.update()

        #clock.resize(int(datas['width']), int(datas['height'])) 

    def closeEvent(self, event: QCloseEvent) -> None:
        if lists['close_sets']:
            event.ignore()
            lists['close_sets'] = False
        else:
            event.accept()
# 设置窗口new
class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        #self.setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))
        
        qconfig.themeChanged(self.qss)
class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.close_event_args = None
        self.datas = datas
        self.addui()
        self.initNavigation()
        self.initWindow()
        #获取系统主题色
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor(), save=False)
    def initNavigation(self):
        self.addSubInterface(self.home, FluentIcon.HOME, '时钟设置')
        self.addSubInterface(self.updates, FluentIcon.UPDATE, '更新日志')
        self.addSubInterface(self.classes, FluentIcon.CALENDAR, '编辑课表')
        #self.addSubInterface(self.albumInterface, FluentIcon.BOOK_SHELF, '课表管理')
        #self.navigationInterface.addSeparator()
        #self.addSubInterface(self.hh, FluentIcon.SETTING, '高级设置')
        self.addSubInterface(self.info, FluentIcon.INFO, '关于', NavigationItemPosition.BOTTOM)
    def addui(self):
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度

        try:
            self.home = uic.loadUi('Resource/ui/set_home.ui')
            self.home.setObjectName("home")
            self.updates = uic.loadUi('Resource/ui/set_updates.ui')
            self.updates.setObjectName("updates")
            self.info = uic.loadUi('Resource/ui/set_info.ui')
            self.info.setObjectName("info")
            self.classes = uic.loadUi('Resource/ui/set_classes.ui')
            self.classes.setObjectName("classes")
        except Exception as e:
            self.error("导入UI文件出现错误，详细的错误内容为\n" + str(e),"导入错误",True)


        # 触摸屏滑动适配
        scroll = self.home.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)  
        scroll = self.updates.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.info.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)

        # 获取主界面中的控件
        #self.myButton = self.home.findChild(SwitchButton, 'CW2_onof_button')
        #print(self.myButton)
        #self.myButton.setChecked(True)# 设置按钮状态为选中
        #print(self.myButton.isChecked())# 打印按钮状态


        #------设置控件开始--------

        #字体大小
        self.CW1_spinBox = self.home.findChild(SpinBox, 'CW1_spinBox')
        self.CW1_spinBox.setValue(int(datas["fontSize"]))
        self.CW1_spinBox.setSingleStep(5)
        self.CW1_spinBox.setRange(0, 2000)
        self.CW1_spinBox.valueChanged.connect(lambda value: self.update_time(value,'fontSize'))

        #时间x坐标
        self.CW2_Slider = self.home.findChild(Slider, 'CW2_Slider')
        self.CW2_Slider.setMaximum(display_x)
        self.CW2_Slider.setValue(int(datas["x"]))
        self.CW2_Slider.valueChanged.connect(lambda value: self.update_time(value,'x'))

        #时间y坐标
        self.CW3_Slider = self.home.findChild(Slider, 'CW3_Slider')
        self.CW3_Slider.setMaximum(display_y)
        self.CW3_Slider.setValue(int(datas["y"]))
        self.CW3_Slider.valueChanged.connect(lambda value: self.update_time(value,'y'))

        #置顶
        self.CW4_onof_button = self.home.findChild(SwitchButton, 'CW4_onof_button')
        if datas["comboBox"] == "置顶":
            self.CW4_onof_button.setChecked(True)
        else:
            self.CW4_onof_button.setChecked(False)
        self.CW4_onof_button.checkedChanged.connect(lambda value: self.update_time(value,'comboBox'))

        #选择颜色
        self.CW5_color_button = self.home.findChild(PushButton, 'CW5_color_button')
        self.CW5_color_button.clicked.connect(self.choose_color)

        #选择字体
        self.CW6_font_button = self.home.findChild(PushButton, 'CW6_font_button')
        self.CW6_font_button.clicked.connect(self.choose_font)

        #鼠标穿透
        self.CW7_onof_button = self.home.findChild(SwitchButton, 'CW7_onof_button')
        if datas["Penetrate"] == "False":
            self.CW7_onof_button.setChecked(False)
        else:
            self.CW7_onof_button.setChecked(True)
        self.CW7_onof_button.checkedChanged.connect(lambda value: self.update_time(value,'Penetrate'))

        #开机启动按钮
        self.CW8_onof_button = self.home.findChild(SwitchButton, 'CW8_onof_button')
        if self.read_startup_program():
            self.CW8_onof_button.setChecked(True)
        else:
            self.CW8_onof_button.setChecked(False)
        self.CW8_onof_button.checkedChanged.connect(lambda value: self.update_time(value,'startup'))

        #------设置关于页面的控件--------
        self.version = self.info.findChild(BodyLabel, 'version')
        self.version.setText(f'当前版本：{Version}')
        self.Join_qq = self.info.findChild(PushButton, 'Join_qq')
        self.Join_qq.clicked.connect(lambda :webbrowser.open('https://qm.qq.com/q/KN7UVWFr6C'))
        self.qq_clipboard_button = self.info.findChild(PushButton, 'qq_clipboard_button')
        self.qq_clipboard_button.clicked.connect(self.qq_clipboard)
        self.bilibili_button = self.info.findChild(PushButton, 'bilibili_button')
        self.bilibili_button.clicked.connect(lambda :webbrowser.open('https://space.bilibili.com/627622081'))

        #------设置课表页面的控件--------
        self.TableWidget = self.classes.findChild(TableWidget, 'TableWidget')
        # 启用边框并设置圆角
        self.TableWidget.setBorderVisible(True)
        self.TableWidget.setBorderRadius(8)
        done, ls = self.convert_table()
        self.widget_time = self.convert_time()
        self.TableWidget.setWordWrap(False)
        # 设置表格的行数和列数
        self.TableWidget.setRowCount(ls)
        self.TableWidget.setColumnCount(8)
        self.TableWidget.setHorizontalHeaderLabels(['时间','星期一','星期二','星期三','星期四','星期五','星期六','星期日'])
        # 禁止用户修改列宽
        #self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 设置列宽为固定
        for i in range(ls):
            item = QTableWidgetItem(self.widget_time[i])
            self.TableWidget.setItem(i, 0, item)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        for i, Info in enumerate(done):
            for j in range(7):
                item = QTableWidgetItem(Info[j])
                self.TableWidget.setItem(i, j+1, item)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)# 设置单元格文本居中对齐
        class_time
        # 连接单元格内容改变信号到table_update函数
        self.TableWidget.itemChanged.connect(self.table_update)
        # 按钮
        self.Table_Button = self.classes.findChild(PushButton, 'Table_Button')
        self.Table_Button.clicked.connect(self.on_resize)
        self.Table_Time = QTimer()
        self.Table_Time.timeout.connect(self.on_resize)
        self.Table_Time.start(1500)

    def on_resize(self):
        # 重新平均设置列宽
        total_width = self.TableWidget.viewport().width() - 120 # 获取视口宽度
        column_width = total_width // 7  # 计算每列宽度
        for col in range(7):
            self.TableWidget.setColumnWidth(col+1, column_width)  # 设置每列宽度
        self.TableWidget.setColumnWidth(0, 120)  # 设置第一列宽度
        self.Table_Time.stop()

    def table_update(self, item=None):
         # 如果单元格对象为空
        if item is None:
            pass
        else:
            row = item.row()  # 获取行数#row是第x-1节
            col = item.column()  # 获取列数#col多少就是星期几
            text = item.text()  # 获取内容#text是课程名
            if col == 0:
                if lists["widgets_on"] == False:
                    w = MessageBox("警告", "请不要在此处修改时间，\n如果需要修改请前往“时间线”进行编辑。", self)
                    w.yesButton.setText("好")
                    w.cancelButton.hide()
                    w.buttonLayout.insertStretch(1)
                    if w.exec():
                        lists["widgets_on"] = True
                        item = QTableWidgetItem(self.widget_time[int(row)])
                        self.TableWidget.setItem(int(row), int(col), item)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        lists["widgets_on"] = False
            else:
                ins = 0
                inss = []
                for i in range(len(class_table[str(col)])):
                    f = list(class_table[str(col)][i].keys())[0]
                    ins += len(class_table[str(col)][i][f]) #获得每天有多少节课
                    inss.append(len(class_table[str(col)][i][f]))
                for i in range(1,len(inss)):#计算每个时间段的结束位置
                    inss[i] = inss[i-1] + inss[i]
                if 0 <= row < ins and 1 <= col <= 7:
                    t = 0
                    for i in range(len(inss)):
                        if row+1 <= inss[i]:
                            period = list(class_table[str(col)][i].keys())[0] # 获取对应时间段
                            break
                    # 确定当前行属于哪个时间段以及这是该时间段的第几节课
                    period_index = 0
                    if i != 0:
                        period_index = row - inss[i-1]
                    else:
                        period_index = row
                    # 检查该时间段是否有课程列表
                    if class_table[str(col)][i][period]:
                        class_table[str(col)][i][period][period_index] = text# 如果有课程列表，则更新第一个课程名称
                    else: # 暂时不用(不会被调用到)
                        class_table[str(col)][i][period] = [text]# 如果没有课程列表，则创建一个并添加新课程名称
                    
                    # 更新后的class_table
                    e = main.white_Widgets()
                    if e != None:
                        self.error("保存课表出现错误：\n" + str(e))
                else:
                    self.error("修改了无效的行或索引")
    def convert_table(self):
        # 将class_table转换为二维列表
        jies = []
        for week in range(1, 8):
            day = []
            for wu in range(len(class_table[str(week)])):
                wus = list(class_table[str(week)][wu].keys())[0]
                if class_table[str(week)][wu][wus] == []:
                    for kong in range(len(class_time[list(class_table[str(week)][wu].keys())[0]])):
                        day.append("")
                else:
                    for jie in range(len(class_table[str(week)][wu][wus])):
                        day.append(class_table[str(week)][wu][wus][jie])
            jies.append(day)
        done = [list(t) for t in list(zip(*jies))]# 使用zip函数转置列表,由于zip返回的是元组，如果需要列表，可以使用列表推导式转换
        return done,len(day)
    def convert_time(self):
        result = []
        for values in class_time.values():
            result.extend(values)
        return result
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.update_time(color.name(),'textColor')
    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.update_time(font.family(),'fontname')
            #self.update_time(font.family(),'fontFamily')
    def qq_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText('917509031')
        TeachingTip.create(
            target=self.qq_clipboard_button,
            icon=InfoBarIcon.SUCCESS,
            title='复制成功！',
            content="快去加入QQ群来一起交流吧！",
            isClosable=True,
            #tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=1000,
            parent=self
        )
    def update_time(self,value,choose):
        global clock
        def white_reg():
            try:
                # 创建或打开注册表键
                registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
                # 获取当前设置的值
                datas[choose] = str(value)
                # 将设置写入注册表
                reg.SetValueEx(registry_key, choose, 0, reg.REG_SZ, str(value))
                #lists['sets'] = True
                clock.update_settings(choose)
            except Exception as e:
                self.error(str(e))
        if choose == "fontSize":
            white_reg()
        elif choose == "textColor":
            white_reg()
        elif choose == "x":
            white_reg()
        elif choose == "y":
            white_reg()
        elif choose == "comboBox":
            if value == True:
                value = "置顶"
                white_reg()
            else:
                value = "桌面"
                white_reg()
        elif choose == "fontname":
            white_reg()
        elif choose == "Penetrate":
            value = str(value)
            white_reg()
        elif choose == "startup":
            if self.startup_program(value) == False:
                self.CW8_onof_button.setChecked(False)
    def error(self,e,msg="错误",grades=False):
        if grades:
            w = Dialog(msg, str(e)+"\n 此问题非常严重，直接影响程序运行，只能关闭程序，给您带来不便，请谅解。", self)
            w.yesButton.setText("关闭程序")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            if w.exec():
                # 停止监听器线程
                theme_manager.themeListener.terminate()
                theme_manager.themeListener.deleteLater()
                QApplication.quit()
        else:
            w = MessageBox(msg, e, self)
            w.yesButton.setText("关闭程序")
            w.cancelButton.setText("忽略错误")
            if w.exec():
                # 停止监听器线程
                theme_manager.themeListener.terminate()
                theme_manager.themeListener.deleteLater()
                QApplication.quit()
            else:pass
        #w = Dialog("标题", "这是一条消息通知", self)
    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('ico\LINGYUN.ico'))
        self.setWindowTitle('凌云时间 - 设置 - v' + Version)
        self.navigationInterface.setExpandWidth(200)
        self.navigationInterface.setCollapsible(False)
    def closeEvent(self, e):
        lists['close_sets'] = True
    def startup_program(self, zt, program_path=script_full_path, program_name="凌云班级时间"):
        try:
            # 打开注册表项，为当前用户设置开机启动
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
            # 设置程序开机启动
            if zt:
                reg.SetValueEx(key, program_name, 0, reg.REG_SZ, program_path)
            else:
                reg.DeleteValue(key, program_name)
            reg.CloseKey(key)
            return True
        except WindowsError:
            self.error("写入注册表失败，请检查权限是否充足\n或者尝试以管理员身份运行\n最后还是不行可以反馈给开发者。","访问注册表出错")
            return False
        except Exception as e:
            self.error("读写注册表出现问题，以下为详细问题：（请报告给开发者）\n" + str(e))
            return False
    def read_startup_program(self,program_name="凌云班级时间"):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_READ)
            try:
                reg.QueryValueEx(key, program_name)
                return True  # 如果存在，则返回True
            except FileNotFoundError:
                return False  # 如果不存在，则返回False
            finally:
                reg.CloseKey(key)
        except Exception as e:
            self.error("读取注册表出现问题，以下为详细问题：（请报告给开发者）\n" + str(e))
            return False

# 一键黑屏
class BlackScreen(QWidget):
    def __init__(self,notime):
        super().__init__()
        self.initUI(notime)

    def initUI(self,notime):
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        w_width = screen_geometry.width()  # 屏幕宽度
        w_height = screen_geometry.height()  # 屏幕高度
        
        # 设置窗口标题和大小（这里假设您想要全屏）
        self.setWindowTitle('黑幕')
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, w_width, w_height)

        # 创建按钮并添加到布局中
        self.button = TransparentPushButton(FluentIcon.EMBED.icon(color='#FFFFFF'),"     退出", self)
        self.button.setStyleSheet("""color:#ffffff;""")
        self.button.setGeometry(QRect(w_width-150, w_height-120, 50, 50))

        # 创建标签
        self.time_hei = QLabel('00:00:00',self)#, alignment=Qt.AlignCenter)
        self.time_hei.setAlignment(Qt.AlignLeft)
        self.time_hei.setGeometry(QRect(int(datas['x']), int(datas['y']), 500, 500))
        # 设置字体，大小，并加粗
        fonts = QFont(datas['fontname'], int(datas['fontSize']), QFont.Bold)  # 这里将字体权重设置为Bold
        self.time_hei.setFont(fonts)
        # 设置文本颜色为白色
        self.time_hei.setStyleSheet(f'color:white;')
    

        """self.zdy_hei = QLabel('',self)
        self.zdy_hei.setAlignment(Qt.AlignRight)
        self.zdy_hei.setGeometry(QRect(int(datas['x'])-200, int(datas['y'])+100, 500, 400))
        self.zdy_hei.setFont(fonts)
        self.zdy_hei.setStyleSheet(f'color:white;')"""

        # 定时器更新时钟
        self.notime = notime
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.uptime)
        self.timer.start(int(datas['update']))

        # 设置按钮样式
        self.setStyleSheet("""QWidget {background-color: black;}""")

        # 连接按钮点击事件
        self.button.clicked.connect(self.up_close)
    

    def uptime(self):
        if datas['comboBox'] == '置顶' or bool(self.notime):
            self.time_hei.hide()
        else:
            self.time_hei.show()
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        self.time_hei.setText(time_str)

    def up_close(self):
        self.destroy()
# 主题色
class ThemeManager(QObject):
    # 定义一个自定义信号
    customSignal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        

        # 连接 themeChanged 信号到槽函数
        qconfig.themeChanged.connect(self.onThemeChanged)
        # 创建主题监听器
        self.themeListener = SystemThemeListener(self)
        # 启动监听器
        self.themeListener.start()

    def closeEvent(self, e):
        # 停止监听器线程
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    @pyqtSlot()  # 标记这是一个槽函数
    def onThemeChanged(self):
        #print("主题已改变！")
        # 在这里添加处理主题改变后的逻辑
        setTheme(Theme.AUTO)
        self.customSignal.emit("1")




    def toggleTheme(self, theme):
        setTheme(theme)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # 云母特效启用时需要增加重试机制
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))
# 桌面组件
class Desktop_Component(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    def initUI(self):
        global display_x, display_y
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)# 使背景透明
        self.move(display_x,12)
        self.uic_ui()

        self.class_up_time = QTimer(self)
        self.class_down_time = QTimer(self)
        self.alert() # 倒计时模块
        
        #窗口在屏幕的位置初始化
        self.DP_x = display_x - 255
        self.DP_y = 12
        

        self.animation_i = display_x - 260

        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(400)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rect = QPropertyAnimation(self, b'geometry')
        self.animation_rect.setDuration(450)
        self.animation_rect.setStartValue(QRect(display_x, self.DP_y, self.width(), self.height()))
        self.animation_rect.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect.setEasingCurve(QEasingCurve.InOutCirc)

        self.animation.start()
        self.animation_rect.start()
    def mousePressEvent(self, event):
        # 获取窗口的坐标位置
        window_pos = self.frameGeometry().topLeft()
        if window_pos.x() == self.DP_x:
            self.animation_rect = QPropertyAnimation(self, b'geometry')
            self.animation_rect.setDuration(450)
            self.animation_rect.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
            self.animation_rect.setEndValue(QRect(display_x-35, self.DP_y, self.width(), self.height()))
            self.animation_rect.setEasingCurve(QEasingCurve.InOutCirc)
            self.animation_rect.start()
        elif window_pos.x() == display_x-35:
            self.animation_rect = QPropertyAnimation(self, b'geometry')
            self.animation_rect.setDuration(450)
            self.animation_rect.setStartValue(QRect(display_x-35, self.DP_y, self.width(), self.height()))
            self.animation_rect.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
            self.animation_rect.setEasingCurve(QEasingCurve.InOutCirc)
            self.animation_rect.start()
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
        self.lingyun_Bar.setCustomBarColor(QColor(0, 0, 255), QColor(0, 255, 0))

        self.todayclass_Title = self.findChild(QLabel,"todayclass_Title")
        self.Widgets_ORD = self.findChild(StrongBodyLabel,"class_ORD")
        self.Widgets = self.findChild(StrongBodyLabel,"class_widget")
        
        self.lingyun_background = self.findChild(QLabel,"lingyun_background")
        self.lingyun_background_2 = self.findChild(QLabel,"lingyun_background_2")
        self.todayclass_background = self.findChild(QLabel,"todayclass_background")
        self.todayclass_background.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(0, 225, 245, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 8px""")

        self.TOPIC()

        font = QFont("MiSans Demibold", 16)
        self.Widgets_ORD.setFont(font)
        self.Widgets_ORD.setIndent(8)
        self.Widgets.setFont(font)
        self.Widgets.setIndent(8)
        font = QFont("MiSans Demibold",21)
        font.setWeight(QFont.Bold)
        self.lingyun_down.setFont(font)

        
        self.update_Widgets()

        # 定时器更新颜色
        self.cols = [0,0,1,0]
        self.col = ["220","70","0","60"]
        self.up_col = QTimer(self)
        self.up_col.timeout.connect(self.update_color)
        self.up_col.start(10)

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
        theme = "dark" if isDarkTheme() else "light"
        if theme == "light":
            self.lingyun_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.todayclass_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            #self.lingyun_class.setStyleSheet("color: rgba(0, 0, 0, 255)")
            #self.lingyun_down.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
        elif theme == "dark":
            self.lingyun_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.todayclass_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            #self.Widgets_ORD.setStyleSheet("line-height: 100px;color: rgba(255, 255, 255, 255)")
            #self.Widgets.setStyleSheet("color: rgba(255, 255, 255, 255)")
            #self.lingyun_class.setStyleSheet("color: rgba(255, 255, 255, 255)")
            #self.lingyun_down.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")  
    def closeEvent(self, event: QCloseEvent) -> None:
        if lists['close_sets']:
            event.ignore()
            lists['close_sets'] = False
        else:
            event.accept()

    def update_Widgets(self):
        # 该def生成课程表并且展示（初始化时调用1次）
        global class_table,class_time,class_ORD_Filtration
        current_day = datetime.now().strftime("%w") # 获取当前星期
        if current_day == "0": current_day = "7"
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
    def get_current_time_period(self, class_time):
        # 该def获得当前课程名字（初始化时调用1次,倒计时为00:01也会调用一次）
        now = datetime.now().strftime("%H:%M:%S")
        week = datetime.now().strftime("%w")
        if week == "0":week = "7"
        for period, times in class_time.items(): # 遍历所有时间段
            for index, time_range in enumerate(times):
                start_time, end_time = map(lambda x: datetime.strptime(x, "%H:%M").time(), time_range.split('-'))
                current_time = datetime.strptime(now, "%H:%M:%S").time()
                if start_time <= current_time < end_time: # 检查当前时间是否在时间段内
                    for day_courses in class_table[week]: # 检查当天是否有对应的课程
                        if period in day_courses: # 尝试返回课程名称
                            try: return day_courses[period][index]
                            except IndexError: continue # 如果索引越界，继续检查下一个时间段
                    return None # 如果没有找到课程（理论上不应该发生，除非课程列表为空），返回 None
        return None # 如果没有找到匹配的时间段，返回 None

    def updateCountdown(self):
        # 该def为倒计时模块上课服务（计时器调用）
        now = datetime.now()
        for period, times in class_time.items():
            for index, time_range in enumerate(times):
                start_time_str, end_time_str = time_range.split('-')
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
                
                current_time = now.time()
                
                # 将当前时间和结束时间转换为包含当前日期的datetime对象
                current_datetime = datetime.combine(now.date(), current_time)
                end_datetime = datetime.combine(now.date(), end_time)
                
                # 检查当前时间是否在时间段内
                if start_time <= current_time <= end_time:
                    remaining_time = end_datetime - current_datetime
                    remaining_minutes = remaining_time.seconds // 60
                    remaining_seconds = remaining_time.seconds % 60
                    # 计算总时间（秒）
                    total_time_seconds = (datetime.combine(now.date(), end_time) - datetime.combine(now.date(), start_time)).total_seconds()
                    # 计算剩余时间的百分比
                    remaining_percentage = 100 - (remaining_time.total_seconds() / total_time_seconds) * 100
                    break
        # 更新标签显示
        s = f"{remaining_minutes:02}:{remaining_seconds:02}"
        self.lingyun_down.setText(s)
        self.lingyun_Bar.setVal(remaining_percentage)
        if s == "00:01":
            self.timess = QTimer(self)
            self.timess.timeout.connect(lambda:self.alert(1))
            self.timess.start(2200)
            self.class_down_time.stop()
    def updateCountdowns(self,times): 
        # 该def为倒计时模块下课服务（计时器调用）
        now = datetime.now()
        current_time = now.time()
        for i in range(len(times) - 1):
            start_time = datetime.strptime(times[i].split('-')[1], '%H:%M').time()
            next_start_time = datetime.strptime(times[i+1].split('-')[0], '%H:%M').time()
            if start_time < current_time < next_start_time:
                #print('当前时间段', start_time ,  next_start_time)
                # 计算时间差
                start_datetime = datetime.combine(now.date(), start_time)
                current_datetime = datetime.combine(now.date(), current_time)
                next_start_datetime = datetime.combine(now.date(), next_start_time)
                remaining_time = next_start_datetime - current_datetime
                remaining_minutes = remaining_time.seconds // 60
                remaining_seconds = remaining_time.seconds % 60
                # 计算剩余时间的百分比
                total_time = next_start_datetime - start_datetime
                remaining_percentage = 100 - (remaining_time.total_seconds() / total_time.total_seconds()) * 100

        # 更新标签显示
        s = f"{remaining_minutes:02}:{remaining_seconds:02}"
        self.lingyun_down.setText(s)
        self.lingyun_Bar.setVal(remaining_percentage)
        if s == "00:01":
            self.timess = QTimer(self)
            self.timess.timeout.connect(lambda:self.alert(1))
            self.timess.start(2200)
            self.class_up_time.stop()
    def class_coming(self):
        # 该def为检测是否快开始上课（计时器调用）
        now = datetime.now()
        current_time = now.time()
        t = False
        for period, times in class_time.items():
            start_time = datetime.strptime(times[0].split('-')[0], '%H:%M').time()
            start_datetime = datetime.combine(now.date(), start_time)
            current_datetime = datetime.combine(now.date(), current_time)
            remaining_time = start_datetime - current_datetime
            # 计算剩余时间的分钟数
            remaining_minutes = remaining_time.total_seconds() / 60
            # 判断剩余时间是否小于15分钟
            if 0 < remaining_minutes < 15:
                t = True
                break
        if t:
            remaining_minutes = remaining_time.seconds // 60
            remaining_seconds = remaining_time.seconds % 60

            # 更新标签显示
            s = f"{remaining_minutes:02}:{remaining_seconds:02}"
            self.lingyun_down.setText(s)
            if s == "00:01":
                self.timess = QTimer(self)
                self.timess.timeout.connect(lambda:self.alert(1))
                self.timess.start(2200)
                self.coming_time.stop()
    def alert(self,st = None):
        result = self.get_current_time_period(class_time)
        if st != None:
            self.timess.stop() 
        if result == None: # 下课
            now = datetime.now()
            for period, times in class_time.items():
                end_time = datetime.strptime(times[-1].split('-')[1], "%H:%M").time()
                start_time = datetime.strptime(times[0].split('-')[0], "%H:%M").time()
                current_time = now.time()
                if start_time < current_time < end_time: # 有没有在任何时间段内
                    self.TitleLabel.setText("课间")
                    self.class_up_time.timeout.connect(lambda: self.updateCountdowns(times))
                    self.class_up_time.start(1000)
                    break
                else:
                    self.TitleLabel.setText("暂无课程")
                    self.lingyun_down.setText("00:00")
                    self.lingyun_Bar.setVal(100)
                    self.coming_time = QTimer(self)
                    self.coming_time.timeout.connect(self.class_coming)
                    self.coming_time.start(1000)
                    break
                    
            if st != None:
               warn.ui("up") #调用下课提醒
            return "up"
        else: # 上课
            self.TitleLabel.setText(result) 
            self.class_down_time.timeout.connect(self.updateCountdown)
            self.class_down_time.start(1000)
            if st != None:
               warn.ui("down") #调用上课提醒
            return "down"
         
# 上下课提醒
class class_warn(QWidget):
    def __init__(self):
        super().__init__()
        self.finish_wav = 'Resource/audio/finish.wav'
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)# 使背景透明
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.move(display_x,12)
    def ui(self,types):
        self.warn = uic.loadUi('Resource/ui/class_warn.ui', self)
        self.warn.setObjectName('warn')
        self.label = self.findChild(QLabel,"warn_label")
        if types == "up":
            self.label.setText("已下课")
        elif types == "down":
            self.label.setText("上课")

        #窗口在屏幕的位置初始化
        self.DP_x = display_x - 255
        self.DP_y = 12

        self.animation_i = display_x - 260


        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rect = QPropertyAnimation(self, b'geometry')
        self.animation_rect.setDuration(250)
        self.animation_rect.setStartValue(QRect(self.DP_x + 80, self.DP_y, self.width(), self.height()))
        self.animation_rect.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect.setEasingCurve(QEasingCurve.InOutCirc)


        self.show()

        self.animation.start()
        self.animation_rect.start()

        thread = threading.Thread(target=self.wav)
        thread.start()

        self.times = QTimer(self)
        self.times.timeout.connect(self.exits)
        self.times.start(1300)

    def wav(self):
        devices = AudioUtilities.GetSpeakers()
        clsctx = CLSCTX_ALL
        interface = devices.Activate(IAudioEndpointVolume._iid_, clsctx, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(False, None)
        volume.SetMasterVolumeLevelScalar(1.0, None)  # 将音量设置为70%
        playsound(self.finish_wav)

    def exits(self):
        self.times.stop()
        self.animations = QPropertyAnimation(self, b'windowOpacity')
        self.animations.setDuration(200)
        self.animations.setStartValue(1)
        self.animations.setEndValue(0)
        self.animations.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rects = QPropertyAnimation(self, b'geometry')
        self.animation_rects.setDuration(250)
        self.animation_rects.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rects.setEndValue(QRect(self.DP_x + 40, self.DP_y, self.width(), self.height()))
        self.animation_rects.setEasingCurve(QEasingCurve.InOutCirc)

        #self.animations.finished.connect(self.hide)
        self.animations.start()
        self.animation_rects.start()



















































# 托盘右键菜单
class SystemTrayMenus(SystemTrayMenu):
    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon('ico/LINGYUN.ico'), self)
        self.tray_icon.setToolTip('凌云时间')
        
        menu = SystemTrayMenu()
        settings_action = Action(FluentIcon.SETTING,'设置', self)
        settings_action.triggered.connect(self.setting_show)

        black_screen_action = Action('开启黑屏', self)
        black_screen_action.triggered.connect(lambda: self.black_screen(False))
        
        black_screen = Action(FluentIcon.HOME_FILL,'开启黑屏(不带时间)', self)
        black_screen.triggered.connect(lambda: self.black_screen(True))
        
        # 添加退出操作
        quit_action = Action(FluentIcon.CLOSE,'退出', self)
        quit_action.triggered.connect(self.exit_app)
        
        menu.addAction(settings_action)
        menu.addAction(black_screen)
        menu.addAction(black_screen_action)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def setting_show(self):
        self.settings_window = MainWindow()
        self.settings_window.show()
    def black_screen(self,notime):
        self.black_screen_window = BlackScreen(notime)
        self.black_screen_window.showFullScreen()  # 使用全屏显示
        self.black_screen_window.show()
    def exit_app(self):
        # 停止监听器线程
        theme_manager.themeListener.terminate()
        theme_manager.themeListener.deleteLater()
        QApplication.quit()

    

        

#获取启动参数
"""arg = ''
def get_argument():
    global arg
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if i == 0:
                continue  # 忽略第一个参数，它通常是程序名
            if arg is None:
                arg = ''
            else:
                arg = arg[1:]
    else:
        pass
get_argument()"""


if __name__ == '__main__':
    # 适配高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    # 定义缺失的 CLSCTX 常量
    CLSCTX_INPROC_HANDLER = 0x2
    CLSCTX_INPROC_SERVER = 0x1
    CLSCTX_LOCAL_SERVER = 0x4
    CLSCTX_REMOTE_SERVER = 0x10
    CLSCTX_SERVER = CLSCTX_INPROC_SERVER | CLSCTX_LOCAL_SERVER | CLSCTX_REMOTE_SERVER
    CLSCTX_ALL = CLSCTX_INPROC_HANDLER | CLSCTX_SERVER
    app = QApplication(sys.argv)
    main = Initialization()
    sys.exit(app.exec_())
