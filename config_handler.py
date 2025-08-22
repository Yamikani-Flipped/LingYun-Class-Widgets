import winreg as reg
from PyQt5.QtWidgets import QMessageBox

class ConfigHandler:
    def __init__(self):
        # 注册表路径
        self.registry_path = r'SOFTWARE\LingYunTimes'
        # 初始化配置映射关系
        self.setup_mappings()
        # 内存配置缓存
        self.config = self._load_initial_config()  # 从注册表加载初始配置

    def setup_mappings(self):
        """设置配置项与处理函数的映射关系"""
        self.mappings = {
            # 值预处理函数：将原始值转换为需要存储/使用的值
            "preprocessors": {
                # "配置项标识": 处理函数
            },
            
            # 业务逻辑处理器：处理UI更新、状态变更等
            "handlers": {
                # "配置项标识": 处理函数
            },
            
            # 不需要后续处理的配置项（如触发动作后立即完成）
            "immediate_returns": set(),
            
            # 需要特殊存储逻辑的配置项
            "special_storages": {
                # "配置项标识": 存储函数
            }
        }

    def _load_initial_config(self):
        """从注册表加载初始配置"""
        config = {}
        try:
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, self.registry_path, 0, reg.KEY_READ)
            try:
                idx = 0
                while True:
                    # 枚举所有值
                    name, value, _ = reg.EnumValue(registry_key, idx)
                    config[name] = value
                    idx += 1
            except OSError:
                # 枚举完毕
                pass
            finally:
                reg.CloseKey(registry_key)
        except FileNotFoundError:
            # 注册表项不存在，返回空配置
            pass
        except Exception as e:
            self._handle_error(f"加载初始配置失败: {str(e)}")
        return config

    # ------------------------------
    # 通用处理入口
    # ------------------------------
    def handle_config(self, raw_value, config_key):
        """处理配置变更的主入口"""
        try:
            # 1. 预处理值
            processed_value = self._preprocess(raw_value, config_key)
            
            # 2. 执行业务逻辑处理
            self._handle_business(processed_value, config_key)
            
            # 3. 检查是否需要立即返回（不执行后续操作）
            if config_key in self.mappings["immediate_returns"]:
                return
            
            # 4. 存储配置（通用逻辑）
            self._store_config(processed_value, config_key)
            
            # 5. 通用UI更新（如果有）
            self._update_common_ui(processed_value, config_key)
            
        except Exception as e:
            self._handle_error(f"处理配置项 {config_key} 失败: {str(e)}")

    # ------------------------------
    # 内部处理方法
    # ------------------------------
    def _preprocess(self, value, config_key):
        """值预处理"""
        processor = self.mappings["preprocessors"].get(config_key)
        return processor(value) if processor else value

    def _handle_business(self, value, config_key):
        """业务逻辑处理"""
        handler = self.mappings["handlers"].get(config_key)
        if handler:
            # 支持带参数和不带参数的处理函数
            try:
                handler(value)
            except TypeError:
                # 如果函数不需要参数，则不带参数调用
                handler()

    def _store_config(self, value, config_key):
        """存储配置（默认通用逻辑 - 写入注册表）"""
        # 检查是否有特殊存储逻辑
        special_storage = self.mappings["special_storages"].get(config_key)
        if special_storage:
            special_storage(value, config_key)
            return
            
        # 通用存储逻辑：写入注册表
        try:
            # 创建或打开注册表键
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, self.registry_path)
            
            # 转换为字符串存储（REG_SZ类型）
            str_value = str(value)
            
            # 更新内存缓存
            self.config[config_key] = str_value
            
            # 将设置写入注册表
            reg.SetValueEx(registry_key, config_key, 0, reg.REG_SZ, str_value)
            
        except Exception as e:
            raise Exception(f"写入注册表失败: {str(e)}")
        finally:
            # 确保注册表键被关闭
            if 'registry_key' in locals():
                reg.CloseKey(registry_key)

    def _update_common_ui(self, value, config_key):
        """通用UI更新（可根据需要实现）"""
        # 示例：发送信号通知UI更新
        # self.ui_updated.emit(config_key, value)
        pass

    def _handle_error(self, error_msg):
        """错误处理"""
        print(f"配置处理错误: {error_msg}")
        QMessageBox.warning(None, "配置错误", error_msg)

    # ------------------------------
    # 示例处理函数
    # ------------------------------
    # def _preprocess_volume(self, value):
    #     """处理音量值（示例）"""
    #     return max(0, min(100, int(value)))  # 确保音量在0-100之间
    #
    # def _handle_mute(self, value):
    #     """处理静音状态（示例）"""
    #     if value:
    #         self.audio_player.mute()
    #         self.mute_icon.show()
    #     else:
    #         self.audio_player.unmute()
    #         self.mute_icon.hide()
