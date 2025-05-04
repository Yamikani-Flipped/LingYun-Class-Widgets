# -*- coding: utf-8 -*-
import sys, os, logging, winreg as reg, webbrowser, warnings, json,threading,ast,time,requests,simpleaudio as sa,yaml,shutil,psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime,timedelta
from qfluentwidgets import (
    FluentWindow,FluentIcon,SubtitleLabel,Slider,Action,SystemTrayMenu,PushButton,
    SpinBox,NavigationItemPosition,InfoBarIcon,TeachingTip,BodyLabel,SwitchButton,
    TransparentPushButton,SystemThemeListener,isDarkTheme,CardWidget,TableWidget,
    setThemeColor,setTheme,SmoothScrollArea,TitleLabel,ProgressBar,StrongBodyLabel,
    MessageBox,Dialog,ListWidget,TextEdit,ComboBox,TimePicker,PrimaryPushButton,
    CalendarPicker,LineEdit,PasswordLineEdit,IconInfoBadge,IndeterminateProgressBar,
    Flyout,FlyoutAnimationType,Theme,qconfig,RadioButton)
from qframelesswindow.utils import getSystemAccentColor
from qframelesswindow import TitleBar,AcrylicWindow
from packaging import version
from plyer import notification

"""from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes"""


warnings.filterwarnings("ignore", category=DeprecationWarning) # 忽略警告
Version = '1.5.11'
Version_Parse = version.parse(Version)
# 获取当前完整路径,获取当前文件名（os.path.basename(sys.argv[0])获得的是exe名字）
script_dir = sys.argv[0].replace(os.path.basename(sys.argv[0]),"")
script_full_path = sys.argv[0]
os.chdir(script_dir)# 切换工作目录





