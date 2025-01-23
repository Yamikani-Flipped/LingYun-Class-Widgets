import sys,os
import winreg as reg
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime
import warnings
from qfluentwidgets import (
    Theme, setTheme, FluentWindow, FluentIcon , ToolButton, ListWidget, ComboBox, CaptionLabel,
    SpinBox, LineEdit, PrimaryPushButton, TableWidget, Flyout, InfoBarIcon,
    FlyoutAnimationType, NavigationItemPosition, MessageBox, SubtitleLabel, PushButton, SwitchButton,
    CalendarPicker, BodyLabel, ColorDialog, isDarkTheme, TimeEdit, EditableComboBox, MessageBoxBase,
    SearchLineEdit, Slider, PlainTextEdit, ToolTipFilter, ToolTipPosition, RadioButton, HyperlinkLabel,
    PrimaryDropDownPushButton, Action, RoundMenu, CardWidget, ImageLabel, StrongBodyLabel,
    TransparentDropDownToolButton, Dialog, SmoothScrollArea,ColorPickerButton,SystemTrayMenu,setFont
    ,NavigationItemPosition, FluentWindow, SubtitleLabel,
)

"""SwitchButton开关按钮"""

# 加载UI文件
home = uic.loadUi('时间/menu-sound232.ui')
home.setObjectName("home")

# 查找控件并保存到变量（CW2的按钮）
myButton = home.findChild(SwitchButton, 'CW2_onof_button')

# 设置按钮状态（True就是开启，false就是关闭）
myButton.setChecked(True)

# 打印按钮状态
myButton.isChecked()
