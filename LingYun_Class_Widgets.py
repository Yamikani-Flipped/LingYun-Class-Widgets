# -*- coding: utf-8 -*-

# very small
import sys, os, logging, winreg as reg, webbrowser, warnings, json,threading,time,uuid,glob
from datetime import datetime,timedelta,date
import traceback
import shutil,zipfile,tempfile
import download_ly, LNC# ,install_ly
from WaveAnimation import WaveAnimation
from Version_ly import version
from lottery import FloatWindow,load_student_list,save_student_list
from Sortable import HorizontalSortWidget
from config_handler import ConfigHandler
from Desktop_shortcut_component import ShortcutManager
import xml.etree.ElementTree as ET
from functools import partial

# small (<1MB)
import requests,simpleaudio as sa,yaml
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# medium (<10MB)
import psutil # 1.5MB
from qfluentwidgets import (FluentWindow,FluentIcon,SubtitleLabel,Slider,Action,SystemTrayMenu,PushButton,
    SpinBox,NavigationItemPosition,InfoBarIcon,TeachingTip,BodyLabel,SwitchButton,TransparentPushButton,
    SystemThemeListener,isDarkTheme,CardWidget,TableWidget,setThemeColor,setTheme,SmoothScrollArea,TitleLabel,
    ProgressBar,StrongBodyLabel,MessageBox,Dialog,ListWidget,TextEdit,ComboBox,TimePicker,PrimaryPushButton,
    CalendarPicker,LineEdit,PasswordLineEdit,Flyout,FlyoutAnimationType,Theme,qconfig,RadioButton,HyperlinkButton,
    ElevatedCardWidget,SegmentedWidget,IndeterminateProgressBar,InfoBar,ZhDatePicker,PlainTextEdit)     


# big
from PyQt5 import uic
from PyQt5.QtCore import pyqtProperty,  QTimer, QPropertyAnimation, QEasingCurve, Qt, QObject, pyqtSignal, pyqtSlot, QRect, QPoint, QEvent, QDate, QTime, QRectF, QThread, QDateTime,QRunnable, QThreadPool, pyqtSignal, QObject, QSharedMemory
from PyQt5.QtGui import QFontDatabase, QFont, QColor,QFontMetrics,QIcon,QPainter,QPainterPath,QCloseEvent,QGuiApplication,QRegion,QBrush
from PyQt5.QtWidgets import QLabel, QWidget,QMainWindow, QScroller, QHBoxLayout, QButtonGroup, QSpacerItem,QFrame, QListWidgetItem, QMessageBox,QApplication,QFileDialog,QFontDialog,QSystemTrayIcon,QTableWidgetItem,QColorDialog,QStackedWidget,QVBoxLayout,QSizePolicy

import ast
from win10toast import ToastNotifier
#from pathlib import Path
from ctypes import byref, windll, c_ulong, c_bool, POINTER ,wintypes,create_unicode_buffer
import subprocess



warnings.filterwarnings("ignore", category=DeprecationWarning) # 忽略警告
Version = '1.6.15'
Version_Parse = version(Version)
# 1.6.6以上版本修改为配置文件存电脑文档文件夹中
#USER_RES = str(Path(__file__).resolve().parent.parent / "Resource").replace('\\', '/') + "/"
def getDocPath(pathID=5):
    '''path=5: My Documents'''
    buf= create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(None, pathID, None, 0, buf)
    return buf.value
USER_RES = getDocPath() + "/LingYun_Profile/"
UNIQUE_KEY = "lingyun.studio.lingyunclasswidgets.singleinstance"
RES = "Resource/"

# 获取当前完整路径,获取当前文件名（os.path.basename(sys.argv[0]获得的是exe名字）
script_dir = sys.argv[0].replace(os.path.basename(sys.argv[0]),"")
script_full_path = sys.argv[0]
os.chdir(script_dir)# 切换工作目录QPropertyAnimation

WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016
SE_SHUTDOWN_NAME = "SeShutdownPrivilege"
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x0002
PROCESS_QUERY_INFORMATION = 0x0400

# closeEvent

# 初始化程序整体
class Initialization(QObject):
    update_ui_signal = pyqtSignal(str, str, str)

    def __init__(self,parent=None):
        super(Initialization, self).__init__(parent)
    def init(self):
        global theme_manager,theme,clock,tops,warn,DP_Comonent,gl_weekday,cloud_sync,adj_weekday,toaster,update_channel,ncu,desk_short,Lottery
 
        # 检测是否完成云同步变量
        cloud_sync = False

        # 调课的星期
        adj_weekday = 0
        gl_weekday = str(datetime.now().weekday() + 1)

        # 更新频道
        update_channel = None
        ncu = {}
        self.in_update = False
        
        # 初始化数据
        self.get_datas()

        # 初始化日志记录器
        #if config.get("print_log") == "True":
        self.logger = self.save_logger(f"{USER_RES}log")

        if self.welcome() == False:
            welcome = Window()
            welcome.show()
            return

        #yun_warn = Yun_warn()
        #yun_warn.warn_update("Wait","云端获取数据中...")

        # 初始化主题管理器
        theme_manager = ThemeManager()
        theme_manager.toggleTheme(Theme.AUTO)
        theme = "dark" if isDarkTheme() else "light"

        # 云同步
        if config.get("yun_Switch") == "True":
            QTimer.singleShot(int(config.get('yun_time'))*1000,self.yun_data)

        # 创建桌面时钟
        clock = TransparentClock()
        #clock.resize(int(datas['width']), int(datas['height']))  # 设置窗口大小
        clock.move(int(config['x']), int(config['y']))  # 设置窗口位置

        # 显示时钟和桌面组件
        if config.get("cl_Switch") == "True":
            clock.show()
        else:
            lists['close_sets'] == True
            clock.hide()

        if os.path.exists(f"{RES}ui/dp/{config.get('dp_choose')}") == False:
            config['dp_choose'] = "class_dp0.ui"
            config['dp_display_edge'] = '510'
            self.write_to_registry("dp_choose","class_dp0.ui")
            self.write_to_registry("dp_display_edge","510")

        self.yun_check_verison(None) # 检查云端版本

        # 创建托盘图标
        tops = SystemTrayMenus()
        tops.create_tray_icon()
        # 创建桌面组件
        DP_Comonent = Desktop_Component()
        warn = class_warn()

        Lottery = FloatWindow()  # 创建抽签窗口

        if config.get("lot_Switch") == "True":
            Lottery.show()
            Lottery.activateWindow()
        if config.get("lot_pin") == "True":
            # 在原有Flag上添加Qt.WindowStaysOnTopHint
            Lottery.setWindowFlags(Lottery.windowFlags() | Qt.WindowStaysOnTopHint)
            
        

        # 创建快捷桌面组件
        desk_short = ShortcutManager()
        if config.get('dsc_Switch') == "True":
            desk_short.show()

        theme_manager.customSignal.connect(DP_Comonent.TOPIC)
    def get_datas(self):
        global lists,config,class_weekday,gl_weekday,class_dan,up_work,default_class,default_config,duty_again

        up_work = False


        # 默认课程表和时间
        default_class = [["07:20-08:00","07:20-07:50"],{"1":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"2":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"3":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"4":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"5":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"6":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"7":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}]},{"1":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"2":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"3":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"4":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"5":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"6":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"7":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}]},{"default":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"1":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"2":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"3":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"4":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"5":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"6":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"7":{"上午":["07:50-08:35","08:45-09:30","09:50-10:35","10:45-11:30"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]}},{"default":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"1":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"2":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"3":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"4":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"5":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"6":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"7":{"上午":["07:50-08:35","08:45-09:30","09:50-10:35","10:45-11:30"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]}},{"1":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"2":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"3":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"4":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"5":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"6":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"7":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]}}]
        class_weekday = "通用"
        class_dan = ""

        duty_again = {"mode":"again","date_begin":"20250520","duty":{"1":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]}}}
        
        #新数据格式  “dp”为桌面组件的数据，“set”为设置数据，clock为时钟数据
        default_config = {'dp_Switch': 'True', #是否开启桌面组件
                  'dp_Pin' : 'False', #是否置顶 True,False,Under
                  'dp_Typeface' : '', #字体
                  'dp_Bell' : 'True', #是否开启上下课提醒
                  'dp_Sysvolume' : 'True', #是否修改系统音量
                  'dp_Sysvolume_value' : '100', #要修改的系统音量
                  'dp_Curriculum_ramp' : 'True', #是否开启当前课程背景渐变
                  'dp_Countdown_ramp' : 'True', #是否开启倒计时背景渐变
                  'dp_drup_ramp' : 'True', #是否开启值日生背景渐变
                  'dp_Countdown_Bar_color_up' : '#00CD00', #倒计时进度条颜色 下课
                  'dp_Countdown_Bar_color_down' : '	#FF0000', # 上课
                  'dp_Countdown_Bar_color_next_down' : '#FF8C00', # 即将上课
                  'dp_Countdown_color_up' : "['#00CC00', 0, 169, 17, 171, 255, 155]", # 提醒下课的颜色
                  'dp_Countdown_color_down' : "['#f39c12', 255, 160, 0, 255, 245, 157]", #0:波纹rgb 1,2,3:渐变色左下角 4,5,6:渐变色右上角
                  'dp_Countdown_color_next_down' : "['#f86b4f', 248, 107, 79, 255, 250, 250]",
                  'dp_Countdown_color_ls' : "['#00CC00', 0, 169, 17, 171, 255, 155]", # 提醒放学的颜色
                  'dp_Preliminary' : "True", #是否开启预备铃声
                  'dp_Countdown_Bar_school_lag' : '0', #学校广播时差
                  'dp_Course_ramp' : 'True', #是否开启课程背景渐变
                  'dp_biweekly' : 'False', #是否开启双周切换
                  'dp_danweekly' : '2025,1,1', #单周起始时间
                  'dp_choose' : 'class_dp4.ui', # 选择桌面组件ui文件
                  'dp_duty' : 'True', #是否开启值日生组件
                  'dp_display_edge' : '480', #距离屏幕边缘的距离
                  'dp_duty_TimePicker_from' : '16:0', # 晚边开始时间
                  'dp_duty_TimePicker_to' : '19:0', # 晚边结束时间
                  'dp_drup_audio' : 'False', #是否播放提醒音频
                  'dp_audio_s' : "4", # 提醒的延迟秒数
                  'dp_xiping' : 'True', #是否息屏开启桌面组件
                  'dp_widgets' : "default.json", # 选择使用的json文件
                  'dp_Curriculum_ramp_action' : '0', # 双击当前课程的操作
                  'dp_countdown_action' : '0', # 双击倒计时的操作
                  'dp_todayclass_action' : '2', # 双击今日课程的操作
                  'dp_duty_action' : '1', # 双击值日生的操作 
                  'dp_display_count' : 'True', #是否显示全屏倒计时
                  'dp_count' : '10', # 下课倒计时时间
                  'dp_count_font' : '', # 倒计时字体


                  # 0.无操作，1.值日生编辑，2.课程表编辑，3.时间编辑


                  'comboBox': '桌面',
                  'x' : '700',
                  'y' : '100',
                  'width' : '200',
                  'height' : '100',
                  'fontSize' : '72',
                  'fontname' : '',
                  'update' : '700',
                  'Penetrate' : 'True',


                  'setting_title' : '', # 设置标题加内容


                  #'cl_Penetrate' : 'True', # 穿透
                  'cl_Switch' : 'True', #是否启用桌面时钟
                  'cl_UpdateTime' : '1000', # 更新间隔
                  'cl_Transparent' : '210', # 透明度

                  #'cl_time_Typeface' : '微软雅黑', # 字体
                  'cl_time_TextColor' : '[255,255,255]', # 文字颜色
                  'cl_time_Switch' : 'True', #是否显示时间
                  'cl_time_Second' : 'True', #是否显示秒钟

                  'cl_date_Switch' : 'True', #是否开启日期显示
                  'cl_date_Typeface' : '', #日期字体
                  'cl_date_TextSize' : '18', #日期文字大小
                  'cl_date_TextColor' : '[255,255,255]', #日期文字颜色
                  'cl_date_mediate' : 'True', #日期居中
                  'cl_date_language' : "en-us", #日期语言

                  'yun_Switch' : 'False', #是否开启云同步
                  'yun_equipment' : '', # 设备编号
                  'yun_password' : '', # 密码
                  'yun_https' : '', # 云同步地址
                  'yun_time' : '5', # 云同步延迟
                  'timeleg_Switch' : 'True', # 是否时差同步
                  'json_Switch' : 'True', #是否开启json数据存储

                  'check_update' : 'True', #是否检查更新
                  'print_log' : 'True', #是否记录日志
                  'check_net' : "True", #是否检测网络连接
                  'auto_update' : "True", #是否自动更新
                  'update_channel' : 'stable', # 更新渠道 stable:稳定版 beta:测试版
                  'update_ncu' : '0',

                  'dsc_Switch' : 'True', # 是否开启桌面组件
                  'dsc_x' : '0', # 桌面组件x位置
                  'dsc_y' : '0', # 桌面组件y位置
                  'dsc_width' : 'None', # 桌面组件宽度 None为自动
                  'dsc_lock' : 'False', # 是否锁定桌面组件位置
                  'dsc_put' : 'True', # 是否开启收起按钮
                  'dsc_Typeface' : '', # 桌面组件字体
                  'dsc_Typeface_size' : '15', # 桌面组件字体大小
                  'dsc_teacherfile_path' : 'None', # 教师文件夹路径 None为自动
                  'dsc_Color' : '#000000',
                  'dsc_tran' : '50', # 桌面组件透明度
                  'dsc_halo_switch' : 'True', # 光环开关
                  'dsc_length' : 'None', # 桌面组件长度 None为自动

                  'lot_Switch' : 'True', # 是否开启抽签
                  'lot_audio' : 'True', # 抽签声音
                  'lot_Pin' : 'True', # 抽签置顶



                  }
        
        if Version_Parse.pre != None:
            default_config["update_channel"] = "beta"

        config = {}
        for key in default_config:
            default_value = default_config[key]
            registry_value = self.read_from_registry(key, default_value)
            if registry_value is not None:
                config[key] = registry_value

        lists = {'close_sets' : False, # 设置是否关闭（主要处理关闭事件）
                 "widgets_on" : False, # 设置窗口的编辑时间线是否打开
                 "click_Counter" : False, # 设置时间线的屏蔽节数计数
                 }
        
        
        self.load_data()
        if "mode" in duty_table:
            config["duty_mode"] = "again"
        else:
            config["duty_mode"] = "weekday"

    def load_data(self,js=None):
        global class_all,class_ORD_Filtration, class_table, class_time, duty_table, class_dan,class_table_a,class_table_b,class_time_a,class_time_b,class_time_a,class_time_b

        # 从文件加载数据 json
        if js == None:
            class_all = self.loads_from_json(-1)
        else:
            class_all = js
        class_ORD_Filtration = class_all[0]
        class_table_a = class_all[1]
        class_table_b = class_all[2]
        class_time_a = class_all[3]
        class_time_b = class_all[4]
        duty_table = class_all[5]


        class_dan = ""
        if config.get("dp_biweekly") == "True":
            start_date = datetime.strptime(config.get('dp_danweekly'), "%Y,%m,%d")
            current_date = datetime.now()
            current_monday = current_date - timedelta(days=current_date.weekday())
            start_monday = start_date - timedelta(days=start_date.weekday())
            delta = current_monday - start_monday
            weeks_diff = delta.days // 7
            if weeks_diff % 2 == 0:
                class_table = class_table_a
                class_time = class_time_a
                class_dan = "单周"
            else:
                class_table = class_table_b
                class_time = class_time_b
                class_dan = "双周"
        else:
            class_table = class_table_a
            class_time = class_time_a

    def yun_data(self):
        url = config.get("yun_https") + "/default_config_class.json"
        self.fetch_json(url, self.yun_config_class_data)
        if config.get("timeleg_Switch") == "True":
            url = config.get("yun_https") + "/config_wys_time.json"
            self.fetch_json(url, self.yun_timeleg_data)
        if config.get('json_Switch') == "True":
            url = config.get("yun_https") + "/" +config.get("yun_equipment") + "/default.json"
            self.fetch_json(url, self.yun_json_data)
    
    
    # 发送通用网络请求
    '''
    def fetch_data(self, url, callback, flags=None, error_callback=None):
        def fetch():
            flag = False
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    flag = True                    
                    callback(response,200)  # 返回
                else:
                    if config.get("print_log") == "True":# and hasattr(Initialization, 'logger'):
                        self.logger.warning(f"网络请求失败，状态码: {response.status_code}")
            except Exception as e:
                if config.get("print_log") == "True":# and hasattr(Initialization, 'logger'):
                    self.logger.warning(f"网络请求失败 {str(e)}")
            if flag == False and error_callback != None:
                print("网络请求失败，状态码:",flags)
                error_callback(False,flags) # 返回错误


        # 创建并启动线程
        thread = threading.Thread(target=fetch)
        thread.start()
    # 发送json网络请求
    def fetch_json(self, url, callback, error_callback=None):
        #global yun_warn
        def fetch():
            #global yun_warn
            flag = False
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    callback(data)  # 返回
                    flag = True
                else:
                    if config.get("print_log") == "True":# and hasattr(Initialization, 'logger'):
                        self.logger.warning(f"网络请求失败，状态码: {response.status_code}")
                    #yun_warn.warn_update("Error",f"请求失败，状态码: {response.status_code}")
                    #yun_warn.edit()
            except Exception as e:

                if config.get("print_log") == "True":# and hasattr(Initialization, 'logger'):
                    self.logger.warning(f"网络请求失败 {str(e)}")
                #yun_warn.warn_update("Error",f"请求失败:{e}")
                #yun_warn.edit()
            if flag == False and error_callback != None:
                error_callback(False,url) # 返回错误

        # 创建并启动线程
        thread = threading.Thread(target=fetch)
        thread.start()
    
    '''

    def fetch_data(self, url, callback, flags=None, error_callback=None):
        task = FetchTask(url, callback)
        
        # 连接信号
        if error_callback:
            task.signals.error.connect(lambda msg: error_callback(False, flags))
        
        # 添加到线程池
        QThreadPool.globalInstance().start(task)
    
    def fetch_json(self, url, callback, error_callback=None):
        task = JsonFetchTask(url, callback, error_callback)
        QThreadPool.globalInstance().start(task)

    def yun_check_verison(self,data=None,flag=None,ty=None):
        global yun_version,yun_data_version,update_channel,ncu
        if self.in_update:
            return
        if flag == 200: # 成功
            # 云版本号
            data = data.json()
            j = json.dumps(data, indent=4, ensure_ascii=False)
            #if config.get("update_channel") == "beta":
            if Version_Parse.prerelease:  # 如果是测试版
                if ast.literal_eval(j)['beta_version'] == "None":
                    yun_version = version(ast.literal_eval(j)['version'])
                else:
                    yun_version = version(ast.literal_eval(j)['beta_version'])
            else:
                yun_version = version(ast.literal_eval(j)['version'])
            yun_data_version = ast.literal_eval(j)
            # 更新频道
            ncu = {
                "Github_1":f"https://bgithub.xyz/Yamikani-Flipped/LingYun-Class-Widgets/releases/download/v{yun_version.version_str}/LingYun_Class_Widgets_v{yun_version.version_str}_Install_x64.exe",
                "Github_2":f"https://github.moeyy.xyz/https://github.com/Yamikani-Flipped/LingYun-Class-Widgets/releases/download/v{yun_version.version_str}/LingYun_Class_Widgets_v{yun_version.version_str}_Install_x64.exe",
                "Gitee":f"https://gitee.com/yamikani/LingYun-Class-Widgets/releases/download/v{yun_version.version_str}/LingYun_Class_Widgets_v{yun_version.version_str}_Install_x64.exe",
                }
            update_channel = list(ncu.values())[int(config.get("update_ncu"))]
            tys = None

            if Version_Parse < yun_version:  # 有新版本
                # 自动更新 (待完善，链接需要灵活，设置可改)
                tys = "update"
                config["auto_update"] = "False" 
                if config.get("auto_update") == "True":
                    if config.get("check_update") == "True" and ty == None:
                        self.to_message('凌云班级组件正在更新中','下载完成后稍后会自动重启进行安装。')
                        save = tempfile.gettempdir() + "/LingYun/Temp.zip"
                        download_ly.download_file(update_channel,save,main.download_ok)
                else:
                    if config.get("check_update") == "True":
                        self.to_message('凌云班级组件有新版本啦！',f'目前已禁用自动更新。建议及时更新，以获取最佳体验，请前往设置->关于中查看!(新版本为{yun_version.full_version})')
            #elif Version_Parse >= yun_version:
            #    # print("当前版本与云端一致或更高")
            #    pass
            if "settings_window" in globals():
                self.update_ui_signal.emit(yun_version.full_version, "check_end", tys)
            return


        elif flag == None: # 第一次请求
            url = "https://raw.bgithub.xyz/Yamikani-Flipped/LingYun-Class-Widgets/main/config_public.json"
            self.fetch_data(url, self.yun_check_verison,1,self.yun_check_verison)
            return 
        elif flag == 1: # 第2次请求
            url = "https://lingyun-6e2.pages.dev/config_public.json"
            self.fetch_data(url, self.yun_check_verison,2,self.yun_check_verison)
            return        
        #elif flag == 2: # 第二次请求 失效
        #    url = "https://github.moeyy.xyz/https://github.com/Yamikani-Flipped/LingYun-Class-Widgets/blob/main/config_public.json"
        #    self.fetch_data(url, self.yun_check_verison,2,self.yun_check_verison)
        #    return
        elif flag == 2: # 第3次请求
            url = "https://gitee.com/yamikani/LingYun-Class-Widgets/raw/main/config_public.json"
            self.fetch_data(url, self.yun_check_verison,3,self.yun_check_verison)
            return
        
        elif flag == 3: # 连续3次失败，通知失败
            if config.get("check_net") == "True": # 通知
                print("网络连接失败，无法获取云端版本信息！")
                self.to_message("网络连接失败，请检查网络！","如果要禁用此通知，请前往“设置>软件设置”进行修改。如果网络已连接，请检查是否打开了VPN，防火墙是否拦截。")
            if "settings_window" in globals():
                settings_window.check_update("获取失败","check_end")


    def to_message(self,title,msg):
        # 创建通知器对象
        if "toaster" not in globals():
            toaster = ToastNotifier()

        # 显示通知
        toaster.show_toast(title, msg,duration=2,threaded=True,icon_path=f"{RES}ico/LINGYUN.ico")

        #toast_ly.send_windows_notification(title, msg, f"{RES}ico/LINGYUN.ico", 2)
        #if "toast" not in globals():
        #    global toast
        #    toast = WindowsBalloonTip()
        #toast.show_notification(title, msg, f"{RES}ico/LINGYUN.ico", 2)

    def download_ok(self,path,error):
        if path:
            self.logger.info(f"自动更新下载新版本成功: {path}")
            self.in_update = False
            temp = tempfile.gettempdir()
            save = temp + "/LingYun/"
            subprocess.Popen([os.path.join(save, "temp.exe")] + ["/passive"])
            tops.exitSignal.emit()

        else:
            self.logger.warning(f"自动更新下载新版本时出现错误: {error}")

            
    def zip_update(self):
        temp = tempfile.gettempdir()
        zips = temp + "/LingYun/Temp.zip"
        save = temp + "/LingYun/"
        with zipfile.ZipFile(zips, 'r') as zip_ref:
            members = zip_ref.namelist()
            root_folder = None
            if members and members[0].endswith('/'):
                root_folder = members[0]
            for member in members:
                if member == root_folder:
                    continue
                if root_folder and member.startswith(root_folder):
                    target_name = member[len(root_folder):]
                else:
                    target_name = member 
                target_path = os.path.join(save, target_name)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                if not target_name.endswith('/'):
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
        # 即将启动temp里的exe，1：安装路径，2：旧版本号
        subprocess.Popen([os.path.join(save, "LingYun_Class_Widgets.exe")] + ["/update",script_dir,Version])
        tops.exitSignal.emit()

    def yun_json_data(self,data,flag=None):
        global DP_Comonent, warn#,yun_warn
        # 云同步json数据
        j = json.dumps(data, indent=4, ensure_ascii=False)
        js = ast.literal_eval(j)
        directory = f'{USER_RES}jsons'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, config.get("dp_widgets"))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)
        self.load_data(js)
        
        # 刷新UI数据
        DP_Comonent.refresh_all_data()
        
        if "settings_window" in globals():
            settings_window.start_yun("ok")


    def yun_config_class_data(self,data,flag=None):
        j = json.dumps(data, indent=4, ensure_ascii=False)
        js = ast.literal_eval(j)
        if config.get("yun_equipment") in js.get("False"):
            return
        if config.get("yun_equipment") in js.get("True"):
            url = config.get("yun_https") + "/" + config.get("yun_equipment") + "/default_config.json"
            self.fetch_json(url, self.yun_config_data)
        else:
            url = config.get("yun_https") + "/default_config.json"
            self.fetch_json(url, self.yun_config_data)

    def yun_config_data(self,data,flag=None):
        # 云同步配置数据
        global clock
        j = json.dumps(data, indent=4, ensure_ascii=False)
        js = ast.literal_eval(j)
        for key in js:
            config[key] = js[key]
            self.write_to_registry(key, js[key])
            # 更新配置(暂时不实时，没必要，也会有问题)
            #clock.update_settings(key) # 更新时钟设置
        
        
    def yun_timeleg_data(self,data,flag=None):
        # 云时间表时差
        j = json.dumps(data, indent=4, ensure_ascii=False)
        yun_timeleg = ast.literal_eval(j)['time']
        config["dp_Countdown_Bar_school_lag"] = yun_timeleg
        self.write_to_registry("dp_Countdown_Bar_school_lag", yun_timeleg)

    def convert_widget(self,cho=-1,weekday=None): # cho为选择模式，-1为全部，1为获取今日课表信息，2为获取当前课表信息
        global today_widget,current_widget,course_widget,time_widget,guo_widget,adj_weekday,current_widgets
        try:
            if weekday == None:
                if adj_weekday == 0:
                    day = datetime.now().isoweekday()
                else:
                    day = adj_weekday
            else:
                day = int(weekday)

            
            ############################
            ct = class_time[str(day)]
            ############################

            # 定义
            today_widgets = []  
            current_widgets = None
            course_widgets = {}
            time_widgets = {}
            guo_widgets = ""

            # 1.获取适合读取的今日课表:today_widget 
            if cho == -1 or cho == 1 or cho == 2 or cho == 4 or cho == 5: # 有2是因为2依赖1
                day_schedule = class_table.get(str(day), [])
                for period in day_schedule:
                    for time_of_day, classes in period.items(): #classes为那个午段课程名称列表
                        times = ct.get(time_of_day, [])
                        s = 1
                        for i, (time, cls) in enumerate(zip(times, classes), start=1):
                            if cls != "":
                                if time in class_ORD_Filtration:
                                    today_widgets.append([-1, time, time_of_day, cls])
                                else:
                                    today_widgets.append([s, time, time_of_day, cls])
                                    s += 1
            
            # 2.获得当前所在的时间段和当前课程current_widget
            if cho == -1 or cho == 2:
                lag = int(config.get("dp_Countdown_Bar_school_lag")) # 从配置中获取时差
                # 获取当前时间并补全日期信息（这里我们简单地使用今天的日期）
                current_datetime = datetime.combine(datetime.today().date(), datetime.now().time())
                adjusted_datetime = current_datetime # 初始化调整后的时间
                if lag < 0:
                    adjusted_datetime = current_datetime + timedelta(seconds=-lag)
                adjusted_time = adjusted_datetime.time() # （可选）提取时间部分
                
                for item in today_widgets:
                    start_time, end_time = item[1].split('-')
                    start_time = datetime.strptime(start_time, "%H:%M").time()
                    end_time = datetime.strptime(end_time, "%H:%M").time()
                    
                    # 注意：这里使用调整后的时间进行比较
                    if start_time <= adjusted_time <= end_time:
                        current_widgets = item
                        break
                else:
                    current_widgets = None # 当前没在任何时间段内，也就是下课

            # 3.获取适合读取的课程数量:course_widget
            if cho == -1 or cho == 3 or cho == 4:
                day_schedule = class_table.get(str(day), [])
                for period in day_schedule: # period为一个字典，用于记录每个午段课程数
                    j = list(period.keys())[0]
                    course_widgets[j] = 0
                    for time_of_day, classes in period.items():
                        times = ct.get(time_of_day, [])
                        for cls in classes:
                            if cls != "":
                                course_widgets[time_of_day] += 1
            
            # 4.获取处理每个午别的起始时间和结束时间time_widget
            if cho == -1 or cho == 4:
                # 初始化结果字典
                time_widgets = {key: None for key in course_widgets.keys()}
                course_count = {key: 0 for key in course_widgets.keys()}
                # 存储时间段的字典
                time_slots = {key: [] for key in course_widgets.keys()}
                # 遍历today_widget，记录时间段并计数
                for entry in today_widgets:
                    period = entry[2]
                    start_end = entry[1].split('-')
                    time_slots[period].append((start_end[0], start_end[1]))
                    course_count[period] += 1
                # 处理每个午别的起始时间和结束时间
                for period, times in time_slots.items():
                    if times:
                        start_times = [datetime.strptime(time[0], '%H:%M') for time in times]
                        end_times = [datetime.strptime(time[1], '%H:%M') for time in times]
                        start_time = min(start_times).strftime('%H:%M')
                        end_time = max(end_times).strftime('%H:%M')
                        time_widgets[period] = f'{start_time}-{end_time}'
                    else:
                        time_widgets[period] = None
            
            # 5.获取过渡时间guo_widget
            if cho == -1 or cho == 5:
                def time_to_minutes(time_str):
                    """将时间字符串转换为分钟数"""
                    t = datetime.strptime(time_str, '%H:%M')
                    return t.hour * 60 + t.minute
                
                #now = datetime.now()
                lag = int(config.get("dp_Countdown_Bar_school_lag")) # 从配置中获取时差
                # 获取当前时间并补全日期信息（这里我们简单地使用今天的日期）
                current_datetime = datetime.combine(datetime.today().date(), datetime.now().time())
                adjusted_datetime = current_datetime # 初始化调整后的时间
                if lag < 0:
                    adjusted_datetime = current_datetime + timedelta(seconds=-lag)
                now = adjusted_datetime#.time() # （可选）提取时间部分


                current_time_minutes = now.hour * 60 + now.minute

                for i in range(1, len(today_widgets)):
                    start_time_prev = time_to_minutes(today_widgets[i-1][1].split('-')[1])
                    start_time_curr = time_to_minutes(today_widgets[i][1].split('-')[0])
                    period_prev = today_widgets[i-1][2]
                    period_curr = today_widgets[i][2]

                    # 如果午别不同，返回None
                    if period_prev != period_curr:
                        guo_widgets = None
                        continue

                    # 检查当前时间是否在过渡时间段内
                    if start_time_prev <= current_time_minutes < start_time_curr:
                        guo_widgets = today_widgets[i-1][1].split('-')[1] + '-' + today_widgets[i][1].split('-')[0]
                        break
                if guo_widgets == "":
                    guo_widgets = None

            #print("课程是：",today_widget)
            #print("当前课程是：",current_widget)
            #print("课程数量是：",course_widget)
            #print("课程时间是：",time_widget)
            #print("过渡时间是：",guo_widget)
            #print("===============================")
            if weekday == None:
                today_widget = today_widgets
                current_widget = current_widgets
                course_widget = course_widgets
                time_widget = time_widgets
                guo_widget = guo_widgets
            else:
                return today_widgets, current_widgets, course_widgets, time_widgets, guo_widgets
        except Exception as e: #使用错误的课表，需要恢复默认值
            #QWaitCondition.wait(self.lock, 1000)
            w = Dialog("错误", f"你可能使用了错误的课表文件，导致初始化失败！请先删除“{config['dp_widgets']}”，然后重新打开本程序。敬请谅解！", None)
            w.cancelButton.hide()
            w.yesButton.setText("好")
            theme_manager.themeListener.terminate()
            theme_manager.themeListener.deleteLater()
            if w.exec():QTimer.singleShot(100, lambda: QApplication.quit())
            return "close"

    def white_Widgets(self):
        # 保存课程表和时间到文件
        global class_dan,class_time,class_ORD_Filtration,class_table,class_table_a,class_table_b,class_time_a,class_time_b,duty_table
        try:
            if class_dan == "双周":
                class_time_b = class_time
                class_table_b = class_table
                self.saves_to_json()

            else:
                class_time_a = class_time
                class_table_a = class_table
                self.saves_to_json()

            # DP_Comonent.update_Widgets(0)
            return None
        except Exception as e:
            return e

    def loads_from_json(self, index):
        global default_class
        directory = f'{USER_RES}jsons'

        file_path = os.path.join(directory, config.get("dp_widgets"))
        if os.path.exists(file_path): # 如果文件存在，则读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                if index == -1:
                    return json.load(f)
                else:
                    return json.load(f)[index]
        else: # 如果文件不存在，则返回默认数据并保存默认数据到文件
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, config.get("dp_widgets"))
            #config["dp_widgets"] = default_config.get("dp_widgets")
            #self.write_to_registry("dp_widgets", default_config.get("dp_widgets"))
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_class, f, ensure_ascii=False, indent=4)
            if index == -1:
                return default_class
            else:
                return default_class[index]

    def saves_to_json(self):
        global class_ORD_Filtration, class_table_a, class_table_b, class_time_a, class_time_b, duty_table
        class_all = [class_ORD_Filtration, class_table_a, class_table_b, class_time_a, class_time_b, duty_table]

        directory = f'{USER_RES}jsons'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, config.get("dp_widgets"))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(class_all, f, ensure_ascii=False, indent=4)

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
    # 是否首次使用
    def welcome(self):
        value_name = 'welcome'
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes', 0, reg.KEY_QUERY_VALUE) as key:
                value, regtype = reg.QueryValueEx(key, value_name)
                if value == 'True':
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False
        except Exception as e:
            # 捕获其他异常
            QMessageBox.critical(self, '错误', f'读取注册表失败：{e}')
            # 返回None
            return False

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        # 获取完整的堆栈跟踪信息
        traceback_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # 记录详细错误信息到日志
        main.logger.error("Uncaught exception:\n" + traceback_details)
        
        # 关闭相关资源
        theme_manager.themeListener.terminate()
        theme_manager.themeListener.deleteLater()
        
        # 构建包含行号信息的错误消息
        error_msg = (
            f"错误的详细信息为下，目前无法继续运行，请反馈给开发者。敬请谅解！\n\n"
            f"错误类型: {exc_type.__name__}\n"
            f"错误信息: {str(exc_value)}\n\n"
            "错误日志保存在此电脑用户“文档”中LingYun_Profile下的log文件夹中。"
        )
        
        # 使用现有Dialog类创建对话框
        w = Dialog("运行出现错误", error_msg, None)
        w.yesButton.setText("好")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        
        # 显示对话框
        if w.exec():
            pass
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

    # 日志
    def save_logger(self,log_dir, log_level=logging.INFO):

        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = f"LingYun_{datetime.now().strftime('%Y%m%d')}.log"
        # 日志文件的完整路径
        log_path = os.path.join(log_dir, log_filename)

        # 创建日志记录器
        logger = logging.getLogger("LingYun_Logger")
        logger.setLevel(log_level)

        # 创建文件处理器，将日志写入文件
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(log_level)

        # 创建日志格式
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # 将处理器添加到记录器
        logger.addHandler(file_handler)

        return logger