# 初始化程序整体
class Initialization():
    def __init__(self):
        pass
        #self.init()
    def init(self):
        global theme_manager,theme,clock,tops,warn,DP_Comonent,Ripple,gl_weekday,cloud_sync,adj_weekday#,yun_warn
        


        # 检测是否完成云同步变量
        cloud_sync = False

        # 调课的星期
        adj_weekday = 0

        gl_weekday = str(datetime.now().weekday() + 1)

        # 初始化数据
        self.get_datas()

        # 初始化日志记录器
        #if config.get("print_log") == "True":
        self.logger = self.save_logger("Resource/log")

        if self.welcome() == False:
            welcome = Window()
            welcome.show()
            return



        # 云版本号
        url = "https://lingyun-6e2.pages.dev/config_public.json"
        self.fetch_json(url, self.yun_verison_data)

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

        if os.path.exists(f"Resource/ui/dp/{config.get('dp_choose')}") == False:
            config['dp_choose'] = "class_dp0.ui"
            config['dp_display_edge'] = '510'
            self.write_to_registry("dp_choose","class_dp0.ui")
            self.write_to_registry("dp_display_edge","510")

            




    
        # 创建托盘图标
        tops = SystemTrayMenus()
        tops.create_tray_icon()
        # 创建桌面组件
        DP_Comonent = Desktop_Component()
        warn = class_warn()
        Ripple = RippleEffect()
        # 连接Sender对象的自定义信号到Receiver对象的槽函数
        theme_manager.customSignal.connect(DP_Comonent.TOPIC)


    def get_datas(self):
        global lists,config,class_weekday,gl_weekday,class_dan,up_work,default_class

        up_work = False
        
        # 默认课程表和时间
        default_class = [["07:20-08:00","07:20-07:50"],{"1":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"2":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"3":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"4":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"5":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"6":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"7":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}]},{"1":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"2":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"3":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"4":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"5":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"6":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}],"7":[{"上午":["","","",""]},{"下午":["","","",""]},{"晚上":[""]}]},{"default":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"1":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"2":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"3":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"4":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"5":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"6":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"7":{"上午":["07:50-08:35","08:45-09:30","09:50-10:35","10:45-11:30"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]}},{"default":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"1":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"2":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"3":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"4":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"5":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"6":{"上午":["08:00-08:45","08:55-09:40","10:10-10:55","11:10-11:50"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]},"7":{"上午":["07:50-08:35","08:45-09:30","09:50-10:35","10:45-11:30"],"下午":["14:10-14:50","15:05-15:45","15:55-16:35","16:45-17:25"],"晚上":["18:30-20:30"]}},{"1":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"2":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"3":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"4":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"5":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"6":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]},"7":{"擦黑板":[""],"倒垃圾":[""],"班级扫地":["",""],"班级拖地":["",""],"走廊打扫":[""],"包干区":["",""]}}]
        class_weekday = "通用"
        class_dan = ""

        # 默认数据时钟数据
        data = {'comboBox': '桌面',
                'x' : '700',
                'y' : '100',
                'width' : '200',
                'height' : '100',
                'fontSize' : '72',
                #'textColor' : '255,255,255,255',
                'fontname' : '',
                'update' : '700',
                'Penetrate' : 'True',
                }
        
        #新数据格式  “dp”为桌面组件的数据，“set”为设置数据，clock为时钟数据
        default_config = {'dp_Switch': 'True', #是否开启桌面组件
                  'dp_Pin' : 'False', #是否置顶
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

                  }
        
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

    def load_data(self):
        global class_all,class_ORD_Filtration, class_table, class_time, duty_table, class_dan,class_table_a,class_table_b,class_time_a,class_time_b,class_time_a,class_time_b

        # 从文件加载数据 json
        class_all = self.loads_from_json(-1)
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


    def fetch_json(self,url, callback):
        #global yun_warn
        #在一个新线程中获取 JSON 数据
        def fetch():
            #global yun_warn
            flag = False
            try:
                response = requests.get(url)  # 发送 GET 请求
                if response.status_code == 200:  # 检查请求是否成功
                    data = response.json()  # 解析 JSON 数据
                    callback(data)  # 调用回调函数处理数据
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
            if flag == False and config.get("check_net") == "True":
                notification.notify(
                    title = '网络连接失败，请检查网络！',
                    message = '如果要禁用此通知，请前往“设置>软件设置”进行修改。如果网络已连接，请检查是否打开了VPN，防火墙是否拦截。',

                    app_name='LingYun Class Widgets',
                    app_icon='Resource/ico/LINGYUN.ico',  # 自定义图标路径
                    timeout = 5,
                )
        # 创建并启动线程
        thread = threading.Thread(target=fetch)
        thread.start()

    def yun_verison_data(self,data):
        global Version_Parse,yun_version

        # 云版本号
        j = json.dumps(data, indent=4, ensure_ascii=False)
        yun_version = version.parse(ast.literal_eval(j)['version'])

        if Version_Parse < yun_version and config.get("check_update") == "True": # 有新版本
            notification.notify(
                    title = '凌云班级组件有新版本啦！',
                    message = f'建议及时更新，以获取最佳体验，请前往设置中查看！(新版本号为{yun_version})',
                    app_name='LingYun Class Widgets',
                    app_icon='Resource/ico/LINGYUN.ico',  # 自定义图标路径
                    timeout = 2,
                )
        elif Version_Parse == yun_version:
            pass

    def yun_json_data(self,data):
        global DP_Comonent, warn, Ripple#,yun_warn
        # 云同步json数据
        j = json.dumps(data, indent=4, ensure_ascii=False)
        js = ast.literal_eval(j)
        directory = 'Resource\\jsons'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, "default.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)
        self.load_data(js)
        #yun_warn.warn_update("Success","云同步成功")
        #yun_warn.edit()

    def yun_config_class_data(self,data):
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

    def yun_config_data(self,data):
        # 云同步配置数据
        global clock
        j = json.dumps(data, indent=4, ensure_ascii=False)
        js = ast.literal_eval(j)
        for key in js:
            config[key] = js[key]
            self.write_to_registry(key, js[key])
            # 更新配置(暂时不实时，没必要，也会有问题)
            #clock.update_settings(key) # 更新时钟设置
        

    def yun_timeleg_data(self,data):
        # 云时间表时差
        j = json.dumps(data, indent=4, ensure_ascii=False)
        yun_timeleg = ast.literal_eval(j)['time']
        config["dp_Countdown_Bar_school_lag"] = yun_timeleg
        self.write_to_registry("dp_Countdown_Bar_school_lag", yun_timeleg)

    def convert_widget(self,cho=-1): # cho为选择模式，-1为全部，1为获取今日课表信息，2为获取当前课表信息
        global today_widget,current_widget,course_widget,time_widget,guo_widget,adj_weekday
        if adj_weekday == 0:
            day = datetime.now().weekday() + 1
        else:
            day = adj_weekday
        ############################
        ct = class_time[str(day)]
        ############################

        # 定义
        today_widget = []  
        current_widget = None
        course_widget = {}
        time_widget = {}
        guo_widget = ""

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
                                today_widget.append([-1, time, time_of_day, cls])
                            else:
                                today_widget.append([s, time, time_of_day, cls])
                                s += 1
        
        # 2.获得当前所在的时间段和当前课程current_widget
        """if cho == -1 or cho == 2:
            current_time = datetime.now().time()
            for item in today_widget:
                start_time, end_time = item[1].split('-')
                start_time = datetime.strptime(start_time, "%H:%M").time()
                end_time = datetime.strptime(end_time, "%H:%M").time()
                if start_time <= current_time <= end_time:
                    current_widget = item
                    break
            else:
                current_widget = None # 当前没在任何时间段内，也就是下课"""
        if cho == -1 or cho == 2:
            lag = int(config.get("dp_Countdown_Bar_school_lag")) # 从配置中获取时差
            # 获取当前时间并补全日期信息（这里我们简单地使用今天的日期）
            current_datetime = datetime.combine(datetime.today().date(), datetime.now().time())
            adjusted_datetime = current_datetime # 初始化调整后的时间
            if lag < 0:
                adjusted_datetime = current_datetime + timedelta(seconds=-lag)
            adjusted_time = adjusted_datetime.time() # （可选）提取时间部分
            
            for item in today_widget:
                start_time, end_time = item[1].split('-')
                start_time = datetime.strptime(start_time, "%H:%M").time()
                end_time = datetime.strptime(end_time, "%H:%M").time()
                
                # 注意：这里使用调整后的时间进行比较
                if start_time <= adjusted_time <= end_time:
                    current_widget = item
                    break
            else:
                current_widget = None # 当前没在任何时间段内，也就是下课

        # 3.获取适合读取的课程数量:course_widget
        if cho == -1 or cho == 3 or cho == 4:
            day_schedule = class_table.get(str(day), [])
            for period in day_schedule: # period为一个字典，用于记录每个午段课程数
                j = list(period.keys())[0]
                course_widget[j] = 0
                for time_of_day, classes in period.items():
                    times = ct.get(time_of_day, [])
                    for cls in classes:
                        if cls != "":
                            course_widget[time_of_day] += 1
        
        # 4.获取处理每个午别的起始时间和结束时间time_widget
        if cho == -1 or cho == 4:
            # 初始化结果字典
            time_widget = {key: None for key in course_widget.keys()}
            course_count = {key: 0 for key in course_widget.keys()}
            # 存储时间段的字典
            time_slots = {key: [] for key in course_widget.keys()}
            # 遍历today_widget，记录时间段并计数
            for entry in today_widget:
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
                    time_widget[period] = f'{start_time}-{end_time}'
                else:
                    time_widget[period] = None
        
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

            for i in range(1, len(today_widget)):
                start_time_prev = time_to_minutes(today_widget[i-1][1].split('-')[1])
                start_time_curr = time_to_minutes(today_widget[i][1].split('-')[0])
                period_prev = today_widget[i-1][2]
                period_curr = today_widget[i][2]

                # 如果午别不同，返回None
                if period_prev != period_curr:
                    guo_widget = None
                    continue

                # 检查当前时间是否在过渡时间段内
                if start_time_prev <= current_time_minutes < start_time_curr:
                    guo_widget = today_widget[i-1][1].split('-')[1] + '-' + today_widget[i][1].split('-')[0]
                    break
            if guo_widget == "":
                guo_widget = None

            

        #print("课程是：",today_widget)
        #print("当前课程是：",current_widget)
        #print("课程数量是：",course_widget)
        #print("课程时间是：",time_widget)
        #print("过渡时间是：",guo_widget)
        #print("===============================")

    def white_Widgets(self):
        # 保存课程表和时间到文件
        global class_dan,class_time,class_ORD_Filtration,class_table,class_table_a,class_table_b,class_time_a,class_time_b,duty_table
        try:
            if class_dan == "双周":
                class_time_b = class_time
                class_table_b = class_table
                self.saves_to_json()
                #self.save_to_json(class_table, 'class_table_b.json')
                #self.save_to_json(class_time, 'class_time_b.json')
            else:
                class_time_a = class_time
                class_table_a = class_table
                self.saves_to_json()
                #self.save_to_json(class_table, 'class_table_a.json')
                #self.save_to_json(class_time, 'class_time_a.json')

            #self.save_to_json(class_ORD_Filtration, 'class_ORD_Filtration.json')
            DP_Comonent.update_Widgets(0)
            return None
        except Exception as e:
            return e

    def save_to_json(self, data, filename): #弃用
        global class_dan
        if class_dan == "双周":
            if filename == "class_time.json":
                filename = 'class_time_b.json'
            if filename == "class_table.json":
                filename = 'class_table_b.json'
        else:
            if filename == "class_time.json":
                filename = 'class_time_a.json'
            if filename == "class_table.json":
                filename = 'class_table_a.json'            

        directory = 'Resource\\json'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_json(self, filename, default_data): #弃用
        directory = 'Resource\\json'
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 如果文件不存在，返回默认数据并可能保存默认数据到文件
            #self.save_to_json(default_data, filename)
            return default_data
        
    def loads_from_json(self, index):
        global default_class
        directory = 'Resource\\jsons'

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
            config["dp_widgets"] = config.get("dp_widgets")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_class, f, ensure_ascii=False, indent=4)
            if index == -1:
                return default_class
            else:
                return default_class[index]
            
    
    def saves_to_json(self):
        global class_ORD_Filtration, class_table_a, class_table_b, class_time_a, class_time_b, duty_table
        class_all = [class_ORD_Filtration, class_table_a, class_table_b, class_time_a, class_time_b, duty_table]

        directory = 'Resource\\jsons'
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

    def handle_exception(self,exc_type, exc_value, exc_traceback):
        # 捕获到异常时运行的代码
        #logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        main.logger.error(f"Uncaught exception: {exc_type}\n{exc_value}\n{exc_traceback}")
        theme_manager.themeListener.terminate()
        theme_manager.themeListener.deleteLater()

        w = Dialog("运行出现致命错误", f"错误的详细信息为下，目前无法继续运行，请反馈给开发者。敬请谅解！\n错误日志保存在本目录Resource下的log文件夹中。 \n {exc_value}", None)
        w.yesButton.setText("好")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
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


