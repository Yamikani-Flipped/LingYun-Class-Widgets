from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from playsound import playsound


# 定义缺失的 CLSCTX 常量
CLSCTX_INPROC_HANDLER = 0x2
CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4
CLSCTX_REMOTE_SERVER = 0x10
CLSCTX_SERVER = CLSCTX_INPROC_SERVER | CLSCTX_LOCAL_SERVER | CLSCTX_REMOTE_SERVER
CLSCTX_ALL = CLSCTX_INPROC_HANDLER | CLSCTX_SERVER

# 获取扬声器设备
devices = AudioUtilities.GetSpeakers()
# 激活音量控制接口
clsctx = CLSCTX_ALL
interface = devices.Activate(IAudioEndpointVolume._iid_, clsctx, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# 解除静音
volume.SetMute(False, None)
volume.SetMasterVolumeLevelScalar(0.7, None)  # 将音量设置为70%



sound_file = 'path/to/your/soundfile.wav'
playsound(sound_file)