class FetchSignals(QObject):
    finished = pyqtSignal(object, int)
    error = pyqtSignal(str)

class FetchTask(QRunnable):
    def __init__(self, url, callback=None):
        super().__init__()
        self.url = url
        self.callback = callback
        self.signals = FetchSignals()
    
    def run(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                if self.callback:
                    self.callback(response, 200)
                self.signals.finished.emit(response, 200)
            else:
                error_msg = f"网络请求失败，状态码: {response.status_code}"
                self.signals.error.emit(error_msg)
        except Exception as e:
            error_msg = f"网络请求失败 {str(e)}"
            self.signals.error.emit(error_msg)

class JsonFetchTask(QRunnable):
    def __init__(self, url, callback=None, error_callback=None):
        super().__init__()
        self.url = url
        self.callback = callback
        self.error_callback = error_callback
        self.signals = FetchSignals()
    
    def run(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                if self.callback:
                    self.callback(data)
                self.signals.finished.emit(data, 200)
            else:
                error_msg = f"JSON请求失败，状态码: {response.status_code}"
                self.signals.error.emit(error_msg)
                if self.error_callback:
                    self.error_callback(False, self.url)
        except Exception as e:
            error_msg = f"JSON请求失败 {str(e)}"
            self.signals.error.emit(error_msg)
            if self.error_callback:
                self.error_callback(False, self.url)

# 时钟类
class TransparentClock(QMainWindow):
    def __init__(self):
        global week_day_dict,config
        super().__init__()

        self.timer = uic.loadUi(f'{RES}ui/timerr.ui',self)

        # 设置窗口属性
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.allow_shutdown = False
        
        # 窗口置顶
        if config['comboBox'] == "置顶":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # 鼠标穿透
        if config['Penetrate'] == 'True':
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
 
        
        
        self.time_label = self.timer.findChild(QLabel, 'time_label')
        self.date_label = self.timer.findChild(QLabel, 'date_label')

        # 设置字体 大小 加粗 颜色 透明度
        time_font = self.font_file(f"{RES}MiSans-Bold.ttf",config["fontname"],config["fontSize"])
        date_font = self.font_file(f"{RES}MiSans-Bold.ttf",config.get('cl_date_Typeface'), config.get('cl_date_TextSize'))
        
        #time_font.setStyleHint(QFont.Monospace)
        #time_font.setFixedPitch(True)
        
        self.time_label.setFont(time_font)
        self.date_label.setFont(date_font)

        time_rgba = ast.literal_eval(config.get("cl_time_TextColor"))
        self.time_label.setStyleSheet(f'color: rgba({time_rgba[0]},{time_rgba[1]},{time_rgba[2]},{int(config.get("cl_Transparent"))});')
        date_rgba = ast.literal_eval(config.get("cl_date_TextColor"))
        self.date_label.setStyleSheet(f'color: rgba({date_rgba[0]},{date_rgba[1]},{date_rgba[2]},{int(config.get("cl_Transparent"))});')

        # 显示日期
        if config.get('cl_date_Switch') == "True":
            self.date_label.show()
        else:
            self.date_label.hide()

        self.animations()



        # 将星期转换为中文
        week_day_dict = {
            "Monday": "一",
            "Tuesday": "二",
            "Wednesday": "三",
            "Thursday": "四",
            "Friday": "五",
            "Saturday": "六",
            "Sunday": "日"
        }
        # 更新时钟
        self.update_time()

        self.animation_show.start()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(int(config.get('cl_UpdateTime')))

        # 保持日期居中
        self.resize(QFontMetrics(self.time_label.font()).horizontalAdvance(self.time_label.text()), self.height())
        self.mediate_date = QTimer(self)
        self.mediate_date.timeout.connect(self.date_mediate)
        self.mediate_date.start(60000)
    
    def font_file(self,file,font_name,font_size):
        # 加载字体文件datas
        if font_name == "":
            font_id = QFontDatabase.addApplicationFont(file)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font = QFont(font_families[0], int(font_size),  QFont.Bold)
                else:
                    font = QFont(font_name, int(font_size),  QFont.Bold)
            else:
                font = QFont(font_name, int(font_size),  QFont.Bold)
        else:
            font = QFont(font_name, int(font_size),  QFont.Bold)
        return font

    def update_time(self):
        global gl_weekday
        if gl_weekday != str(datetime.now().weekday() + 1):
            restart_program()
        now = datetime.now()
        formatted_date = self.api_formatted_date()        
        self.time_label.setText(now.strftime('%H:%M:%S' if config.get("cl_time_Second") == "True" else '%H:%M'))
        self.date_label.setText(formatted_date)

    def date_mediate(self):
        # 保持日期居中
        if config.get("cl_date_mediate") == "True" and config.get('cl_time_Switch') == "True":
            self.resize(QFontMetrics(self.time_label.font()).horizontalAdvance(self.time_label.text()), self.height())


    def api_formatted_date(self) -> str:
        now = datetime.now()
        if config.get("cl_date_language") == "zh-cn":
            # 格式化日期
            m = now.strftime('%m').lstrip('0')
            d = now.strftime('%d').lstrip('0')
            formatted_date = now.strftime(f"{m}月{d}日 星期{now.strftime('%A')}")
            # 替换英文星期为中文星期
            for eng, ch in week_day_dict.items():
                formatted_date = formatted_date.replace(eng, ch)
        elif config.get("cl_date_language") == "en-us":
            formatted_date = now.strftime('%B %d %A')
        return formatted_date


    def update_settings(self,choose):
        #实时更新
        if choose == "fontSize" or choose == "fontname": 
            font = self.font_file(f"{RES}MiSans-Bold.ttf",config['fontname'],config['fontSize'])
            self.time_label.setFont(font)
        elif choose == "cl_UpdateTime":
            self.timer.stop()
            self.timer.start(int(config.get('cl_UpdateTime')))
        elif choose == "x" or choose == "y":
            #clock.resize(int(da tas['width']), int(da tas['height']))  
            clock.move(int(config['x']), int(config['y']))  
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


        if choose == "cl_Switch":
            if config.get('cl_Switch') == "True":
                self.show()
                self.animation_show.start()
            else:
                self.animation_hide.start()
                hide_timer = QTimer(self)
                hide_timer.singleShot(500, self.hide)

                #self.hide()

        if choose == "cl_time_TextColor" or choose == "cl_Transparent":
            rgba = ast.literal_eval(config.get("cl_time_TextColor"))
            self.time_label.setStyleSheet(f'color: rgba({rgba[0]},{rgba[1]},{rgba[2]},{int(config.get("cl_Transparent"))});')
            #self.date_label.setStyleSheet(f'color: rgba(255,255,255,{int(config.get("cl_Transparent"))/100});')
        
        if choose == "cl_date_TextColor" or choose == "cl_Transparent":
            rgba = ast.literal_eval(config.get("cl_date_TextColor"))
            self.date_label.setStyleSheet(f'color: rgba({rgba[0]},{rgba[1]},{rgba[2]},{int(config.get("cl_Transparent"))});')
        elif choose == "cl_date_Switch":
            if config.get('cl_date_Switch') == "True":
                self.date_label.show()
            else:
                self.date_label.hide()
        elif choose == 'cl_date_TextSize' or choose == 'cl_date_Typeface':
            date_font = self.font_file(f"{RES}MiSans-Bold.ttf",config.get('cl_date_Typeface'),config.get('cl_date_TextSize'))
            self.date_label.setFont(date_font)
        elif choose == "cl_time_Switch":
            if config.get('cl_time_Switch') == "True":
                self.time_label.show()
            else:
                self.time_label.hide()
            self.timer.stop()
            self.update_time()
            self.timer.start(int(config.get('cl_UpdateTime')))
        elif choose == "cl_time_Second":
            self.update_time()

    def animations(self):
        # 从隐藏淡入：animation_show
        self.animation_show = QPropertyAnimation(self, b'windowOpacity')
        self.animation_show.setDuration(550)
        self.animation_show.setStartValue(0)
        self.animation_show.setEndValue(1)
        self.animation_show.setEasingCurve(QEasingCurve.OutQuad)

        # 从显示淡出：animation_hide
        self.animation_hide = QPropertyAnimation(self, b'windowOpacity')
        self.animation_hide.setDuration(550)
        self.animation_hide.setStartValue(1)
        self.animation_hide.setEndValue(0)
        self.animation_hide.setEasingCurve(QEasingCurve.InQuad)

    """def closeEvent(self, event):
        event.ignore()"""




# 设置窗口
class MainWindow(FluentWindow):
    def __init__(self):
        global display_x,display_y

        super().__init__()
        self.close_event_args = None

        self.addexe = AddNewExeDialog()    

        self.addui()
        self.initNavigation()
        self.initWindow()
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry() 
        display_x = screen_geometry.width() 
        display_y = screen_geometry.height()

        self.CH = ly_ConfigHandler()



        main.update_ui_signal.connect(self.update_ui_with_check_result)

        
        #获取系统主题色
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(self.getSystemAccentColor(), save=False)
    def getSystemAccentColor(self):
        DwmGetColorizationColor = windll.dwmapi.DwmGetColorizationColor
        DwmGetColorizationColor.restype = c_ulong
        DwmGetColorizationColor.argtypes = [POINTER(c_ulong), POINTER(c_bool)]
        color = c_ulong()
        code = DwmGetColorizationColor(byref(color), byref(c_bool()))
        if code != 0: # Unable to obtain system accent color
            return QColor()
        return QColor(color.value)
    
    def initNavigation(self):
        #self.addSubInterface(self.main, FluentIcon.HOME, '欢迎')
        self.addSubInterface(self.home, FluentIcon.HISTORY, '时钟设置')
        self.addSubInterface(self.dp_class, FluentIcon.TILES, '桌面组件设置')
        self.addSubInterface(self.classes, FluentIcon.CALENDAR, '编辑课表')
        self.addSubInterface(self.classes_time, FluentIcon.BOOK_SHELF, '时间线编辑')
        self.addSubInterface(self.duty, FluentIcon.CALENDAR, '值日表配置')
        self.addSubInterface(self.display, FluentIcon.DEVELOPER_TOOLS, '息屏显示配置')
        self.addSubInterface(self.adjustment, FluentIcon.SETTING, '调课管理')
        self.addSubInterface(self.dsc, FluentIcon.FOLDER, '桌面快捷组件设置')
        self.addSubInterface(self.lottery, FluentIcon.SPEED_OFF, '随机抽签设置')
        
        
        #self.navigationInterface.addSeparator()
        #self.addSubInterface(self.hh, FluentIcon.SETTING, '高级设置')
        
        self.addSubInterface(self.yun, FluentIcon.CLOUD, '集中控制'     ,NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.soft, FluentIcon.SETTING, '软件设置'  ,NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.updates, FluentIcon.UPDATE, '更新日志',NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.info, FluentIcon.INFO, '关于与更新'   ,NavigationItemPosition.BOTTOM)
        

        self.stackedWidget.currentChanged.connect(lambda index: self.stacked(index))
    def addui(self):
        try:
            self.home = uic.loadUi(f'{RES}ui/set_home.ui')
            self.home.setObjectName("home")
            self.updates = uic.loadUi(f'{RES}ui/set_updates.ui')
            self.updates.setObjectName("updates")
            self.info = uic.loadUi(f'{RES}ui/set_info.ui')
            self.info.setObjectName("info")
            self.classes = uic.loadUi(f'{RES}ui/set_classes.ui')
            self.classes.setObjectName("classes")
            self.classes_time = uic.loadUi(f'{RES}ui/set_classes_time.ui')
            self.classes_time.setObjectName("classes_time")
            self.dp_class = uic.loadUi(f'{RES}ui/set_dp_class.ui')
            self.dp_class.setObjectName("dp_class")
            self.soft = uic.loadUi(f'{RES}ui/set_soft.ui')
            self.soft.setObjectName("soft")
            self.display = uic.loadUi(f'{RES}ui/set_display.ui')
            self.display.setObjectName("display")
            self.duty = uic.loadUi(f'{RES}ui/set_duty.ui')
            self.duty.setObjectName("duty")
            self.yun = uic.loadUi(f'{RES}ui/set_yun.ui')
            self.yun.setObjectName("yun")
            self.adjustment = uic.loadUi(f'{RES}ui/set_adjustment.ui')
            self.adjustment.setObjectName("adjustment")
            self.dsc = uic.loadUi(f'{RES}ui/set_dsc.ui')
            self.dsc.setObjectName("dsc")
            self.lottery = uic.loadUi(f'{RES}ui/set_lottery.ui')
            self.lottery.setObjectName("lottery")

        except Exception as e:
            self.error("导入UI文件出现错误，详细的错误内容为\n" + str(e),"导入错误",True)

        # 触摸屏滑动适配
        scroll = self.home.findChild(SmoothScrollArea, 'sd_scroll')
        #scroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)  
        #SmoothScroll().setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll = self.updates.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.info.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.classes_time.findChild(SmoothScrollArea, 'sm')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.dp_class.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.soft.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.duty.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.yun.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.display.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.adjustment.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.dsc.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)
        scroll = self.lottery.findChild(SmoothScrollArea, 'sd_scroll')
        QScroller.grabGesture(scroll.viewport(), QScroller.LeftMouseButtonGesture)

        #self.myButton = self.home.findChild(SwitchButton, 'CW2_onof_button')
        #print(self.myButton)
        #self.myButton.setChecked(True)# 设置按钮状态为选中
        #print(self.myButton.isChecked())# 打印按钮状态

        self.set_home()
        self.set_info()
        self.set_dp_class()
        self.set_classes()
        self.set_classes_time()
        self.set_duty()
        self.set_yun()
        self.set_updates()
        self.set_soft()
        self.set_display()
        self.set_Adjustment()
        self.set_dsc()
        self.set_lottery()

        #self.stackedWidget.currentChanged.connect(lambda: print(self.stackedWidget.currentWidget()))

    def switchTo(self, interface: QWidget) -> None:
        self.stackedWidget.setCurrentWidget(interface, popOut=False)

    def set_updates(self):
        self.cs = self.updates.findChild(PushButton, 'cs')
        self.cs.hide()
        #self.cs.clicked.connect(lambda :self.Flyout())
    def set_home(self):
        #字体大小
        self.CW1_spinBox = self.home.findChild(SpinBox, 'CW1_spinBox')
        self.CW1_spinBox.setValue(int(config["fontSize"]))
        self.CW1_spinBox.setSingleStep(5)
        self.CW1_spinBox.setRange(0, 2000)
        self.CW1_spinBox.valueChanged.connect(lambda value: self.update_time(value,'fontSize'))

        #时间x坐标
        self.CW2_Slider = self.home.findChild(Slider, 'CW2_Slider')
        self.CW2_Slider.setMaximum(display_x)
        self.CW2_Slider.setValue(int(config["x"]))
        self.CW2_Slider.valueChanged.connect(lambda value: self.update_time(value,'x'))

        #时间y坐标
        self.CW3_Slider = self.home.findChild(Slider, 'CW3_Slider')
        self.CW3_Slider.setMaximum(display_y)
        self.CW3_Slider.setValue(int(config["y"]))
        self.CW3_Slider.valueChanged.connect(lambda value: self.update_time(value,'y'))

        #置顶
        self.CW4_onof_button = self.home.findChild(SwitchButton, 'CW4_onof_button')
        if config["comboBox"] == "置顶":
            self.CW4_onof_button.setChecked(True)
        else:
            self.CW4_onof_button.setChecked(False)
        self.CW4_onof_button.checkedChanged.connect(lambda value: self.update_time(value,'comboBox'))

        #选择时间颜色
        self.CW5_color_button = self.home.findChild(PushButton, 'CW5_color_button')
        self.CW5_color_button.clicked.connect(lambda:self.choose_color("time"))

        #选择日期颜色
        self.cl_date_TextColor_button = self.home.findChild(PushButton, 'cl_date_TextColor_button')
        self.cl_date_TextColor_button.clicked.connect(lambda:self.choose_color("date"))


        #选择字体
        self.CW6_font_button = self.home.findChild(PushButton, 'CW6_font_button')
        self.CW6_font_button.clicked.connect(lambda:self.choose_font("time"))

        #鼠标穿透
        self.CW7_onof_button = self.home.findChild(SwitchButton, 'CW7_onof_button')
        if config["Penetrate"] == "False":
            self.CW7_onof_button.setChecked(False)
        else:
            self.CW7_onof_button.setChecked(True)
        self.CW7_onof_button.checkedChanged.connect(lambda value: self.update_time(value,'Penetrate'))

        #开机启动按钮
        self.CW8_onof_button = self.soft.findChild(SwitchButton, 'CW8_onof_button')
        if self.read_startup_program():
            self.CW8_onof_button.setChecked(True)
        else:
            self.CW8_onof_button.setChecked(False)
        self.CW8_onof_button.checkedChanged.connect(lambda value: self.update_time(value,'startup'))

        #启用桌面时钟
        self.cl_Switch_button = self.home.findChild(SwitchButton, 'cl_Switch_button')
        if config.get("cl_Switch") == "False":
            self.cl_Switch_button.setChecked(False)
        else:
            self.cl_Switch_button.setChecked(True)
        self.cl_Switch_button.checkedChanged.connect(lambda value: self.update_time(value,'cl_Switch'))

        # 透明度
        self.cl_Transparent_Slider = self.home.findChild(Slider, 'cl_Transparent_Slider')
        self.cl_Transparent_Slider.setMaximum(255)
        self.cl_Transparent_Slider.setMinimum(40)
        self.cl_Transparent_Slider.setValue(int(config.get("cl_Transparent")))
        self.cl_Transparent_Slider.valueChanged.connect(lambda value: self.update_time(value,'cl_Transparent'))

        # 显示日期
        self.cl_date_Switch_button = self.home.findChild(SwitchButton, 'cl_date_Switch_button')
        if config.get("cl_date_Switch") == "False":
            self.cl_date_Switch_button.setChecked(False)
        else:
            self.cl_date_Switch_button.setChecked(True)
        self.cl_date_Switch_button.checkedChanged.connect(lambda value: self.update_time(value,'cl_date_Switch'))

        # 日期实时居中
        self.cl_date_mediate_button = self.home.findChild(SwitchButton, 'cl_date_mediate_button')
        if config.get("cl_date_mediate") == "False":
            self.cl_date_mediate_button.setChecked(False)
        else:
            self.cl_date_mediate_button.setChecked(True)
        self.cl_date_mediate_button.checkedChanged.connect(lambda value: self.update_time(value,'cl_date_mediate'))

        # 日期字体大小
        self.cl_date_TextSize_spinBox = self.home.findChild(SpinBox, 'cl_date_TextSize_spinBox')
        self.cl_date_TextSize_spinBox.setValue(int(config.get("cl_date_TextSize")))
        self.cl_date_TextSize_spinBox.setSingleStep(2)
        self.cl_date_TextSize_spinBox.setRange(0, 1000)
        self.cl_date_TextSize_spinBox.valueChanged.connect(lambda value: self.update_time(value,'cl_date_TextSize'))

        # 日期字体
        self.cl_date_Typeface_button = self.home.findChild(PushButton, 'cl_date_Typeface_button')
        self.cl_date_Typeface_button.clicked.connect(lambda:self.choose_font("date"))

        # 日期语言
        cl_date_language_ComboBox = self.home.findChild(ComboBox, 'cl_date_language_ComboBox')
        cl_date_language_ComboBox.addItems(["简体中文","English"])
        cl_date_language_ComboBox.setPlaceholderText("选择语言")# 设置提示文本
        cl_date_language_ComboBox.setCurrentIndex(-1)# 取消选中
        cl_date_language_ComboBox.currentIndexChanged.connect(lambda value: self.update_time(value,'cl_date_language'))


        # 显示时间
        self.cl_time_Switch_button = self.home.findChild(SwitchButton, 'cl_time_Switch_button')
        if config.get("cl_time_Switch") == "False":
            self.cl_time_Switch_button.setChecked(False)
        else:
            self.cl_time_Switch_button.setChecked(True)
        self.cl_time_Switch_button.checkedChanged.connect(lambda value: self.update_time(value,'cl_time_Switch'))

        # 时间秒钟
        self.cl_time_Second_button = self.home.findChild(SwitchButton, 'cl_time_Second_button')
        if config.get("cl_time_Second") == "False":
            self.cl_time_Second_button.setChecked(False)
        else:
            self.cl_time_Second_button.setChecked(True)
        self.cl_time_Second_button.checkedChanged.connect(lambda value: self.update_time(value,'cl_time_Second'))

        # 还原默认字体（日期）
        self.default_date_font_PushButton = self.home.findChild(PushButton, 'default_date_font_PushButton')
        self.default_date_font_PushButton.clicked.connect(lambda:self.update_time("","cl_date_Typeface"))

        # 还原默认字体（时间）
        self.default_time_font_PushButton = self.home.findChild(PushButton, 'default_time_font_PushButton')
        self.default_time_font_PushButton.clicked.connect(lambda:self.update_time("","fontname"))
    def set_dp_class(self):
        #------设置桌面组件页面的控件--------
        self.dp_Switch_button = self.dp_class.findChild(SwitchButton, 'dp_Switch_button')
        if config.get('dp_Switch') == "True":
            self.dp_Switch_button.setChecked(True)
        else:
            self.dp_Switch_button.setChecked(False)
        self.dp_Switch_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Switch'))
        
        self.dp_Pin_box = self.dp_class.findChild(ComboBox, 'dp_Pin_box')
        self.dp_Pin_box.addItems(["置顶","正常","置于底层(会禁用收起)"])# True,False,Under
        if config.get('dp_Pin') == "True":
            self.dp_Pin_box.setCurrentIndex(0)
        elif config.get('dp_Pin') == "False":
            self.dp_Pin_box.setCurrentIndex(1)
        elif config.get('dp_Pin') == "Under":
            self.dp_Pin_box.setCurrentIndex(2)
        self.dp_Pin_box.currentIndexChanged.connect(lambda value: self.update_dp(value,'dp_Pin'))

        self.dp_Typeface_button = self.dp_class.findChild(PushButton, 'dp_Typeface_button')
        self.dp_Typeface_button.clicked.connect(self.choose_font_dp)

        self.CardWidget_8 = self.dp_class.findChild(CardWidget, 'CardWidget_8')
        self.CardWidget_11 = self.dp_class.findChild(CardWidget, 'CardWidget_11')

        self.dp_Bell_button = self.dp_class.findChild(SwitchButton, 'dp_Bell_button')
        if config.get('dp_Bell') == "True":
            self.dp_Bell_button.setChecked(True)
            self.CardWidget_8.show()
        else:
            self.dp_Bell_button.setChecked(False)
            self.CardWidget_8.hide()
        self.dp_Bell_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Bell'))

        self.dp_Sysvolume_button = self.dp_class.findChild(SwitchButton, 'dp_Sysvolume_button')
        if config.get('dp_Sysvolume') == "True":
            self.dp_Sysvolume_button.setChecked(True)
            self.CardWidget_11.show()
        else:
            self.dp_Sysvolume_button.setChecked(False)
            self.CardWidget_11.hide()
        self.dp_Sysvolume_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Sysvolume'))
        
        self.dp_Sysvolume_slider = self.dp_class.findChild(Slider, 'dp_Sysvolume_slider')
        self.dp_Sysvolume_slider.setValue(int(config.get('dp_Sysvolume_value')))
        self.dp_Sysvolume_slider.valueChanged.connect(lambda value: self.update_dp(value,'dp_Sysvolume_value'))

        self.dp_Curriculum_ramp_button = self.dp_class.findChild(SwitchButton, 'dp_Curriculum_ramp_button')
        if config.get('dp_Curriculum_ramp') == "True":
            self.dp_Curriculum_ramp_button.setChecked(True)
        else:
            self.dp_Curriculum_ramp_button.setChecked(False)
        self.dp_Curriculum_ramp_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Curriculum_ramp'))

        self.dp_Countdown_ramp_button = self.dp_class.findChild(SwitchButton, 'dp_Countdown_ramp_button')
        if config.get('dp_Countdown_ramp') == "True":
            self.dp_Countdown_ramp_button.setChecked(True)
        else:
            self.dp_Countdown_ramp_button.setChecked(False)
        self.dp_Countdown_ramp_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Countdown_ramp'))

        self.dp_Countdown_Bar_color_next_down_button = self.dp_class.findChild(PushButton, 'dp_Countdown_Bar_color_next_down_button')
        self.dp_Countdown_Bar_color_next_down_button.clicked.connect(lambda: self.choose_color_dp("next_down"))
        self.dp_Countdown_Bar_color_down_button = self.dp_class.findChild(PushButton, 'dp_Countdown_Bar_color_down_button')
        self.dp_Countdown_Bar_color_down_button.clicked.connect(lambda: self.choose_color_dp("down"))
        self.dp_Countdown_Bar_color_up_button = self.dp_class.findChild(PushButton, 'dp_Countdown_Bar_color_up_button')
        self.dp_Countdown_Bar_color_up_button.clicked.connect(lambda: self.choose_color_dp("up"))

        self.dp_Countdown_Bar_school_lag_SpinBox = self.dp_class.findChild(SpinBox, 'dp_Countdown_Bar_school_lag_SpinBox')
        self.dp_Countdown_Bar_school_lag_SpinBox.setValue(int(config.get('dp_Countdown_Bar_school_lag')))
        self.dp_Countdown_Bar_school_lag_SpinBox.valueChanged.connect(lambda value: self.update_dp(value,'dp_Countdown_Bar_school_lag'))

        self.dp_Course_ramp_button = self.dp_class.findChild(SwitchButton, 'dp_Course_ramp_button')
        if config.get('dp_Course_ramp') == "True":
            self.dp_Course_ramp_button.setChecked(True)
        else:
            self.dp_Course_ramp_button.setChecked(False)
        self.dp_Course_ramp_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Course_ramp'))

        self.default_dp_font_PushButton = self.dp_class.findChild(PushButton, 'default_dp_font_PushButton')
        self.default_dp_font_PushButton.clicked.connect(lambda:self.update_dp("",'dp_Typeface'))

        self.dp_biweekly_button = self.dp_class.findChild(SwitchButton, 'dp_biweekly_button')
        if config.get('dp_biweekly') == "True":
            self.dp_biweekly_button.setChecked(True)
        else:
            self.dp_biweekly_button.setChecked(False)
        self.dp_biweekly_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_biweekly'))

        self.dp_danweekly_CalendarPicker = self.dp_class.findChild(CalendarPicker, 'dp_danweekly_CalendarPicker')
        date = config.get('dp_danweekly').split(',')
        self.dp_danweekly_CalendarPicker.setDate(QDate(int(date[0]), int(date[1]), int(date[2])))
        # 日期发生改变
        self.dp_danweekly_CalendarPicker.dateChanged.connect(lambda date: self.update_dp(date,'dp_danweekly'))

        self.dan_StrongBodyLabel = self.dp_class.findChild(StrongBodyLabel, 'dan_StrongBodyLabel')
        self.dan_StrongBodyLabel.setText(f"目前是{class_dan}")
        if config.get("dp_biweekly") == "False":
            self.dan_StrongBodyLabel.hide()

        global warn
        self.dan_PushButton = self.dp_class.findChild(PushButton, 'dan_PushButton')
        self.dan_PushButton.clicked.connect(lambda: warn.ui("down"))
        self.dan_PushButton.hide()

        self.dp_Preliminary_button = self.dp_class.findChild(SwitchButton,"dp_Preliminary_button")
        if config.get("dp_Preliminary") == "True":
            self.dp_Preliminary_button.setChecked(True)
        else:
            self.dp_Preliminary_button.setChecked(False)
        self.dp_Preliminary_button.checkedChanged.connect(lambda value:self.update_dp(value,"dp_Preliminary"))

        self.dp_drup_ramp_button = self.dp_class.findChild(SwitchButton, 'dp_drup_ramp_button')
        if config.get('dp_drup_ramp') == "True":
            self.dp_drup_ramp_button.setChecked(True)
        else:
            self.dp_drup_ramp_button.setChecked(False)
        self.dp_drup_ramp_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_drup_ramp'))

        self.choose_box = self.dp_class.findChild(ComboBox, 'dp_choose_box')
        entries = os.listdir(f'{RES}ui/dp/')
        self.files = [entry for entry in entries if os.path.isfile(os.path.join(f'{RES}ui/dp/', entry))]
        
        self.choose_box.addItems(self.files)
        try:
            self.choose_box.setCurrentIndex(self.files.index(config.get("dp_choose")))
        except:
            self.error("配置文件中的dp_choose参数有误，请重新选择","警告",False,True)
        self.choose_box.currentIndexChanged.connect(self.choose_box_changed)    

        self.dp_duty_button = self.dp_class.findChild(SwitchButton, 'dp_duty_button')

        if config.get('dp_duty') == "True":
            self.dp_duty_button.setChecked(True)
        else:
            self.dp_duty_button.setChecked(False)
        self.dp_duty_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_duty'))

        self.dp_display_edge_SpinBox = self.dp_class.findChild(SpinBox, 'dp_display_edge_SpinBox')
        self.dp_display_edge_SpinBox.setValue(int(config.get('dp_display_edge')))
        self.dp_display_edge_SpinBox.valueChanged.connect(lambda value: self.update_dp(value,'dp_display_edge'))

        self.dp_drup_audio_button = self.dp_class.findChild(SwitchButton, 'dp_drup_audio_button')
        if config.get('dp_drup_audio') == "True":
            self.dp_drup_audio_button.setChecked(True)
        else:
            self.dp_drup_audio_button.setChecked(False)
        self.dp_drup_audio_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_drup_audio'))

        self.TimePicker_from = self.dp_class.findChild(TimePicker, 'TimePicker_from')
        self.TimePicker_to = self.dp_class.findChild(TimePicker, 'TimePicker_to')
        
        self.TimePicker_from.setTime(QTime(int(config.get("dp_duty_TimePicker_from").split(':')[0]), int(config.get("dp_duty_TimePicker_from").split(':')[1])))
        self.TimePicker_to.setTime(QTime(int(config.get("dp_duty_TimePicker_to").split(':')[0]), int(config.get("dp_duty_TimePicker_to").split(':')[1])))

        self.TimePicker_from.timeChanged.connect(lambda time: self.update_dp(time,'dp_duty_TimePicker_from'))
        self.TimePicker_to.timeChanged.connect(lambda time: self.update_dp(time,'dp_duty_TimePicker_to'))

        self.dp_audio_s_SpinBox = self.dp_class.findChild(SpinBox, 'dp_audio_s_SpinBox')
        self.dp_audio_s_SpinBox.setValue(int(config.get('dp_audio_s')))
        self.dp_audio_s_SpinBox.valueChanged.connect(lambda value: self.update_dp(value,'dp_audio_s'))

        self.dp_chowidgets_box = self.dp_class.findChild(ComboBox, 'dp_chowidgets_box')
        self.update_file()
        try:
            self.dp_chowidgets_box.setCurrentIndex(self.json_widgets.index(config.get("dp_widgets").split('.')[0]))
        except:
            self.error("配置文件中的dp_widgets参数有误，请重新选择","警告",False,True)
        self.dp_chowidgets_box.currentIndexChanged.connect(lambda value:self.update_dp(value,'dp_widgets'))
        #self.dp_chowidgets_box.currentIndexChanged.connect(lambda value:self.inex('dp_widgets'))

        # 导入导出
        self.dp_import_button = self.dp_class.findChild(PushButton, 'dp_import_button')
        self.dp_import_button.clicked.connect(lambda:self.inex("import"))
        self.dp_export_button = self.dp_class.findChild(PushButton, 'dp_export_button')
        self.dp_export_button.clicked.connect(lambda:self.inex("export"))
        self.dp_imescs_button = self.dp_class.findChild(PushButton, 'dp_imescs_button')
        self.dp_imescs_button.clicked.connect(lambda:self.inex("imescs"))
        self.dp_exescs_button = self.dp_class.findChild(PushButton, 'dp_exescs_button')
        self.dp_exescs_button.clicked.connect(lambda:self.inex("exescs"))
        self.dp_openwidgets_button = self.dp_class.findChild(PushButton, 'dp_openwidgets_button')
        self.dp_openwidgets_button.clicked.connect(lambda:self.inex("openwidgets"))

        self.lingyun_radio = self.dp_class.findChild(RadioButton, 'lingyun_Radio')
        self.cw_radio = self.dp_class.findChild(RadioButton, 'cw_Radio')
        self.lcw_layout = self.dp_class.findChild(QHBoxLayout, 'horizontalLayout')
        self.lcw_Group = QButtonGroup(self.lcw_layout)
        self.lcw_Group.addButton(self.lingyun_radio)
        self.lcw_Group.addButton(self.cw_radio)

        # 桌面组件双击操作
        self.Curriculum_ramp_ComboBox = self.dp_class.findChild(ComboBox, 'Curriculum_ramp_ComboBox')
        self.countdown_ComboBox = self.dp_class.findChild(ComboBox, 'countdown_ComboBox')
        self.todayclass_ComboBox = self.dp_class.findChild(ComboBox, 'todayclass_ComboBox')
        self.duty_ComboBox = self.dp_class.findChild(ComboBox, 'duty_ComboBox')
        self.action = ["无操作","打开值日表编辑","打开课表编辑","打开时间线编辑"]
        self.Curriculum_ramp_ComboBox.addItems(self.action)
        self.countdown_ComboBox.addItems(self.action)
        self.todayclass_ComboBox.addItems(self.action)
        self.duty_ComboBox.addItems(self.action)
        self.Curriculum_ramp_ComboBox.setCurrentIndex(int(config.get("dp_Curriculum_ramp_action")))
        self.countdown_ComboBox.setCurrentIndex(int(config.get("dp_countdown_action")))
        self.todayclass_ComboBox.setCurrentIndex(int(config.get("dp_todayclass_action")))
        self.duty_ComboBox.setCurrentIndex(int(config.get("dp_duty_action")))
        self.Curriculum_ramp_ComboBox.currentIndexChanged.connect(lambda value: self.update_dp(value,'dp_Curriculum_ramp_action'))
        self.countdown_ComboBox.currentIndexChanged.connect(lambda value: self.update_dp(value,'dp_countdown_action'))
        self.todayclass_ComboBox.currentIndexChanged.connect(lambda value: self.update_dp(value,'dp_todayclass_action'))
        self.duty_ComboBox.currentIndexChanged.connect(lambda value: self.update_dp(value,'dp_duty_action'))
    def set_soft(self):
        #------设置软件页面的控件--------
        self.update_button = self.soft.findChild(SwitchButton, 'update_button')
        self.info_button = self.soft.findChild(SwitchButton, 'info_button')
        self.check_net_button = self.soft.findChild(SwitchButton, 'check_net_button')
        self.set_openwidgets_button = self.soft.findChild(PushButton, 'set_openwidgets_button')


        self.set_openwidgets_button.clicked.connect(lambda:self.inex("open_Profile"))


        if config.get("check_update") == "True":
            self.update_button.setChecked(True)
        else:
            self.update_button.setChecked(False)
        self.update_button.checkedChanged.connect(lambda value: self.update_dp(value,'check_update'))

        if config.get("print_log") == "True":
            self.info_button.setChecked(True)
        else:
            self.info_button.setChecked(False)
        self.info_button.checkedChanged.connect(lambda value: self.update_dp(value,'print_log'))

        if config.get("check_net") == "True":
            self.check_net_button.setChecked(True)
        else:
            self.check_net_button.setChecked(False)
        self.check_net_button.checkedChanged.connect(lambda value: self.update_dp(value,'check_net'))

    def set_info(self):
        #------设置关于页面的控件--------
        global Version, yun_version
        if "yun_version" not in globals():
            yun_version = "获取失败"
            vs = yun_version
        else:
            vs = yun_version.full_version
        self.version = self.info.findChild(BodyLabel, 'version')
        self.version.setText(f'当前版本：{Version}')
        self.yun_version = self.info.findChild(BodyLabel, 'yun_version')
        self.yun_version.setText(f'最新版本：{vs}')

        self.Join_qq = HyperlinkButton(
            url='https://qm.qq.com/q/KN7UVWFr6C',
            text='加入QQ群',
            parent=self,
            icon=FluentIcon.LINK)
        
        self.qq_clipboard_button = TransparentPushButton(text="复制QQ群号",parent=self.info,icon=FluentIcon.COPY)
        self.qq_clipboard_button.clicked.connect(self.qq_clipboard)

        self.Layout_http = self.info.findChild(QHBoxLayout, 'horizontalLayout_10')
        self.spacerItem1 = QSpacerItem(40, 20)
        self.spacerItem2 = QSpacerItem(40, 20)

        self.bilibili_button = HyperlinkButton(
            url='https://space.bilibili.com/627622081',
            text='Bilibili',
            parent=self,
            icon=FluentIcon.LINK)
        #self.bilibili_button.setMaximumWidth(100)

        self.github_button = HyperlinkButton(
            url='https://github.com/Yamikani-Flipped/LingYun-Class-Widgets',
            text='Github',
            parent=self,
            icon=FluentIcon.LINK)
        #self.github_button.setMaximumWidth(100)

        self.thank_button = TransparentPushButton(text="致谢",parent=self.info,icon=FluentIcon.MEGAPHONE)
        self.thank_button.clicked.connect(lambda:self.error(e="致谢的第三方app及网站。以下为引用列表：\nClass Widgets：1.沿用了部分的ui文件（大部分已做整改）\n2.上下课、即将上课提醒的音频文件的使用\n3.作品中上下课提醒中“波澜”的部分代码的使用。\n\n软件部分图片来自Icons8网站。\n\n同时感谢所有的使用者和智教联盟网站的支持和指导！\n\n相关链接：\n智教联盟：https://forum.smart-teach.cn/\nClass Widgets仓库：https://github.com/Class-Widgets/Class-Widgets\nicons8：https://icons8.com/",msg="致谢",grades=False,vas=True))

        
        self.Layout_http.addItem(self.spacerItem1)
        self.Layout_http.addWidget(self.Join_qq)
        self.Layout_http.addWidget(self.qq_clipboard_button)
        self.Layout_http.addWidget(self.bilibili_button)
        self.Layout_http.addWidget(self.github_button)
        self.Layout_http.addWidget(self.thank_button)
        self.Layout_http.addItem(self.spacerItem2)

        # 自动更新
        self.autoupdate_button = self.info.findChild(SwitchButton, 'autoupdate_button')
        config["auto_update"] = "False"
        if config.get("auto_update") == "True":
            self.autoupdate_button.setChecked(True)
        else:
            self.autoupdate_button.setChecked(False)
        self.autoupdate_button.checkedChanged.connect(lambda value: self.update_dp(value,'auto_update'))

        # 更新频道
        self.update_channel_ComboBox = self.info.findChild(ComboBox, 'update_channel_ComboBox')
        self.warning_SubtitleLabel = self.info.findChild(StrongBodyLabel, 'warning_SubtitleLabel')
        self.warning_SubtitleLabel.hide()

        s = "正式版" if Version_Parse.is_prerelease == False else "测试版(beta)"
        self.update_channel_ComboBox.addItem(s)
        #upc = []
        #if yun_version == "获取失败":
        #    s = "正式版" if config.get("update_channel") == "beta" else "测试版(beta)"
        #    upc = [f"{s}(请先检查更新)"]
        #    self.update_channel_ComboBox.addItems(upc)
        #else:
        #    upc = ["正式版"]
        #    if yun_data_version["beta_version"] != "None":
        #        upc.append("测试版(Beta)")
        #    else:
        #        if config.get("update_channel") == "beta":
        #            upc.append("测试版(Beta)(目前没有测试版本)")
        #            self.warning_SubtitleLabel.setText("警告：目前官方没有测试版本，建议及时退出测试版以转回正式版，在测试版中可能存在未知的问题。")
        #            self.warning_SubtitleLabel.show()
        #
        #
        #    self.update_channel_ComboBox.addItems(upc)
        #    if config.get("update_channel") == "beta":
        #        self.update_channel_ComboBox.setCurrentIndex(1)
        #    elif config.get("update_channel") == "stable":
        #        self.update_channel_ComboBox.setCurrentIndex(0)
        self.update_channel_callback = lambda value: self.update_dp(value, 'update_channel_w')    



        # 检查更新
        self.horizontalLayout_update = self.info.findChild(QHBoxLayout, 'horizontalLayout_update')
        self.update_check = PrimaryPushButton(text="检查更新",parent=self.info,icon=FluentIcon.SYNC)
        self.update_check.setMaximumWidth(150)
        self.horizontalLayout_update.addWidget(self.update_check)



        # 下载进度
        self.down_ElevatedCardWidget = self.info.findChild(ElevatedCardWidget, 'down_ElevatedCardWidget')
        self.down_ElevatedCardWidget.hide()

        self.info_Label = self.info.findChild(StrongBodyLabel, 'info_Label')
        self.percent_Label = self.info.findChild(StrongBodyLabel, 'percent_Label')
        self.down_ProgressBar = self.info.findChild(ProgressBar, 'down_ProgressBar')
        self.down_im_ProgressBar = self.info.findChild(IndeterminateProgressBar, 'down_im_ProgressBar')
        self.down_ProgressBar.hide()


        # 更新源
        self.updatesource_ComboBox = self.info.findChild(ComboBox, 'updatesource_ComboBox')
        if len(ncu) == 0:
            self.updatesource_ComboBox.addItems(["请先检查更新"])
        else:
            self.updatesource_ComboBox.addItems(ncu.keys())
            self.updatesource_ComboBox.setCurrentIndex(int(config.get("update_ncu")))
        self.updatesource_callback = lambda value: self.update_dp(value, 'update_ncu')  


        def current_connect():
            self.update_check.clicked.connect(self.check_update)
            #self.update_channel_ComboBox.currentIndexChanged.connect(self.update_channel_callback)            
            self.updatesource_ComboBox.currentIndexChanged.connect(self.updatesource_callback)
        QTimer.singleShot(500, current_connect)  # 延时1秒执行，确保界面加载完成

    def set_classes(self):
        #------设置课表页面的控件--------
        self.TableWidget = self.classes.findChild(TableWidget, 'TableWidget')
        # 启用边框并设置圆角
        self.TableWidget.setBorderVisible(True)
        self.TableWidget.setBorderRadius(10)
        self.set_table_update()
        # 按钮
        self.Table_Button = self.classes.findChild(PushButton, 'Table_Button')
        self.Table_Button.clicked.connect(self.on_resize)
        self.Table_Time = QTimer()
        self.Table_Time.timeout.connect(self.on_resize)
        self.Table_Time.start(1500)

        self.SD_ComboBox = self.classes.findChild(ComboBox, 'SD_ComboBox')
        self.SD_ComboBox.addItems(["单周课表","双周课表"])
        self.SD_ComboBox.currentIndexChanged.connect(self.SD_changed)

        self.copy_Button = self.classes.findChild(PushButton, 'copy_Button')
        self.copy_Button.hide()

        self.up_Button = self.classes.findChild(PushButton, 'up_Button')
        self.up_Button.clicked.connect(self.set_table_update)
        #self.up_Button.hide()
    def set_classes_time(self):
        #------设置时间线页面的控件--------
        self.TimeWidget = self.classes_time.findChild(ListWidget, 'ListWidget_time')
        self.name_edit = self.classes_time.findChild(TextEdit, 'name_edit')
        self.name_label = self.classes_time.findChild(BodyLabel, 'name_label')
        self.name_box = self.classes_time.findChild(ComboBox, 'name_box')
        self.add_button = self.classes_time.findChild(PushButton, 'add_Button')
        self.TimePicker_from = self.classes_time.findChild(TimePicker, 'TimePicker_from')
        self.TimePicker_to = self.classes_time.findChild(TimePicker, 'TimePicker_to')
        self.addtime_Button = self.classes_time.findChild(PrimaryPushButton, 'addtime_Button')
        self.add_name_box = self.classes_time.findChild(ComboBox, 'add_name_box')
        self.cancel_Button = self.classes_time.findChild(PushButton, 'cancel_Button')
        self.del_Button = self.classes_time.findChild(PushButton, 'del_Button')
        self.edit_label = self.classes_time.findChild(SubtitleLabel, 'edit_Label')
        self.CardWidget4 = self.classes_time.findChild(CardWidget, 'CardWidget4')
        self.ct_CardWidget2 = self.classes_time.findChild(CardWidget, 'CardWidget2')
        self.edit_Button = self.classes_time.findChild(PushButton, 'edit_Button')
        self.TimePicker_from_edit = self.classes_time.findChild(TimePicker, 'TimePicker_from_edit')
        self.TimePicker_to_edit = self.classes_time.findChild(TimePicker, 'TimePicker_to_edit')
        self.Counter_SwitchButton = self.classes_time.findChild(SwitchButton, 'Counter_SwitchButton')
        self.week_ComboBox = self.classes_time.findChild(ComboBox, 'week_ComboBox')
        self.auto_update_Button = self.classes_time.findChild(SwitchButton, 'auto_update_Button')



        self.Time_Widget_update()
        self.TimeWidget.itemClicked.connect(self.click_TimeWidget)        
        self.name_edit.setPlaceholderText("请输入")
        self.name_edit.hide()
        self.name_label.hide()
        self.name_box.addItems(["上午","下午","晚上","自定义"])
        self.name_box.currentIndexChanged.connect(self.name_box_changed)
        self.add_button.clicked.connect(self.add_aptime)
        self.from_time = ""
        self.to_time = ""
        self.add_name = "上午"
        self.TimePicker_from.timeChanged.connect(lambda t: setattr(self, 'from_time', t.toString()))
        self.TimePicker_to.timeChanged.connect(lambda t: setattr(self, 'to_time', t.toString()))
        self.addtime_Button.clicked.connect(self.add_time)
        self.add_name_box.addItems(self.ap_list)
        self.add_name_box.currentIndexChanged.connect(lambda: setattr(self, 'add_name', self.add_name_box.currentText()))
        self.cancel_Button.clicked.connect(self.cancel_Widget)
        self.del_Button.clicked.connect(self.del_Widget)
        self.edit_label.hide()
        self.CardWidget4.hide()
        self.TimeWidget.itemSelectionChanged.connect(self.update_widgets_visibility)

        self.edit_Button.clicked.connect(self.edit_time)
        self.from_time_edit = ""
        self.to_time_edit = ""

        self.Counter_SwitchButton.checkedChanged.connect(lambda value: self.click_Counter_Button(value))
        self.Counter_SwitchButton.setDisabled(True)

        self.week_ComboBox.addItems(['通用','周一','周二','周三','周四','周五','周六','周日'])
        self.week_ComboBox.currentIndexChanged.connect(self.week_changed)
        self.auto_update_Button.setChecked(True)


    def set_duty(self):
        #------设置值日表页面的控件--------
        global duty_table
        self.duty_Widget = self.duty.findChild(ListWidget, 'duty_Widget')
        self.week_box = self.duty.findChild(ComboBox, 'week_box')
        self.name_Edit = self.duty.findChild(LineEdit, 'name_Edit')
        self.project_Edit = self.duty.findChild(LineEdit, 'project_Edit')
        self.Add_Button = self.duty.findChild(PushButton, 'Add_Button')
        self.Del_Button = self.duty.findChild(PushButton, 'Del_Button')
        self.name_Button = self.duty.findChild(PushButton, 'name_Button')
        self.project_Button = self.duty.findChild(PushButton, 'project_Button')

        self.duty_SegmentedWidget = self.duty.findChild(SegmentedWidget, 'duty_SegmentedWidget')
        self.duty_stackedWidget = self.duty.findChild(QStackedWidget, 'duty_stackedWidget')

        # 轮回法
        self.again_ZhDatePicker = self.duty.findChild(ZhDatePicker, 'again_ZhDatePicker')
        self.again_box = self.duty.findChild(ComboBox, 'again_box')
        self.again_new_PrimaryPushButton = self.duty.findChild(PrimaryPushButton, 'again_new_PrimaryPushButton')
        self.again_project_Edit = self.duty.findChild(LineEdit, 'again_project_Edit')
        self.again_project_Button = self.duty.findChild(PushButton, 'again_project_Button')
        self.again_name_Edit = self.duty.findChild(LineEdit, 'again_name_Edit')
        self.again_name_Button = self.duty.findChild(PushButton, 'again_name_Button')
        self.again_Add_Button = self.duty.findChild(PushButton, 'again_Add_Button')
        self.again_Del_Button = self.duty.findChild(PushButton, 'again_Del_Button')

        self.dutyw_CardWidget = self.duty.findChild(CardWidget, 'dutyw_CardWidget')
        self.dutyw2_CardWidget = self.duty.findChild(CardWidget, 'dutyw2_CardWidget')
        self.initializew_button = self.duty.findChild(PushButton, 'initializew_button')
        self.initializew2_button = self.duty.findChild(PushButton, 'initializew2_button')

        self.warning_verticalLayout = self.duty.findChild(QHBoxLayout, 'warning_verticalLayout')
        self.warning_InfoBar = InfoBar.warning(
                title='警告',
                content="星期法或轮回法不能同时存在，在有数据时建议先导出。",
                orient=Qt.Horizontal,
                isClosable=True,
               # position=InfoBarPosition.TOP_RIGHT,
                duration=50000,
                parent=self.duty
        )
        self.warning_verticalLayout.addWidget(self.warning_InfoBar)

        self.duty_SegmentedWidget.clear()
        self.duty_SegmentedWidget.addItem(routeKey="weekday", text="星期法", onClick=lambda: self.duty_stackedWidget.setCurrentIndex(0))
        self.duty_SegmentedWidget.addItem(routeKey="again", text="轮回法", onClick=lambda:self.duty_stackedWidget.setCurrentIndex(1))
        if config.get("duty_mode") == "weekday":
            self.duty_stackedWidget.setCurrentIndex(0)
            self.duty_SegmentedWidget.setCurrentItem("weekday")
            self.dutyw_CardWidget.hide()
            
        elif config.get("duty_mode") == "again":
            self.duty_stackedWidget.setCurrentIndex(1)
            self.duty_SegmentedWidget.setCurrentItem("again")
            self.dutyw2_CardWidget.hide()

        self.initializew_button.clicked.connect(lambda: self.update_duty('initializew')) # 切换到星期法
        self.initializew2_button.clicked.connect(lambda: self.update_duty('initializew2')) # 切换到轮回法

        
        # 选择星期
        self.week = datetime.now().weekday()
        self.week_box.addItems(['周一','周二','周三','周四','周五','周六','周日'])
        self.week_box.setCurrentIndex(datetime.now().weekday())        
        self.week_box.currentIndexChanged.connect(self.duty_week_changed)

        QTimer.singleShot(100, self.yc)  # 延时执行，确保界面加载完成    

    def yc(self):
            self.duty_Widget.clear()
            self.name_Button.clicked.connect(partial(self.update_duty,'name'))
            self.project_Button.clicked.connect(partial(self.update_duty,'project'))
            self.Add_Button.clicked.connect(partial(self.update_duty,'add_item'))
            self.Del_Button.clicked.connect(partial(self.update_duty,'del_item'))
            if config.get("duty_mode") == "again":
                date = duty_table.get("date_begin")
                self.again_ZhDatePicker.setDate(QDate(int(date[:4]), int(date[4:6]), int(date[6:])))
                self.again_ZhDatePicker.dateChanged.connect(lambda date: self.update_duty('again_ZhDatePicker'))
                self.again_box.addItems(list((duty_table.get("duty")).keys()))
                group_key, duty_groups = self.duty_again_group()
                QTimer.singleShot(100, partial(self.duty_week_changed,int(group_key)-1))
                self.again_box.setCurrentIndex(int(group_key) - 1)
                self.duty_Widget.itemSelectionChanged.connect(partial(self.update_duty,"again_duty_widget"))                
                # 禁用星期法组件
                self.name_Button.setDisabled(True)
                self.project_Button.setDisabled(True)
                self.Add_Button.setDisabled(True)
                self.Del_Button.setDisabled(True)
                self.week_box.setDisabled(True)
                self.name_Edit.setDisabled(True)
                self.project_Edit.setDisabled(True)


            elif config.get("duty_mode") == "weekday":
                self.duty_Widget.itemSelectionChanged.connect(partial(self.update_duty,"duty_widget"))
                QTimer.singleShot(100, partial(self.duty_week_changed,datetime.now().weekday()))
                # 禁用轮回法组件
                self.again_ZhDatePicker.setDisabled(True)
                self.again_box.setDisabled(True)
                self.again_new_PrimaryPushButton.setDisabled(True)
                self.again_project_Edit.setDisabled(True)
                self.again_project_Button.setDisabled(True)
                self.again_name_Edit.setDisabled(True)
                self.again_name_Button.setDisabled(True)
                self.again_Add_Button.setDisabled(True)
                self.again_Del_Button.setDisabled(True)
            self.again_box.currentIndexChanged.connect(self.duty_week_changed) 
            self.again_new_PrimaryPushButton.clicked.connect(partial(self.update_duty, 'again_new'))
            self.again_project_Button.clicked.connect(partial(self.update_duty, 'again_project'))    
            self.again_name_Button.clicked.connect(partial(self.update_duty, 'again_name'))
            self.again_Add_Button.clicked.connect(partial(self.update_duty, 'again_add_item'))
            self.again_Del_Button.clicked.connect(partial(self.update_duty, 'again_del_item'))

    def set_display(self):
        self.dp_xiping_button = self.display.findChild(SwitchButton, 'dp_xiping_button')
        if config.get('dp_xiping') == "True":
            self.dp_xiping_button.setChecked(True)
        else:
            self.dp_xiping_button.setChecked(False)
        self.dp_xiping_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_xiping'))

        self.dp_display_count_button = self.display.findChild(SwitchButton, 'dp_display_count_button')
        if config.get('dp_display_count') == "True":
            self.dp_display_count_button.setChecked(True)
        else:
            self.dp_display_count_button.setChecked(False)
        self.dp_display_count_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_display_count'))
        
        self.dp_count_SpinBox = self.display.findChild(SpinBox, 'dp_count_SpinBox')
        self.dp_count_SpinBox.setValue(int(config.get('dp_count')))
        self.dp_count_SpinBox.valueChanged.connect(lambda value: self.update_dp(value,'dp_count'))

        self.count_font_PushButton = self.display.findChild(PushButton, 'count_font_PushButton')
        self.count_font_PushButton.clicked.connect(self.count_font)

    def set_Adjustment(self):
        #------调课管理--------
        self.adj_Combobox = self.adjustment.findChild(ComboBox, 'adj_ComboBox')
        self.adj_Combobox.addItems(["默认","星期一","星期二","星期三","星期四","星期五","星期六","星期日"])
        #self.adj_Combobox.setPlaceholderText("请选择调整的星期")# 设置提示文本
        self.adj_Combobox.currentIndexChanged.connect(self.adj_week_changed)

    def set_dsc(self):
        global desk_short
        self.sort_verticalLayout = self.dsc.findChild(QVBoxLayout, 'sort_verticalLayout')
        self.sorter = HorizontalSortWidget()

        self.dsc_Switch_button = self.dsc.findChild(SwitchButton, 'dsc_Switch_button')
        self.default_dsc_xy_PushButton = self.dsc.findChild(PushButton, 'default_dsc_xy_PushButton')
        self.dsc_lock_button = self.dsc.findChild(SwitchButton, 'dsc_lock_button')
        self.dsc_put_button = self.dsc.findChild(SwitchButton, 'dsc_put_button')
        self.dsc_Typeface_button = self.dsc.findChild(PushButton, 'dsc_Typeface_button')
        self.default_dsc_font_PushButton = self.dsc.findChild(PushButton, 'default_dsc_font_PushButton')
        self.dsc_Color_button = self.dsc.findChild(PushButton, 'dsc_Color_button')
        self.dsc_short_LineEdit = self.dsc.findChild(LineEdit, 'dsc_short_LineEdit')
        self.dsc_short_button = self.dsc.findChild(PushButton, 'dsc_short_button')
        self.dsc_addexe_button = self.dsc.findChild(PushButton, 'dsc_addexe_button')
        self.dsc_MoveTeacherFile_button = self.dsc.findChild(PushButton, 'dsc_MoveTeacherFile_button')
        self.dsc_tran_Slider = self.dsc.findChild(Slider, 'dsc_tran_Slider')
        self.dsc_tran_BodyLabel = self.dsc.findChild(BodyLabel, 'dsc_tran_BodyLabel')
        self.dsc_update_short_button = self.dsc.findChild(PushButton, 'dsc_update_short_button')
        self.dsc_halo_button = self.dsc.findChild(SwitchButton, 'dsc_halo_button')
        self.dsc_length_BodyLabel = self.dsc.findChild(BodyLabel, 'dsc_length_BodyLabel')
        self.dsc_length_Slider = self.dsc.findChild(Slider, 'dsc_length_Slider')




        if config.get("dsc_Switch") == "True":
            self.dsc_Switch_button.setChecked(True)
        else:
            self.dsc_Switch_button.setChecked(False)
                
            # 禁用按钮
            controls = [
                self.dsc_lock_button,
                self.default_dsc_xy_PushButton,
                self.dsc_Typeface_button,
                self.default_dsc_font_PushButton,
                self.dsc_put_button,
                self.dsc_Color_button,
                self.dsc_tran_Slider,
                self.dsc_short_button,
                self.dsc_addexe_button,
                self.dsc_update_short_button,
                self.dsc_MoveTeacherFile_button,
                self.dsc_halo_button,
                self.dsc_length_Slider,
                self.dsc_length_BodyLabel

            ]
            for control in controls:
                control.setDisabled(True)

        if config.get("dsc_lock") == "True":
            self.dsc_lock_button.setChecked(True)
        else:
            self.dsc_lock_button.setChecked(False)

        if config.get("dsc_put") == "True":
            self.dsc_put_button.setChecked(True)
        else:
            self.dsc_put_button.setChecked(False)

        if config.get("dsc_halo_switch") == "True":
            self.dsc_halo_button.setChecked(True)
        else:
            self.dsc_halo_button.setChecked(False)

        try:
            self.dsc_tran_Slider.setValue(int(config.get("dsc_tran")))
        except:    
            self.dsc_tran_Slider.setValue(50)
            self.CH.handle_config("50",'dsc_tran')

        self.dsc_tran_BodyLabel.setText(config.get("dsc_tran"))  
        self.dsc_length_Slider.setMaximum(display_x)
        if config.get("dsc_length") == "None":
            self.dsc_length_Slider.setValue(display_x / 2)
            self.dsc_length_BodyLabel.setText(str(display_x/2))
        else:
            self.dsc_length_Slider.setValue(int(config.get("dsc_length")))
            self.dsc_length_BodyLabel.setText(config.get("dsc_length"))
        
        
        
        self.dsc_lock_button.checkedChanged.connect(lambda value: self.CH.handle_config(str(value),'dsc_lock'))
        self.dsc_Switch_button.checkedChanged.connect(lambda value: self.CH.handle_config(str(value),'dsc_Switch'))
        self.default_dsc_xy_PushButton.clicked.connect(lambda: self.CH.handle_config(None, 'default_dsc_xy'))
        self.dsc_Typeface_button.clicked.connect(self.choose_font_dsc)
        self.default_dsc_font_PushButton.clicked.connect(lambda: self.CH.handle_config(None, 'default_dsc_font'))
        self.dsc_put_button.checkedChanged.connect(lambda value: self.CH.handle_config(value, 'dsc_put'))
        self.dsc_Color_button.clicked.connect(self.choose_color_dsc)
        self.dsc_tran_Slider.valueChanged.connect(lambda value: self.CH.handle_config(value, 'dsc_tran'))
        self.dsc_short_button.clicked.connect(self.dsc_addshort)
        self.dsc_addexe_button.clicked.connect(self.addexe.show)
        self.dsc_update_short_button.clicked.connect(self.update_dsc_sorter)
        self.dsc_MoveTeacherFile_button.clicked.connect(desk_short.changeTeacherFilesPath)
        self.dsc_halo_button.checkedChanged.connect(lambda value: self.CH.handle_config(str(value),'dsc_halo_switch'))
        self.dsc_length_Slider.valueChanged.connect(lambda value: self.CH.handle_config(str(value), 'dsc_length'))



        shurt_data = desk_short.get_current_state()
        # 按当前显示顺序提取快捷方式（保持原有顺序）
        current_order_shortcuts = shurt_data['shortcuts']
        # 将当前顺序的快捷方式名称添加到排序组件
        self.sorter.addItems([item['name'] for item in current_order_shortcuts])
        # 存储名称到临时编号的映射，用于后续应用排序
        self.shortcut_temp_id_map = {item['name']: item['temp_id'] for item in current_order_shortcuts}
        self.sorter.orderChanged.connect(self.update_dsc_order)
        self.sort_verticalLayout.addWidget(self.sorter)

    def set_lottery(self):
        self.lot_Switch_button = self.lottery.findChild(SwitchButton, 'lot_Switch_button')
        self.lot_pin_button = self.lottery.findChild(SwitchButton, 'lot_pin_button')
        self.lot_PlainTextEdit = self.lottery.findChild(PlainTextEdit, 'lot_PlainTextEdit')
        self.lot_ListWidget = self.lottery.findChild(ListWidget, 'lot_ListWidget')
        self.lot_add_button = self.lottery.findChild(PrimaryPushButton, 'lot_add_button')
        self.lot_del_button = self.lottery.findChild(PushButton, 'lot_del_button')

        if config.get("lot_Switch") == "True":
            self.lot_Switch_button.setChecked(True)
        else:
            self.lot_Switch_button.setChecked(False)

        if config.get("lot_pin") == "True":
            self.lot_pin_button.setChecked(True)
        else:
            self.lot_pin_button.setChecked(False)

        self.lot_PlainTextEdit.clear()

        self.lot_list = load_student_list()

        self.lot_del_button.hide()

        self.lot_ListWidget.clear()
        self.lot_ListWidget.addItems(self.lot_list)

        self.lot_Switch_button.checkedChanged.connect(lambda value: self.CH.handle_config(value,'lot_Switch'))
        self.lot_pin_button.checkedChanged.connect(lambda value: self.CH.handle_config(value,'lot_pin'))
        self.lot_add_button.clicked.connect(self.add_lot)
        self.lot_del_button.clicked.connect(self.del_lot)

        # 列表被选中
        self.lot_ListWidget.itemSelectionChanged.connect(self.lot_item_selected)

    def add_lot(self):
        text = self.lot_PlainTextEdit.toPlainText().strip()
        if text != "":
            if "#" in text: #分割多个人
                names = [name.strip() for name in text.split("#") if name.strip()]
                for name in names:
                    if name not in self.lot_list:
                        self.lot_list.append(name)
                        self.lot_ListWidget.addItem(name)
                self.lot_PlainTextEdit.clear()
            else:
                self.lot_list.append(text)
                self.lot_ListWidget.addItem(text)
                self.lot_PlainTextEdit.clear()
            save_student_list(self.lot_list)
            Lottery.handle_update("student_list")


        else:
            self.error(e="请输入姓名",msg="错误",grades=False,vas=True)

    def del_lot(self):
        selected_items = self.lot_ListWidget.selectedItems()
        if not selected_items:
            self.error(e="请先选择要删除的项",msg="错误",grades=False,vas=True)
            return
        for item in selected_items:
            self.lot_list.remove(item.text())
            self.lot_ListWidget.takeItem(self.lot_ListWidget.row(item))
        save_student_list(self.lot_list)

    def lot_item_selected(self):
        selected_items = self.lot_ListWidget.selectedItems()
        if selected_items:
            self.lot_del_button.show()
        else:
            self.lot_del_button.hide()
        
        
    def update_dsc_order(self, new_order):
        global desk_short
        try:
            sorted_temp_ids = [
            self.shortcut_temp_id_map[name] 
            for name in new_order ]
            #if name in self.shortcut_temp_id_map]  # 只处理存在的名称

            success = desk_short.sort_shortcuts(sorted_temp_ids)
            #if success:
            #    shortcut_id = {item['name']: item['temp_id'] for item in (desk_short.get_current_state()['shortcuts'])}
            #    #print(f"排序成功，编号顺序: {sorted_temp_ids},\n真实排序：{shortcut_id}")
            #else:
            #    print("排序失败")
        except Exception as e:
            print(f"处理排序时发生错误: {str(e)}")
    def update_dsc_sorter(self):
        global desk_short
        try:
            shurt_data = desk_short.get_current_state()
            # 按当前显示顺序提取快捷方式（保持原有顺序）
            current_order_shortcuts = shurt_data['shortcuts']
            # 将当前顺序的快捷方式名称添加到排序组件
            self.sorter.clear()
            self.sorter.addItems([item['name'] for item in current_order_shortcuts])
            # 存储名称到临时编号的映射，用于后续应用排序
            self.shortcut_temp_id_map = {item['name']: item['temp_id'] for item in current_order_shortcuts}
            self.dsc_update_short_button.setText("成功!")
            QTimer.singleShot(1000, lambda: self.dsc_update_short_button.setText("刷新列表"))
        except Exception as e:
            main.logger.error("更新排序组件时发生错误:\n" + str(e))
            self.dsc_update_short_button.setText("失败!")
            QTimer.singleShot(1000, lambda: self.dsc_update_short_button.setText("刷新列表"))

    @pyqtSlot(str, str, str)
    def update_ui_with_check_result(self, current_cloud_version, check_type, update_status):
        self.check_update(current_cloud_version, check_type, update_status)
    def check_update(self,data=None,types=None,tys=None):
        if types == None:
            self.update_check.setDisabled(True)
            self.yun_version.setText(f'正在检查新版本...')
            main.yun_check_verison()
            #self.update_channel_ComboBox.currentIndexChanged.disconnect(self.update_channel_callback)
            #self.update_channel_ComboBox.clear()
            #self.update_channel_ComboBox.addItems(["正在检查新版本"])
            self.updatesource_ComboBox.currentIndexChanged.disconnect(self.updatesource_callback)
            self.updatesource_ComboBox.clear()
            self.updatesource_ComboBox.addItems(["正在检查新版本"])
            self.warning_SubtitleLabel.hide()

        elif types == "check_end":
            self.yun_version.setText(f"最新版本：{data}")
            upc = []
            if yun_version == "获取失败":

                #s = "正式版" if config.get("update_channel") == "beta" else "测试版(beta)"
                s = "正式版" if Version_Parse.is_prerelease == False else "测试版(beta)"
                upc = [f"{s}(请先检查网络)"]
                #self.update_channel_ComboBox.clear()
                #self.update_channel_ComboBox.addItems(upc)
                self.updatesource_ComboBox.clear()
                self.updatesource_ComboBox.addItems(["请先检查网络"])

                
            else:
                upc = ["正式版"]
                if yun_data_version["beta_version"] != "None":
                    upc.append("测试版(Beta)")
                else:
                    if config.get("update_channel") == "beta":
                        upc.append("测试版(Beta)(目前没有测试版本)")
                        self.warning_SubtitleLabel.show()

                #self.update_channel_ComboBox.clear()
                #self.update_channel_ComboBox.addItems(upc)
                self.updatesource_ComboBox.clear()
                self.updatesource_ComboBox.addItems(ncu.keys())

                #if config.get("update_channel") == "beta":
                #    self.update_channel_ComboBox.setCurrentIndex(1)
                #elif config.get("update_channel") == "stable":
                #    self.update_channel_ComboBox.setCurrentIndex(0)
            self.update_check.setEnabled(True)
            self.updatesource_ComboBox.currentIndexChanged.connect(self.updatesource_callback)

            if tys == "update": # 有更新
                #wm = MessageBox("检测到新版本", "建议及时更新，以获取最新的改近以及新功能。", self)
                self.down_im_ProgressBar.hide()
                wm = MessageBox("检测到新版本", "目前暂时不可直接下载，请移步至官方下载网站进行下载新版本。辛苦啦~", self)
                wm.yesButton.setText("打开")
                wm.cancelButton.setText("暂不更新")
                if wm.exec():
                    #打开url

                    webbrowser.open("https://www.yuque.com/yamikani/lingyun/yrlp9d1ob88b74z5")
                    
                    return


                    self.update_check.setDisabled(True)
                    if update_channel == None:
                        ws = MessageBox("警告", "下载地址获取失败，未作任何更改。可以尝试更换更新线路。你可以稍后再试或者进行反馈。", self)
                        ws.yesButton.setText("好")
                        ws.cancelButton.hide()
                        #self.update_channel_ComboBox.setCurrentIndex(0)
                        if ws.exec():
                            self.update_check.setEnabled(True)
                    else:
                        print(f"开始下载更新程序，下载地址：{update_channel}")
                        save = tempfile.gettempdir() + "/LingYun/Temp.exe"
                        self.down_ElevatedCardWidget.show()
                        #self.download_ok(save,None)
                        download_ly.download_file(update_channel,save,self.download_ok,self.download_plan)
            #self.update_channel_ComboBox.currentIndexChanged.connect(self.update_channel_callback)

    def download_plan(self,bytes_downloaded, total_size, info_text):
        #self.down_im_ProgressBar.hide()
        #self.down_ProgressBar.show()


        if total_size > 0:
            
            progress = (bytes_downloaded / total_size) * 100
            print(progress)
            #self.down_ProgressBar.setValue(int(progress))

            self.info_Label.setText(f"正在下载，请耐心等待 {info_text}")
            self.percent_Label.setText(f"{progress:.2f}%")
        else:
            print(f"已下载 {bytes_downloaded} 字节")

    def download_ok(self,path,error):
        if error == None:
            self.in_update = False
            self.down_ProgressBar.setValue(int(100))
            self.info_Label.setText(f"下载完成，即将自动启动更新程序软件以继续安装")
            self.percent_Label.setText(f"100%")
            main.download_ok(path,None)
        else:
            self.down_ProgressBar.setValue(int(100))
            self.down_ProgressBar.hide()            
            self.down_im_ProgressBar.show()
            self.info_Label.setText(f"下载失败，错误信息为：\n{error}")
            self.percent_Label.setText(f"--%")
            main.download_ok(None,error)

    def adj_week_changed(self, index):
        global adj_weekday,DP_Comonent
        adj_weekday = index
        if adj_weekday == 0:
            adj_weekday = datetime.now().weekday() + 1
        a = main.convert_widget(-1)
        if a == "close":
            return
        DP_Comonent.clear_ui()
        DP_Comonent.alert(None,adj_weekday)
        QTimer.singleShot(1000, DP_Comonent.refresh_and_restart_countdown)
        

    def SD_changed(self,value):
        global class_table_a, class_table_b, class_time_a, class_time_b

        if value == 0: # 单周
            done, ls = self.convert_table(class_table_a)
            self.widget_time = self.convert_time(class_time_a)
        else: # 双周
            done, ls = self.convert_table(class_table_b)

            self.widget_time = self.convert_time(class_time_b)

        lists["widgets_on"] = True            
        self.TableWidget.itemChanged.disconnect(self.table_update)  
        self.TableWidget.clear()        
        self.TableWidget.setWordWrap(False)

        # 设置表格的行数和列数
        self.TableWidget.setRowCount(ls)
        self.TableWidget.setColumnCount(8)
        self.TableWidget.setHorizontalHeaderLabels(['时间','星期一','星期二','星期三','星期四','星期五','星期六','星期日'])

        for i in range(ls):
            item = QTableWidgetItem(self.widget_time[i])
            self.TableWidget.setItem(i, 0, item)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        for i, Info in enumerate(done):
            for j in range(7):
                item = QTableWidgetItem(Info[j])
                self.TableWidget.setItem(i, j+1, item)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)# 设置单元格文本居中对齐
        lists["widgets_on"] = False
        self.TableWidget.itemChanged.connect(self.table_update)
    def week_changed(self):
        global class_weekday
        self.TimeWidget.clearSelection()
        class_weekday = self.week_ComboBox.currentText()
        self.Counter_SwitchButton.setDisabled(True)
        self.Counter_SwitchButton.setChecked(False)

        if class_weekday != "通用":
            self.ct_CardWidget2.hide()
        else:
            self.ct_CardWidget2.show()
        self.Time_Widget_update()
    def set_yun(self):
        #------设置集中控制页面的控件--------
        self.yun_Button = self.yun.findChild(SwitchButton, 'yun_button')
        self.yun_PasswordLineEdit = self.yun.findChild(PasswordLineEdit, 'yun_PasswordLineEdit')
        self.password_PushButton = self.yun.findChild(PushButton, 'password_PushButton')
        self.equipment_LineEdit = self.yun.findChild(LineEdit, 'equipment_LineEdit')
        self.http_LineEdit = self.yun.findChild(LineEdit, 'http_LineEdit')
        self.timeleg_button = self.yun.findChild(SwitchButton, 'timeleg_button')
        self.json_button = self.yun.findChild(SwitchButton, 'json_button')
        self.yun_xg_PasswordLineEdit = self.yun.findChild(PasswordLineEdit, 'yun_xg_PasswordLineEdit')
        self.xg_PushButton = self.yun.findChild(PushButton, 'xg_password_PushButton')
        self.equipment_PushButton = self.yun.findChild(PushButton, 'equipment_PushButton')
        self.http_PushButton = self.yun.findChild(PushButton, 'http_PushButton')
        self.yuntime_SpinBox = self.yun.findChild(SpinBox, 'yuntime_SpinBox')
        self.start_PushButton = self.yun.findChild(PushButton, 'start_PushButton')

        
        self.CardWidget_yun = self.yun.findChild(CardWidget, 'CardWidget_13')
        self.CardWidget_equipment = self.yun.findChild(CardWidget, 'CardWidget_8')
        self.CardWidget_https = self.yun.findChild(CardWidget, 'CardWidget_11')
        self.CardWidget_timeleg = self.yun.findChild(CardWidget, 'CardWidget_10')
        self.CardWidget_json = self.yun.findChild(CardWidget, 'CardWidget_9')
        self.CardWidget_xg = self.yun.findChild(CardWidget, 'CardWidget_14')

        
        self.CardWidget_yun.hide()
        self.CardWidget_equipment.hide()
        self.CardWidget_https.hide()
        self.CardWidget_timeleg.hide()
        self.CardWidget_json.hide()
        self.CardWidget_xg.hide()


        self.password_PushButton.clicked.connect(lambda:self.yun_sever("None","password"))

        if config.get("yun_Switch") == "True":
            self.yun_Button.setChecked(True)
        else:
            self.yun_Button.setChecked(False)
        self.yun_Button.checkedChanged.connect(lambda value:self.yun_sever(value,"yun_Switch"))

        self.equipment_LineEdit.setText(config.get("yun_equipment"))
        self.equipment_PushButton.clicked.connect(lambda:self.yun_sever(self.equipment_LineEdit.text(),"yun_equipment"))

        self.http_LineEdit.setText(config.get("yun_https"))
        self.http_PushButton.clicked.connect(lambda:self.yun_sever(self.http_LineEdit.text(),"yun_https"))

        

        if config.get("timeleg_Switch") == "True":
            self.timeleg_button.setChecked(True)
        else:
            self.timeleg_button.setChecked(False)
        if config.get("json_Switch") == "True":
            self.json_button.setChecked(True)
        else:
            self.json_button.setChecked(False)

        self.timeleg_button.checkedChanged.connect(lambda value:self.yun_sever(value,"timeleg_Switch"))
        self.json_button.checkedChanged.connect(lambda value:self.yun_sever(value,"json_Switch"))
        self.xg_PushButton.clicked.connect(lambda:self.yun_sever(self.yun_xg_PasswordLineEdit.text(),"yun_password"))
        self.yuntime_SpinBox.setValue(int(config.get("yun_time")))
        self.yuntime_SpinBox.valueChanged.connect(lambda value:self.yun_sever(value,"yun_time"))
        self.start_PushButton.clicked.connect(self.start_yun)

    def start_yun(self,flag=None):
        ## !!!!!!!! flag待调整
        if flag != "ok":
            if config.get("yun_Switch") != "True":
                self.error("请先启用云同步","警告",False,True)
                return
            if config.get("yun_equipment") == "":
                self.error("请先设置设备名称","警告",False,True)
                return
            if config.get("yun_https") == "":
                self.error("请先设置服务器地址","警告",False,True)
                return
            self.start_PushButton.setText("正在同步")
            self.start_PushButton.setDisabled(True)
            main.yun_data()
        else:
            self.start_PushButton.setText("立即执行同步")
            self.start_PushButton.setEnabled(True)



    def yun_sever(self,value,sever):
        if sever == "password":
            password = self.yun_PasswordLineEdit.text()
            if password == config.get("yun_password"):
                self.CardWidget_yun.show()
                self.CardWidget_equipment.show()
                self.CardWidget_https.show()
                self.CardWidget_timeleg.show()
                self.CardWidget_json.show()
                self.CardWidget_xg.show()
            else:
                self.error("密码可能是错误的","警告",False,True)
                self.yun_PasswordLineEdit.clear()
            return

        try:
            # 创建或打开注册表键
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
            # 获取当前设置的值
            config[sever] = str(value)
            # 将设置写入注册表
            reg.SetValueEx(registry_key, sever, 0, reg.REG_SZ, str(value))
        except Exception as e:
            self.error(str(e))
        finally:
            if 'registry_key' in locals():
                reg.CloseKey(registry_key)

        '''if sever == "yun_Switch":
            print(config.get("yun_Switch"))
            pass
        elif sever == "yun_equipment":
            print(config.get("yun_equipment"))
            pass
        elif sever == "yun_https":
            print(config.get("yun_https"))
            pass
        elif sever == "timeleg_Switch":
            print(config.get("timeleg_Switch"))
            pass
        elif sever == "json_Switch":
            print(config.get("json_Switch"))
            pass'''
    """# 加密函数
    def encrypt_data(self,data, key):
        # 生成随机的初始化向量 (IV)
        iv = get_random_bytes(16)
        # 创建 AES 加密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # 对数据进行填充并加密
        encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        # 返回 IV 和加密后的数据
        return iv + encrypted_data

    # 解密函数
    def decrypt_data(self,encrypted_data, key):
        # 提取 IV
        iv = encrypted_data[:16]
        # 提取加密数据
        ciphertext = encrypted_data[16:]
        # 创建 AES 解密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # 解密并去除填充
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        # 返回解密后的数据
        return decrypted_data.decode('utf-8')

    """
    def Flyout(self,title,content,target,icon=InfoBarIcon.SUCCESS):
        '''
        icon=InfoBarIcon.SUCCESS,
        title='Lesson 4',
        content="表达敬意吧",
        target=self.cs,
        parent=self,
        isClosable=True,
        aniType=FlyoutAnimationType.PULL_UP
        '''
        Flyout.create(
            icon=icon,
            title=title,
            content=content,
            target=target,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
    def update_duty(self,choose:str):
        global DP_Comonent,duty_table
        if choose.startswith("again"):
            action = choose[6:]  # 提取操作类型（如"del_item"）


            # 获取当前组号（基于日期计算）
            date_begin_str = duty_table["date_begin"]
            date_begin = datetime.strptime(date_begin_str, "%Y%m%d").date()
            today = date.today()  # 使用实际日期
            
            # 计算工作日天数
            workdays = 0
            current_date = date_begin
            while current_date < today:
                current_date += timedelta(days=1)
                if current_date.isoweekday() not in [6, 7]:  # 跳过周末
                    workdays += 1
                    
            # 计算当前组号（1-based）
            duty_groups = duty_table["duty"]
            num_groups = len(duty_groups)
            current_group = (workdays % num_groups) + 1
            group_key = str(current_group)

            if current_group != int(self.again_box.currentText()):
                current_group = int(self.again_box.currentText())
                group_key = str(current_group)

            if action == "duty_widget":
                if self.duty_Widget.currentItem() == None:
                    self.again_name_Edit.clear()
                    self.again_project_Edit.clear()
                    return
                text = self.duty_Widget.currentItem().text().split("-")[0]
                try:
                    self.again_project_Edit.setText(text)
                    self.again_name_Edit.setText(" ".join(duty_groups[group_key].get(text, [])))
                except Exception as e:
                    self.again_project_Edit.clear()
                    self.again_name_Edit.clear()
                    
            elif action == "name":
                name = self.again_name_Edit.text()
                if len(name) > 20 or len(name) < 1:
                    self.error("名字长度必须介于1到20之间", "警告", False, True)
                    return
                if self.duty_Widget.currentItem() == None:
                    self.error("请先选择一个项目", "警告", False, True)
                    return
                text = self.duty_Widget.currentItem().text().split("-")[0]
                names = name.split("#")
                duty_groups[group_key][text] = names
                #self.update_duty_display()  # 更新显示
                
            elif action == "project":
                name = self.project_Edit.text()
                if len(name) > 6 or len(name) < 1:
                    self.error("项目长度必须介于1到6之间", "警告", False, True)
                    return
                if self.duty_Widget.currentItem() == None:
                    self.error("请先选择一个项目", "警告", False, True)
                    return
                text = self.duty_Widget.currentItem().text().split("-")[0]
                if text in duty_groups[group_key]:
                    duty_groups[group_key][name] = duty_groups[group_key].pop(text)
                    main.saves_to_json()
                    #self.update_duty_display()  # 更新显示
                    
            elif action == "add_item":
                name = self.again_name_Edit.text()
                project = self.again_project_Edit.text()
                if name == "" or project == "":
                    self.error("请先输入项目名字和负责人员", "警告", False, True)
                    return
                if len(name) > 20 or len(name) < 1:
                    self.error("名字长度必须介于1到20之间", "警告", False, True)
                    return
                if len(project) > 6 or len(project) < 1:
                    self.error("项目长度必须介于1到6之间", "警告", False, True)
                    return
                names = name.split(" ")
                duty_groups[group_key][project] = names
                #self.update_duty_display()  # 更新显示
                
            elif action == "del_item":
                if self.duty_Widget.currentItem() == None:
                    self.error("请先选择一个项目", "警告", False, True)
                    return
                text = self.duty_Widget.currentItem().text().split("-")[0]
                if text in duty_groups[group_key]:
                    duty_groups[group_key].pop(text)
                    
                    #self.update_duty_display()  # 更新显示

            elif action == "new":
                # 新组编号
                group = int(list(duty_groups.keys())[-1]) + 1
                new_group_data = {key: [] for key in duty_groups[str(group-1)]}
                duty_groups[str(group)] = new_group_data
                try:
                    self.again_box.currentIndexChanged.disconnect(self.duty_week_changed)
                except TypeError:
                    # 如果未连接，会抛出 TypeError，直接忽略
                    pass
                self.again_box.clear()
                self.again_box.addItems(list(duty_groups.keys()))
                self.again_box.currentIndexChanged.connect(self.duty_week_changed) 
                self.again_box.setCurrentIndex(int(group)-1)
                #QTimer.singleShot(100, lambda: )
            elif action == "ZhDatePicker":
                duty_table["date_begin"] = self.again_ZhDatePicker.date.toString("yyyyMMdd")
            # 更新桌面组件显示
            if action != "duty_widget":
                duty_table["duty"] = duty_groups
                main.saves_to_json()
                self.duty_week_changed(current_group - 1)
                DP_Comonent.update_duty()
            #return
        
        elif choose == "initializew":
            # 切换到星期法
            self.again_ZhDatePicker.setDisabled(True)
            self.again_box.setDisabled(True)
            self.again_new_PrimaryPushButton.setDisabled(True)
            self.again_project_Edit.setDisabled(True)
            self.again_project_Button.setDisabled(True)
            self.again_name_Edit.setDisabled(True)
            self.again_name_Button.setDisabled(True)
            self.again_Add_Button.setDisabled(True)
            self.again_Del_Button.setDisabled(True)

            # 解禁
            self.name_Button.setDisabled(False)
            self.project_Button.setDisabled(False)
            self.Add_Button.setDisabled(False)
            self.Del_Button.setDisabled(False)
            self.week_box.setDisabled(False)
            self.name_Edit.setDisabled(False)
            self.project_Edit.setDisabled(False)

            self.dutyw2_CardWidget.show()
            self.dutyw_CardWidget.hide()


            duty_table = default_class[5]
            main.saves_to_json()
            config["duty_mode"] = "weekday"
            self.duty_week_changed(datetime.now().weekday())
            self.duty_Widget.itemSelectionChanged.connect(lambda: self.update_duty("duty_widget"))
            self.error("请重启本程序以生效","切换到星期法成功",False,False)
        elif choose == "initializew2":
            # 切换到轮回法
            self.name_Button.setDisabled(True)
            self.project_Button.setDisabled(True)
            self.Add_Button.setDisabled(True)
            self.Del_Button.setDisabled(True)
            self.week_box.setDisabled(True)
            self.name_Edit.setDisabled(True)
            self.project_Edit.setDisabled(True)
            self.dutyw2_CardWidget.hide()
            self.dutyw_CardWidget.show()

            #解禁
            self.again_ZhDatePicker.setDisabled(False)
            self.again_box.setDisabled(False)
            self.again_new_PrimaryPushButton.setDisabled(False)
            self.again_project_Edit.setDisabled(False)
            self.again_project_Button.setDisabled(False)
            self.again_name_Edit.setDisabled(False)
            self.again_name_Button.setDisabled(False)
            self.again_Add_Button.setDisabled(False)
            self.again_Del_Button.setDisabled(False)


            duty_table = duty_again
            main.saves_to_json()
            config["duty_mode"] = "again"
            dates = duty_table.get("date_begin")
            self.again_ZhDatePicker.setDate(QDate(int(dates[:4]), int(dates[4:6]), int(dates[6:])))
            self.again_ZhDatePicker.dateChanged.connect(lambda date: self.update_duty('again_ZhDatePicker'))
            self.again_box.clear()
            self.again_box.addItems(list((duty_table.get("duty")).keys()))
            group_key, duty_groups = self.duty_again_group()
            QTimer.singleShot(100, lambda: self.duty_week_changed(int(group_key)-1))
            self.again_box.setCurrentIndex(int(group_key) - 1)
            self.duty_Widget.itemSelectionChanged.connect(lambda: self.update_duty("again_duty_widget"))                
            self.error("请重启本程序以生效","切换到星期法成功",False,False)
        elif choose == "duty_widget":
            if self.duty_Widget.currentItem() == None:
                self.name_Edit.clear()
                self.project_Edit.clear()
                return
            week = str(self.week)
            duty = duty_table.get(week, [])
            text = self.duty_Widget.currentItem().text().split("-")[0]
            try:
                self.project_Edit.setText(text)
                self.name_Edit.setText(" ".join(duty[text]))
            except Exception as e:
                self.project_Edit.clear()
                self.name_Edit.clear()
        elif choose == "name":
            week = str(self.week)
            name = self.name_Edit.text()
            if len(name) > 20 or len(name) < 1:
                self.error("名字长度必须介于1到20之间","警告",False,True)
                return
            if self.duty_Widget.currentItem() == None:
                self.error("请先选择一个项目","警告",False,True)
                return
            text = self.duty_Widget.currentItem().text().split("-")[0]
            names = name.split("#")
            duty_table[week][text] = names
            main.saves_to_json()
            #main.save_to_json(duty_table,"duty_table.json")
            self.duty_week_changed(self.week - 1)
        elif choose == "project":
            week = str(self.week)
            name = self.project_Edit.text()
            if len(name) > 6 or len(name) < 1:
                self.error("名字长度必须介于1到6之间","警告",False,True)
                return
            if self.duty_Widget.currentItem() == None:
                self.error("请先选择一个项目","警告",False,True)
                return
            text = self.duty_Widget.currentItem().text().split("-")[0]
            duty_table[week][name] = duty_table[week].pop(text) # 修改项目名字
            main.saves_to_json()
            #main.save_to_json(duty_table,"duty_table.json")
            self.duty_week_changed(self.week - 1)
        elif choose == "add_item":
            week = str(self.week)
            name = self.name_Edit.text()
            project = self.project_Edit.text()
            if name == "" or project == "":
                self.error("请先输入项目名字和负责人员","警告",False,True)
                return
            if len(name) > 20 or len(name) < 1:
                self.error("名字长度必须介于1到20之间","警告",False,True)
                return
            if len(project) > 6 or len(project) < 1:
                self.error("项目长度必须介于1到6之间","警告",False,True)
                return
            names = name.split(" ")
            duty_table[week][project] = names
            main.saves_to_json()
            #main.save_to_json(duty_table,"duty_table.json")
            self.duty_week_changed(self.week - 1)
        elif choose == "del_item":
            week = str(self.week)
            if self.duty_Widget.currentItem() == None:
                self.error("请先选择一个项目","警告",False,True)
                return
            text = self.duty_Widget.currentItem().text().split("-")[0]
            duty_table[week].pop(text)
            main.saves_to_json()
            #main.save_to_json(duty_table,"duty_table.json")
            self.duty_week_changed(self.week - 1)

        if self.week == datetime.now().weekday() + 1:
            DP_Comonent.update_duty()
    def duty_week_changed(self,index):
        if config.get("duty_mode") == "weekday":
            self.week = index + 1
            week = str(index + 1)
            duty0 = duty_table.get(week, [])
            formatted_tasks = []
            for task, students in duty0.items():
                # 将学生列表用空格连接
                students_str = '、'.join(students)
                # 格式化为 "任务(学生1 学生2)" 的形式
                formatted_task = f"{task}-（{students_str}）"
                formatted_tasks.append(formatted_task)

            self.name_Edit.clear()
            self.project_Edit.clear()
            self.duty_Widget.clear()
            self.duty_Widget.addItems(formatted_tasks)
        elif config.get("duty_mode") == "again":
            today_duty = duty_table["duty"].get(str(index+1), {})
            formatted_tasks = []
            for task, students in today_duty.items():
                # 将学生列表用空格连接
                students_str = '、'.join(students)
                # 格式化为 "任务(学生1 学生2)" 的形式
                formatted_task = f"{task}-（{students_str}）"
                formatted_tasks.append(formatted_task)
            self.again_name_Edit.clear()
            self.again_project_Edit.clear()
            self.duty_Widget.clear()
            self.duty_Widget.addItems(formatted_tasks)

    def duty_again_group(self):
        date_begin_str = duty_table["date_begin"]
        date_begin = datetime.strptime(date_begin_str, "%Y%m%d").date()
        today = date.today()
        workdays = 0
        current_date = date_begin
        while current_date < today:
            current_date += timedelta(days=1)
            if current_date.isoweekday() not in [6, 7]:
                workdays += 1
        duty_groups = duty_table["duty"]
        num_groups = len(duty_groups)
        group_index = (workdays % num_groups) + 1
        group_key = str(group_index)
        #print(f"当前组号：{group_key}, 工作日天数：{workdays}, 组数：{num_groups}")
        return group_key,duty_groups
    def click_TimeWidget(self,index):
        global class_ORD_Filtration,lists,main
        lists["click_Counter"] = True
        self.Counter_SwitchButton.setDisabled(False)
        if index.text() in class_ORD_Filtration:
            self.Counter_SwitchButton.setChecked(True)
        else:
            self.Counter_SwitchButton.setChecked(False)
        lists["click_Counter"] = False
    def click_Counter_Button(self,value):
        global class_ORD_Filtration,lists,main        
        if lists.get("click_Counter") == False:
            t = self.TimeWidget.currentItem().text()
            if self.TimeWidget.currentItem() == None:
                self.error("请先选择一个时间段","警告",False,True)
                lists["click_Counter"] = True
                if value == True:self.Counter_SwitchButton.setChecked(False)
                else:self.Counter_SwitchButton.setChecked(True)
                return
            if t in self.ap_list:
                self.error(f"请选择时间段。“{t}”不是时间段。","警告",False,True)
                lists["click_Counter"] = True
                if value == True:self.Counter_SwitchButton.setChecked(False)
                else:self.Counter_SwitchButton.setChecked(True)
                return
            try:
                if t not in class_ORD_Filtration:
                    class_ORD_Filtration.append(str(t))
                else:
                    class_ORD_Filtration.remove(str(t))
            except Exception as e:
                self.error("逻辑出问题，可能是配置中已经存在或者是读取后手动修改，请检查json文件，或者重试。\n以下为详细错误信息：\n"+str(e),"警告",False,True)
            
            main.white_Widgets()
        else:
            lists["click_Counter"] = False
    def stacked(self,st):
        """if st == 3:
            w = MessageBox("提示", "在你编辑时间线时，桌面组件需要被关闭，因为在修改时间时可能造成冲突而出错。\n点击确定后关闭桌面组件，重启本软件可以恢复。感谢您的理解！", self)
            w.yesButton.setText("确定")
            w.cancelButton.setText("不关闭进行编辑(不建议)")
            if w.exec():
                DP_Comonent.animation_hide.start()
                DP_Comonent.animation_rect_hide.start()
                tim = QTimer()
                tim.singleShot(1000, lambda: DP_Comonent.close())
            else:pass"""
    def choose_font_dp(self):
        font, ok = QFontDialog.getFont(self)
        if ok:
            self.update_dp(font.family(),'dp_Typeface')
            config['dp_Typeface'] = font.family()
    def choose_font_dsc(self):
        font, ok = QFontDialog.getFont(self)
        if ok:
            self.CH.handle_config(str(font.family()),'dsc_Typeface')
            self.CH.handle_config(str(font.pointSize()),'dsc_Typeface_size')
            desk_short.handle_update('Typeface', font)
    def choose_color_dsc(self):
        color = QColorDialog.getColor()
        if color.isValid():
            #config['dsc_Color'] = color.name()
            self.CH.handle_config(color.name(),'dsc_Color')
            #desk_short.handle_update('Color', color)
    def count_font(self):
        font, ok = QFontDialog.getFont(self)
        if ok:
            self.update_dp(font.family(),'dp_count_font')
    def choose_color_dp(self ,types):
        color = QColorDialog.getColor()
        if color.isValid():
            DP_Comonent.lingyun_Bar.setCustomBarColor(QColor(color), QColor(color))
            config[f'dp_Countdown_Bar_color_{types}'] = color.name()
            self.update_dp(color.name(),f'dp_Countdown_Bar_color_{types}')
    def choose_box_changed(self,index):
        try:
            # 创建或打开注册表键
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
            # 获取当前设置的值
            config["dp_choose"] = self.files[index]
            # 将设置写入注册表
            reg.SetValueEx(registry_key, "dp_choose", 0, reg.REG_SZ, str(self.files[index]))
        except Exception as e:
            self.error(str(e))
        
        self.error("需要重启才可以使更改生效。","提示",False,False)
    def dsc_addshort(self):
        text = self.dsc_short_LineEdit.text()
        if text == "":
            self.error("请输入快捷方式名称","警告",False,True)
            return
        shurt_name = [item['name'] for item in desk_short.get_current_state()['shortcuts']]
        if text in shurt_name:
            self.error("快捷方式已存在","警告",False,True)
            return
        desk_short.addNewFolderShortcut(text)
        self.dsc_short_LineEdit.clear()
    def dsc_add_exe_shortcut(self):
        text = self.dsc_short_LineEdit.text()
        if text == "":
            self.error("请输入快捷方式名称","警告",False,True)
            return
        shurt_name = [item['name'] for item in desk_short.get_current_state()['shortcuts']]
        if text in shurt_name:
            self.error("快捷方式已存在","警告",False,True)
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "选择可执行文件", "", "Executable Files (*.exe);;All Files (*)")
        if file_path:
            desk_short.addNewExeShortcut(text,file_path)
            self.dsc_short_LineEdit.clear()

    def update_dp(self,value,choose):
        if choose == "dp_widgets":
            DP_Comonent.lingyun_down.setText("--:--")
            value = self.json_widgets[value] + ".json"
        
        if choose == "dp_Pin":
            if value == 0:
                value = "True"
            elif value == 1:
                value = "False"
            elif value == 2:
                value = "Under"

        if choose == "dp_duty_TimePicker_from":
            value = f"{value.hour()}:{value.minute()}"
        if choose == "dp_duty_TimePicker_to":
            value = f"{value.hour()}:{value.minute()}"

        if choose == "dp_danweekly":
            value = f"{value.year()},{value.month()},{value.day()}"

        if choose == "update_channel_w":
            if value == 0:
                values = "stable"
            elif value == 1:
                values = "beta"

            self.update_channel(values)
            return
        try:
            # 创建或打开注册表键
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
            # 获取当前设置的值
            config[choose] = str(value)
            # 将设置写入注册表
            reg.SetValueEx(registry_key, choose, 0, reg.REG_SZ, str(value))
        except Exception as e:
            self.error(str(e))
        finally:
            if 'registry_key' in locals():
                reg.CloseKey(registry_key)

        config[choose] = str(value)

        if choose == "dp_widgets":
            self.inex("dp_widgets")

        if choose == "dp_Bell":
            if str(value) == "True":
                self.CardWidget_8.show()
                if config.get('dp_Sysvolume') == "True":
                    self.CardWidget_11.show()
                else:
                    self.CardWidget_11.hide()
            else:
                self.CardWidget_8.hide()
                self.CardWidget_11.hide()
        if choose == "dp_Sysvolume":
            if str(value) == "True" :
                self.CardWidget_11.show()
            else:
                self.CardWidget_11.hide()
        if choose == "dp_biweekly":
            self.Flyout(title="提示",content="修改成功！重启后生效",target=self.dp_biweekly_button)
        if choose == "dp_Typeface":
            self.Flyout(title="提示",content="操作成功！",target=self.default_dp_font_PushButton)




        return_choices = {
            "dp_Curriculum_ramp_action", "dp_countdown_action", "dp_todayclass_action", "dp_duty_action",
            "check_update", "print_log", "check_net", "dp_xiping", "auto_update","update_channel",
            "update_ncu","dp_count","dp_display_count","dp_count_font"
        }
        if choose in return_choices:
            return
        
        DP_Comonent.update_ui(value,choose)

    def update_channel(self,value):
        global update_channel
        return
        if value == "stable":
            w = MessageBox("提示", "你目前在Beta版，是否确定需要回到正式版？", self)
            w.yesButton.setText("确定回去")
            w.cancelButton.setText("取消")
            w.buttonLayout.insertStretch(1)

            if w.exec():
                self.update_dp(value,"update_channel")
                if update_channel == None:
                    ws = MessageBox("警告", "下载地址获取失败，未作任何更改。可以尝试更换更新线路。你可以稍后再试或者进行反馈。", self)
                    ws.yesButton.setText("好")
                    ws.cancelButton.hide()
                    self.update_channel_ComboBox.currentIndexChanged.disconnect(self.update_channel_callback)
                    self.update_channel_ComboBox.setCurrentIndex(0)
                    self.update_channel_ComboBox.currentIndexChanged.connect(self.update_channel_callback)                    
                    if ws.exec():
                        pass
                else: 
                    save = tempfile.gettempdir() + "/LingYun/Temp.zip"
                    download_ly.download_file(update_channel,save,main.download_ok)
                #切换...
            else:
                self.update_channel_ComboBox.currentIndexChanged.disconnect(self.update_channel_callback)
                self.update_channel_ComboBox.setCurrentIndex(1)
                self.update_channel_ComboBox.currentIndexChanged.connect(self.update_channel_callback)
                # 把标签改回去

        elif value == "beta":
            w = MessageBox("提示", "你目前在正式版，是否确定需要切换到Beta版？\n如果确定，那将开始下载Beta版并且自动开始更新。\n在更新过程中请不要关机，将在1-5分钟内完成，这取决于网速。", self)
            w.yesButton.setText("确定并开始更新")
            w.cancelButton.setText("取消")
            w.buttonLayout.insertStretch(1)
            if w.exec():
                self.update_dp(value,"update_channel")
                if update_channel == None:
                    ws = MessageBox("警告", "下载地址获取失败，未作任何更改。可以尝试更换更新线路。你可以稍后再试或者进行反馈。", self)
                    ws.yesButton.setText("好")
                    ws.cancelButton.hide()
                    self.update_channel_ComboBox.currentIndexChanged.disconnect(self.update_channel_callback)
                    self.update_channel_ComboBox.setCurrentIndex(0)
                    self.update_channel_ComboBox.currentIndexChanged.connect(self.update_channel_callback)                    
                    if ws.exec():
                        pass
                else:
                    save = tempfile.gettempdir() + "/LingYun/Temp.zip"
                    download_ly.download_file(update_channel,save,main.download_ok)

            else:
                # 把标签改回去
                self.update_channel_ComboBox.currentIndexChanged.disconnect(self.update_channel_callback)
                self.update_channel_ComboBox.setCurrentIndex(0)
                self.update_channel_ComboBox.currentIndexChanged.connect(self.update_channel_callback)

    def update_widgets_visibility(self):
        t = self.TimeWidget.currentItem().text()
        if self.TimeWidget.selectedItems() and "-" in t:
            self.edit_label.show()
            self.CardWidget4.show()
            self.TimePicker_from_edit.setTime(QTime.fromString(t.split("-")[0], "HH:mm"))
            self.TimePicker_to_edit.setTime(QTime.fromString(t.split("-")[1], "HH:mm"))
        else:
            self.edit_label.hide()
            self.CardWidget4.hide()
    def edit_time(self):
        self.from_time_edit = self.TimePicker_from_edit.time.toString("HH:mm:ss")
        self.to_time_edit = self.TimePicker_to_edit.time.toString("HH:mm:ss")
        if self.from_time_edit == "" or self.to_time_edit == "":
            self.error("请先选择开始时间和结束时间","警告",False,True)
            return
        if self.from_time_edit > self.to_time_edit:
            self.error("开始时间不能大于结束时间","警告",False,True)
            return
        if self.from_time_edit == self.to_time_edit:
            self.error("开始时间不能等于结束时间","警告",False,True)
            return
        
        # 去掉秒数并格式化时间段
        start_time_formatted = datetime.strptime(self.from_time_edit, "%H:%M:%S").strftime("%H:%M")
        end_time_formatted = datetime.strptime(self.to_time_edit, "%H:%M:%S").strftime("%H:%M")
        time_period = f"{start_time_formatted}-{end_time_formatted}"

        # 提供的时间段和要修改的时间段
        old_time_period = self.TimeWidget.currentItem().text()

        zp = {"周一":"1","周二":"2","周三":"3","周四":"4","周五":"5","周六":"6","周日":"7"}
        s = self.week_ComboBox.currentText()

        # 找出时间段并进行修改
        if s == "通用":
            for ins in class_time:
                for period in class_time[ins]:
                    if old_time_period in class_time[ins][period]:
                        index = class_time[ins][period].index(old_time_period)
                        class_time[ins][period][index] = time_period
                        break
        else:
            s = zp[s]
            for period in class_time[s]:
                if old_time_period in class_time[s][period]:
                    index = class_time[s][period].index(old_time_period)
                    class_time[s][period][index] = time_period
                    break

        main.saves_to_json()
        self.TimeWidget.clearSelection()
        self.Time_Widget_update()
        self.add_name_box.clear()
        self.add_name_box.addItems(self.ap_list)

        if self.auto_update_Button.isChecked():
            self.set_table_update()
    def del_Widget(self):
        if self.TimeWidget.currentItem() is None:
            self.error("请先选择一个时间段","警告",False,True)
            return
        if self.TimeWidget.currentItem().text() in self.ap_list:
            self.error(f"请选择一个时间段。\n如果你需要删除这整个“{self.TimeWidget.currentItem().text()}”，那么你应该先删除“{self.TimeWidget.currentItem().text()}”下所有的时间段。","警告",False,True)
            return
        w = MessageBox("提示", "你确定要删除吗？\n这样会使那一段内星期一至星期日的那一节课全部删除，确定？\n此操作不可逆！", self)
        w.cancelButton.setText("确定")
        w.yesButton.setText("我再想想")
        if w.exec():pass
        else:
            time_period = self.TimeWidget.currentItem().text()
            # 找出时间段的位置和午别
            found = False
            for ins in class_time:
                for period in class_time[ins]:
                    if time_period in class_time[ins][period]:
                        index = class_time[ins][period].index(time_period)
                        #class_time[ins][period].remove(time_period)
                        class_time[ins][period].pop(index)
                        found_period = period
                        found = True
                        break
            if found:
                # 检查午别是否为空，如果为空则删除午别
                if not class_time["default"][found_period]:
                    for ins in class_time:
                        del class_time[ins][found_period]
                    # 在 class_table 中删除对应的午别
                    for day in range(1, 8):
                        day_str = str(day)
                        for period in class_table[day_str]:
                            if found_period in period:
                                del period[found_period]
                        # 移除空字典
                        class_table[day_str] = [p for p in class_table[day_str] if p]
                else:
                    # 在 class_table 中删除对应的课程
                    for day in range(1, 8):
                        day_str = str(day)
                        for period in class_table[day_str]:
                            if found_period in period:
                                if len(period[found_period]) > index:
                                    del period[found_period][index]
                        # 移除空字典
                        class_table[day_str] = [p for p in class_table[day_str] if p]

            main.saves_to_json()
            self.TimeWidget.clearSelection()
            self.Time_Widget_update()
            self.add_name_box.clear()
            self.add_name_box.addItems(self.ap_list)
            if self.auto_update_Button.isChecked():
                self.set_table_update()
    def cancel_Widget(self):
        self.TimeWidget.clearSelection()
    def add_time(self):
        if self.from_time == "" or self.to_time == "":
            self.error("请先选择开始时间和结束时间","警告",False,True)
            return
        if self.from_time > self.to_time:
            self.error("开始时间不能大于结束时间","警告",False,True)
            return
        if self.from_time == self.to_time:
            self.error("开始时间不能等于结束时间","警告",False,True)
            return
        for i in range(1, 8):
            for item in class_table[str(i)]:
                if self.add_name in item:
                    item[self.add_name].append('未设置')
        
        # 去掉秒数并格式化时间段
        start_time_formatted = datetime.strptime(self.from_time, "%H:%M:%S").strftime("%H:%M")
        end_time_formatted = datetime.strptime(self.to_time, "%H:%M:%S").strftime("%H:%M")
        time_period = f"{start_time_formatted}-{end_time_formatted}"
        # 向“上午”键的值的末尾添加新的时间段
        for ins in class_time:
            class_time[ins][self.add_name].append(time_period)

        main.saves_to_json()
        self.Time_Widget_update()
        if self.auto_update_Button.isChecked():
            self.set_table_update()
        
    def Time_Widget_update(self):
        self.TimeWidget.clear()
        self.ap_list = []
        s = class_weekday
        zp = {"周一":"1","周二":"2","周三":"3","周四":"4","周五":"5","周六":"6","周日":"7"}
        if s == "通用":
            ins = "default"
        else:
            ins = zp[s]

        for i in class_time[ins]: # i是午别名字，class_time[i]是时间段
            self.ap_list.append(i)
            item = QListWidgetItem(i)
            item.setTextAlignment(Qt.AlignCenter)
            self.TimeWidget.addItem(item)
            for time in class_time[ins][i]:
                time_item = QListWidgetItem(time)
                time_item.setTextAlignment(Qt.AlignCenter)
                self.TimeWidget.addItem(time_item)
    def add_aptime(self):
        if self.name_box.currentIndex() == 3:
            name = self.name_edit.toPlainText()
        else:
            name = self.name_box.currentText()
        if not name:
            self.error("请先输入时间段","警告",False,True)
            return
        if name in self.ap_list:
            self.error("时间段已存在,请不要重复添加","警告",False,True)
            return
        for ins in class_time:
            class_time[ins][name] = ["00:00-00:01"]
        for i in range(1,8):
            class_table[str(i)].append({name:['未设置']})

        main.saves_to_json()
        
        self.Time_Widget_update()
        self.add_name_box.clear()
        self.add_name_box.addItems(self.ap_list)
        if self.auto_update_Button.isChecked():
            self.set_table_update()
    def name_box_changed(self):
        index = self.name_box.currentIndex()
        if index == 3:
            self.name_edit.show()
            #self.name_label.show()
        elif index == 0 or index == 1 or index == 2:
            self.name_edit.hide()
            #self.name_label.hide()
    def on_resize(self):
        # 重新平均设置列宽
        total_width = self.TableWidget.viewport().width() - 120 # 获取视口宽度
        column_width = total_width // 7  # 计算每列宽度
        for col in range(7):
            self.TableWidget.setColumnWidth(col+1, column_width)  # 设置每列宽度
        self.TableWidget.setColumnWidth(0, 120)  # 设置第一列宽度
        self.Table_Time.stop()


    def set_table_update(self,index=None):
        try:
            self.TableWidget.itemChanged.disconnect(self.table_update)
        except:
            pass
        self.TableWidget.clear()
        if index != None:
            if index == 0:
                done, ls = self.convert_table(class_table_a)
                self.widget_time = self.convert_time(class_time_a)
            else:
                done, ls = self.convert_table(class_table_b)
                self.widget_time = self.convert_time(class_time_b)
        else:
            done, ls = self.convert_table(class_table_a)
            self.widget_time = self.convert_time(class_time_a)

        self.TableWidget.setWordWrap(False)
        # 设置表格的行数和列数
        self.TableWidget.setRowCount(ls)
        self.TableWidget.setColumnCount(8)
        self.TableWidget.setHorizontalHeaderLabels(['时间','星期一','星期二','星期三','星期四','星期五','星期六','星期日'])
        for i in range(ls):
            item = QTableWidgetItem(self.widget_time[i])
            self.TableWidget.setItem(i, 0, item)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        for i, Info in enumerate(done):
            for j in range(7):
                item = QTableWidgetItem(Info[j])
                self.TableWidget.setItem(i, j+1, item)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)# 设置单元格文本居中对齐
        self.TableWidget.itemChanged.connect(self.table_update)
        try:
            self.up_Button.setText("成功!")
            QTimer.singleShot(800, lambda: self.up_Button.setText("刷新课表"))
        except:
            pass

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
    def convert_table(self,classt):
        # 将class_table转换为二维列表
        weeks = str(datetime.now().weekday() + 1)
        jies = []
        for week in range(1, 8):
            day = []
            for wu in range(len(classt[str(week)])):
                wus = list(classt[str(week)][wu].keys())[0]
                if classt[str(week)][wu][wus] == []:
                    for kong in range(len(class_time[weeks][list(classt[str(week)][wu].keys())[0]])):
                        day.append("")
                else:
                    for jie in range(len(classt[str(week)][wu][wus])):
                        day.append(classt[str(week)][wu][wus][jie])
            jies.append(day)
        done = [list(t) for t in list(zip(*jies))]# 使用zip函数转置列表,由于zip返回的是元组，如果需要列表，可以使用列表推导式转换
        return done,len(day)
    def convert_time(self,class_t):
        result = []
        for values in class_t["default"].values():
            result.extend(values)
        return result
    def choose_color(self,ty):
        color = QColorDialog.getColor()
        #color_rgba = color.getRgb()
        colors = [color.red(),color.green(),color.blue()]
        if color.isValid():
            if ty == "time":
                self.update_time(colors,"cl_time_TextColor")
            elif ty == "date":
                self.update_time(colors,"cl_date_TextColor")
            #self.update_time(colors,'cl_time_TextColor')
    def choose_font(self,ty):
        font, ok = QFontDialog.getFont()
        if ok:
            if ty == "time":
                self.update_time(font.family(),'fontname')
            elif ty == "date":
                self.update_time(font.family(),'cl_date_Typeface')

            #self.update_time(font.family(),'')
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
                config[choose] = str(value)
                # 将设置写入注册表
                reg.SetValueEx(registry_key, choose, 0, reg.REG_SZ, str(value))
                clock.update_settings(choose)
            except Exception as e:
                self.error(str(e))
        if choose == "fontSize" or choose == "x" or choose == "y":
            white_reg()
        if choose == "fontname":
            white_reg()
            self.Flyout(title="提示",content="重置成功！",target=self.default_time_font_PushButton)
        elif choose == "comboBox":
            if value == True:value = "置顶"
            else:value = "桌面"
            white_reg()
        elif choose == "Penetrate":
            value = str(value)
            white_reg()
            self.Flyout(title="提示",content=f"修改成功！重启后生效",target=self.CW7_onof_button)
        elif choose == "startup":
            if self.startup_program(value) == False:
                self.CW8_onof_button.setChecked(False)
        
        def white_reg_new():
            try:
                # 创建或打开注册表键
                registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
                # 获取当前设置的值
                config[choose] = str(value)
                # 将设置写入注册表
                reg.SetValueEx(registry_key, choose, 0, reg.REG_SZ, str(value))
                clock.update_settings(choose)
            except Exception as e:
                self.error(str(e))
        
        if choose == "cl_Switch" or choose == "cl_time_TextColor" or choose == "cl_date_TextColor" or choose == "cl_Transparent":
            white_reg_new()
        elif choose == "cl_date_Switch":
            white_reg_new()
        elif choose == "cl_date_mediate":
            white_reg_new()
        elif choose == "cl_date_TextSize":
            white_reg_new()
        elif choose == "cl_date_Typeface":
            white_reg_new()
            self.Flyout(title="提示",content="重置成功！",target=self.default_date_font_PushButton)
        elif choose == "cl_time_Switch":
            white_reg_new()
        elif choose == "cl_date_language":
            if value == 0:
                value = "zh-cn"
            elif value == 1:
                value = "en-us"
            white_reg_new()
        elif choose == "cl_time_Second":
            white_reg_new()
    def error(self,e,msg="错误",grades=False,vas=False):
        if grades:
            w = Dialog(msg, str(e)+"\n 此问题影响了程序运行，请重启本程序，给您带来不便，请谅解。", self)
            w.yesButton.setText("重启软件")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            if w.exec():
                self.close()
                restart_program()
                #theme_manager.themeListener.terminate()
                #theme_manager.themeListener.deleteLater()
                #QApplication.quit()
        else:
            if vas:
                w = MessageBox(msg, e, self)
                w.yesButton.setText("好")
                w.cancelButton.hide()
                w.buttonLayout.insertStretch(1)
                if w.exec():pass
            else:
                w = MessageBox(msg, e, self)
                w.yesButton.setText("重启软件")
                w.cancelButton.setText("忽略")
                if w.exec():
                    self.close()
                    restart_program()
                    #theme_manager.themeListener.terminate()
                    #theme_manager.themeListener.deleteLater()
                    #QApplication.quit()
                else:pass
    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(f'{RES}ico/LINGYUN.ico'))
        self.setWindowTitle('凌云班级组件 - 设置 - v' + Version + " " + config.get("setting_title"))
        self.navigationInterface.setExpandWidth(200)
        self.navigationInterface.setCollapsible(False)
    def closeEvent(self, event: QCloseEvent) -> None:
        #lists['close_sets'] = True
        self.CardWidget_yun.hide()
        self.CardWidget_equipment.hide()
        self.CardWidget_https.hide()
        self.CardWidget_timeleg.hide()
        self.CardWidget_json.hide()
        self.CardWidget_xg.hide()

        self.yun_PasswordLineEdit.clear()

        '''self.hide()
        event.ignore()'''

    def startup_program(self, zt, program_path=script_full_path, program_name="LingYun_Class_Widgets"):
        try:
            # 打开注册表项，为当前用户设置开机启动
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
            # 设置程序开机启动
            program_path = f'"{script_full_path}"' # remove_last_folder(script_dir)
            print(f"设置开机启动路径: {program_path}")
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
    def read_startup_program(self,program_name="LingYun_Class_Widgets"):
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
    def json_to_yaml(self,json_path, yaml_path):
        with open(json_path, 'r', encoding='utf-8') as jf:
            data = json.load(jf)

        result = {
            'version': 1,
            'subjects': [],
            'schedules': []
        }

        subjects = set()
        for day_data in [data[1], data[2]]: 
            for day_num, day_schedule in day_data.items():
                for period in day_schedule:
                    for time_period, courses in period.items():
                        subjects.update(courses)
        
        
        for subject in subjects:
            if subject:   
                result['subjects'].append({
                    'name': subject,
                    'simplified_name': subject[0],   
                    'teacher': '',
                    'room': ''
                })

        

        for day_num, day_schedule in data[1].items():
            schedule = {
                'name': f'星期{day_num}-单周',
                'enable_day': int(day_num),
                'weeks': 'odd',
                'classes': []
            }
            
            section_counter = 1
            for period_schedule in day_schedule:
                for period, courses in period_schedule.items():
                    if isinstance(courses, list):   
                        for i, subject in enumerate(courses):
                            time_slot = data[3][day_num][period][i].split('-')
                            schedule['classes'].append({
                                'subject': subject if subject else None,   
                                'start_time': f"{time_slot[0]}:00",
                                'end_time': f"{time_slot[1]}:00",
                                'room': f'{day_num}0{section_counter}'
                            })
                            section_counter += 1
            
            result['schedules'].append(schedule)
        

        for day_num, day_schedule in data[2].items():
            schedule = {
                'name': f'星期{day_num}-双周',
                'enable_day': int(day_num),
                'weeks': 'even',
                'classes': []
            }
            
            section_counter = 1
            
            for period_schedule in day_schedule:
                for period, courses in period_schedule.items():
                    if isinstance(courses, list):   
                        for i, subject in enumerate(courses):
                            time_slot = data[4][day_num][period][i].split('-')
                            schedule['classes'].append({
                                'subject': subject if subject else None,   
                                'start_time': f"{time_slot[0]}:00",
                                'end_time': f"{time_slot[1]}:00",
                                'room': f'{day_num}0{section_counter}'
                            })
                            section_counter += 1
            
            result['schedules'].append(schedule)
        
        with open(yaml_path, 'w', encoding='utf-8') as yf:
            yaml.dump(result, yf, allow_unicode=True, sort_keys=False)

    def yaml_to_json(self,yaml_path, json_path):
        with open(yaml_path, 'r', encoding='utf-8') as yf:
            data = yaml.safe_load(yf)

        
        result = [
            [],   
            {"1": []},  # default data for Monday
            {},   
            {"1": {}},  # default time slots for Monday
            {},   
            {
            "1": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            },
            "2": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            },
            "3": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            },
            "4": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            },
            "5": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            },
            "6": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            },
            "7": {
                "擦黑板": [
                    ""
                ],
                "倒垃圾": [
                    ""
                ],
                "班级扫地": [
                    "",
                    ""
                ],
                "班级拖地": [
                    "",
                    ""
                ],
                "走廊打扫": [
                    ""
                ],
                "包干区": [
                    "",
                    ""
                ]
            }
        }

        ]
        
        
        for day in data['schedules']:
            day_num = day['enable_day']
            week_type = day['weeks']

            day_data = []
            time_slots = {}
            
            
            time_periods = set()
            for cls in day['classes']:
                start_hour = int(cls['start_time'].split(':')[0])
                period = "晚上" if start_hour >= 18 else ("下午" if start_hour >= 12 else "上午")
                time_periods.add(period)
            
            
            for period in sorted(time_periods):
                day_data.append({period: []})
                time_slots[period] = []
            
            sorted_classes = sorted(day['classes'], key=lambda x: x['start_time'])
            
            def parse_time(time_str):
                formats = ["%H:%M:%S", "%H:%M"] 
                for fmt in formats:
                    try:
                        parsed_time = datetime.strptime(time_str, fmt)
                        return parsed_time.strftime("%H:%M")  # 统一返回 "时:分" 格式
                    except ValueError:
                        continue            

            for cls in sorted_classes:
                #start = parse_time(cls['start_time'])
                #end = parse_time(cls['end_time'])

                start = datetime.strptime(cls['start_time'], "%H:%M:%S").strftime("%H:%M")
                end = datetime.strptime(cls['end_time'], "%H:%M:%S").strftime("%H:%M")
                time_str = f"{start}-{end}"
                
                
                start_hour = int(start.split(':')[0])
                time_period = "晚上" if start_hour >= 18 else ("下午" if start_hour >= 12 else "上午")
                
                subject = cls['subject'] if cls['subject'] is not None else ""   


                for item in day_data:
                    if time_period in item:
                        item[time_period].append(subject)
                        break
                
                time_slots[time_period].append(time_str)


            if day_num == 1:
                result[3]["default"] = time_slots.copy()
                result[4]["default"] = time_slots.copy()

            if week_type == 'odd':
                result[1][str(day_num)] = day_data
                result[3][str(day_num)] = time_slots
            elif week_type == 'even':
                result[2][str(day_num)] = day_data
                result[4][str(day_num)] = time_slots
            elif week_type == 'all':
                result[1][str(day_num)] = day_data
                result[2][str(day_num)] = day_data
                result[3][str(day_num)] = time_slots
                result[4][str(day_num)] = time_slots

        
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(result, jf, ensure_ascii=False, indent=2)
    def inex(self,value):
        if value == "import":
            file_path, _ = QFileDialog.getOpenFileName(self, '选择凌云班级组件的课表文件', '', 'JSON文件(*.json)')
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)

                if len(data) == 6:
                    if isinstance(data[0], list) and isinstance(data[1], dict) and isinstance(data[2], dict) and isinstance(data[3], dict) and isinstance(data[4], dict) and isinstance(data[5], dict):
                        destination_dir = f'{USER_RES}jsons'
                        os.makedirs(destination_dir, exist_ok=True)
                        file_name = os.path.basename(file_path)
                        destination_path = os.path.join(destination_dir, file_name)
                        shutil.copy(file_path, destination_path)
                        self.dp_chowidgets_box.currentIndexChanged.disconnect()
                        self.update_file()
                        self.Flyout(title="提示",content="导入成功！选择后即可使用。",target=self.dp_import_button)
                        self.dp_chowidgets_box.currentIndexChanged.connect(lambda value:self.update_dp(value,'dp_widgets'))
                else:
                    self.error("您导入的可能不是凌云班级组件生成的课表文件。","导入失败",False,True)
        elif value == "export":
            file_path, _ = QFileDialog.getSaveFileName(self, '保存当前课表数据', '', 'JSON文件(*.json)')
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as jf:
                    json.dump(class_all, jf, ensure_ascii=False, indent=2)
                    
                    self.Flyout(title="提示",content=f"导出成功！\n已保存在{file_path}。",target=self.dp_export_button)
        elif value == "openwidgets":
            os.startfile(f'{USER_RES}jsons')
        elif value == "open_Profile":
            os.startfile(USER_RES)
        elif value == "dp_widgets":
            self.error("重启软件后生效。","提示",False,False)
        elif value == "exescs":
            file_path, _ = QFileDialog.getSaveFileName(self, '保存为CSES通用格式', '', 'CSES文件(*.yaml)')
            if file_path:
                self.json_to_yaml(f'{USER_RES}jsons/{config.get("dp_widgets")}',file_path)
                self.Flyout(title="转换并导出成功！",content=f"\n已保存在{file_path}。",target=self.dp_exescs_button)
        elif value == "imescs":
            if self.lcw_Group.checkedButton() == None:
                self.error("即这个CSES课表从哪个课表软件导出的。","请先选择一个导出源",False,True)
                return
            flag = True
            file_path, _ = QFileDialog.getOpenFileName(self, '选择CSES通用格式文件', '', 'CSES文件(*.yaml *.yml)')

            if file_path:
                if self.lcw_Group.checkedButton().text() == "凌云班级组件":
                    name = os.path.basename(file_path).split('.')[0]
                    try:
                        self.yaml_to_json(file_path, f'{USER_RES}jsons/{name}.json')
                    except Exception as e:
                        error = e
                        flag = False
                elif self.lcw_Group.checkedButton().text() == "Class Widgets":
                    name = os.path.basename(file_path).split('.')[0]
                    try:
                        self.yaml_to_json_class_widgets(file_path, f'{USER_RES}jsons/{name}.json')
                    except Exception as e:
                        error = e
                        flag = False
                if flag == False:
                    self.error(f"您可能选择了错误的导出源，或者目前还未适配该源。\n建议向开发者反馈以获得帮助。\n以下为错误信息：\n{error}","转换失败",False,True)
                else:

                    self.dp_chowidgets_box.currentIndexChanged.disconnect()
                    self.update_file()
                    self.Flyout(title="提示",content="导入成功！选择后即可使用。",target=self.dp_imescs_button)
                    self.dp_chowidgets_box.currentIndexChanged.connect(lambda value:self.update_dp(value,'dp_widgets'))
    def yaml_to_json_class_widgets(self,yaml_path, json_path):
        with open(yaml_path, 'r', encoding='utf-8') as yf:
            yaml_data = yaml.safe_load(yf)

        result = [[],{},{},{},{},{}]

        time_slots = {}
        period_info = {}

        if 'schedules' in yaml_data:
            for schedule in yaml_data['schedules']:
                
                period = schedule['name'].split('_')[0]
                
                
                if schedule.get('classes'):
                    start_time = schedule['classes'][0]['start_time']
                    if period not in period_info or start_time < period_info[period]['earliest_time']:
                        period_info[period] = {
                            'earliest_time': start_time,
                            'name': period
                        }
                
                
                if period not in time_slots:
                    time_slots[period] = []
                    
                
                for cls in schedule.get('classes', []):
                    time_str = f"{cls['start_time']}-{cls['end_time']}"
                    if time_str not in time_slots[period]:
                        time_slots[period].append(time_str)
        
        
        sorted_periods = sorted(period_info.values(), key=lambda x: x['earliest_time'])
        period_names = [p['name'] for p in sorted_periods]
        
        
        for day in range(1, 8):
            day_str = str(day)
            result[1][day_str] = []
            result[2][day_str] = []
            for period in period_names:
                result[1][day_str].append({period: []})
                result[2][day_str].append({period: []})
            result[3][day_str] = {}
            result[4][day_str] = {}
            for period in period_names:
                result[3][day_str][period] = time_slots.get(period, [""])
                result[4][day_str][period] = time_slots.get(period, [""])
            result[5][day_str] = {
                "擦黑板": [""],
                "倒垃圾": [""],
                "班级扫地": ["", ""],
                "班级拖地": ["", ""],
                "走廊打扫": [""],
                "包干区": ["", ""]
            }
            if 'duty' in yaml_data and day_str in yaml_data['duty']:
                for duty_type, names in yaml_data['duty'][day_str].items():
                    if duty_type in result[5][day_str]:
                        result[5][day_str][duty_type] = names if isinstance(names, list) else [names]

            for schedule in yaml_data.get('schedules', []):
                if str(schedule['enable_day']) == day_str and 'duty' in schedule:
                    for duty_type, names in schedule['duty'].items():
                        if duty_type in result[5][day_str]:
                            if isinstance(names, list):
                                result[5][day_str][duty_type] = names
                            else:
                                result[5][day_str][duty_type] = [names]

        if 'schedules' in yaml_data:
            schedule_groups = {}
            for schedule in yaml_data['schedules']:
                day_str = str(schedule['enable_day'])
                week_type = schedule.get('weeks', 'all')
                key = (day_str, week_type)
                if key not in schedule_groups:
                    schedule_groups[key] = []
                schedule_groups[key].append(schedule)

            for day in range(1, 8):
                day_str = str(day)
                result[1][day_str] = []
                result[2][day_str] = []
                for period in period_names:
                    result[1][day_str].append({period: []})
                    result[2][day_str].append({period: []})

            for (day_str, week_type), schedules in schedule_groups.items():
                for schedule in schedules:
                    for class_info in schedule.get('classes', []):
                        period = schedule['name'].split('_')[0]
                        subject = class_info.get('subject', '')
                        time_str = f"{class_info['start_time']}-{class_info['end_time']}"
                        targets = []
                        if week_type == 'all':
                            targets = [result[1], result[2]]
                        elif week_type == 'odd':
                            targets = [result[1]]
                        else:   
                            targets = [result[2]]
                        for target in targets:
                            period_obj = None
                            for item in target[day_str]:
                                if period in item:
                                    period_obj = item
                                    break
                            
                            if period_obj:
                                required_length = len(time_slots.get(period, []))
                                while len(period_obj[period]) < required_length:
                                    period_obj[period].append("")
                                if period in time_slots and time_str in time_slots[period]:
                                    idx = time_slots[period].index(time_str)
                                    if idx < len(period_obj[period]):
                                        period_obj[period][idx] = subject
                if day_str == "1":
                    result[3]["default"] = time_slots.copy()
                    result[4]["default"] = time_slots.copy()
        try:
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(result, jf, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入文件时出错: {str(e)}")
    def update_file(self):
        self.dp_chowidgets_box.clear()
        all_widgets = os.listdir(f'{USER_RES}jsons/') 
        json_widgets = [f for f in all_widgets if f.endswith('.json')]
        self.json_widgets = [file.replace('.json', '') for file in json_widgets]  # 去掉文件扩展名
        self.dp_chowidgets_box.addItems(self.json_widgets)
        self.dp_chowidgets_box.setCurrentIndex(self.json_widgets.index(config.get("dp_widgets").split(".")[0]))

# 息屏组件
class BlackScreen(QWidget):
    def __init__(self, notime):
        super().__init__()
        self.nested_window = DP_Comonent
        self.nested_window2 = clock
        self.initUI(notime)

    def initUI(self, notime):
        global DP_Comonent
        #self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        w_width = screen_geometry.width()  # 屏幕宽度
        w_height = screen_geometry.height()  # 屏幕高度

        if notime == True:
            DP_Comonent.dc_dp("notime")
        else:
            DP_Comonent.dc_dp("open")
        
        # 设置窗口标题和大小
        self.setWindowTitle('LingYun Class Widgets Black Screen')
        self.setGeometry(0, 0, w_width, w_height)
        self.setStyleSheet("""QWidget {background-color: black;}""")

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建容器区域用于嵌套窗口（使用绝对定位）
        self.container_widget = QWidget(self)
        self.container_widget.setStyleSheet("background-color: transparent; border: none;")
        self.container_widget.resize(w_width, w_height)

        self.container_widget2 = QWidget(self)
        self.container_widget2.setStyleSheet("background-color: transparent; border: none;")
        self.container_widget2.resize(w_width, w_height)    

        '''
        # 日期和时间标签
        self.date_label = QLabel(self)
        self.date_label.setAlignment(Qt.AlignLeft)
        
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignLeft)
        
        # 设置字体
        self.time_font = self.font_file(f"{RES}MiSans-Bold.ttf", config['fontname'], config['fontSize'])
        self.time_label.setFont(self.time_font)
        self.time_label.setStyleSheet(f'color:white;')
        self.time_label.setAttribute(Qt.WA_TranslucentBackground)


        self.date_font = self.font_file(f"{RES}MiSans-Bold.ttf", config.get("cl_date_Typeface"), config.get("cl_date_TextSize"))
        self.date_label.setFont(self.date_font)
        self.date_label.setStyleSheet(f'color:white;')
        self.date_label.setAttribute(Qt.WA_TranslucentBackground)

        # 预计算并设置固定宽度
        #self.setup_fixed_sizes()  
        self.time_label.hide()
        self.date_label.hide()    
        '''


        # 创建退出按钮
        self.button = TransparentPushButton(FluentIcon.EMBED.icon(color='#FFFFFF'), "     退出", self)
        self.button.setStyleSheet("""color:#ffffff;""")
        self.button.setGeometry(QRect(w_width-150, w_height-120, 50, 50))      
    

        if not notime:
            #self.time_label.show()
            self.nest_window()
            self.nest_window2()
        #else:
        #    self.time_label.hide()
            
        # 初始化日期和时间显示
        #self.uptime()

        # 保存原始窗口的位置和大小，用于分离后恢复
        self.original_geometry = None
        self.nested_position = None  # 保存嵌套前的位置
        self.original_geometry2 = None
        self.nested_position2 = None  # 保存嵌套前的位置
        
        # 定时器更新时钟
        #clock.hide()
        #self.timer = QTimer(self)
        #self.timer.timeout.connect(self.uptime)
        #self.timer.start(1000)

        # 检测时间开启倒计时
        self.count_timer = QTimer(self)
        self.count_timer.timeout.connect(self.Frame_countdown)
        self.count_timer.start(1000)


        # 连接按钮点击事件
        self.button.clicked.connect(self.up_close)


    def Frame_countdown(self):
        if config.get("dp_display_count") == "True":
            if self.isVisible() and self.isActiveWindow():
                if DP_Comonent.countdown == f"00:{str(int(config.get('dp_count'))+1)}":
                    self.countdown_window = LNC.CountdownWindow(
                        countdown=int(config.get('dp_count'))+1,
                        font=config.get("dp_count_font"))
                    self.countdown_window.start_countdown()
                    self.countdown_window.show()

    def up_close(self):
        DP_Comonent.dc_dp("close")
        self.detach_window()
        self.detach_window2()

        if config.get('cl_Switch') == "True":
            clock.show()
        self.destroy()
        
    def nest_window(self):
        """将指定窗口嵌套到容器中，保持原x、y坐标不变"""
        if self.nested_window and self.nested_window.parent() is None:
            # 保存原始窗口的位置和大小
            self.original_geometry = self.nested_window.geometry()
            
            # 计算嵌套窗口在容器中的相对位置
            # 保持原窗口的x、y坐标相对于屏幕不变
            global_pos = self.nested_window.pos()
            container_pos = self.container_widget.mapFromGlobal(global_pos)
            self.nested_position = container_pos
            
            # 将窗口添加到容器中（使用绝对定位）
            self.nested_window.setParent(self.container_widget)
            self.nested_window.move(container_pos)
            self.nested_window.show()

    def nest_window2(self):
        """将指定窗口嵌套到容器中，保持原x、y坐标不变"""
        if self.nested_window2 and self.nested_window2.parent() is None:
            # 保存原始窗口的位置和大小
            self.original_geometry2 = self.nested_window2.geometry()
            
            # 计算嵌套窗口在容器中的相对位置
            # 保持原窗口的x、y坐标相对于屏幕不变
            global_pos = self.nested_window2.pos()
            container_pos = self.container_widget2.mapFromGlobal(global_pos)
            self.nested_position2 = container_pos
            
            # 将窗口添加到容器中（使用绝对定位）
            self.nested_window2.setParent(self.container_widget2)
            self.nested_window2.move(container_pos)
            self.nested_window2.show()

            self.nested_window2.time_label.setStyleSheet(f'color: rgba(255,255,255,255);')
            self.nested_window2.date_label.setStyleSheet(f'color: rgba(255,255,255,255);')

    def detach_window(self):
        """从容器中分离窗口，恢复为独立窗口"""
        if self.nested_window and self.nested_window.parent() == self.container_widget:
            # 计算窗口在屏幕中的绝对位置
            if self.nested_position:
                global_pos = self.container_widget.mapToGlobal(self.nested_position)
            else:
                global_pos = self.nested_window.pos()
            
            # 设置父窗口为None
            self.nested_window.setParent(None)

            self.nested_window.setWindowFlags(self.nested_window.windowFlags() | Qt.Window | Qt.Tool)
            
            # 恢复原始窗口的位置和大小
            if self.original_geometry:
                self.nested_window.setGeometry(
                    global_pos.x(), 
                    global_pos.y(), 
                    self.original_geometry.width(), 
                    self.original_geometry.height()
                )
            else:
                self.nested_window.move(global_pos)
            
            # 显示窗口
            self.nested_window.show()

    def detach_window2(self):
        """从容器中分离窗口，恢复为独立窗口"""
        if self.nested_window2 and self.nested_window2.parent() == self.container_widget2:
            # 计算窗口在屏幕中的绝对位置
            if self.nested_position2:
                global_pos = self.container_widget2.mapToGlobal(self.nested_position2)
            else:
                global_pos = self.nested_window2.pos()
            
            # 设置父窗口为None
            self.nested_window2.setParent(None)

            self.nested_window2.setWindowFlags(self.nested_window2.windowFlags() | Qt.Window | Qt.Tool)
            
            # 恢复原始窗口的位置和大小
            if self.original_geometry2:
                self.nested_window2.setGeometry(
                    global_pos.x(), 
                    global_pos.y(), 
                    self.original_geometry2.width(), 
                    self.original_geometry2.height()
                )
            else:
                self.nested_window2.move(global_pos)
            
            # 显示窗口
            self.nested_window2.show()

            time_rgba = ast.literal_eval(config.get("cl_time_TextColor"))
            date_rgba = ast.literal_eval(config.get("cl_date_TextColor"))            
            self.nested_window2.time_label.setStyleSheet(f'color: rgba({time_rgba[0]},{time_rgba[1]},{time_rgba[2]},{int(config.get("cl_Transparent"))});')
            self.nested_window2.date_label.setStyleSheet(f'color: rgba({date_rgba[0]},{date_rgba[1]},{date_rgba[2]},{int(config.get("cl_Transparent"))});')

    def closeEvent(self, event: QCloseEvent) -> None:
        self.up_close()


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
'''
class Desktop_Component(QWidget):
    def __init__(self, ):
        super().__init__()
        self.warn_function = ThrottledFunction(self.warning, 5)
        self.dc = False # 息屏标志
        self.initUI()
    def initUI(self):
        global display_x, display_y
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度
        
        self.flags = Qt.SplashScreen | Qt.FramelessWindowHint | Qt.Tool
        if config.get('dp_Pin') == 'True':
            self.flags |= Qt.WindowStaysOnTopHint
        elif config.get('dp_Pin') == 'Under':
            self.flags |= Qt.WindowDoesNotAcceptFocus
        self.setWindowFlags(self.flags)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.move(display_x,12)
        f = self.uic_ui()
        if f == False:
            return
        
        self.class_time = QTimer(self)

        self.countdown = ""

        self.updown = False # false下课 ture上课
        self.timess = QTimer(self)
         
        QTimer.singleShot(1000, self.alert) # 倒计时模块
        QTimer.singleShot(1000, self.update_Widgets)
        QTimer.singleShot(1000, self.update_duty)

        #窗口在屏幕的位置初始化
        self.DP_x = display_x - int(config.get("dp_display_edge"))
        self.DP_y = 12
        self.animation_i = display_x - 260
        self.animations()

        if config.get('dp_Switch') == "True":
            self.show()
            self.animation_show.start()
            self.animation_rect_show.start()
    def showEvent(self, event):
        self.lower()

    def animations(self):
        # 从隐藏显示+淡入：animation_show,animation_rect_show
        self.animation_show = QPropertyAnimation(self, b'windowOpacity')
        self.animation_show.setDuration(400)
        self.animation_show.setStartValue(0)
        self.animation_show.setEndValue(1)
        self.animation_show.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rect_show = QPropertyAnimation(self, b'geometry')
        self.animation_rect_show.setDuration(450)
        self.animation_rect_show.setStartValue(QRect(display_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_show.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_show.setEasingCurve(QEasingCurve.InOutCirc)

        # 从显示隐藏+淡出：animation_hide,animation_rect_hide
        self.animation_hide = QPropertyAnimation(self, b'windowOpacity')
        self.animation_hide.setDuration(600)
        self.animation_hide.setStartValue(1)
        self.animation_hide.setEndValue(0)
        self.animation_hide.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rect_hide = QPropertyAnimation(self, b'geometry')
        self.animation_rect_hide.setDuration(450)
        self.animation_rect_hide.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_hide.setEndValue(QRect(display_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_hide.setEasingCurve(QEasingCurve.InOutCirc)

        # 从显示到贴屏幕边缘：animation_rect_shrink
        self.animation_rect_shrink = QPropertyAnimation(self, b'geometry')
        self.animation_rect_shrink.setDuration(450)
        self.animation_rect_shrink.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_shrink.setEndValue(QRect(display_x-35, self.DP_y, self.width(), self.height()))
        self.animation_rect_shrink.setEasingCurve(QEasingCurve.InOutCirc)

        # 从贴屏幕边缘到显示：animation_rect_expand
        self.animation_rect_expand = QPropertyAnimation(self, b'geometry')
        self.animation_rect_expand.setDuration(450)
        self.animation_rect_expand.setStartValue(QRect(display_x-35, self.DP_y, self.width(), self.height()))
        self.animation_rect_expand.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_expand.setEasingCurve(QEasingCurve.InOutCirc)
    def setRoundedCorners(self, radius):
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())  # 使用QRectF而不是QRect
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    def uic_ui(self):
        # 检查ui文件是否存在
        if os.path.exists(f"{RES}ui/dp/{config.get('dp_choose')}"):
            self.classes = uic.loadUi(f"{RES}ui/dp/{config.get('dp_choose')}",self)
        else:
            files = glob.glob(os.path.join(f"{RES}ui\\dp\\", '*.ui'))
            if files:
                self.classes = uic.loadUi(files[0],self)
                config.set('dp_choose', os.path.basename(files[0]))
            else:
                self.close()
                return False
        self.classes.setObjectName("classes")
        config["dp_display_edge"] = self.classes.width()


        self.dp_info = {}
        if check_component_in_ui(f"{RES}ui/dp/{config.get('dp_choose')}", "ui_info"):
            # 为新版本ui
            self.ui_info = self.findChild(QLabel, "ui_info")
            self.dp_info = ast.literal_eval(self.ui_info.text())

            self.ui_info.hide()

        # 当前课程
        self.lingyun_Title = self.findChild(QLabel,"lingyun_Title")
        self.lingyun_class = self.findChild(TitleLabel,"lingyun_class")
        self.lingyun_background = self.findChild(QLabel,"lingyun_background")

        self.lingyun_class.installEventFilter(self)
        self.lingyun_Title.installEventFilter(self)
        self.lingyun_background.installEventFilter(self)

        # 倒计时
        self.lingyun_Title_2 = self.findChild(QLabel,"lingyun_Title_2")
        self.lingyun_background_2 = self.findChild(QLabel,"lingyun_background_2")
        self.lingyun_down = self.findChild(TitleLabel,"lingyun_down")
        self.lingyun_Bar = self.findChild(ProgressBar,"lingyun_Bar")
        self.lingyun_Bar.setRange(0, 100)
        self.lingyun_Bar.setCustomBarColor(QColor(0, 0, 255), QColor(0, 255, 0))

        self.lingyun_down.installEventFilter(self)
        self.lingyun_background_2.installEventFilter(self)
        self.lingyun_Title_2.installEventFilter(self)

        # 今日课程
        self.todayclass_Title = self.findChild(QLabel,"todayclass_Title")
        self.Widgets_ORD = self.findChild(StrongBodyLabel,"class_ORD")
        self.Widgets = self.findChild(StrongBodyLabel,"class_widget")
        self.todayclass_background = self.findChild(QLabel,"todayclass_background")

        self.todayclass_Title.installEventFilter(self)
        self.Widgets_ORD.installEventFilter(self)
        self.Widgets.installEventFilter(self)
        self.todayclass_background.installEventFilter(self)

        # 值日生组件
        self.duty_background = self.findChild(QLabel,"duty_background")
        self.duty_Title = self.findChild(QLabel,"duty_Title")
        self.duty_project_widget = self.findChild(StrongBodyLabel,"duty_project_widget")
        self.duty_name_widget = self.findChild(StrongBodyLabel,"duty_name_widget")

        self.duty_Title.installEventFilter(self)
        self.duty_project_widget.installEventFilter(self)
        self.duty_name_widget.installEventFilter(self)
        self.duty_background.installEventFilter(self)

        if config.get('dp_duty') == 'False':
            self.duty_background.hide()
            self.duty_Title.hide()
            self.duty_project_widget.hide()
            self.duty_name_widget.hide()

        self.click_timer = QTimer(self)
        self.click_timer.setInterval(200)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.on_single_click)
        self.press_position = QPoint()
        self.waiting_for_double_click = False  # 等待双击事件标志
        self.touch_tolerance = 500  # 触摸容差


        self.TOPIC()
        font_name = self.font_files(f"{RES}MiSans-Bold.ttf",config.get("dp_Typeface"))
        font = QFont(font_name, 16)
        self.Widgets_ORD.setFont(font)
        self.Widgets_ORD.setIndent(8)
        self.Widgets.setFont(font)
        self.Widgets.setIndent(8)
        self.duty_project_widget.setFont(font)
        self.duty_project_widget.setIndent(8)
        self.duty_name_widget.setFont(font)
        self.duty_name_widget.setIndent(8)
        font = QFont(font_name,21)
        font.setWeight(QFont.Bold)
        self.lingyun_down.setFont(font)

        font = QFont(font_name,14)
        font.setWeight(QFont.Bold)
        font = QFont(font_name,21)
        font.setWeight(QFont.Bold)
        self.lingyun_class.setFont(font)


        self.cols = [0,0,1,0,0]
        self.col = ["240","190","130","110",9]
        
        self.up_col = QTimer(self)
        self.up_col.timeout.connect(self.update_color)
        self.up_col.start(20)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.press_position = event.pos()
            self.pressed_button = event.button()
            
        elif event.type() == QEvent.MouseButtonRelease:
            if (event.pos() - self.press_position).manhattanLength() <= self.touch_tolerance:
                if event.button() == Qt.LeftButton:
                    self.on_single_click()
                elif event.button() == Qt.RightButton:
                    self.on_double_click(source)
            return super().eventFilter(source, event)
        
        # 忽略双击事件
        elif event.type() == QEvent.MouseButtonDblClick:
            return True
        
        return super().eventFilter(source, event)
    def on_single_click(self):
        # 获取窗口的坐标位置

        if self.dc or config.get('dp_Pin') == 'Under':
            return
        window_pos = self.frameGeometry().topLeft()
        if window_pos.x() == self.DP_x:
            self.animation_rect_shrink.start()
        elif window_pos.x() == display_x-35:
            self.animation_rect_expand.start()
    
    def on_double_click(self, source):
        global settings_window , display_x , display_y, tops
        flag = "0"
        if source == self.lingyun_class or source == self.lingyun_Title or source == self.lingyun_background:
            #当前课程
            flag = config.get("dp_Curriculum_ramp_action")
        elif source == self.lingyun_down or source == self.lingyun_background_2 or source == self.lingyun_Title_2:
            #倒计时
            flag = config.get("dp_countdown_action")
        elif source == self.todayclass_Title or source == self.todayclass_background or source == self.Widgets_ORD or source == self.Widgets:
            #今日课程
            flag = config.get("dp_todayclass_action")
        elif source == self.duty_Title or source == self.duty_project_widget or source == self.duty_name_widget or source == self.duty_background:
            # 值日生
            flag = config.get("dp_duty_action")
        if flag == "1":
            tops.setting_show()
            settings_window.switchTo(settings_window.duty)
        elif flag == "2":
            tops.setting_show()
            settings_window.switchTo(settings_window.classes)
        elif flag == "3":
            tops.setting_show()
            settings_window.switchTo(settings_window.classes_time)

    def update_ui(self,value,choose):
        if choose == "dp_Switch":
            if value:
                config['dp_Switch'] = "True"
                self.show()
                self.animation_show.start()
                self.animation_rect_show.start()
            else:
                config['dp_Switch'] = "False"
                self.animation_hide.start()
                self.animation_rect_hide.start()

                #self.hide()
        elif choose == "dp_Pin":

            if value == "True":
                if not (self.flags & Qt.WindowStaysOnTopHint):
                    self.flags |= Qt.WindowStaysOnTopHint
                if self.flags & Qt.WindowDoesNotAcceptFocus:
                    self.flags &= ~Qt.WindowDoesNotAcceptFocus
                self.setWindowFlags(self.flags)
            elif value == "False":
                if self.flags & Qt.WindowStaysOnTopHint:
                    self.flags &= ~Qt.WindowStaysOnTopHint
                if self.flags & Qt.WindowDoesNotAcceptFocus:
                    self.flags &= ~Qt.WindowDoesNotAcceptFocus
                self.setWindowFlags(self.flags)
            elif value == "Under":
                if not(self.flags & Qt.WindowStaysOnTopHint):
                    self.flags &= ~Qt.WindowStaysOnTopHint
                if not(self.flags & Qt.WindowDoesNotAcceptFocus):
                    self.flags |= Qt.WindowDoesNotAcceptFocus
                self.setWindowFlags(self.flags)
                window_pos = self.frameGeometry().topLeft()
                if window_pos.x() == display_x-35:
                    QTimer.singleShot(500, self.animation_rect_expand.start)
            if config.get("dp_Switch"):
                self.show()
        elif choose == "dp_Typeface":
            config["dp_Typeface"] = str(value)
            font_name = self.font_files(f"{RES}MiSans-Bold.ttf",config.get("dp_Typeface"))
            font = QFont(font_name, 16)
            #font.setWeight(QFont.Bold)
            self.Widgets_ORD.setFont(font)
            self.Widgets_ORD.setIndent(8)
            self.Widgets.setFont(font)
            self.Widgets.setIndent(8)
            font = QFont(font_name,21)
            font.setWeight(QFont.Bold)
            self.lingyun_down.setFont(font)

            font = QFont(font_name,14)
            font.setWeight(QFont.Bold)

            font = QFont(font_name,21)
            font.setWeight(QFont.Bold)
            self.lingyun_class.setFont(font)
        elif choose == "dp_Bell":
            config['dp_Bell'] = str(value)
        elif choose == "dp_Sysvolume":
            config['dp_Sysvolume'] = str(value)
        elif choose == "dp_Sysvolume_value":
            config['dp_Sysvolume_value'] = str(value)
        elif choose == "dp_Curriculum_ramp":
            config['dp_Curriculum_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_Countdown_ramp":
            config['dp_Countdown_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_Countdown_Bar_color":
            config['dp_Countdown_Bar_color'] = str(value)
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_Bar_color")), QColor(0, 255, 0))
        elif choose == "dp_Countdown_Bar_school_lag":
            config['dp_Countdown_Bar_school_lag'] = str(value)
        elif choose == "dp_Course_ramp":
            config['dp_Course_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_drup_ramp":
            #config['dp_drup_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_duty":
            if config['dp_duty'] == "False":
                self.duty_background.hide()
                self.duty_Title.hide()
                self.duty_project_widget.hide()
                self.duty_name_widget.hide()
            else:
                self.duty_background.show()
                self.duty_Title.show()
                self.duty_project_widget.show()
                self.duty_name_widget.show()
        elif choose == "dp_display_edge":
            pass
            #self.DP_x = display_x - int(config.get("dp_display_edge"))
    def dc_dp(self,event):
        if event == "open":
            self.dc = True
            #self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            if config.get("dp_xiping") == "True":
                self.show()
            else:
                self.hide()
            window_pos = self.frameGeometry().topLeft()
            if window_pos.x() == display_x-35:
                QTimer.singleShot(500, self.animation_rect_expand.start)
            self.TOPIC()
            self.lingyun_down.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.lingyun_class.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.Widgets_ORD.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.Widgets.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.duty_name_widget.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.duty_project_widget.setStyleSheet("color: rgba(255, 255, 255, 255)")

        elif event == "notime":
            self.hide()

        else:
            self.dc = False
            self.TOPIC()
            self.update_color()
            if config['dp_Pin'] == "False":
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.lingyun_down.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.lingyun_class.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.Widgets_ORD.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.Widgets.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.duty_name_widget.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.duty_project_widget.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.show()
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
    def update_color(self):
        if self.dc:
            if self.cols[4] == 0:
                if self.col[4] < -120:
                    self.cols[4] = 1
                self.col[4] = self.col[4]-5
            else:
                if self.col[4] > 755:
                    self.cols[4] = 0
                self.col[4] = self.col[4]+5
            if self.col[4] < 0:
                hc = "#000000"
            elif self.col[4] > 255:
                hc = "#ffffff"
            else:
                hc = f"#{self.col[4]:02x}{self.col[4]:02x}{self.col[4]:02x}"
            self.lingyun_background.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            self.lingyun_background_2.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            self.todayclass_background.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            self.duty_background.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            return
        if config.get("dp_Curriculum_ramp") == "True" or config.get("dp_Countdown_ramp") == "True" or config.get("dp_Course_ramp") == "True" or config.get("dp_drup_ramp") == "True":
            if config.get("dp_Curriculum_ramp") == "True": # 当前课程
                self.lingyun_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[2]}, {self.col[1]}, {self.col[1]}, 255), stop:1 rgba({self.col[0]}, {self.col[0]}, {self.col[2]}, 255));border-radius: 10px")
            if config.get("dp_Countdown_ramp") == "True": # 倒计时
                self.lingyun_background_2.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[0]}, {self.col[1]}, {self.col[0]}, 255), stop:1 rgba({self.col[2]}, {self.col[1]}, {self.col[1]}, 255));border-radius: 10px")
            if config.get("dp_Course_ramp") == "True": # 今日课程
                self.todayclass_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[3]}, {self.col[0]}, {self.col[2]}, 255), stop:1 rgba({self.col[0]}, {self.col[1]}, {self.col[0]}, 255));border-radius: 10px")
            if config.get("dp_drup_ramp") == "True": # 值日生
                self.duty_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[0]}, {self.col[1]}, {self.col[0]}, 255), stop:1 rgba({self.col[2]}, {self.col[1]}, {self.col[1]}, 255));border-radius: 10px")

            for i in range(4):
                if self.cols[i] == 0:
                    if self.col[i] == "100":
                        self.cols[i] = 1
                    self.col[i] = str(int(self.col[i])-1)
                else:
                    if self.col[i] == "254":
                        self.cols[i] = 0
                    self.col[i] = str(int(self.col[i])+1)
        else:
            theme = "dark" if isDarkTheme() else "light"
            if theme == "light":
                self.todayclass_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            elif theme == "dark":
                self.todayclass_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
    def TOPIC(self):
        if self.dc == False:
            theme = "dark" if isDarkTheme() else "light"
        else:
            theme = "dark"
        if theme == "light":
            self.lingyun_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.todayclass_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.duty_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")

            if config.get("dp_Curriculum_ramp") == "True":
                self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.lingyun_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            if config.get("dp_Countdown_ramp") == "True":
                self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.lingyun_background_2.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            if config.get("dp_drup_ramp") == "True":
                self.duty_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.duty_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            if config.get("dp_Course_ramp") == "True":
                self.todayclass_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.todayclass_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")

        elif theme == "dark":
            self.lingyun_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.todayclass_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.duty_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            
            if config.get("dp_Curriculum_ramp") == "True":
                self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            else:
                self.lingyun_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
            if config.get("dp_Countdown_ramp") == "True": 
                self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")  
            else:
                self.lingyun_background_2.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
            if config.get("dp_drup_ramp") == "True":
                self.duty_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            else:
                self.duty_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
            if config.get("dp_Course_ramp") == "True":
                self.todayclass_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            else:
                self.todayclass_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
    def closeEvent(self, event: QCloseEvent) -> None:
        #event.accept()
        if not is_system_shutting_down():
            event.ignore()
    def update_widget(self): # 暂不使用
        # 新！该def更新课程表和时间表（初始化时调用1次）

        times_today = []
        widgets_today = []

        wu = today_widget[0][2]
        for i in range(len(today_widget)):
            if wu == today_widget[i][2]:
                pass
    def update_Widgets(self,cho=None):
        # 该def生成课程表并且展示（初始化时调用1次）
        global class_table,class_time,class_ORD_Filtration,adj_weekday
        week = str(datetime.now().isoweekday()) if adj_weekday == 0 else str(adj_weekday)
        if cho is not None:
            a = Initialization.convert_widget(-1)
            if a == "close":
                return
        if week == "7":
            weeks = "0"
        else:
            weeks = week
        #tom_today_widget, tom_current_widget, tom_course_widgets, tom_time_widgets, tom_guo_widgets = main.convert_widget(-1,int(week) + 1)
        tom_today_widget = main.convert_widget(-1,int(weeks)+1)[0]

        if self.dp_info == {} or self.dp_info["tom"] != 'True':
            if today_widget == []:
                self.Widgets_ORD.setText("今日")
                self.Widgets.setText("全天无课")
            else:
                self.done_class = []
                self.done_class_ORD = []
                courses = class_table.get(week, [])
                for course_block in courses:
                    for period, classes in course_block.items():
                        if all(s == "" for s in classes):
                            continue
                        self.done_class_ORD.append(period) # 时间段标识
                        self.done_class.append("——")
                        section_counter = 1  # 节数计数器
                        for i, cls in enumerate(classes):
                            class_time_slot = class_time[week][period][i]
                            if class_time_slot in class_ORD_Filtration:
                                # 时间段被过滤
                                self.done_class.append(cls)
                                self.done_class_ORD.append("")
                            else:
                                self.done_class.append(cls)
                                self.done_class_ORD.append(f"第{section_counter}节")
                                section_counter += 1
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
        else:
            if today_widget == []:
                self.Widgets_ORD.setText("无课")
            else:
                self.done_class = []
                courses = class_table.get(week, [])
                for course_block in courses:
                    for period, classes in course_block.items():
                        if all(s == "" for s in classes):
                            continue
                        self.done_class.append("——")                          
                        for i, cls in enumerate(classes):
                            class_time_slot = class_time[week][period][i]
                            self.done_class.append(cls)

                self.class_i = ""
                for j in range(len(self.done_class)):
                    i = self.done_class[j]
                    if len(i) > 0:
                        self.class_i = self.class_i + i + "\n"
                self.Widgets_ORD.setText(self.class_i)

            if tom_today_widget == []:
                self.Widgets.setText("无课")
            else:
                self.done_class = []
                courses = class_table.get(str(datetime.now().weekday() + 2), [])
                for course_block in courses:
                    for period, classes in course_block.items():
                        if all(s == "" for s in classes):
                            continue
                        self.done_class.append("——")                          
                        for i, cls in enumerate(classes):
                            class_time_slot = class_time[week][period][i]
                            self.done_class.append(cls)

                self.class_i = ""
                for j in range(len(self.done_class)):
                    i = self.done_class[j]
                    if len(i) > 0:
                        self.class_i = self.class_i + i + "\n"
                self.Widgets.setText(self.class_i)


    def update_duty(self):
        # 该def更新值日生表（初始化时调用1次）
        global duty_table,adj_weekday
        if config.get("duty_mode") == "weekday":
            week = str(adj_weekday) if adj_weekday != 0 else str(datetime.now().weekday() + 1)
            duty = duty_table.get(week, [])
            if duty == {}:
                self.duty_project_widget.setText("--")
                self.duty_name_widget.setText("今日没有值日生")
                return
            project = ""
            name = ""
            for i in duty:
                project = project + i + "\n"
                for j in duty[i]:
                    name = name +j + " "
                name = name + "\n"
            self.duty_project_widget.setText(project)
            self.duty_name_widget.setText(name)
        elif config.get("duty_mode") == "again":
            # 解析初始日期
            date_begin_str = duty_table["date_begin"]
            date_begin = datetime.strptime(date_begin_str, "%Y%m%d").date()
            # 获取今天的日期
            today = date.today()
            
            # 计算工作日天数
            workdays = 0
            current_date = date_begin
            while current_date < today:
                current_date += timedelta(days=1)
                # 跳过周末 (6: 周日, 7: 周六)
                if current_date.isoweekday() not in [6, 7]:
                    workdays += 1
            
            # 获取值日组数据
            duty_groups = duty_table["duty"]
            num_groups = len(duty_groups)
            
            # 计算今天的值日组索引 (1-based)
            group_index = (workdays % num_groups) + 1
            group_key = str(group_index)
            
            # 获取今天的值日组
            today_duty = duty_groups.get(group_key, {})
            
            # 格式化值日项目和人员
            project = ""
            name = ""
            for i in today_duty:
                project = project + i + "\n"
                for j in today_duty[i]:
                    name = name + j + " "
                name = name + "\n"
            
            # 更新界面
            self.duty_project_widget.setText(project)
            self.duty_name_widget.setText(name)
    def update_countdown(self):
        # 新！该def为倒计时模块上下课服务（计时器调用）
        now = datetime.now()
        current_time = now.time()
        current_datetime = datetime.combine(now.date(), current_time)

        lag = int(config.get("dp_Countdown_Bar_school_lag"))

        try:
            if current_widget is None: # 下课（调用前已经把放学排除）
                start_datetime = datetime.combine(now.date(), datetime.strptime(guo_widget.split('-')[0], '%H:%M').time())
                end_datetime = datetime.combine(now.date(), datetime.strptime(guo_widget.split('-')[1], '%H:%M').time())
                remaining_time = end_datetime - current_datetime # 计算剩余时间
            else: # 上课
                start_datetime = datetime.combine(now.date(), datetime.strptime(current_widget[1].split('-')[0], '%H:%M').time())
                end_datetime = datetime.combine(now.date(), datetime.strptime(current_widget[1].split('-')[1], '%H:%M').time())
                remaining_time = end_datetime - current_datetime  # 计算剩余时间
        except Exception as e:
            self.class_time.stop()
            self.alert(1)
            #w = Dialog("警告", "您目前修改的课表已经影响到桌面组件的运行，将把桌面组件暂停服务，但是您可以继续编辑，完成后请重启本软件。", MainWindow())
            #w.yesButton.setText("好")
            #w.cancelButton.hide()
            #w.buttonLayout.insertStretch(1)
            #if w.exec():pass
            return

        # 更新显示
        lag = int(config.get("dp_Countdown_Bar_school_lag"))
        adjusted_remaining_time = remaining_time + timedelta(seconds=lag)
        
        s = f"{(adjusted_remaining_time.seconds // 60):02}:{(adjusted_remaining_time.seconds % 60):02}"
        self.countdown = s
        self.lingyun_down.setText(s)


        if lag < 0:
            next = end_datetime + timedelta(seconds=lag)
            rema = next - current_datetime # 计算剩余时间
        else:
            next = end_datetime# - timedelta(seconds=lag)
            rema = next - current_datetime # 计算剩余时间
        remaining_percentage = 100 - (rema.total_seconds() / (end_datetime - start_datetime).total_seconds()) * 100 # 计算剩余时间的百分比
        self.lingyun_Bar.setVal(remaining_percentage)


        if s == "00:00":
            self.class_time.stop()
            self.warn_function("alert")

            #QTimer.singleShot(1000,lambda: self.alert(1))
        
        elif current_widget is None and s == "03:01" and config.get("dp_Preliminary") == "True":
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_color_next_down")), QColor(config.get("dp_Countdown_color_next_down")))
            self.warn_function("warn.ui")
            #QTimer.singleShot(1000,lambda: warn.ui("next_down"))
    def warning(self,defs):
        if defs == "alert":
            QTimer.singleShot(1000,lambda: self.alert(1))
        elif defs == "warn.ui":
            QTimer.singleShot(1000,lambda: warn.ui("next_down"))
    def class_coming(self): #待检修(检修1次)
        # 该def为检测是否快开始上课（计时器调用）
        now = datetime.now()
        current_time = now.time()
        current_datetime = datetime.combine(now.date(), current_time)
        t = False

        for i in today_widget:
            start_time = datetime.strptime(i[1].split('-')[0], '%H:%M').time()
            remaining_time = datetime.combine(now.date(), start_time) - current_datetime
            # 计算剩余时间的分钟数
            remaining_minutes = remaining_time.total_seconds() / 60
            remaining_seconds = remaining_time.total_seconds() % 60
            # 判断剩余时间是否小于20分钟
            if 0 < remaining_minutes < 20:
                t = True
                break

        
        if t:
            self.lingyun_Bar.setVal(0)
            remaining_minutes = remaining_time.seconds // 60
            remaining_seconds = remaining_time.seconds % 60

            # 更新标签显示
            s = f"{remaining_minutes:02}:{remaining_seconds:02}"
            self.lingyun_down.setText(s)
            if s == "03:01" and config.get("dp_Preliminary") == "True":
                self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_color_next_up")), QColor(config.get("dp_Countdown_color_next_up")))
                self.warn_function("warn.ui")

            if s == "00:00":
                self.coming_time.stop()
                self.warn_function("alert")
                #QTimer.singleShot(1000,lambda: self.alert(1))
    def alert(self,st = None):
        global DP_Comonent
 
        # 调用一次 上下课会被调用
        a = Initialization.convert_widget(-1)
        if a == "close":
            return
          
        if current_widget is None: #下课或者放学
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_Bar_color_up")), QColor(config.get("dp_Countdown_Bar_color_up")))
            if guo_widget != None: # 下课
                self.lingyun_class.setText("课间")
                self.class_time.timeout.connect(self.update_countdown)
                self.class_time.start(1000)
                # 调用下课提醒
                if st != None and config.get("dp_Bell") == "True" and config.get("dp_Switch") == "True":
                    warn.ui("up") 
            else: # 放学
                self.class_time.stop()

                self.lingyun_class.setText("暂无课程")
                self.lingyun_down.setText("00:00")
                self.lingyun_Bar.setVal(100)
                # 调用放学提醒
                if st != None and config.get("dp_Bell") == "True" and config.get("dp_Switch") == "True":
                    warn.ui("ls") 

                self.coming_time = QTimer(self)
                self.coming_time.timeout.connect(self.class_coming)
                self.coming_time.start(1000)

                # 提醒值日生
                if config.get("dp_drup_audio") == "True" and st != None:
                    from_time = datetime.strptime(config.get("dp_duty_TimePicker_from"), "%H:%M").time()
                    to_time = datetime.strptime(config.get("dp_duty_TimePicker_to"), "%H:%M").time()
                    now = datetime.now().time()
                    if from_time <= now <= to_time:
                        self.finish_wav = f"{USER_RES}/audio/duty_warn.wav"
                        timer = threading.Timer(int(config.get("dp_audio_s")), self.wav,args =(config.get("dp_Sysvolume_value"), config.get("dp_Sysvolume")))
                        timer.start()
        

        else: # 上课TitleLabel
            self.lingyun_class.setText(current_widget[3])
            #self.lingyun_Bar.setCustomBarColor(QColor(0,255,0), QColor(0,255,0))
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_Bar_color_down")), QColor(config.get("dp_Countdown_Bar_color_down")))
            self.class_time.timeout.connect(self.update_countdown)
            self.class_time.start(1000)

            # 调用上课提醒
            if st != None and config.get("dp_Bell") == "True" and config.get("dp_Switch") == "True":
                warn.ui("down")

        
        #print("课程是：",today_widget)
        #print("当前课程是：",current_widget)
        #print("课程数量是：",course_widget)
        #print("课程时间是：",time_widget)
        #print("过渡时间是：",guo_widget)
    def wav(self, value, vas):
        if vas == "True":
            devices = AudioUtilities.GetSpeakers()
            clsctx = CLSCTX_ALL
            interface = devices.Activate(IAudioEndpointVolume._iid_, clsctx, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            # 获取当前音量值
            original_volume = volume.GetMasterVolumeLevelScalar()
            volume.SetMute(False, None)
            vs = float(int(value) / 100)
            volume.SetMasterVolumeLevelScalar(vs, None)  # 将音量设置为100
        
        
        wave_obj = sa.WaveObject.from_wave_file(self.finish_wav)# 读取 WAV 文件
        play_obj = wave_obj.play()# 播放 WAV 文件
        play_obj.wait_done()# 等待播放完成
        
        #playsound(self.finish_wav)
        if vas == "True":
            volume.SetMasterVolumeLevelScalar(original_volume, None)
class ThrottledFunction:
    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.last_execution_time = 0

    def __call__(self, *args, **kwargs):
        now = time.time()
        if now - self.last_execution_time >= self.interval:
            self.last_execution_time = now
            self.func(*args, **kwargs)
'''
class Desktop_Component(QWidget):
    def __init__(self):
        super().__init__()
        self.warn_function = ThrottledFunction(self.warning, 5)
        self.dc = False # 息屏标志
        self.initUI()
        


        self.init_update_timers()
        self.refresh_all_data(False)

        self.countdown_running = False  # 倒计时运行状态标记

        # 1. 分钟级计时器 - 用于定期刷新（如课程切换检测）
        self.minute_timer = QTimer(self)
        self.minute_timer.setInterval(60000)
        #self.minute_timer.timeout.connect(self.update_countdown)
        self.minute_timer.timeout.connect(self.minute_level_update)
        
        # 2. 秒级计时器 - 用于实时倒计时显示（如果需要）
        self.class_time = QTimer(self)
        self.class_time.setInterval(1000)
        self.class_time.timeout.connect(self.second_level_update)

        # 3. 上课提醒计时器 - 用于检测即将上课的情况
        self.coming_time = QTimer(self)
        self.coming_time.setInterval(1000)
        self.coming_time.timeout.connect(self.class_coming)

    def initUI(self):
        global display_x, display_y
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度
        
        self.flags = Qt.SplashScreen | Qt.FramelessWindowHint | Qt.Tool
        if config.get('dp_Pin') == 'True':
            self.flags |= Qt.WindowStaysOnTopHint
        elif config.get('dp_Pin') == 'Under':
            self.flags |= Qt.WindowDoesNotAcceptFocus
        self.setWindowFlags(self.flags)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.move(display_x,12)
        f = self.uic_ui()
        if f == False:
            return
        

        self.countdown = ""

        self.updown = False # false下课 ture上课
         
        QTimer.singleShot(1000, self.alert) # 倒计时模块
        QTimer.singleShot(1000, self.update_Widgets)
        QTimer.singleShot(1000, self.update_duty)

        #窗口在屏幕的位置初始化
        self.DP_x = display_x - int(config.get("dp_display_edge"))
        self.DP_y = 12
        self.animation_i = display_x - 260
        self.animations()

        if config.get('dp_Switch') == "True":
            self.show()
            self.animation_show.start()
            self.animation_rect_show.start()

    def showEvent(self, event):
        self.lower()

    def animations(self):
        # 从隐藏显示+淡入：animation_show,animation_rect_show
        self.animation_show = QPropertyAnimation(self, b'windowOpacity')
        self.animation_show.setDuration(400)
        self.animation_show.setStartValue(0)
        self.animation_show.setEndValue(1)
        self.animation_show.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rect_show = QPropertyAnimation(self, b'geometry')
        self.animation_rect_show.setDuration(450)
        self.animation_rect_show.setStartValue(QRect(display_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_show.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_show.setEasingCurve(QEasingCurve.InOutCirc)

        # 从显示隐藏+淡出：animation_hide,animation_rect_hide
        self.animation_hide = QPropertyAnimation(self, b'windowOpacity')
        self.animation_hide.setDuration(600)
        self.animation_hide.setStartValue(1)
        self.animation_hide.setEndValue(0)
        self.animation_hide.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_rect_hide = QPropertyAnimation(self, b'geometry')
        self.animation_rect_hide.setDuration(450)
        self.animation_rect_hide.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_hide.setEndValue(QRect(display_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_hide.setEasingCurve(QEasingCurve.InOutCirc)

        # 从显示到贴屏幕边缘：animation_rect_shrink
        self.animation_rect_shrink = QPropertyAnimation(self, b'geometry')
        self.animation_rect_shrink.setDuration(450)
        self.animation_rect_shrink.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_shrink.setEndValue(QRect(display_x-35, self.DP_y, self.width(), self.height()))
        self.animation_rect_shrink.setEasingCurve(QEasingCurve.InOutCirc)

        # 从贴屏幕边缘到显示：animation_rect_expand
        self.animation_rect_expand = QPropertyAnimation(self, b'geometry')
        self.animation_rect_expand.setDuration(450)
        self.animation_rect_expand.setStartValue(QRect(display_x-35, self.DP_y, self.width(), self.height()))
        self.animation_rect_expand.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect_expand.setEasingCurve(QEasingCurve.InOutCirc)

    def setRoundedCorners(self, radius):
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())  # 使用QRectF而不是QRect
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def uic_ui(self):
        # 检查ui文件是否存在
        if os.path.exists(f"{RES}ui/dp/{config.get('dp_choose')}"):
            self.classes = uic.loadUi(f"{RES}ui/dp/{config.get('dp_choose')}",self)
        else:
            files = glob.glob(os.path.join(f"{RES}ui\\dp\\", '*.ui'))
            if files:
                self.classes = uic.loadUi(files[0],self)
                config.set('dp_choose', os.path.basename(files[0]))
            else:
                self.close()
                return False
        self.classes.setObjectName("classes")
        config["dp_display_edge"] = self.classes.width()


        self.dp_info = {}
        if check_component_in_ui(f"{RES}ui/dp/{config.get('dp_choose')}", "ui_info"):
            # 为新版本ui
            self.ui_info = self.findChild(QLabel, "ui_info")
            self.dp_info = ast.literal_eval(self.ui_info.text())

            self.ui_info.hide()

        # 当前课程
        self.lingyun_Title = self.findChild(QLabel,"lingyun_Title")
        self.lingyun_class = self.findChild(TitleLabel,"lingyun_class")
        self.lingyun_background = self.findChild(QLabel,"lingyun_background")

        self.lingyun_class.installEventFilter(self)
        self.lingyun_Title.installEventFilter(self)
        self.lingyun_background.installEventFilter(self)

        # 倒计时
        self.lingyun_Title_2 = self.findChild(QLabel,"lingyun_Title_2")
        self.lingyun_background_2 = self.findChild(QLabel,"lingyun_background_2")
        self.lingyun_down = self.findChild(TitleLabel,"lingyun_down")
        self.lingyun_Bar = self.findChild(ProgressBar,"lingyun_Bar")
        self.lingyun_Bar.setRange(0, 100)
        self.lingyun_Bar.setCustomBarColor(QColor(0, 0, 255), QColor(0, 255, 0))

        self.lingyun_down.installEventFilter(self)
        self.lingyun_background_2.installEventFilter(self)
        self.lingyun_Title_2.installEventFilter(self)

        # 今日课程
        self.todayclass_Title = self.findChild(QLabel,"todayclass_Title")
        self.Widgets_ORD = self.findChild(StrongBodyLabel,"class_ORD")
        self.Widgets = self.findChild(StrongBodyLabel,"class_widget")
        self.todayclass_background = self.findChild(QLabel,"todayclass_background")

        self.todayclass_Title.installEventFilter(self)
        self.Widgets_ORD.installEventFilter(self)
        self.Widgets.installEventFilter(self)
        self.todayclass_background.installEventFilter(self)

        # 值日生组件
        self.duty_background = self.findChild(QLabel,"duty_background")
        self.duty_Title = self.findChild(QLabel,"duty_Title")
        self.duty_project_widget = self.findChild(StrongBodyLabel,"duty_project_widget")
        self.duty_name_widget = self.findChild(StrongBodyLabel,"duty_name_widget")

        self.duty_Title.installEventFilter(self)
        self.duty_project_widget.installEventFilter(self)
        self.duty_name_widget.installEventFilter(self)
        self.duty_background.installEventFilter(self)

        if config.get('dp_duty') == 'False':
            self.duty_background.hide()
            self.duty_Title.hide()
            self.duty_project_widget.hide()
            self.duty_name_widget.hide()

        self.click_timer = QTimer(self)
        self.click_timer.setInterval(200)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.on_single_click)
        self.press_position = QPoint()
        self.waiting_for_double_click = False  # 等待双击事件标志
        self.touch_tolerance = 500  # 触摸容差


        self.TOPIC()
        font_name = self.font_files(f"{RES}MiSans-Bold.ttf",config.get("dp_Typeface"))
        font = QFont(font_name, 16)
        self.Widgets_ORD.setFont(font)
        self.Widgets_ORD.setIndent(8)
        self.Widgets.setFont(font)
        self.Widgets.setIndent(8)
        self.duty_project_widget.setFont(font)
        self.duty_project_widget.setIndent(8)
        self.duty_name_widget.setFont(font)
        self.duty_name_widget.setIndent(8)
        font = QFont(font_name,21)
        font.setWeight(QFont.Bold)
        self.lingyun_down.setFont(font)

        font = QFont(font_name,14)
        font.setWeight(QFont.Bold)
        font = QFont(font_name,21)
        font.setWeight(QFont.Bold)
        self.lingyun_class.setFont(font)


        self.cols = [0,0,1,0,0]
        self.col = ["240","190","130","110",9]
        
        self.up_col = QTimer(self)
        self.up_col.timeout.connect(self.update_color)
        self.up_col.start(20)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.press_position = event.pos()
            self.pressed_button = event.button()
            
        elif event.type() == QEvent.MouseButtonRelease:
            if (event.pos() - self.press_position).manhattanLength() <= self.touch_tolerance:
                if event.button() == Qt.LeftButton:
                    self.on_single_click()
                elif event.button() == Qt.RightButton:
                    self.on_double_click(source)
            return super().eventFilter(source, event)
        
        # 忽略双击事件
        elif event.type() == QEvent.MouseButtonDblClick:
            return True
        
        return super().eventFilter(source, event)

    def on_single_click(self):
        # 获取窗口的坐标位置

        if self.dc or config.get('dp_Pin') == 'Under':
            return
        window_pos = self.frameGeometry().topLeft()
        if window_pos.x() == self.DP_x:
            self.animation_rect_shrink.start()
        elif window_pos.x() == display_x-35:
            self.animation_rect_expand.start()
    
    def on_double_click(self, source):
        global settings_window , display_x , display_y, tops
        flag = "0"
        if source == self.lingyun_class or source == self.lingyun_Title or source == self.lingyun_background:
            #当前课程
            flag = config.get("dp_Curriculum_ramp_action")
        elif source == self.lingyun_down or source == self.lingyun_background_2 or source == self.lingyun_Title_2:
            #倒计时
            flag = config.get("dp_countdown_action")
        elif source == self.todayclass_Title or source == self.todayclass_background or source == self.Widgets_ORD or source == self.Widgets:
            #今日课程
            flag = config.get("dp_todayclass_action")
        elif source == self.duty_Title or source == self.duty_project_widget or source == self.duty_name_widget or source == self.duty_background:
            # 值日生
            flag = config.get("dp_duty_action")
        if flag == "1":
            tops.setting_show()
            settings_window.switchTo(settings_window.duty)
        elif flag == "2":
            tops.setting_show()
            settings_window.switchTo(settings_window.classes)
        elif flag == "3":
            tops.setting_show()
            settings_window.switchTo(settings_window.classes_time)

    def update_ui(self,value,choose):
        if choose == "dp_Switch":
            if value:
                config['dp_Switch'] = "True"
                self.show()
                self.animation_show.start()
                self.animation_rect_show.start()
            else:
                config['dp_Switch'] = "False"
                self.animation_hide.start()
                self.animation_rect_hide.start()

                #self.hide()
        elif choose == "dp_Pin":

            if value == "True":
                if not (self.flags & Qt.WindowStaysOnTopHint):
                    self.flags |= Qt.WindowStaysOnTopHint
                if self.flags & Qt.WindowDoesNotAcceptFocus:
                    self.flags &= ~Qt.WindowDoesNotAcceptFocus
                self.setWindowFlags(self.flags)
            elif value == "False":
                if self.flags & Qt.WindowStaysOnTopHint:
                    self.flags &= ~Qt.WindowStaysOnTopHint
                if self.flags & Qt.WindowDoesNotAcceptFocus:
                    self.flags &= ~Qt.WindowDoesNotAcceptFocus
                self.setWindowFlags(self.flags)
            elif value == "Under":
                if not(self.flags & Qt.WindowStaysOnTopHint):
                    self.flags &= ~Qt.WindowStaysOnTopHint
                if not(self.flags & Qt.WindowDoesNotAcceptFocus):
                    self.flags |= Qt.WindowDoesNotAcceptFocus
                self.setWindowFlags(self.flags)
                window_pos = self.frameGeometry().topLeft()
                if window_pos.x() == display_x-35:
                    QTimer.singleShot(500, self.animation_rect_expand.start)
            if config.get("dp_Switch"):
                self.show()
        elif choose == "dp_Typeface":
            config["dp_Typeface"] = str(value)
            font_name = self.font_files(f"{RES}MiSans-Bold.ttf",config.get("dp_Typeface"))
            font = QFont(font_name, 16)
            #font.setWeight(QFont.Bold)
            self.Widgets_ORD.setFont(font)
            self.Widgets_ORD.setIndent(8)
            self.Widgets.setFont(font)
            self.Widgets.setIndent(8)
            font = QFont(font_name,21)
            font.setWeight(QFont.Bold)
            self.lingyun_down.setFont(font)

            font = QFont(font_name,14)
            font.setWeight(QFont.Bold)

            font = QFont(font_name,21)
            font.setWeight(QFont.Bold)
            self.lingyun_class.setFont(font)
        elif choose == "dp_Bell":
            config['dp_Bell'] = str(value)
        elif choose == "dp_Sysvolume":
            config['dp_Sysvolume'] = str(value)
        elif choose == "dp_Sysvolume_value":
            config['dp_Sysvolume_value'] = str(value)
        elif choose == "dp_Curriculum_ramp":
            config['dp_Curriculum_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_Countdown_ramp":
            config['dp_Countdown_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_Countdown_Bar_color":
            config['dp_Countdown_Bar_color'] = str(value)
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_Bar_color")), QColor(0, 255, 0))
        elif choose == "dp_Countdown_Bar_school_lag":
            config['dp_Countdown_Bar_school_lag'] = str(value)
        elif choose == "dp_Course_ramp":
            config['dp_Course_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_drup_ramp":
            #config['dp_drup_ramp'] = str(value)
            self.TOPIC()
        elif choose == "dp_duty":
            if config['dp_duty'] == "False":
                self.duty_background.hide()
                self.duty_Title.hide()
                self.duty_project_widget.hide()
                self.duty_name_widget.hide()
            else:
                self.duty_background.show()
                self.duty_Title.show()
                self.duty_project_widget.show()
                self.duty_name_widget.show()
        elif choose == "dp_display_edge":
            pass
            #self.DP_x = display_x - int(config.get("dp_display_edge"))

    def dc_dp(self,event):
        if event == "open":
            self.dc = True
            #self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            if config.get("dp_xiping") == "True":
                self.show()
            else:
                self.hide()
            window_pos = self.frameGeometry().topLeft()
            if window_pos.x() == display_x-35:
                QTimer.singleShot(500, self.animation_rect_expand.start)
            self.TOPIC()
            self.lingyun_down.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.lingyun_class.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.Widgets_ORD.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.Widgets.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.duty_name_widget.setStyleSheet("color: rgba(255, 255, 255, 255)")
            self.duty_project_widget.setStyleSheet("color: rgba(255, 255, 255, 255)")

        elif event == "notime":
            self.hide()

        else:
            self.dc = False
            self.TOPIC()
            self.update_color()
            if config['dp_Pin'] == "False":
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.lingyun_down.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.lingyun_class.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.Widgets_ORD.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.Widgets.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.duty_name_widget.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.duty_project_widget.setStyleSheet("color: rgba(0, 0, 0, 255)")
            self.show()

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

    def update_color(self):
        if self.dc:
            if self.cols[4] == 0:
                if self.col[4] < -120:
                    self.cols[4] = 1
                self.col[4] = self.col[4]-5
            else:
                if self.col[4] > 755:
                    self.cols[4] = 0
                self.col[4] = self.col[4]+5
            if self.col[4] < 0:
                hc = "#000000"
            elif self.col[4] > 255:
                hc = "#ffffff"
            else:
                hc = f"#{self.col[4]:02x}{self.col[4]:02x}{self.col[4]:02x}"
            self.lingyun_background.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            self.lingyun_background_2.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            self.todayclass_background.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            self.duty_background.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);border-radius: 12px;border:2px solid {hc}")
            return
        if config.get("dp_Curriculum_ramp") == "True" or config.get("dp_Countdown_ramp") == "True" or config.get("dp_Course_ramp") == "True" or config.get("dp_drup_ramp") == "True":
            if config.get("dp_Curriculum_ramp") == "True": # 当前课程
                self.lingyun_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[2]}, {self.col[1]}, {self.col[1]}, 255), stop:1 rgba({self.col[0]}, {self.col[0]}, {self.col[2]}, 255));border-radius: 10px")
            if config.get("dp_Countdown_ramp") == "True": # 倒计时
                self.lingyun_background_2.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[0]}, {self.col[1]}, {self.col[0]}, 255), stop:1 rgba({self.col[2]}, {self.col[1]}, {self.col[1]}, 255));border-radius: 10px")
            if config.get("dp_Course_ramp") == "True": # 今日课程
                self.todayclass_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[3]}, {self.col[0]}, {self.col[2]}, 255), stop:1 rgba({self.col[0]}, {self.col[1]}, {self.col[0]}, 255));border-radius: 10px")
            if config.get("dp_drup_ramp") == "True": # 值日生
                self.duty_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({self.col[0]}, {self.col[1]}, {self.col[0]}, 255), stop:1 rgba({self.col[2]}, {self.col[1]}, {self.col[1]}, 255));border-radius: 10px")

            for i in range(4):
                if self.cols[i] == 0:
                    if self.col[i] == "100":
                        self.cols[i] = 1
                    self.col[i] = str(int(self.col[i])-1)
                else:
                    if self.col[i] == "254":
                        self.cols[i] = 0
                    self.col[i] = str(int(self.col[i])+1)
        else:
            theme = "dark" if isDarkTheme() else "light"
            if theme == "light":
                self.todayclass_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            elif theme == "dark":
                self.todayclass_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")

    def TOPIC(self):
        if self.dc == False:
            theme = "dark" if isDarkTheme() else "light"
        else:
            theme = "dark"
        if theme == "light":
            self.lingyun_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.todayclass_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")
            self.duty_Title.setStyleSheet("color: rgba(0, 0, 0, 95)")

            if config.get("dp_Curriculum_ramp") == "True":
                self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.lingyun_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            if config.get("dp_Countdown_ramp") == "True":
                self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.lingyun_background_2.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            if config.get("dp_drup_ramp") == "True":
                self.duty_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.duty_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")
            if config.get("dp_Course_ramp") == "True":
                self.todayclass_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(255, 205, 235, 255), stop:1 rgba(255, 255, 255, 255));border-radius: 10px")
            else:
                self.todayclass_background.setStyleSheet("background-color: rgba(255, 255, 255, 255);border-radius: 10px")

        elif theme == "dark":
            self.lingyun_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.lingyun_Title_2.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.todayclass_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            self.duty_Title.setStyleSheet("color: rgba(112, 112, 112, 255)")
            
            if config.get("dp_Curriculum_ramp") == "True":
                self.lingyun_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            else:
                self.lingyun_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
            if config.get("dp_Countdown_ramp") == "True": 
                self.lingyun_background_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")  
            else:
                self.lingyun_background_2.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
            if config.get("dp_drup_ramp") == "True":
                self.duty_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            else:
                self.duty_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")
            if config.get("dp_Course_ramp") == "True":
                self.todayclass_background.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(68, 5, 45, 255), stop:1 rgba(0, 0, 0, 255));border-radius: 10px")
            else:
                self.todayclass_background.setStyleSheet("background-color: rgba(0, 0, 0, 255);border-radius: 10px")

    """def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()"""

    def warning(self,defs):
        if defs == "alert":
            QTimer.singleShot(1000,lambda: self.alert(1))
        elif defs == "warn.ui":
            QTimer.singleShot(1000,lambda: warn.ui("next_down"))

    def class_coming(self): #待检修(检修1次)
        # 该def为检测是否快开始上课（计时器调用）
        now = datetime.now()
        current_time = now.time()
        current_datetime = datetime.combine(now.date(), current_time)
        t = False

        for i in today_widget:
            start_time = datetime.strptime(i[1].split('-')[0], '%H:%M').time()
            remaining_time = datetime.combine(now.date(), start_time) - current_datetime
            # 计算剩余时间的分钟数
            remaining_minutes = remaining_time.total_seconds() / 60
            remaining_seconds = remaining_time.total_seconds() % 60
            # 判断剩余时间是否小于20分钟
            if 0 < remaining_minutes < 20:
                t = True
                break

        if t:
            self.lingyun_Bar.setVal(0)
            remaining_minutes = remaining_time.seconds // 60
            remaining_seconds = remaining_time.seconds % 60

            # 更新标签显示
            s = f"{remaining_minutes:02}:{remaining_seconds:02}"
            self.lingyun_down.setText(s)
            if s == "03:01" and config.get("dp_Preliminary") == "True":
                self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_color_next_up")), QColor(config.get("dp_Countdown_color_next_up")))
                self.warn_function("warn.ui")

            if s == "00:00":
                self.coming_time.stop()
                self.warn_function("alert")

    def wav(self, value, vas):
        if vas == "True":
            devices = AudioUtilities.GetSpeakers()
            clsctx = CLSCTX_ALL
            interface = devices.Activate(IAudioEndpointVolume._iid_, clsctx, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            # 获取当前音量值
            original_volume = volume.GetMasterVolumeLevelScalar()
            volume.SetMute(False, None)
            vs = float(int(value) / 100)
            volume.SetMasterVolumeLevelScalar(vs, None)  # 将音量设置为100
        
        
        wave_obj = sa.WaveObject.from_wave_file(self.finish_wav)# 读取 WAV 文件
        play_obj = wave_obj.play()# 播放 WAV 文件
        play_obj.wait_done()# 等待播放完成
        
        #playsound(self.finish_wav)
        if vas == "True":
            volume.SetMasterVolumeLevelScalar(original_volume, None)

###############

    def start_countdown(self):
        """启动倒计时模块，确保计时器正确启动"""
        self.countdown_running = False  # 先重置状态
        if not self.countdown_running:
            self.minute_timer.stop()
            self.minute_timer.start()    
            self.countdown_running = True
            self.update_countdown() # 立即更新一次
            self.class_time.start()

    def stop_countdown(self,ui_update=True):
        """停止所有相关计时器，统一状态"""
        if self.countdown_running:
            # print("停止主倒计时系统")
            self.minute_timer.stop()
            self.class_time.stop()
            if ui_update:
                self.lingyun_down.setText("--:--")
            self.countdown_running = False

    def minute_level_update(self):
        """分钟级更新 - 处理课程切换、数据刷新等低频操作"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行分钟级更新")
        # 检查是否需要刷新数据（如课程是否已切换）
        self.refresh_all_data(update_ui=True)
        # 仅在必要时更新倒计时（如课程信息变化）
        self.update_countdown()

    def second_level_update(self):
        """秒级更新 - 仅处理显示刷新，不涉及数据计算"""
        try:
            # print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行秒级更新")
            # 只更新显示，不重新计算课程数据
            if hasattr(self, 'countdown') and self.countdown_running:
                # 解析当前倒计时并减1秒
                minutes, seconds = map(int, self.countdown.split(':'))
                total_seconds = minutes * 60 + seconds
                if total_seconds > 0:
                    total_seconds -= 1
                    new_minutes = total_seconds // 60
                    new_seconds = total_seconds % 60
                    self.countdown = f"{new_minutes:02}:{new_seconds:02}"
                    self.lingyun_down.setText(self.countdown)

                    self.update_progress_bar()
                    if config.get("dp_Switch") == "True":
                        if current_widget is None and self.countdown == "03:01" and config.get("dp_Preliminary") == "True":
                            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_color_next_down")), QColor(config.get("dp_Countdown_color_next_down")))
                            self.warn_function("warn.ui")
                else:
                    self.minute_level_update()
                    self.class_time.stop()

                    
                
        except Exception as e:
            print(f"秒级更新错误: {str(e)}")

    def update_progress_bar(self):
        """更新进度条，基于当前剩余时间计算百分比"""
        try:
            # 确保有必要的时间数据
            if not hasattr(self, 'start_datetime') or not hasattr(self, 'end_datetime'):
                return

            # 计算总课程时长（秒）
            total_duration = (self.end_datetime - self.start_datetime).total_seconds()
            if total_duration <= 0:
                self.lingyun_Bar.setVal(0)
                return

            # 计算当前剩余时间（秒）
            minutes, seconds = map(int, self.countdown.split(':'))
            remaining_seconds = minutes * 60 + seconds

            # 计算进度百分比（已过时间/总时长）
            elapsed_seconds = total_duration - remaining_seconds
            progress_percentage = (elapsed_seconds / total_duration) * 100
            
            # 确保百分比在0-100范围内
            progress_percentage = max(0, min(100, progress_percentage))
            
            # 更新进度条
            self.lingyun_Bar.setVal(progress_percentage)
            
        except Exception as e:
            print(f"进度条更新错误: {str(e)}")
################


    def init_update_timers(self):
        """初始化定时更新计时器"""
        # 每天凌晨2点更新当日课表和值日生
        self.daily_timer = QTimer(self)
        self.daily_timer.setInterval(24 * 60 * 60 * 1000)  # 24小时
        
        # 修正：正确计算下次凌晨2点的时间
        now = QDateTime.currentDateTime()
        target_time = QTime(2, 0, 0)  # 凌晨2点
        next_update = QDateTime(now.date(), target_time)
        
        # 如果当前时间已经过了今天的2点，则设置为明天的2点
        if now > next_update:
            next_update = next_update.addDays(1)
        
        # 计算从现在到下次更新的毫秒数
        msecs_to_update = now.msecsTo(next_update)
        self.daily_timer.start(msecs_to_update)
        self.daily_timer.timeout.connect(self.refresh_and_restart_countdown)

    def clear_ui(self):
        """清空UI显示"""
        self.lingyun_class.setText("暂无课程")
        self.lingyun_down.setText("--:--")
        self.Widgets.setText("--")
        self.Widgets_ORD.setText("--")
        self.duty_project_widget.setText("--")
        self.duty_name_widget.setText("暂无数据")

    def refresh_and_restart_countdown(self):
        """刷新数据并重启倒计时系统"""
        # print("刷新数据并重启倒计时")
        self.lingyun_Bar.setVal(0)
        self.refresh_all_data()
        self.start_countdown()

    def refresh_all_data(self, update_ui=True):
        """刷新所有数据（课表、值日生）"""
        try:
            self.calculate_today_classes()
            self.calculate_tomorrow_classes()
            self.calculate_duty()
            if update_ui:
                self.update_Widgets()
                self.update_duty()

        except Exception as e:
            # 记录错误但不崩溃
            print(f"数据刷新错误: {str(e)}")
            # 可以添加错误日志记录

    def calculate_today_classes(self):
        """计算今日课程并缓存"""
        global class_table, class_ORD_Filtration, adj_weekday
        self.today_classes = []
        self.today_classes_ord = []
        
        week = str(datetime.now().isoweekday()) if adj_weekday == 0 else str(adj_weekday)
        week = "0" if week == "7" else week  # 处理周日
        
        courses = class_table.get(week, [])
        for course_block in courses:
            for period, classes in course_block.items():
                if all(s == "" for s in classes):
                    continue
                self.today_classes_ord.append(period)
                self.today_classes.append("——")
                section_counter = 1
                for i, cls in enumerate(classes):
                    class_time_slot = class_time[week][period][i]
                    if class_time_slot in class_ORD_Filtration:
                        self.today_classes.append(cls)
                        self.today_classes_ord.append("")
                    else:
                        self.today_classes.append(cls)
                        self.today_classes_ord.append(f"第{section_counter}节")
                        section_counter += 1

        # 格式化显示文本
        self.class_text = ""
        self.class_ord_text = ""
        for j in range(len(self.today_classes)):
            cls = self.today_classes[j]
            ords = self.today_classes_ord[j]
            if len(cls) > 0:
                self.class_text += cls + "\n"
                self.class_ord_text += ords + "\n"

    def calculate_tomorrow_classes(self):
        """计算明日课程并缓存"""
        global class_table, adj_weekday
        self.tomorrow_classes = []
        
        today_weekday = datetime.now().isoweekday() if adj_weekday == 0 else adj_weekday
        tomorrow_weekday = today_weekday + 1
        tomorrow_weekday = 0 if tomorrow_weekday == 7 else tomorrow_weekday  # 处理周日
        week = str(tomorrow_weekday)
        
        courses = class_table.get(week, [])
        for course_block in courses:
            for period, classes in course_block.items():
                if all(s == "" for s in classes):
                    continue
                self.tomorrow_classes.append("——")
                for cls in classes:
                    self.tomorrow_classes.append(cls)

        # 格式化显示文本
        self.tomorrow_text = ""
        for cls in self.tomorrow_classes:
            if len(cls) > 0:
                self.tomorrow_text += cls + "\n"

    def calculate_duty(self):
        """计算今日值日生并缓存"""
        global duty_table, adj_weekday
        self.duty_projects = ""
        self.duty_names = ""
        
        try:
            if config.get("duty_mode") == "weekday":
                week = str(adj_weekday) if adj_weekday != 0 else str(datetime.now().weekday() + 1)
                duty = duty_table.get(week, {})
                if not duty:
                    self.duty_projects = "--"
                    self.duty_names = "今日没有值日生"
                    return

                for project, names in duty.items():
                    self.duty_projects += project + "\n"
                    self.duty_names += " ".join(names) + "\n"

            elif config.get("duty_mode") == "again":
                # 解析初始日期
                date_begin_str = duty_table.get("date_begin", "")
                if not date_begin_str:
                    self.duty_projects = "--"
                    self.duty_names = "未设置值日起始日期"
                    return
                    
                date_begin = datetime.strptime(date_begin_str, "%Y%m%d").date()
                today = date.today()
                
                # 计算工作日天数（跳过周末）
                workdays = 0
                current_date = date_begin
                while current_date < today:
                    current_date += timedelta(days=1)
                    if current_date.isoweekday() not in [6, 7]:  # 6:周六, 7:周日
                        workdays += 1
                
                # 获取值日组数据
                duty_groups = duty_table.get("duty", {})
                num_groups = len(duty_groups)
                if num_groups == 0:
                    self.duty_projects = "--"
                    self.duty_names = "未设置值日组"
                    return
                    
                # 计算今天的值日组索引 (1-based)
                group_index = (workdays % num_groups) + 1
                group_key = str(group_index)
                today_duty = duty_groups.get(group_key, {})
                
                for project, names in today_duty.items():
                    self.duty_projects += project + "\n"
                    self.duty_names += " ".join(names) + "\n"
                    
        except Exception as e:
            self.duty_projects = "--"
            self.duty_names = f"计算错误: {str(e)}"

    def update_Widgets(self, cho=None):
        """更新课程表显示（使用缓存数据）"""
        if cho is not None:
            a = main.convert_widget(-1)
            if a == "close":
                return

        # 使用缓存的数据更新UI
        if self.dp_info == {} or self.dp_info["tom"] != 'True':
            if not self.today_classes:
                self.Widgets_ORD.setText("今日")
                self.Widgets.setText("全天无课")
            else:
                self.Widgets_ORD.setText(self.class_ord_text)
                self.Widgets.setText(self.class_text)
        else:
            if not self.today_classes:
                self.Widgets_ORD.setText("无课")
            else:
                self.Widgets_ORD.setText(self.class_text)

            if not self.tomorrow_classes:
                self.Widgets.setText("无课")
            else:
                self.Widgets.setText(self.tomorrow_text)

    def update_duty(self):
        """更新值日生显示（使用缓存数据）"""
        self.duty_project_widget.setText(self.duty_projects)
        self.duty_name_widget.setText(self.duty_names)

    def update_countdown(self):
        """更新倒计时，修复归零时无法重启的问题"""
        try:
            now = datetime.now()
            current_datetime = datetime.combine(now.date(), now.time())

            # 验证当前课程时间有效性
            if current_widget is None and guo_widget:
                time_parts = guo_widget.split('-')
                if len(time_parts) != 2:
                    raise ValueError(f"无效的下课时间格式: {guo_widget}")
                start_datetime = datetime.combine(now.date(), datetime.strptime(time_parts[0], '%H:%M').time())
                end_datetime = datetime.combine(now.date(), datetime.strptime(time_parts[1], '%H:%M').time())
            elif current_widget:
                time_parts = current_widget[1].split('-')
                if len(time_parts) != 2:
                    raise ValueError(f"无效的上课时间格式: {current_widget[1]}")
                start_datetime = datetime.combine(now.date(), datetime.strptime(time_parts[0], '%H:%M').time())
                end_datetime = datetime.combine(now.date(), datetime.strptime(time_parts[1], '%H:%M').time())
            else:
                print("当前无课程")
                self.stop_countdown()  # 停止计时器
                return

            self.start_datetime = start_datetime
            self.end_datetime = end_datetime

            # 检查时间有效性
            if end_datetime <= start_datetime:
                raise ValueError("结束时间必须晚于开始时间")
                
            # 计算剩余时间并且加上时差
            remaining_time = (end_datetime - current_datetime) + timedelta(seconds=int(config.get("dp_Countdown_Bar_school_lag", 0)))

            if remaining_time.total_seconds() < 0:
                remaining_time = timedelta(seconds=0)
            adjusted_remaining_time = remaining_time    

            # 限制最大显示时间
            max_minutes = 1000
            max_seconds = max_minutes * 60
            
            # 检查是否超过最大时间
            if adjusted_remaining_time.total_seconds() > max_seconds:
                current_time = time.time()
                if not hasattr(self, 'last_refresh_time'):
                    self.last_refresh_time = 0
                if current_time - self.last_refresh_time > 60:
                    self.refresh_and_restart_countdown()
                    self.last_refresh_time = current_time
                else:
                    adjusted_remaining_time = timedelta(seconds=max_seconds)
                    
            # 更新显示
            s = f"{(adjusted_remaining_time.seconds // 60):02}:{(adjusted_remaining_time.seconds % 60):02}"
            self.countdown = s
            self.lingyun_down.setText(s)

            # 计算进度条
            total_duration = (end_datetime - start_datetime).total_seconds()
            if total_duration <= 0:
                self.lingyun_Bar.setVal(0)
                return
                
            next_time = end_datetime
                
            rema = next_time - current_datetime
            remaining_percentage = 100 - (rema.total_seconds() / total_duration) * 100
            remaining_percentage = max(0, min(100, remaining_percentage))
            self.lingyun_Bar.setVal(remaining_percentage)

            # 处理倒计时为0的情况 - 关键修复
            if s == "00:00":
                # print("倒计时归零，触发提醒")
                self.stop_countdown(False)  # 先停止所有计时器
                self.warn_function("alert")
                # 延迟后重启，等待课程数据更新
                QTimer.singleShot(1000, self.refresh_and_restart_countdown)
                    
        except Exception as e:
            print(f"倒计时计算错误: {str(e)}")
            self.lingyun_down.setText("时间错误")
            self.lingyun_Bar.setVal(0)

    def alert(self,st = None,weekday = None):
        global DP_Comonent

        # 调用一次 上下课会被调用
        a = main.convert_widget(-1,weekday)
        if a == "close":
            return

        
          
        if current_widget is None: #下课或者放学
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_Bar_color_up")), QColor(config.get("dp_Countdown_Bar_color_up")))
            if guo_widget != None: # 下课
                self.lingyun_class.setText("课间")
                #self.class_time.start()
                self.start_countdown()
                # 调用下课提醒
                if st != None and config.get("dp_Bell") == "True" and config.get("dp_Switch") == "True":
                    warn.ui("up")
            else: # 放学
                self.class_time.stop()

                self.lingyun_class.setText("暂无课程")
                self.lingyun_down.setText("00:00")
                self.lingyun_Bar.setVal(100)
                # 调用放学提醒
                if st != None and config.get("dp_Bell") == "True" and config.get("dp_Switch") == "True":
                    warn.ui("ls") 

                self.coming_time.start()

                # 提醒值日生
                if config.get("dp_drup_audio") == "True" and st != None:
                    from_time = datetime.strptime(config.get("dp_duty_TimePicker_from"), "%H:%M").time()
                    to_time = datetime.strptime(config.get("dp_duty_TimePicker_to"), "%H:%M").time()
                    now = datetime.now().time()
                    if from_time <= now <= to_time:
                        self.finish_wav = f"{USER_RES}/audio/duty_warn.wav"
                        timer = threading.Timer(int(config.get("dp_audio_s")), self.wav,args =(config.get("dp_Sysvolume_value"), config.get("dp_Sysvolume")))
                        timer.start()
        

        else: # 上课TitleLabel
            self.lingyun_class.setText(current_widget[3])
            self.lingyun_Bar.setCustomBarColor(QColor(config.get("dp_Countdown_Bar_color_down")), QColor(config.get("dp_Countdown_Bar_color_down")))

            self.start_countdown()

            # 调用上课提醒
            if st != None and config.get("dp_Bell") == "True" and config.get("dp_Switch") == "True":
                warn.ui("down")

        
        # print("课程是:today_widget", today_widget)
        # print("当前课程是:current_widget",current_widget)
        # print("课程数量是:course_widget",course_widget)
        # print("课程时间是:time_widget",time_widget)
        # print("过渡时间是:guo_widget",guo_widget)

class ThrottledFunction:
    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.last_execution_time = 0

    def __call__(self, *args, **kwargs):
        now = time.time()
        if now - self.last_execution_time >= self.interval:
            self.last_execution_time = now
            self.func(*args, **kwargs)


# 上下课提醒
'''
class class_warn(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint |Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.move(display_x, 0)

    def ui(self, types):
        if not hasattr(self, 'warn'):  # 检查是否已经加载了UI
            self.warn = uic.loadUi(f'{RES}ui/class_warn.ui', self)
            self.warn.setObjectName('warn')
            self.label = self.findChild(QLabel, "warn_label")
            self.warn_background = self.findChild(QFrame, "warn_background")
            # 窗口在屏幕的位置初始化
            self.DP_x = display_x - self.width()
            self.DP_y = 0
            self.animation_i = display_x - 260
            self.resize(self.width(), display_y)
        

        tcolor = ast.literal_eval(config.get(f"dp_Countdown_color_{types}"))
        wave = WaveAnimation()
        
        if types == "up":
            self.label.setText("下课")
            wave.start(tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")#;border-radius: 10px")
            self.finish_wav = f'{USER_RES}audio/up.wav'
        elif types == "down":
            self.label.setText("上课")
            wave.start(tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")#;border-radius: 10px")
            self.finish_wav = f'{USER_RES}audio/down.wav'
        elif types == "next_down":
            self.label.setText("即将上课")
            wave.start(tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")#;border-radius: 10px")
            self.finish_wav = f'{USER_RES}audio/next_down.wav'
        elif types == "ls":
            self.label.setText("放学")
            wave.start(tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")
            self.finish_wav = f'{USER_RES}audio/up.wav' 

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

        wave.show()


        thread = QThread()
        # 创建一个工作对象用于在新线程中执行任务
        worker = QObject()
        worker.wav = lambda: self.wav(config.get("dp_Sysvolume_value"), config.get("dp_Sysvolume"))
        worker.moveToThread(thread)
        thread.started.connect(worker.wav)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)  # 线程完成后自动清理
        thread.start()

        self.times = QTimer(self)
        self.times.timeout.connect(self.exits)
        self.times.start(2200)

    def wav(self, value, vas):
        if vas == "True":
            devices = AudioUtilities.GetSpeakers()
            clsctx = CLSCTX_ALL
            interface = devices.Activate(IAudioEndpointVolume._iid_, clsctx, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            # 获取当前音量值
            original_volume = volume.GetMasterVolumeLevelScalar()
            # 检查当前静音状态
            was_muted = volume.GetMute()  # 返回一个元组，第一个元素表示是否静音
            volume.SetMute(False, None)
            vs = float(int(value) / 100)
            volume.SetMasterVolumeLevelScalar(vs, None)  # 将音量设置为100
        
        
        wave_obj = sa.WaveObject.from_wave_file(self.finish_wav)# 读取 WAV 文件
        play_obj = wave_obj.play()# 播放 WAV 文件
        play_obj.wait_done()# 等待播放完成
        
        if vas == "True":
            volume.SetMasterVolumeLevelScalar(original_volume, None)
            volume.SetMute(bool(was_muted), None)

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

        self.animations.start()
        self.animation_rects.start()
class waveEffect(QWidget):
    def __init__(self, color="#00FF00", duration=2200, start_delay=275):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._radius = 0
        self.duration = duration
        self.color = QColor(color)
        self.setGeometry(QApplication.primaryScreen().geometry())
        QTimer.singleShot(start_delay, self.showAnimation)

    @pyqtProperty(int)
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update()

    def showAnimation(self):
        self.animation = QPropertyAnimation(self, b'radius')
        self.animation.setDuration(self.duration)
        self.animation.setStartValue(50)
        self.animation.setEndValue(max(self.width(), self.height()) * 1.7)
        self.animation.setEasingCurve(QEasingCurve.InOutCirc)
        self.animation.start()

        self.fade_animation = QPropertyAnimation(self, b'windowOpacity')
        self.fade_animation.setDuration(self.duration - self.duration // 5)
        self.fade_animation.setKeyValues([(0, 0), (0.06, 0.9), (1, 0)])
        self.fade_animation.setEasingCurve(QEasingCurve.InOutCirc)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        self.DP_x = display_x - 130 #165
        self.DP_y = display_y // 2 #(display_y - 342) // 2 + 12
        loc = QPoint(self.DP_x, self.DP_y)
        painter.drawEllipse(loc, self._radius, self._radius)

    def closeEvent(self, event):
        self.deleteLater()
        self.hide()
        event.ignore()
'''

class WavWorker(QObject):
    """专门用于处理音频播放的工作对象，避免在主线程中阻塞UI"""
    finished = pyqtSignal()  # 添加finished信号
    
    def __init__(self, finish_wav, volume_value, volume_enabled):
        super().__init__()
        self.finish_wav = finish_wav
        self.volume_value = volume_value
        self.volume_enabled = volume_enabled

    def run(self):
        """执行音频播放的方法"""
        original_volume = None
        was_muted = None
        volume = None
        
        try:
            if self.volume_enabled == "True":
                devices = AudioUtilities.GetSpeakers()
                clsctx = CLSCTX_ALL
                interface = devices.Activate(IAudioEndpointVolume._iid_, clsctx, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                # 获取当前音量值
                original_volume = volume.GetMasterVolumeLevelScalar()
                # 检查当前静音状态
                was_muted = volume.GetMute()
                volume.SetMute(False, None)
                vs = float(int(self.volume_value) / 100)
                volume.SetMasterVolumeLevelScalar(vs, None)
            
            # 播放音频
            wave_obj = sa.WaveObject.from_wave_file(self.finish_wav)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            
        except Exception as e:
            print(f"音频播放错误: {str(e)}")
        finally:
            # 恢复原始音量设置
            if self.volume_enabled == "True" and volume:
                try:
                    volume.SetMasterVolumeLevelScalar(original_volume, None)
                    volume.SetMute(bool(was_muted), None)
                except Exception as e:
                    print(f"恢复音量设置错误: {str(e)}")
            
            self.finished.emit()  # 发射完成信号

class class_warn(QWidget):
    def __init__(self):
        super().__init__()
        # 确保display_x和display_y已定义
        self.display_x = QApplication.primaryScreen().geometry().width()
        self.display_y = QApplication.primaryScreen().geometry().height()
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | 
                          Qt.X11BypassWindowManagerHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(self.display_x, 0)
        self.times = None  # 初始化定时器变量

    def ui(self, types):
        if not hasattr(self, 'warn'):  # 检查是否已经加载了UI
            self.warn = uic.loadUi(f'{RES}ui/class_warn.ui', self)
            self.warn.setObjectName('warn')
            self.label = self.findChild(QLabel, "warn_label")
            self.warn_background = self.findChild(QFrame, "warn_background")
            # 窗口在屏幕的位置初始化
            self.DP_x = self.display_x - self.width()
            self.DP_y = 0
            self.animation_i = self.display_x - 260
            self.resize(self.width(), self.display_y)
        

        tcolor = ast.literal_eval(config.get(f"dp_Countdown_color_{types}"))
        wave = WaveAnimation()

        # 根据类型设置不同的显示内容
        if types == "up":
            self.label.setText("下课")
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")
            self.finish_wav = f'{USER_RES}audio/up.wav'
        elif types == "down":
            self.label.setText("上课")
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")
            self.finish_wav = f'{USER_RES}audio/down.wav'
        elif types == "next_down":
            self.label.setText("即将上课")
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")
            self.finish_wav = f'{USER_RES}audio/next_down.wav'
        elif types == "ls":
            self.label.setText("放学")
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")
            self.finish_wav = f'{USER_RES}audio/up.wav' 

        wave.start(tcolor[0])    
        wave.show()


        # 淡入动画
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

        # 位置动画
        self.animation_rect = QPropertyAnimation(self, b'geometry')
        self.animation_rect.setDuration(250)
        self.animation_rect.setStartValue(QRect(self.DP_x + 80, self.DP_y, self.width(), self.height()))
        self.animation_rect.setEndValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rect.setEasingCurve(QEasingCurve.InOutCirc)

        self.show()
        self.animation.start()
        self.animation_rect.start()
        wave.show()

        # 使用QThread播放音频，而不是标准库线程
        self.play_audio()

        # 确保定时器在主线程中创建和启动
        if self.times:
            self.times.stop()
        self.times = QTimer(self)  # 明确指定父对象为当前窗口
        self.times.timeout.connect(self.exits)
        self.times.start(2200)

    def play_audio(self):
        """使用QThread播放音频，避免线程问题"""
        # 创建线程和工作对象
        self.audio_thread = QThread()
        self.audio_worker = WavWorker(
            self.finish_wav,
            config.get("dp_Sysvolume_value"),
            config.get("dp_Sysvolume")
        )
        
        # 将工作对象移动到线程
        self.audio_worker.moveToThread(self.audio_thread)
        
        # 连接信号槽
        self.audio_thread.started.connect(self.audio_worker.run)
        self.audio_worker.finished.connect(self.audio_thread.quit)
        self.audio_thread.finished.connect(self.audio_worker.deleteLater)
        self.audio_thread.finished.connect(self.audio_thread.deleteLater)
        
        # 启动线程
        self.audio_thread.start()

    def exits(self):
        if self.times:
            self.times.stop()
        
        # 淡出动画
        self.animations = QPropertyAnimation(self, b'windowOpacity')
        self.animations.setDuration(200)
        self.animations.setStartValue(1)
        self.animations.setEndValue(0)
        self.animations.setEasingCurve(QEasingCurve.OutQuad)

        # 位置动画
        self.animation_rects = QPropertyAnimation(self, b'geometry')
        self.animation_rects.setDuration(250)
        self.animation_rects.setStartValue(QRect(self.DP_x, self.DP_y, self.width(), self.height()))
        self.animation_rects.setEndValue(QRect(self.DP_x + 40, self.DP_y, self.width(), self.height()))
        self.animation_rects.setEasingCurve(QEasingCurve.InOutCirc)

        # 动画完成后关闭窗口
        self.animations.finished.connect(self.close)
        
        self.animations.start()
        self.animation_rects.start()


# 欢迎窗口
class Window(QWidget):#(AcrylicWindow):

    #from qframelesswindow.utils import getSystemAccentColor
    #from qframelesswindow import TitleBar,AcrylicWindow
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        #self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon(f'{RES}ico/LINGYUN.ico'))


        self.load_pages()
        #self.check_for_updates()
    
    def load_pages(self):
        self.welcome_page = QWidget()
        self.setup_page = QWidget()

        self.w = uic.loadUi(f'{RES}ui/welcome_1.ui', self)

        self.stacked_Widget = self.w.findChild(QStackedWidget, 'stackedWidget')
        self.next_button = self.w.findChild(PushButton, 'next_button')
        self.next_button.clicked.connect(self.next_page)
        self.stacked_Widget.setCurrentIndex(0)
    def next_page(self):
        current_index = self.stacked_Widget.currentIndex()
        #print(current_index)
        if current_index != 3:
            self.stacked_Widget.setCurrentIndex(current_index + 1)
            if current_index == 2:
                self.next_button.setText('完成')
        else:
            try:
                # 尝试创建或打开注册表键
                registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\LingYunTimes')
                # 设置值
                reg.SetValueEx(registry_key, "welcome", 0, reg.REG_SZ, "True")
                # 如果需要，可以在这里添加成功消息
                # QMessageBox.information(self, '成功', '写入注册表成功！')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'写入注册表失败：{e}')
            finally:
                # 关闭注册表键
                if 'registry_key' in locals():
                    reg.CloseKey(registry_key)
            main.init()
            self.hide()
            tops.setting_show()

# 托盘右键菜单
class SystemTrayMenus(SystemTrayMenu):
    exitSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.black_screen_window = None  # 新增：用于记录黑屏窗口实例

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(f'{RES}ico/LINGYUN.ico'), self)
        self.tray_icon.setToolTip('凌云班级组件')
        
        menu = SystemTrayMenu()
        settings_action = Action(FluentIcon.SETTING,'设置', self)
        settings_action.triggered.connect(self.setting_show)

        black_screen_action = Action('息屏显示', self)
        black_screen_action.triggered.connect(lambda: self.show_black_screen(False))
        
        black_screen = Action(FluentIcon.HOME_FILL,'息屏(不带时间)', self)
        black_screen.triggered.connect(lambda: self.show_black_screen(True))

        restart = Action(FluentIcon.UPDATE,'重启本软件', self)
        restart.triggered.connect(restart_program)

        helps = Action(FluentIcon.HELP,'帮助与支持', self)
        helps.triggered.connect(lambda: webbrowser.open("https://www.yuque.com/yamikani/shrqm0/zlb4xtflki2flnw2"))
        

        quit_action = Action(FluentIcon.CLOSE,'退出', self)
        quit_action.triggered.connect(self.exit_app)

       
        menu.addAction(settings_action)
        menu.addAction(black_screen)
        menu.addAction(black_screen_action)
        menu.addAction(restart)
        menu.addAction(helps)
        menu.addSeparator()

        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

        # 更新退出信号
        self.exitSignal.connect(self.exit_app)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_black_screen(False)  # 使用新方法管理窗口显示
        elif reason == QSystemTrayIcon.DoubleClick:
            pass

    def show_black_screen(self, notime):
        """管理黑屏窗口的显示，避免重复创建"""
        # 如果窗口不存在或已关闭，则创建新实例
        if not self.black_screen_window or not self.black_screen_window.isVisible():
            self.black_screen_window = BlackScreen(notime)
            #self.black_screen_window.initUI(notime)  # 显式调用初始化
            self.black_screen_window.showFullScreen()
        else:
            # 若窗口存在则激活并前置显示
            self.black_screen_window.showNormal()
            self.black_screen_window.raise_()
            self.black_screen_window.activateWindow()
            self.black_screen_window.showFullScreen()
            DP_Comonent.dc_dp("open")            
            self.black_screen_window.nest_window()
            self.black_screen_window.nest_window2()

    def setting_show(self):
        global settings_window   
        # not hasattr(self, 'settings_window') 
        if 'settings_window' not in globals():

            settings_window = MainWindow()
            screen_geometry = QGuiApplication.primaryScreen().geometry()  # 获取屏幕的几何信息
            display_x = screen_geometry.width()  # 屏幕宽度
            display_y = screen_geometry.height()  # 屏幕高度  
            window_width = self.width()
            window_height = self.height()
            x = (display_x - window_width) / 3
            y = (display_y - window_height) / 3
            settings_window.move(x, y)
        settings_window.show()
        settings_window.showNormal()
        settings_window.raise_()
        settings_window.activateWindow()

    def exit_app(self):
        global tops,clock,DP_Comonent
    
        if tops and tops.tray_icon:
            tops.tray_icon.hide()

        clock.animation_hide.start()
        DP_Comonent.animation_rect_hide.start() 

        # 停止监听器线程
        theme_manager.themeListener.terminate()
        theme_manager.themeListener.deleteLater()

        QTimer.singleShot(500, lambda: QApplication.quit())

# 配置信息值处理
class ly_ConfigHandler(ConfigHandler):
    def setup_mappings(self):
        super().setup_mappings()
        # 配置映射关系
        self.mappings["handlers"]["default_dsc_xy"] = self._handle_reset_dsc_xy  # 绑定到处理函数
        self.mappings["immediate_returns"].add("default_dsc_xy")  # 标记为立即返回
        self.mappings["handlers"]["dsc_Switch"] = self._dsc_Switch
        self.mappings['handlers']['dsc_lock'] = self._dsc_lock
        self.mappings["handlers"]["dsc_Typeface"] = self._dsc_Typeface
        self.mappings["handlers"]["dsc_Typeface_size"] = self._dsc_Typeface_size
        self.mappings["handlers"]["default_dsc_font"] = self._handle_reset_dsc_font
        self.mappings["immediate_returns"].add("default_dsc_font")
        self.mappings["handlers"]["dsc_put"] = self._dsc_put
        self.mappings["handlers"]["dsc_Color"] = self._dsc_Color
        self.mappings["handlers"]["dsc_tran"] = self._dsc_tran
        self.mappings["handlers"]["dsc_halo_switch"] = self._dsc_halo
        self.mappings["handlers"]["dsc_length"] = self._dsc_length
        self.mappings["handlers"]["lot_Switch"] = self._lot_Switch
        self.mappings["handlers"]["lot_pin"] = self._lot_pin

    
    # 具体处理函数
    def _handle_reset_dsc_xy(self):
        """处理dsc_x和dsc_y的重置逻辑"""

        # 1. 写入注册表：将dsc_x和dsc_y设为-1
        registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, self.registry_path)
        
        reg.SetValueEx(registry_key, "dsc_x", 0, reg.REG_SZ, "-1")
        reg.SetValueEx(registry_key, "dsc_y", 0, reg.REG_SZ, "-1")
        reg.CloseKey(registry_key)        
        self.config["dsc_x"] = "-1"        
        self.config["dsc_y"] = "-1"
        
        # 2. 通知Desktop_shortcut_component
        desk_short.handle_update("default_xy")
    
    def _dsc_Switch(self,value):
        """处理dsc_Switch的逻辑"""
        config["dsc_Switch"] = str(value)
        desk_short.handle_update("switch",value)
        controls = [
                settings_window.dsc_lock_button,
                settings_window.default_dsc_xy_PushButton,
                settings_window.dsc_Typeface_button,
                settings_window.default_dsc_font_PushButton,
                settings_window.dsc_put_button,
                settings_window.dsc_Color_button,
                settings_window.dsc_tran_Slider,
                settings_window.dsc_short_button,
                settings_window.dsc_addexe_button,
                settings_window.dsc_update_short_button,
                settings_window.dsc_MoveTeacherFile_button
            ]
        if value == "False":
            for control in controls:
                if control is not None:
                    control.setDisabled(True)
        else:
            for control in controls:
                if control is not None:
                    control.setEnabled(True)

    def _dsc_lock(self,value=None):
        """处理dsc_lock的逻辑"""
        config["dsc_lock"] = str(value)
        desk_short.handle_update("lock",value)

    def _dsc_Typeface(self,value):
        """处理dsc_Typeface的逻辑"""
        config["dsc_Typeface"] = str(value)

    def _dsc_Typeface_size(self,value):
        """处理dsc_Typeface_size的逻辑"""
        config["dsc_Typeface_size"] = str(value)

    def _handle_reset_dsc_font(self):
        """处理dsc_font的重置逻辑"""
        # 1. 写入注册表：将dsc_font设为默认值
        registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, self.registry_path)
        
        # 写入dsc_font
        reg.SetValueEx(registry_key, "dsc_Typeface", 0, reg.REG_SZ, "")
        reg.SetValueEx(registry_key, "dsc_Typeface_size", 0, reg.REG_SZ, "15")
        reg.CloseKey(registry_key)
        config["dsc_Typeface"] = ""
        config["dsc_Typeface_size"] = "15"

        
        # 2. 通知Desktop_shortcut_component 
        desk_short.handle_update("default_font")

    def _dsc_put(self,value):
        """处理dsc_put的逻辑"""
        config["dsc_put"] = str(value)
        QTimer.singleShot(100, lambda: desk_short.handle_update("put",value))
        
    def _dsc_Color(self,value):
        config["dsc_Color"] = str(value)
        desk_short.handle_update("color",value)

    def _dsc_tran(self,value):
        config["dsc_tran"] = str(value)
        desk_short.handle_update("tran",value)
        settings_window.dsc_tran_BodyLabel.setText(f"{value}")

    def _dsc_halo(self,value):
        config["dsc_halo_switch"] = str(value)
        desk_short.handle_update("halo",value)

    def _dsc_length(self,value):
        config["dsc_length"] = str(value)
        settings_window.dsc_length_BodyLabel.setText(value)        
        desk_short.handle_update("length",value)

    def _lot_Switch(self,value):
        config["lot_Switch"] = str(value)
        Lottery.handle_update("switch",value)

    def _lot_pin(self,value):
        config["lot_pin"] = str(value)
        Lottery.handle_update("pin",value)

class AddNewExeDialog(QWidget):
    """添加新的EXE快捷方式对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        # 用于窗口拖动
        self.dragging = False
        self.offset = QPoint()
    def initUI(self):
        
        self.setWindowTitle("添加新的EXE快捷方式")
        self.setGeometry(display_x / 2 - 200, display_y / 2 - 100, 400, 200)
        # 设置窗口属性 - 去掉标题栏
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowIcon(QIcon(f'{RES}ico/LINGYUN.ico'))
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # 内边距
        self.setLayout(main_layout)

        # EXE文件选择
        exe_layout = QHBoxLayout()
        icon_layout = QHBoxLayout()

        self.exe_path_input = LineEdit(self)
        self.exe_path_input.setPlaceholderText("选择EXE文件...")
        self.exe_path_button = PushButton("浏览", self)
        self.exe_path_button.clicked.connect(self.browse_exe_file)
        exe_layout.addWidget(self.exe_path_input)
        exe_layout.addWidget(self.exe_path_button)
        main_layout.addLayout(exe_layout)
        
        self.default_name = LineEdit(self)
        self.default_name.setPlaceholderText("默认快捷方式名称(先选择exe文件)...")
        main_layout.addWidget(self.default_name)

        # 图标选择
        self.icon_path_input = LineEdit(self)
        self.icon_path_input.setPlaceholderText("选择图标文件...")
        self.icon_path_button = PushButton("浏览", self)
        self.icon_path_button.clicked.connect(self.browse_icon_file)
        icon_layout.addWidget(self.icon_path_input)        
        icon_layout.addWidget(self.icon_path_button)
        main_layout.addLayout(icon_layout)
        self.icon_path_input.hide()
        self.icon_path_button.hide()

        self.tip_label = BodyLabel("请先选择exe路径")
        main_layout.addWidget(self.tip_label)    

        # 按钮
        button_layout = QHBoxLayout()
        add_button = PushButton("添加", self)
        add_button.clicked.connect(self.accept)
        cancel_button = PushButton("取消", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)



    def browse_exe_file(self):
        """浏览并选择EXE文件"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择EXE文件", "", "exe应用程序(*.exe);;所有文件(*)", options=options)
        if file_path:
            self.exe_path_input.setText(file_path)
            # 自动设置图标路径为同目录下的icon.ico（如果存在）
            temp_dir = os.path.join(USER_RES, "temp_icons")
            os.makedirs(temp_dir, exist_ok=True)
            temp_icon_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.ico")
            if extract_icon_with_key(file_path,1,temp_icon_path):
                self.icon_path_input.setText(temp_icon_path)
                self.tip_label.setText("已自动提取该exe质量最佳图标")
            else:
                self.icon_path_input.clear()
                self.icon_path_input.show()
                self.icon_path_button.show()
                self.tip_label.setText("图标提取失败，请手动选择")
            self.default_name.setText(os.path.splitext(os.path.basename(file_path))[0])

    def browse_icon_file(self):
        """浏览并选择图标文件"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图标文件", "", "图像文件 (*.png *.jpg *.jpeg *.bmp *.ico);;所有文件 (*)", options=options)
        if file_path:
            self.icon_path_input.setText(file_path)

    def accept(self):
        """确认添加快捷方式"""
        exe_path = self.exe_path_input.text().strip()
        icon_path = self.icon_path_input.text().strip()
        
        if not exe_path or not os.path.isfile(exe_path) or not exe_path.endswith('.exe'):
            QMessageBox.warning(self, "无效选择", "请选择有效的EXE文件")
            return

        if not icon_path or not os.path.isfile(icon_path):
            QMessageBox.warning(self, "无效图标", "请选择有效的图像文件作为图标")
            return
        
        desk_short.addNewExeShortcut(exe_path, icon_path, self.default_name.text())

        self.hide()
        self.exe_path_input.clear()
        self.icon_path_input.clear()
        self.default_name.clear()

    def reject(self):
        self.hide()
        self.exe_path_input.clear()
        self.icon_path_input.clear()
        self.default_name.clear()