# 时钟类
class TransparentClock(QMainWindow):
    def __init__(self):#, da tas):
        global week_day_dict,config
        super().__init__()

        self.timer = uic.loadUi('Resource/ui/timerr.ui',self)

        # 设置窗口属性
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 窗口置顶
        if config['comboBox'] == "置顶":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # 鼠标穿透
        if config['Penetrate'] == 'True':
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
 

        
        self.time_label = self.timer.findChild(QLabel, 'time_label')
        self.date_label = self.timer.findChild(QLabel, 'date_label')

        # 设置字体 大小 加粗 颜色 透明度
        time_font = self.font_file("Resource/SFUI.ttc",config["fontname"],config["fontSize"])
        date_font = self.font_file("Resource/MiSans-Bold.ttf",config.get('cl_date_Typeface'), config.get('cl_date_TextSize'))

        
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
    
    def font_file(self,file,font_name,font_size):
        # 加载字体文件datas
        if font_name == "":
            font_id = QFontDatabase.addApplicationFont(file)#"Resource/MiSans-Bold.ttf")  # 替换为你的字体文件路径
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font = QFont(font_families[0], int(font_size),  QFont.Bold)  # 使用加载的字体的第一个字体族，设置大小为20
                else:
                    font = QFont(font_name, int(font_size),  QFont.Bold)  # 如果加载失败，使用默认字体:"字体文件未包含可用字体族"
            else:
                font = QFont(font_name, int(font_size),  QFont.Bold)    # 如果加载失败，使用默认字体:"字体文件加载失败"
        else:
            font = QFont(font_name, int(font_size),  QFont.Bold)
        return font

    def update_time(self):
        global gl_weekday
        if gl_weekday != str(datetime.now().weekday() + 1):
            restart_program()
        
        now = datetime.now()
        self.time_label.setText(now.strftime('%H:%M:%S' if config.get("cl_time_Second") == "True" else '%H:%M'))

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


        self.date_label.setText(formatted_date)

        # 保持日期居中
        if config.get("cl_date_mediate") == "True" and config.get('cl_time_Switch') == "True":
            self.resize(QFontMetrics(self.time_label.font()).horizontalAdvance(self.time_label.text()), self.height())

    def update_settings(self,choose):
        #实时更新
        if choose == "fontSize" or choose == "fontname": 
            font = self.font_file("Resource/SFUI.ttc",config['fontname'],config['fontSize'])
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
            date_font = self.font_file("Resource/MiSans-Bold.ttf",config.get('cl_date_Typeface'),config.get('cl_date_TextSize'))
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

    def closeEvent(self, event: QCloseEvent) -> None:
        #event.accept()
        if not is_system_shutting_down():
            event.ignore()


