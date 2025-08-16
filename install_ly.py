import sys,zipfile,threading,os,warnings,tempfile,shutil,subprocess,psutil,re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QFrame,QMessageBox,QProgressBar)
from PyQt5.QtCore import Qt,QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning) # 忽略警告
class UpdateWindow(QMainWindow):
    progress_updated = pyqtSignal(int)
    def __init__(self,arg=None):
        super().__init__()
        # 设置窗口标题和大小
        print(f"Received arguments: {arg}")
        self.setWindowTitle("凌云班级组件更新")
        self.setFixedSize(500, 300)
        self.setWindowIcon(QIcon("Resource/ico/LINGYUN.ico"))

        # 定制窗口并隐藏关闭和最大化按钮
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
            
        
        # 创建中心部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)


        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
                background-color: transparent;
            }
        """)
        
        # 添加logo图片
        self.setup_logo()
        
        # 添加分隔线
        #self.add_separator()
        
        # 添加更新提示文字
        self.setup_update_text()
        
        # 显示窗口
        self.show()


        #self.arg = get_argument()
        if arg is None or len(arg) < 4:
            # 弹窗提示
            QMessageBox.critical(None,"提示","更新失败，参数不足！",QMessageBox.Yes)
            QTimer.singleShot(100,lambda: self.edit_())
            return
        self.arg = arg



        QTimer.singleShot(1000,self.run_update)
        
    def setup_logo(self):
        self.logo_label = QLabel()
        pixmap = QPixmap("Resource/ico/LINGYUN.ico")
        
        # 图片加载失败时
        if pixmap.isNull():
            self.logo_label.setText("LingYun Class Widgets")
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #007BFF;
                    border: 2px dashed #007BFF;
                    padding: 20px;
                }
            """)
        else:
            # 图片适应窗口
            scaled_pixmap = pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
    
    def add_separator(self):
        """添加分隔线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e0e0e0;")
        self.layout.addWidget(line)
    
    def setup_update_text(self):
        """设置更新提示文字"""
        self.update_label = QLabel("正在更新中，请稍候...")
        self.update_label.setAlignment(Qt.AlignCenter)
        
        # 设置字体
        font = QFont()
        font.setPointSize(16)  # 字体大小
        font.setBold(True)     # 粗体
        font.setFamily('Microsoft YaHei')
        self.update_label.setFont(font)

        self.progress_bar = QProgressBar()  # 添加进度条
        self.progress_bar.setTextVisible(False)

        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.update_label, alignment=Qt.AlignCenter)

        # 设置文字样式
        self.update_label.setStyleSheet("color: #343a40;")     

        # 连接信号到槽
        self.progress_updated.connect(self.update_progress_bar)

    def run_update(self):
        """检查并结束指定名称的进程（排除自身）"""
        process_found = False
        process_name = "LingYun_Class_Widgets.exe"
        current_pid = os.getpid()  # 获取当前进程ID
        print("Starting to check and terminate processes...")
        
        for proc in psutil.process_iter(['name', 'pid']):  # 添加获取pid
            try:
                if proc.info['name'] == process_name and proc.info['pid'] != current_pid:  # 排除自身
                    process_found = True
                    proc.terminate()
                    # 等待进程结束，超时时间设为3秒
                    if proc.wait(timeout=3) is not None:
                        self.runs()
                    else:   # 若进程未在3秒内结束，则强制终止
                        proc.kill()
                        self.runs()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("警告")
                msg_box.setText("无法自动退出，请先手动退出旧版本！")
                msg_box.setIcon(QMessageBox.Warning)
                retry_button = msg_box.addButton("重试", QMessageBox.ActionRole)
                cancel_button = msg_box.addButton("取消更新", QMessageBox.RejectRole)
                msg_box.exec_()
                if msg_box.clickedButton() == retry_button:
                    # 重试
                    self.run_update()
                    return
                elif msg_box.clickedButton() == cancel_button:
                    # 取消更新
                    QMessageBox.critical(None,"提示","更新失败，未做更改。正在启动原版本。",QMessageBox.Yes)
                    goal_dir = remove_version_from_path(self.arg[1])
                    subprocess.Popen([goal_dir[0]+"/LingYun_Class_Widgets.exe"])
                    QTimer.singleShot(100,lambda: self.edit_())
                continue
        if not process_found:
            #print(f"未找到名为 {process_name} 的进程")
            self.runs()

    def runs(self):
        self.update_event = threading.Event()
        update_thread = threading.Thread(target=self.zip_update)
        update_thread.start()


    '''
        def zip_update(self): 
            # 获取压缩包信息
            zip_file = zipfile.ZipFile(self.arg[0])
            total_files = len(zip_file.namelist())
            current_file = 0
            temp_dir = os.path.join(tempfile.gettempdir(), "LingYun")
            extract_dir = os.path.join(temp_dir, "Temps")
            percent = 0

            # 检测或指定压缩包内的文件名编码（关键修复点）
            # 若已知编码（如GBK），可直接替换为：encoding = "gbk"
            # 若不确定，可尝试自动检测（需安装chardet库）
            print(zip_file)
            encoding = chardet.detect(zip_file.namelist()[0].encode())["encoding"] or "utf-8"
            #encoding = "utf-8"
            #encoding = "gbk"  # Windows下常见压缩包编码（如WinRAR/7-Zip默认GBK）
            print(f"Detected file name encoding: {encoding}")

            common_prefix = os.path.commonprefix(zip_file.namelist())
            if common_prefix.endswith('/') and common_prefix.count('/') == 1:
                skip_root = True
                root_len = len(common_prefix)
            else:
                skip_root = False

            with zip_file as zip_ref:
                for member in zip_ref.namelist():
                    # 关键步骤：使用指定编码解码文件名（处理中文乱码）
                    try:
                        member = member.encode("cp437").decode(encoding)  # 先转原始字节流，再用目标编码解码
                    except Exception as e:
                        member = member  # 解码失败时保留原始名称

                    target_path = os.path.join(extract_dir, member[root_len:] if skip_root else member)
                    if member.endswith('/'):
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                    current_file += 1
                    percent = int((current_file / total_files / 2) * 100)
                    self.progress_updated.emit(percent)  # 50%


            percent = 50
            self.progress_updated.emit(percent)

            # 开始替换操作
            # 0:zip路径 1:更新路径 2:旧版本号 
            goal_dir = remove_version_from_path(self.arg[1])
            old_version = self.arg[3]
            new_version = self.arg[2]
            print(goal_dir)
            print(f"{goal_dir[0]}\\{new_version}")

            if os.path.exists(self.arg[1]):
                shutil.rmtree(self.arg[1]) # 删除旧版本目录

            target_path = os.path.join(goal_dir[0], self.arg[3])
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            if os.path.exists(f"{goal_dir[0]}/{new_version}"):
                shutil.rmtree(f"{goal_dir[0]}/{new_version}")
            shutil.copytree(f"{temp_dir}\\Temps\\{new_version}", f"{goal_dir[0]}\\{new_version}") # 复制新版本到目标目录
            percent += 30
            self.progress_updated.emit(percent)

            if os.path.exists(f"{goal_dir[0]}/LingYun_Class_Widgets.exe"):
                os.remove(f"{goal_dir[0]}/LingYun_Class_Widgets.exe")
            shutil.copy(f"{temp_dir}/Temps/LingYun_Class_Widgets.exe", f"{goal_dir[0]}/LingYun_Class_Widgets.exe")
            
            percent += 20
            self.progress_updated.emit(percent)
    '''



    def zip_update(self):
        # 获取压缩包信息
        zip_path = self.arg[0]
        goal_dir = self.arg[1]
        new_version = self.arg[2]
        old_version = self.arg[3]
        
        try:
            # 创建临时目录
            temp_dir = os.path.join(tempfile.gettempdir(), "LingYun")
            extract_dir = os.path.join(temp_dir, "Temps")
            os.makedirs(extract_dir, exist_ok=True)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                total_files = len(zip_ref.namelist())
                current_file = 0
                
                # 直接解压所有文件（保留乱码文件名）
                zip_ref.extractall(extract_dir)
                
                # 检测根目录（压缩包的最外层目录）
                root_dir = None
                if os.listdir(extract_dir):
                    first_item = os.listdir(extract_dir)[0]
                    first_item_path = os.path.join(extract_dir, first_item)
                    if os.path.isdir(first_item_path):
                        root_dir = first_item
                        print(f"检测到根目录: {root_dir}")
                
                # 重命名所有文件和目录
                for member in zip_ref.namelist():
                    # 获取解压后的路径（乱码文件名）
                    extracted_path = Path(os.path.join(extract_dir, member))
                    
                    if extracted_path.exists():
                        try:
                            # 解码文件名
                            right_fn = member.encode('cp437').decode('gbk')
                            
                            # 构建目标路径（关键：直接使用解码后的文件名，不手动处理根目录）
                            target_path = Path(os.path.join(extract_dir, right_fn))
                            
                            # 确保目标目录存在
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # 执行重命名
                            extracted_path.rename(target_path)
                        except Exception as e:
                            print(f"重命名文件 {member} 时出错: {e}")
                    
                    # 更新进度
                    current_file += 1
                    percent = int((current_file / total_files / 2) * 100)
                    self.progress_updated.emit(percent)
            
            # 解压完成，进度设为50%
            percent = 50
            self.progress_updated.emit(percent)
            
            # 移除根目录层级（如果存在）
            if root_dir and os.path.exists(os.path.join(extract_dir, root_dir)):
                print(f"正在移除根目录: {root_dir}")
                root_path = os.path.join(extract_dir, root_dir)
                
                # 移动根目录下的所有内容到Temps目录
                for item in os.listdir(root_path):
                    src = os.path.join(root_path, item)
                    dst = os.path.join(extract_dir, item)
                    
                    # 处理目标已存在的情况
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    
                    # 移动文件或目录
                    shutil.move(src, dst)
                
                # 删除空的根目录
                os.rmdir(root_path)
                print(f"根目录 {root_dir} 已成功移除")

            # 开始替换操作
            goal_dir_base, _ = remove_version_from_path(goal_dir)
            old_version_path = os.path.join(goal_dir_base, old_version) # 错的
            new_version_temp_path = os.path.join(extract_dir, new_version)
            new_version_target_path = os.path.join(goal_dir_base, new_version)



            # 删除旧版本目录
            if os.path.exists(self.arg[1]):
                shutil.rmtree(self.arg[1]) # 删除旧版本目录

            # 删除已存在的新版本目录
            if os.path.exists(new_version_target_path):
                shutil.rmtree(new_version_target_path)

            # 复制新版本到目标目录
            if os.path.exists(new_version_temp_path):
                shutil.copytree(new_version_temp_path, new_version_target_path)
                percent += 30
                self.progress_updated.emit(percent)
            else:
                raise FileNotFoundError(f"New version not found in temp directory: {new_version}")

            # 复制主程序exe
            exe_source = os.path.join(extract_dir, "LingYun_Class_Widgets.exe")
            exe_target = os.path.join(goal_dir_base, "LingYun_Class_Widgets.exe")
            
            if os.path.exists(exe_target):
                os.remove(exe_target)
            if os.path.exists(exe_source):
                shutil.copy(exe_source, exe_target)
                percent += 20
                self.progress_updated.emit(percent)
            else:
                raise FileNotFoundError("Main executable not found in zip file")

        except Exception as e:
            print(f"Update error: {e}")
            raise

    def update_progress_bar(self, progress=0):
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.update_wh()

        else:
            self.update_label.setText(f"正在更新，已完成{progress}%")
            self.progress_bar.setValue(progress)

    def update_wh(self):
        self.update_label.setText("更新完成，正在启动...")
        shutil.rmtree(tempfile.gettempdir() + "/LingYun/Temps")
        goal_dir = remove_version_from_path(self.arg[1])
        subprocess.Popen([goal_dir[0]+"/LingYun_Class_Widgets.exe"] + ["/clean"])        
        QTimer.singleShot(3000,lambda: self.edit_())
        #os.startfile(os.path.join(self.arg[1], "LingYun_Class_Widgets.exe"))

    def edit_(self):
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()



def remove_version_from_path(goal_dir: str):
    """
    从目录路径中移除版本号部分（支持带后缀的版本号，如 1.6.0-Beta），并返回版本号
    
    参数:
    goal_dir (str): 目标目录路径
    
    返回:
    list[str, Optional[str]]: 包含移除版本号后的目录路径和提取的版本号（如果存在）
    """
    normalized_path = os.path.normpath(goal_dir).rstrip(os.sep)
    dir_name, base_name = os.path.split(normalized_path)
    
    # 新版本号正则表达式（支持前缀、主版本.次版本.修订版-后缀 格式）
    version_pattern = r'''
        ^                   # 匹配字符串开头
        (?:v|ver|version)?  # 可选的版本前缀（v/ver/version，不区分大小写）
        \s*                 # 可选空格
        (\d+\.\d+\.\d+       # 主版本.次版本.修订版（必须包含至少两个点）
        (?:-\w+)?           # 可选后缀（如 -Beta、-Alpha，支持短横线+字母）
        )                   # 结束分组
        $                   # 匹配字符串结尾
    '''
    match = re.fullmatch(version_pattern, base_name, re.IGNORECASE | re.VERBOSE)
    
    if match:
        version = match.group(1)
        return [dir_name + os.sep, version]
    else:
        return [goal_dir, None]
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 0zip路径 1安装路径 2旧版本号 3新版本号
    window = UpdateWindow([r"C:\Users\username\AppData\Local\Temp\LingYun\temp.zip","F:/WangQi/Apps/LingYun/1.6.0-Beta","1.6.4-Beta","1.6.4-Beta"])
    sys.exit(app.exec_())