# 单实例运行
class SingleInstanceApp(QApplication):
    def __init__(self, argv, unique_key):
        super().__init__(argv)
        self.unique_key = unique_key
        self.shared_memory = QSharedMemory(unique_key)
        self.is_single_instance = self.check_single_instance()
        self.allow_shutdown = False

    def check_single_instance(self):
        """检查是否为单实例运行"""
        # 尝试附加到已有的共享内存
        if self.shared_memory.attach():
            # 附加成功，说明已有实例在运行
            return False
        
        # 尝试创建共享内存
        if self.shared_memory.create(1):
            # 创建成功，是第一个实例
            return True
        else:
            # 创建失败，可能是权限问题或其他错误
            return False
        



# 云获取提醒
'''class Yun_warn(QWidget):
    def __init__(self):
        super().__init__()
        # 设置窗口无边框和窗口背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.init()

    def init(self):
        self.yun_warn = uic.loadUi("Resource/ui/yun_warn.ui",self)

        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度
        self.move((display_x-405),(display_y-130))

        self.label = self.yun_warn.findChild(QLabel, 'label')
        self.warn_background = self.yun_warn.findChild(QWidget, 'warn_background')
        self.IconInfoBadge = self.yun_warn.findChild(IconInfoBadge, 'IconInfoBadge')
        self.IndeterminateProgressBar = self.yun_warn.findChild(IndeterminateProgressBar, 'IndeterminateProgressBar')

        self.show()

    def warn_update(self, state,text): # 更新云获取状态
        self.label.setText(text)
        if state == "Wait":
            self.IndeterminateProgressBar.show()
            self.IconInfoBadge.warning(FluentIcon.CANCEL_MEDIUM)
            self.IconInfoBadge.setStyleSheet("background-color: blue;")
            self.warn_background.setStyleSheet("background-color: rgb(255, 244, 206);border-radius: 12px")
        elif state == "Success":
            self.IndeterminateProgressBar.hide()
            self.IconInfoBadge.success(FluentIcon.ACCEPT_MEDIUM)
            self.warn_background.setStyleSheet("background-color: rgb(223, 246, 221);border-radius: 12px")
        elif state == "Error":
            self.IndeterminateProgressBar.hide()
            self.IconInfoBadge.error(FluentIcon.CANCEL_MEDIUM)
            self.warn_background.setStyleSheet("background-color: rgb(253, 231, 233);border-radius: 12px")

    def edit(self):
        self.close()
        #timer = threading.Timer(0.5, self.hide)
        #timer.start()
'''