# 设置窗口
class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.close_event_args = None
        #self.da tas = dat as
        self.addui()
        self.initNavigation()
        self.initWindow()
        #获取系统主题色
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor(), save=False)
    def initNavigation(self):
        #self.addSubInterface(self.main, FluentIcon.HOME, '欢迎')
        self.addSubInterface(self.home, FluentIcon.HISTORY, '时钟设置')
        self.addSubInterface(self.dp_class, FluentIcon.TILES, '桌面课表设置')
        self.addSubInterface(self.classes, FluentIcon.CALENDAR, '课表编辑')
        self.addSubInterface(self.classes_time, FluentIcon.BOOK_SHELF, '时间线管理')
        self.addSubInterface(self.duty, FluentIcon.CALENDAR, '值日表配置')
        self.addSubInterface(self.display, FluentIcon.DEVELOPER_TOOLS, '息屏显示配置')
        self.addSubInterface(self.adjustment, FluentIcon.SETTING, '调课管理')
        
        
        #self.navigationInterface.addSeparator()
        #self.addSubInterface(self.hh, FluentIcon.SETTING, '高级设置')
        
        self.addSubInterface(self.yun, FluentIcon.CLOUD, '集中控制',NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.soft, FluentIcon.SETTING, '软件设置',NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.updates, FluentIcon.UPDATE, '更新日志', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.info, FluentIcon.INFO, '关于', NavigationItemPosition.BOTTOM)
        

        self.stackedWidget.currentChanged.connect(lambda index: self.stacked(index))
    def addui(self):
        try:
            self.home = uic.loadUi('Resource/ui/set_home.ui')
            self.home.setObjectName("home")
            self.updates = uic.loadUi('Resource/ui/set_updates.ui')
            self.updates.setObjectName("updates")
            self.info = uic.loadUi('Resource/ui/set_info.ui')
            self.info.setObjectName("info")
            self.classes = uic.loadUi('Resource/ui/set_classes.ui')
            self.classes.setObjectName("classes")
            self.classes_time = uic.loadUi('Resource/ui/set_classes_time.ui')
            self.classes_time.setObjectName("classes_time")
            self.dp_class = uic.loadUi('Resource/ui/set_dp_class.ui')
            self.dp_class.setObjectName("dp_class")
            self.soft = uic.loadUi('Resource/ui/set_soft.ui')
            self.soft.setObjectName("soft")
            self.display = uic.loadUi('Resource/ui/set_display.ui')
            self.display.setObjectName("display")
            self.duty = uic.loadUi('Resource/ui/set_duty.ui')
            self.duty.setObjectName("duty")
            self.yun = uic.loadUi('Resource/ui/set_yun.ui')
            self.yun.setObjectName("yun")
            self.adjustment = uic.loadUi('Resource/ui/set_adjustment.ui')
            self.adjustment.setObjectName("adjustment")



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

        #self.stackedWidget.currentChanged.connect(lambda: print(self.stackedWidget.currentWidget()))

    def switchTo(self, interface: QWidget) -> None:
        self.stackedWidget.setCurrentWidget(interface, popOut=False)
        #print("切换到", interface.objectName())
        #self.stackedWidget.setCurrentWidget(interface)
        #self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(interface))

    def set_updates(self):
        self.cs = self.updates.findChild(PushButton, 'cs')
        self.cs.hide()
        #self.cs.clicked.connect(lambda :self.Flyout())
    def set_home(self):
        #------设置控件开始--------hide

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
        
        self.dp_Pin_button = self.dp_class.findChild(SwitchButton, 'dp_Pin_button')
        if config.get('dp_Pin') == "True":
            self.dp_Pin_button.setChecked(True)
        else:
            self.dp_Pin_button.setChecked(False)
        self.dp_Pin_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_Pin'))

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
        entries = os.listdir('Resource/ui/dp/')
        self.files = [entry for entry in entries if os.path.isfile(os.path.join('Resource/ui/dp/', entry))]
        
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
        self.version = self.info.findChild(BodyLabel, 'version')
        self.version.setText(f'当前版本：{Version}')
        self.yun_version = self.info.findChild(BodyLabel, 'yun_version')
        self.yun_version.setText(f'最新版本：{yun_version}')

        self.Join_qq = self.info.findChild(PushButton, 'Join_qq')
        self.Join_qq.clicked.connect(lambda :webbrowser.open('https://qm.qq.com/q/KN7UVWFr6C'))
        self.qq_clipboard_button = self.info.findChild(PushButton, 'qq_clipboard_button')
        self.qq_clipboard_button.clicked.connect(self.qq_clipboard)
        self.bilibili_button = self.info.findChild(PushButton, 'bilibili_button')
        self.bilibili_button.clicked.connect(lambda :webbrowser.open('https://space.bilibili.com/627622081'))

        self.github_button = self.info.findChild(PushButton, 'github_button')
        self.github_button.clicked.connect(lambda :webbrowser.open('https://github.com/Yamikani-Flipped/LingYun-Class-Widgets'))

        self.thank_button = self.info.findChild(PushButton, 'thank_button')
        self.thank_button.clicked.connect(lambda:self.error(e="致谢的第三方app及网站。以下为引用列表：\nClass Widgets：1.沿用了部分的ui文件（大部分已做整改）\n2.上下课、即将上课提醒的音频文件的使用\n3.作品中上下课提醒中“波澜”的部分代码的使用。\n\n软件部分图片来自Icons8网站。\n\n同时感谢所有的使用者和智教联盟网站的支持和指导！\n\n相关链接：\n智教联盟：https://forum.smart-teach.cn/\nClass Widgets仓库：https://github.com/Class-Widgets/Class-Widgets\nicons8：https://icons8.com/",msg="致谢",grades=False,vas=True))
    def set_classes(self):
        #------设置课表页面的控件--------
        self.TableWidget = self.classes.findChild(TableWidget, 'TableWidget')
        # 启用边框并设置圆角
        self.TableWidget.setBorderVisible(True)
        self.TableWidget.setBorderRadius(10)
        self.set_table_update()

        # 连接单元格内容改变信号到table_update函数
        self.TableWidget.itemChanged.connect(self.table_update)
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
        self.up_Button.hide()
    def set_classes_time(self):
        #------设置时间线页面的控件--------
        self.TimeWidget = self.classes_time.findChild(ListWidget, 'ListWidget_time')
        self.Time_Widget_update()
        self.TimeWidget.itemClicked.connect(self.click_TimeWidget)
        self.name_edit = self.classes_time.findChild(TextEdit, 'name_edit')
        self.name_edit.setPlaceholderText("请输入")
        self.name_edit.hide()
        self.name_label = self.classes_time.findChild(BodyLabel, 'name_label')
        self.name_label.hide()
        self.name_box = self.classes_time.findChild(ComboBox, 'name_box')
        self.name_box.addItems(["上午","下午","晚上","自定义"])
        self.name_box.currentIndexChanged.connect(self.name_box_changed)
        self.add_button = self.classes_time.findChild(PushButton, 'add_Button')
        self.add_button.clicked.connect(self.add_aptime)
        self.TimePicker_from = self.classes_time.findChild(TimePicker, 'TimePicker_from')
        self.TimePicker_to = self.classes_time.findChild(TimePicker, 'TimePicker_to')
        self.from_time = ""
        self.to_time = ""
        self.add_name = "上午"
        self.TimePicker_from.timeChanged.connect(lambda t: setattr(self, 'from_time', t.toString()))
        self.TimePicker_to.timeChanged.connect(lambda t: setattr(self, 'to_time', t.toString()))
        self.addtime_Button = self.classes_time.findChild(PrimaryPushButton, 'addtime_Button')
        self.addtime_Button.clicked.connect(self.add_time)
        self.add_name_box = self.classes_time.findChild(ComboBox, 'add_name_box')
        self.add_name_box.addItems(self.ap_list)
        self.add_name_box.currentIndexChanged.connect(lambda: setattr(self, 'add_name', self.add_name_box.currentText()))
        self.cancel_Button = self.classes_time.findChild(PushButton, 'cancel_Button')
        self.cancel_Button.clicked.connect(self.cancel_Widget)
        self.del_Button = self.classes_time.findChild(PushButton, 'del_Button')
        self.del_Button.clicked.connect(self.del_Widget)
        self.edit_label = self.classes_time.findChild(SubtitleLabel, 'edit_Label')
        self.edit_label.hide()
        self.CardWidget4 = self.classes_time.findChild(CardWidget, 'CardWidget4')
        self.CardWidget4.hide()
        # 连接itemSelectionChanged信号到槽函数
        self.TimeWidget.itemSelectionChanged.connect(self.update_widgets_visibility)

        self.edit_Button = self.classes_time.findChild(PushButton, 'edit_Button')
        self.edit_Button.clicked.connect(self.edit_time)
        self.TimePicker_from_edit = self.classes_time.findChild(TimePicker, 'TimePicker_from_edit')
        self.TimePicker_to_edit = self.classes_time.findChild(TimePicker, 'TimePicker_to_edit')
        self.from_time_edit = ""
        self.to_time_edit = ""
        self.TimePicker_from_edit.timeChanged.connect(lambda t: setattr(self, 'from_time_edit', t.toString()))
        self.TimePicker_to_edit.timeChanged.connect(lambda t: setattr(self, 'to_time_edit', t.toString()))

        self.Counter_SwitchButton = self.classes_time.findChild(SwitchButton, 'Counter_SwitchButton')
        self.Counter_SwitchButton.checkedChanged.connect(lambda value: self.click_Counter_Button(value))
        self.Counter_SwitchButton.setDisabled(True)

        self.week_ComboBox = self.classes_time.findChild(ComboBox, 'week_ComboBox')
        self.week_ComboBox.addItems(['通用','周一','周二','周三','周四','周五','周六','周日'])
        self.week_ComboBox.currentIndexChanged.connect(self.week_changed)
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
        

        self.duty_Widget.clear()
        self.duty_Widget.itemSelectionChanged.connect(lambda: self.update_duty("duty_widget"))

        #self.duty_Widget.addItems(duty)

        # 选择星期
        self.week_box.addItems(['周一','周二','周三','周四','周五','周六','周日'])
        self.week_box.currentIndexChanged.connect(self.duty_week_changed)
        self.week = datetime.now().weekday()
        self.week_box.setCurrentIndex(datetime.now().weekday())

        self.name_Button.clicked.connect(lambda: self.update_duty('name'))
        self.project_Button.clicked.connect(lambda: self.update_duty('project'))
        self.Add_Button.clicked.connect(lambda: self.update_duty('add_item'))
        self.Del_Button.clicked.connect(lambda: self.update_duty('del_item'))
    def set_display(self):
        self.dp_xiping_button = self.display.findChild(SwitchButton, 'dp_xiping_button')
        if config.get('dp_xiping') == "True":
            self.dp_xiping_button.setChecked(True)
        else:
            self.dp_xiping_button.setChecked(False)
        self.dp_xiping_button.checkedChanged.connect(lambda value: self.update_dp(value,'dp_xiping'))
    def set_Adjustment(self):
        #------调课管理--------
        self.adj_Combobox = self.adjustment.findChild(ComboBox, 'adj_ComboBox')
        self.adj_Combobox.addItems(["默认","星期一","星期二","星期三","星期四","星期五","星期六","星期日"])
        #self.adj_Combobox.setPlaceholderText("请选择调整的星期")# 设置提示文本
        self.adj_Combobox.currentIndexChanged.connect(self.adj_week_changed)
    def adj_week_changed(self, index):
        global adj_weekday,DP_Comonent
        adj_weekday = index
        Initialization.convert_widget(-1)
        DP_Comonent.update_Widgets()
        DP_Comonent.update_duty()
    def SD_changed(self,value):
        global class_table_a, class_table_b, class_time_a, class_time_b
        self.TableWidget.itemChanged.disconnect(self.table_update)
        lists["widgets_on"] = True
        self.TableWidget.clear()
        if value == 0: # 单周
            done, ls = self.convert_table(class_table_a)
            self.widget_time = self.convert_time(class_time_a)
        else: # 双周
            done, ls = self.convert_table(class_table_b)

            self.widget_time = self.convert_time(class_time_b)
        
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


        #self.yun_Button.clicked.connect(self.yun_Button_clicked)
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
    def update_duty(self,choose):
        global DP_Comonent
        if choose == "duty_widget":
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
            names = name.split(" ")
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

        self.duty_Widget.clear()
        self.duty_Widget.addItems(formatted_tasks)

        self.name_Edit.clear()
        self.project_Edit.clear()
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
        
        self.error("需要重启才可以使更改生效。","提示",False,True)
    def update_dp(self,value,choose):
        if choose == "dp_widgets":
            DP_Comonent.lingyun_down.setText("--:--")
            value = self.json_widgets[value] + ".json"
            
            ###########通知主程序更新组件

            #Initialization().load_data()
            #DP_Comonent.alert()
            #DP_Comonent.update_Widgets()
            #DP_Comonent.update_duty()

        if choose == "dp_duty_TimePicker_from":
            value = f"{value.hour()}:{value.minute()}"
        if choose == "dp_duty_TimePicker_to":
            value = f"{value.hour()}:{value.minute()}"

        if choose == "dp_danweekly":
            value = f"{value.year()},{value.month()},{value.day()}"
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

        if choose == "dp_Curriculum_ramp_action" or choose == "dp_countdown_action" or choose == "dp_todayclass_action" or choose == "dp_duty_action":
            return


        if choose == "check_update" or choose == "print_log" or choose == "check_net" or choose == "dp_xiping":
            return

        DP_Comonent.update_ui(value,choose)
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

        
        #for period in class_time:
        #    if old_time_period in class_time[period]:
        #        index = class_time[period].index(old_time_period)
        #        class_time[period][index] = time_period
        #        break
        main.saves_to_json()
        #main.save_to_json(class_time, 'class_time.json')
        self.TimeWidget.clearSelection()
        self.Time_Widget_update()
        self.add_name_box.clear()
        self.add_name_box.addItems(self.ap_list)
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
            #main.save_to_json(class_table, 'class_table.json')
            
            #main.save_to_json(class_time, 'class_time.json')
            self.TimeWidget.clearSelection()
            self.Time_Widget_update()
            #self.set_table_update()
            self.add_name_box.clear()
            self.add_name_box.addItems(self.ap_list)
    def cancel_Widget(self):
        self.TimeWidget.clearSelection()
    def add_time(self):
        
        #print(self.from_time, self.to_time)
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
        #main.save_to_json(class_table, 'class_table.json')
        #main.save_to_json(class_time, 'class_time.json')
        self.Time_Widget_update()
        #self.set_table_update()
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
        """self.ap_list.append(name)
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignCenter)
        self.TimeWidget.addItem(item)"""
        for ins in class_time:
            class_time[ins][name] = ["00:00-00:01"]
        for i in range(1,8):
            class_table[str(i)].append({name:['未设置']})

        main.saves_to_json()
        #main.save_to_json(class_table, 'class_table.json')
        #main.save_to_json(class_time, 'class_time.json')
        
        self.Time_Widget_update()
        self.add_name_box.clear()
        self.add_name_box.addItems(self.ap_list)

        #self.set_table_update()
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
                    restart_program()
                    #theme_manager.themeListener.terminate()
                    #theme_manager.themeListener.deleteLater()
                    #QApplication.quit()
                else:pass
    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('Resource\ico\LINGYUN.ico'))
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
        self.hide()
        event.ignore()

    def startup_program(self, zt, program_path=script_full_path, program_name="LingYun_Class_Widgets"):
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
                        destination_dir = 'Resource\\jsons'
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
            os.startfile('Resource\\jsons')
        elif value == "dp_widgets":
            self.error("重启软件后生效。","提示",False,False)
        elif value == "exescs":
            file_path, _ = QFileDialog.getSaveFileName(self, '保存为CSES通用格式', '', 'CSES文件(*.yaml)')
            if file_path:
                self.json_to_yaml(f'Resource\\jsons\\{config.get("dp_widgets")}',file_path)
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
                        self.yaml_to_json(file_path, f'Resource\\jsons\\{name}.json')
                    except Exception as e:
                        error = e
                        flag = False
                elif self.lcw_Group.checkedButton().text() == "Class Widgets":
                    name = os.path.basename(file_path).split('.')[0]
                    try:
                        self.yaml_to_json_class_widgets(file_path, f'Resource\\jsons\\{name}.json')
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
        all_widgets = os.listdir('Resource/jsons/')
        json_widgets = [f for f in all_widgets if f.endswith('.json')]
        self.json_widgets = [file.replace('.json', '') for file in json_widgets]  # 去掉文件扩展名
        self.dp_chowidgets_box.addItems(self.json_widgets)
        self.dp_chowidgets_box.setCurrentIndex(self.json_widgets.index(config.get("dp_widgets").split(".")[0]))


