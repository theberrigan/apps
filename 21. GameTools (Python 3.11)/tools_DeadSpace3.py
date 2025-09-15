import os, ctypes
from ctypes import wintypes
from collections import OrderedDict

def patchConfig ():
    CONFIG_PATH = os.path.expandvars(r'%USERPROFILE%\AppData\Local\EA Games\Dead Space 3\system.txt')

    config = OrderedDict()

    with open(CONFIG_PATH, 'r', encoding = 'utf-8') as f:
        for line in f.readlines():
            key, value = [ part.strip() for part in line.split('=', 1) ]
            config[key] = value

    config['Window.VSync'] = 'false'
    config['Window.FOVScale'] = '1.20000000'

    data = '\n'.join([ ' = '.join(item) for item in config.items() ]) + '\n'

    with open(CONFIG_PATH, 'w', encoding = 'utf-8') as f:
        f.write(data)


def getMaxScreenResolution ():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return [ user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) ]


def getDefaultConfig ():
    maxWidth, maxHeight = getMaxScreenResolution()

    return [
        ('Audio.MusicVol', '1.00000000'),
        ('Audio.Output', '0'),
        ('Audio.SFXVol', '1.00000000'),
        ('Audio.Subtitles', 'true'),
        ('Audio.VoiceVol', '1.00000000'),
        ('Misc.MaxJobThreads', '-1'),
        ('QualityOptions.AAMode', '4'),
        ('QualityOptions.ActorMotionBlur', 'true'),
        ('QualityOptions.Aniso', '16'),
        ('QualityOptions.Bloom', 'true'),
        ('QualityOptions.Blur', 'true'),
        ('QualityOptions.ConfigType', '1'),
        ('QualityOptions.Decals', 'true'),
        ('QualityOptions.Distortion', 'true'),
        ('QualityOptions.DoF', 'true'),
        ('QualityOptions.Flare', 'true'),
        ('QualityOptions.Glow', 'true'),
        ('QualityOptions.HighLightQuality', 'true'),
        ('QualityOptions.LightingAccQuality', 'true'),
        ('QualityOptions.ManipColor', 'true'),
        ('QualityOptions.ShaderQuality', '2'),
        ('QualityOptions.Shadows', '5'),
        ('QualityOptions.SSAO2', 'true'),
        ('QualityOptions.SSR', 'true'),
        ('Window.Border', 'true'),
        ('Window.FOVScale', '1.20000000'),
        ('Window.Fullscreen', 'true'),
        ('Window.Gamma', '0.50000000'),
        ('Window.Height', str(maxHeight)),
        ('Window.Hz', '60'),
        ('Window.Left', '0'),
        ('Window.State', '3'),
        ('Window.Top', '0'),
        ('Window.TopMost', 'false'),
        ('Window.VSync', 'false'),
        ('Window.WideScreen', 'false'),
        ('Window.Width', str(maxWidth)),
    ]

'''
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SM_CMONITORS = 80

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
print(user32.EnumDisplaySettingsA)
deviceName = wintypes.LPCSTR()
user32.EnumDisplayDevicesA(deviceName, 0)
print(deviceName.value)
'''

'''
def MonitorEnumProc (hMonitor, hdcMonitor, lprcMonitor, dwData):
    print(dwData)
    return 1;


user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

count = wintypes.LPARAM()

user32.EnumDisplayMonitors(None, None, MonitorEnumProc, ctypes.byref(count))
'''

# EnumDisplayDevices
# EnumDisplayMonitors 

def _monitorEnumProc(hMonitor, hdcMonitor, lprcMonitor, dwData):
    print('call result:', hMonitor, hdcMonitor, lprcMonitor, dwData)

def enum_mons():
    # Callback Factory
    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool, 
        wintypes.HMONITOR,
        wintypes.HDC,
        wintypes.LPRECT,
        wintypes.LPARAM
    )

    # Make the callback function
    enum_callback = MonitorEnumProc(_monitorEnumProc)

    # Enumerate the windows
    print ('return code: %d' % ctypes.windll.user32.EnumDisplayMonitors(
        None, 
        None,
        enum_callback,
        0
        ))

if __name__ == '__main__':
    enum_mons()