# 获取启动参数
def get_argument():
    if len(sys.argv) > 1:
        arg = sys.argv[1:]
        return arg
    else:
        return None

def is_system_shutting_down():
    # 检查系统是否正在关机
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'shutdown':
            #print("System is shutting down.")
            return True
    #print("System is not shutting down.")
    return False

# 开发环境&打包环境
def is_frozen():
    if sys.argv[0].endswith('.exe'):
        return True
    else:
        return False

def restart_program():
    global tops, clock, DP_Comonent
    
    # 停止并清理主题监听器
    if theme_manager and theme_manager.themeListener:
        theme_manager.themeListener.terminate()
        theme_manager.themeListener.wait()
        theme_manager.themeListener.deleteLater()
        theme_manager.themeListener = None
    
    if tops and tops.tray_icon:
        tops.tray_icon.hide()

    clock.animation_hide.start()
    DP_Comonent.animation_rect_hide.start()
    


    '''if is_frozen():
        # 打包环境,executable是当前可执行文件的路径
        executable = os.path.abspath(sys.argv[0])     
        args = [executable] + sys.argv[1:]
        subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)            
    else:
        # 开发环境
        executable = sys.executable
        script_path = os.path.abspath(sys.argv[0])
        args = [executable, script_path] + sys.argv[1:]
    

    def perform_restart():
        if is_frozen():
            # 打包环境
            # subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)
            QTimer.singleShot(100, QApplication.quit)
        else:
            # 开发环境
            os.execl(executable, *args)
    '''
    def perform_restart():
        executable = sys.executable
        script_path = os.path.abspath(sys.argv[0])
        args = [executable, script_path] + sys.argv[1:]
        os.execl(executable, *args)

    # 给动画足够的时间完成
    QTimer.singleShot(500, perform_restart)