# 息屏显示
class BlackScreen(QWidget):
    def __init__(self,notime):
        super().__init__()
        self.initUI(notime)

    def initUI(self,notime):
        global DP_Comonent
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
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setWindowFlags(self.windowFlags() | Qt.WindowDoesNotAcceptFocus)
        self.setGeometry(0, 0, w_width, w_height)



        # 创建标签
        self.time_hei = QLabel('00:00:00',self)#, alignment=Qt.AlignCenter)
        
        self.time_hei.setAlignment(Qt.AlignLeft)
        self.time_hei.setGeometry(QRect(int(config['x']), int(config['y']), 500, 500))

        # 设置字体，大小，并加粗
        fonts = self.font_file("Resource/SFUI.ttc",config['fontname'],config['fontSize'])
        #fonts = QFont(dat as['fontname'], int(da tas['fontSize']), QFont.Bold)  # 这里将字体权重设置为Bold
        self.time_hei.setFont(fonts)
        # 设置文本颜色为白色
        self.time_hei.setStyleSheet(f'color:white;')

        
        # 创建按钮并添加到布局中
        self.button = TransparentPushButton(FluentIcon.EMBED.icon(color='#FFFFFF'),"     退出", self)
        self.button.setStyleSheet("""color:#ffffff;""")
        self.button.setGeometry(QRect(w_width-150, w_height-120, 50, 50))        

        """self.zdy_hei = QLabel('',self)
        self.zdy_hei.setAlignment(Qt.AlignRight)
        self.zdy_hei.setGeometry(QRect(int(da tas['x'])-200, int(da tas['y'])+100, 500, 400))
        self.zdy_hei.setFont(fonts)
        self.zdy_hei.setStyleSheet(f'color:white;')"""

        if not notime:
            self.time_hei.show()
        else:
            self.time_hei.hide()
        # 定时器更新时钟
        clock.hide()
        self.uptime()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.uptime)
        self.timer.start(1000)#(int(dat as['update']))

        # 设置样式
        self.setStyleSheet("""QWidget {background-color: black;}""")

        # 连接按钮点击事件
        self.button.clicked.connect(self.up_close)



    def dc(self):
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        w_width = screen_geometry.width()  # 屏幕宽度
        w_height = screen_geometry.height()  # 屏幕高度
        fonts = self.font_file("Resource/SFUI.ttc",config['fontname'],config['fontSize'])

        self.lingyun_Title_2 = QLabel('倒计时',self)
        self.lingyun_Title_2.setGeometry(QRect(int(w_width)-100, 15, 181, 31))
        #self.lingyun_Title_2.setFont(fonts)
        #self.lingyun_Title_2.setAlignment(Qt.AlignCenter)
        self.lingyun_Title_2.setStyleSheet('color:white;')

    def font_file(self,file,font_name,font_size):
        # 加载字体文件
        #global da tas
        if font_name == "":
            font_id = QFontDatabase.addApplicationFont(file)#"Resource/MiSans-Bold.ttf")  # 替换为你的字体文件路径
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font = QFont(font_families[0], int(font_size),  QFont.Bold)  # 使用加载的字体的第一个字体族，设置大小为20
                else:
                    font = QFont(font_name, int(font_size),  QFont.Bold)  # 如果加载失败，使用默认字体:"字体文件未包含可用字体族"
            else:
                font = QFont(font_name, int(font_size),  QFont.Bold)    # 如果加载失败，使用默认字体:"字体文件加载失败"
        else:
            font = QFont(font_name, int(font_size),  QFont.Bold)
        return font

    def uptime(self):
        now = datetime.now()
        if config.get('cl_time_Second') == "True":
            time_str = now.strftime('%H:%M:%S')
        else:
            time_str = now.strftime('%H:%M')
        self.time_hei.setText(time_str)

    def up_close(self):
        DP_Comonent.dc_dp("close")
        if config.get('cl_Switch') == "True":
            clock.show()
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
    def __init__(self, ):
        super().__init__()
        

        #self.task_queue = queue.Queue()
        #self.events = threading.Event()
        #self.counter = 0
        self.warn_function = ThrottledFunction(self.warning, 5)

        self.dc = False # 息屏标志

        self.initUI()
    def initUI(self):
        global display_x, display_y
        screen = QGuiApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕的几何信息
        display_x = screen_geometry.width()  # 屏幕宽度
        display_y = screen_geometry.height()  # 屏幕高度
        
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)

        self.setWindowFlags(self.windowFlags() | Qt.WindowDoesNotAcceptFocus)
        
        self.setAttribute(Qt.WA_TranslucentBackground)  # 使背景透明


        if config.get('dp_Pin') == 'True':
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.move(display_x,12)
        self.uic_ui()
        
        #self.class_up_time = QTimer(self)
        #self.class_down_time = QTimer(self)

        self.class_time = QTimer(self)
        #self.class_time_down = QTimer(self)

        self.updown = False # false下课 ture上课
        self.timess = QTimer(self)
        self.alert() # 倒计时模块
        self.update_Widgets()
        self.update_duty()
        #self.update_widget()
        
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
        self.classes = uic.loadUi(f"Resource/ui/dp/{config.get('dp_choose')}",self)
        self.classes.setObjectName("classes")

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
        font_name = self.font_files("Resource/MiSans-Bold.ttf",config.get("dp_Typeface"))
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
            self.click_timer.start()
            self.waiting_for_double_click = True
        
        elif event.type() == QEvent.MouseButtonRelease:
            if self.waiting_for_double_click:
                if (event.pos() - self.press_position).manhattanLength() <= self.touch_tolerance:
                    pass
                else:
                    if not self.click_timer.isActive():
                        self.on_single_click()
                    self.waiting_for_double_click = False
                    return super().eventFilter(source, event)
        
        elif event.type() == QEvent.MouseButtonDblClick:
            self.click_timer.stop()
            self.on_double_click(source)
            self.waiting_for_double_click = False
            return True
        
        if not self.waiting_for_double_click:
            return super().eventFilter(source, event)
        
        return False

    def on_single_click(self):
        # 获取窗口的坐标位置
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
            if value:
                config['dp_Pin'] = "True"
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            if config.get("dp_Switch"):
                self.show()
        elif choose == "dp_Typeface":
            config["dp_Typeface"] = str(value)
            font_name = self.font_files("Resource/MiSans-Bold.ttf",config.get("dp_Typeface"))
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
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            if config.get("dp_xiping") == "True":
                self.show()
            else:
                self.hide()
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
        if adj_weekday == 0:
            week = str(datetime.now().weekday() + 1)
        else:
            week = str(adj_weekday)
        if cho is not None:
            Initialization.convert_widget(-1)
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
    def update_duty(self):
        # 该def更新值日生表（初始化时调用1次）
        global duty_table,adj_weekday
        if adj_weekday == 0:
            week = str(datetime.now().weekday() + 1)
        else:
            week = str(adj_weekday)

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

        #lag_seconds = int(config.get("dp_Countdown_Bar_school_lag"))  # 假设lag是以秒为单位的时差
        #lag_minutes = lag_seconds / 60  # 将lag从秒转换为分钟

        now = datetime.now()
        current_time = now.time()
        current_datetime = datetime.combine(now.date(), current_time)
        #week = str(datetime.now().weekday() + 1)
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


        """for period, times in class_time[week].items():
            
            start_time = datetime.strptime(times[0].split('-')[0], '%H:%M').time()
            start_datetime = datetime.combine(now.date(), start_time)
            current_datetime = datetime.combine(now.date(), current_time)
            remaining_time = start_datetime - current_datetime

            # 计算剩余时间的分钟数
            #remaining_minutes = remaining_time.total_seconds() / 60
            remaining_minutes = remaining_time.total_seconds() / 60
            remaining_seconds = remaining_time.total_seconds() % 60
            

            # 判断剩余时间是否小于20分钟
            if 0 < remaining_minutes < 20:
                t = True
                break"""
        
        if t:
            self.lingyun_Bar.setVal(0)
            remaining_minutes = remaining_time.seconds // 60
            remaining_seconds = remaining_time.seconds % 60

            # 更新标签显示
            s = f"{remaining_minutes:02}:{remaining_seconds:02}"
            self.lingyun_down.setText(s)
            if s == "00:00":
                self.coming_time.stop()
                self.warn_function("alert")
                #QTimer.singleShot(1000,lambda: self.alert(1))
    def alert(self,st = None):
        global DP_Comonent
 
        # 调用一次 上下课会被调用
        Initialization.convert_widget(-1)
          
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
                        self.finish_wav = "Resource/audio/duty_warn.wav"
                        timer = threading.Timer(int(config.get("dp_audio_s")), self.wav,args =(config.get("dp_Sysvolume_value"), config.get("dp_Sysvolume")))
                        timer.start()
        

        else: # 上课
            self.TitleLabel.setText(current_widget[3])
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
    
