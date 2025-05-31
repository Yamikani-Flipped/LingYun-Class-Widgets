import threading
import requests
import os
import time
from typing import Callable, Optional

ProgressCallback = Callable[[int, int], None]

def format_size(size):
    """将字节转换为合适的单位（KB、MB 等）"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"
    else:
        return f"{size / (1024 ** 3):.2f} GB"

def format_time(seconds):
    """将秒转换为合适的时间格式（时:分:秒）"""
    if seconds < 60:
        return f"{seconds:.0f} 秒"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:.0f} 分 {seconds:.0f} 秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 3600) % 60
        return f"{hours:.0f} 时 {minutes:.0f} 分 {seconds:.0f} 秒"


def download_file(
    url: str, 
    save_path: str, 
    complete_callback: Optional[Callable[[str, Optional[str]], None]] = None,   
    progress_callback: Optional[ProgressCallback] = None,
    progress_interval: float = 1.0
) -> None:
    """
    下载文件到指定路径，并在下载过程中按时间间隔调用进度回调函数，完成后调用完成回调函数
    参数:
        url: 文件的 URL 地址
        save_path: 保存文件的路径
        complete_callback: 下载完成后调用的回调函数，接收两个参数：文件路径和错误信息        
        progress_callback: 下载过程中调用的回调函数，接收三个参数：已下载字节数和总字节数        
        progress_interval: 进度更新的时间间隔，单位为秒
    """
    def download_task():
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            last_progress_update = time.time()  # 记录上次更新进度的时间
            last_bytes_downloaded = 0  # 记录上次更新时已下载的字节数

            start_time = time.time()
            last_update_time = start_time
            
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    bytes_downloaded += len(chunk)

                    current_time = time.time()
                    if current_time - last_progress_update >= progress_interval:
                        # 计算当前下载速度
                        elapsed_time = current_time - last_update_time
                        downloaded_delta = bytes_downloaded - last_bytes_downloaded
                        speed = downloaded_delta / elapsed_time if elapsed_time > 0 else 0

                        speed_str = format_size(speed)
                        remaining_time_str = format_time((total_size - bytes_downloaded) / speed) if speed > 0 else "未知"
                        info_text = f"{speed_str}/s  剩余时间: {remaining_time_str}"
                        
                        if progress_callback:
                            progress_callback(bytes_downloaded, total_size, info_text)
                        
                        # 更新时间和下载量记录
                        last_progress_update = current_time
                        last_update_time = current_time
                        last_bytes_downloaded = bytes_downloaded
            
            # 调用完成回调函数（成功）
            if complete_callback:
                complete_callback(save_path, None)
                
        except Exception as e:
            # 调用完成回调函数（失败）
            if complete_callback:
                complete_callback(None, str(e))
    thread = threading.Thread(target=download_task)
    thread.daemon = True  # 设置为守护线程，主程序退出时自动终止
    thread.start()

# 进度回调函数的示例实现
def on_progress_update(bytes_downloaded: int, total_size: int, info_text : str) -> None:
    if total_size > 0:
        progress = (bytes_downloaded / total_size) * 100
        print(f"下载进度: {progress:.2f}% ({bytes_downloaded}/{total_size} 字节)")
    else:
        print(f"已下载 {bytes_downloaded} 字节")

# 完成回调函数的示例实现
def on_download_complete(file_path: Optional[str], error: Optional[str]) -> None:
    if file_path:
        print(f"下载完成，文件保存在: {file_path}")
    else:
        print(f"下载失败: {error}")

if __name__ == "__main__":
    URL = "https://gitee.com/yamikani/LingYun-Class-Widgets/releases/download/v1.5.13/LingYun_Class_Widgets_v1.5.13_x64.zip"
    SAVE_PATH = "downloads/file.zip"
    
    # 设置进度更新的时间间隔为2秒
    download_file(URL, SAVE_PATH, on_download_complete, on_progress_update, progress_interval=1.0)
    
    # 主线程可以继续执行其他任务
    print("下载任务已在后台启动...")
    
    input("按任意键退出...")