def check_component_in_ui(ui_file_path, component_name):
    """检查UI文件中是否存在特定名称的组件
    
    Args:
        ui_file_path: UI文件路径
        component_name: 要检查的组件名称（objectName属性）
        
    Returns:
        True if 组件存在, False otherwise
    """
    try:
        tree = ET.parse(ui_file_path)
        root = tree.getroot()
        
        # 在UI文件中查找具有指定objectName的widget
        for widget in root.findall(".//widget"):
            obj_name = widget.get("name")
            if obj_name == component_name:
                return True
                
        # 检查layout和spacer等其他组件类型
        for item in root.findall(".//layout") + root.findall(".//spacer"):
            obj_name = item.get("name")
            if obj_name == component_name:
                return True
                
        return False
    except Exception as e:
        print(f"Error reading UI file: {e}")
        return False

# 去掉路径字符串中的最后一个文件夹
def remove_last_folder(path_str,new_file_name="LingYun_Class_Widgets.exe"):
    """
    移除路径中的最后一个文件夹，并添加新的文件名
    
    参数:
    path_str (str): 原始路径，如 "C:/Users/username/Documents/project/data"
    new_file_name (str): 要添加的文件名，如 "LingYun_Class_Widgets.exe"
    
    返回:
    str: 处理后的完整路径，如 "C:/Users/username/Documents/project/LingYun_Class_Widgets.exe"
    """
    # 1. 获取父目录（脱掉最后一个文件夹）
    parent_dir = os.path.dirname(os.path.normpath(path_str))
    
    # 2. 在父目录中添加新的文件名
    new_path = os.path.join(parent_dir, new_file_name)
    
    return new_path

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
    #app = QApplication(sys.argv)
    app = SingleInstanceApp(sys.argv, UNIQUE_KEY)


    if not app.is_single_instance:
        # 弹出提示对话框
        QMessageBox.critical(None, "凌云班级组件正在运行", "提示：该程序已在运行中，请不要重复启动")
        sys.exit(1)
        
    app.setQuitOnLastWindowClosed(False)
    
    arg = get_argument()
    '''
    if arg and arg[0] == "/update":
        # 0:zip路径 1:新路径 2:旧版本号 3:新版本号
        #window = install_ly.UpdateWindow([tempfile.gettempdir() + "/LingYun/Temp.zip", arg[1], arg[2], Version])
        pass
    else:
    '''
    main = Initialization()
    if os.path.exists(USER_RES) and os.path.isdir(USER_RES):
        main.init()
    else:
        #QMessageBox.critical(None, "警告", "用户资源文件夹不存在或损坏！即将使用默认资源。")
        os.makedirs(USER_RES, exist_ok=True)
        shutil.copytree("LingYun_Profile", USER_RES, dirs_exist_ok=True)
        main.init()
    sys.excepthook = main.handle_exception
    


    # 处理/clean参数
    if arg and arg[0] == "/clean":
        QTimer.singleShot(3000, lambda: shutil.rmtree(tempfile.gettempdir() + "/LingYun"))

    sys.exit(app.exec_())