# 上下课提醒
class class_warn(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint |Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.move(display_x, 0)

    def ui(self, types):
        if not hasattr(self, 'warn'):  # 检查是否已经加载了UI
            self.warn = uic.loadUi('Resource/ui/class_warn.ui', self)
            self.warn.setObjectName('warn')
            self.label = self.findChild(QLabel, "warn_label")
            self.warn_background = self.findChild(QFrame, "warn_background")
            # 窗口在屏幕的位置初始化
            self.DP_x = display_x - self.width()
            self.DP_y = 0
            self.animation_i = display_x - 260
            self.resize(self.width(), display_y)
        

        tcolor = ast.literal_eval(config.get(f"dp_Countdown_color_{types}"))
        
        if types == "up":
            self.label.setText("下课")
            Ripple.init(color=tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")#;border-radius: 10px")
            self.finish_wav = 'Resource/audio/up.wav'
        elif types == "down":
            self.label.setText("上课")
            Ripple.init(color=tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")#;border-radius: 10px")
            self.finish_wav = 'Resource/audio/down.wav'
        elif types == "next_down":
            self.label.setText("即将上课")
            Ripple.init(color=tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")#;border-radius: 10px")
            self.finish_wav = 'Resource/audio/next_down.wav'
        elif types == "ls":
            self.label.setText("放学")
            Ripple.init(color=tcolor[0])
            self.warn_background.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba({tcolor[1]}, {tcolor[2]}, {tcolor[3]}, 255), stop:1 rgba({tcolor[4]}, {tcolor[5]}, {tcolor[6]}, 255))")
            self.finish_wav = 'Resource/audio/up.wav'

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
        Ripple.show()

        self.animation.start()
        self.animation_rect.start()

        thread = threading.Thread(target=self.wav, args=(config.get("dp_Sysvolume_value"), config.get("dp_Sysvolume")))
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
class RippleEffect(QWidget):
    def init(self, color="#00FF00", duration=2200, start_delay=275):
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
        # 在动画结束后关闭窗口
        #opacity_animation.finished.connect(ripple.close)
        event.ignore()

# 欢迎窗口
class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        # customize the style of title bar button
        self.minBtn.setHoverColor(Qt.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        # use qss to customize title bar button
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: black;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)
        self.maxBtn.hide()
class Window(AcrylicWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon('Resource/ico/LINGYUN.ico'))


        self.load_pages()
        #self.check_for_updates()
    
    def load_pages(self):
        self.welcome_page = QWidget()
        self.setup_page = QWidget()

        self.w = uic.loadUi('Resource/ui/welcome_1.ui', self)

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
    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon('Resource/ico/LINGYUN.ico'), self)
        self.tray_icon.setToolTip('凌云班级组件')
        
        menu = SystemTrayMenu()
        settings_action = Action(FluentIcon.SETTING,'设置', self)
        settings_action.triggered.connect(self.setting_show)

        black_screen_action = Action('息屏显示', self)
        black_screen_action.triggered.connect(lambda: self.black_screen(False))
        
        black_screen = Action(FluentIcon.HOME_FILL,'息屏(不带时间)', self)
        black_screen.triggered.connect(lambda: self.black_screen(True))

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

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            #print('单击')
            self.black_screen(False)
        elif reason == QSystemTrayIcon.DoubleClick:
            #print('双击')
            pass

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
    def black_screen(self,notime):
        self.black_screen_window = BlackScreen(notime)
        self.black_screen_window.showFullScreen()  # 使用全屏显示
        self.black_screen_window.show()
    def exit_app(self):
        # 停止监听器线程
        theme_manager.themeListener.terminate()
        theme_manager.themeListener.deleteLater()
        QApplication.quit()

# 云获取提醒
class Yun_warn(QWidget):
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


def is_system_shutting_down():
    # 检查系统是否正在关机
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'shutdown':
            #print("System is shutting down.")
            return True
    #print("System is not shutting down.")
    return False


# 获取启动参数
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

# 重启程序
def restart_program():
    global tops
    tops.tray_icon.hide()
    python = sys.executable
    os.execl(python, python, *sys.argv)

# 检查多开（暂时不用）
def is_program_running():
    pid_file = '/tmp/LingYun.pid'#"/Resource/tmp/LingYun.pid"
    if os.path.isfile(pid_file):
        with open(pid_file, 'r') as f:
            pid = int(f.read())
        try:
            os.kill(pid, 0)  # 检查进程是否存在
            return True
        except OSError:
            os.remove(pid_file)
            return False
    else:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        return False


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
    main.init()
    sys.excepthook = main.handle_exception
    sys.exit(app.exec_())