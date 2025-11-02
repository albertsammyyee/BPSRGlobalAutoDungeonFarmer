import ctypes
import os
import sys
import time
from subprocess import Popen, PIPE

import pygetwindow as gw
import mss
import win32con
import win32gui
from PIL import Image

app_name = "星痕共鸣"


def capture_window(window_title: str):
    # 1. 根据窗口标题查找目标窗口（支持模糊匹配）
    target_windows = gw.getWindowsWithTitle(window_title)
    if not target_windows:
        raise ValueError(f"未找到标题包含'{window_title}'的窗口")

    # 2. 获取第一个匹配窗口的位置和大小（避免多窗口冲突）
    window = target_windows[0]
    window.activate()  # 激活窗口（确保在前台，可选）
    x, y, width, height = window.left, window.top, window.width, window.height

    # 3. 调整窗口区域（排除窗口边框，可选，根据系统微调）
    x += 8  # 适配Windows窗口边框
    y += 32  # 适配标题栏高度
    width -= 16
    height -= 40

    # 4. 使用mss截图（仅截取窗口区域，效率高）
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct.grab(monitor)

        # 5. 转换为PIL图像并保存
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img





def list_file(dir_path, suffix=None):
    # 检查目录是否存在
    if os.path.isdir(dir_path):
        # 获取目录下的所有文件和子目录名称
        items = os.listdir(dir_path)
        # 筛选出文件（排除子目录）
        files = []
        for item in os.listdir(dir_path):
            # 拼接完整路径
            item_path = os.path.join(dir_path, item)
            # 判断是否为文件，且以.json结尾
            if os.path.isfile(item_path) and item.endswith(f".{suffix}"):
                files.append(item)  # 仅添加文件名（不含路径）
        # 打印文件名称
        print("录制文件列表如下：")
        for index, file in enumerate(files):
            print(f"{index}.{file}")
        return files
    else:
        print(f"目录 '{dir_path}' 不存在")
        return []


def run_as_admin():
    """以管理员权限重新运行当前脚本"""
    try:
        if os.name == 'nt':
            # Windows 系统提升权限
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        else:
            # Unix/Linux/macOS 系统提升权限
            # 使用 sudo 重新运行脚本
            args = ['sudo', sys.executable] + sys.argv
            process = Popen(args, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"提升权限失败: {stderr.decode()}")
                return False
        return True
    except Exception as e:
        print(f"提升权限时发生错误: {e}")
        return False


def get_exe_dir():

    #
    # 获取当前 EXE 文件的完整路径
    exe_path = sys.executable
    # 获取 EXE 所在的目录
    exe_dir = os.path.dirname(os.path.abspath(exe_path))
    if "python3.13" in exe_dir:
        return "G:\\xhgm_script\\AutoFuckBKLGetDress\\auto_cj"
    else:
        return exe_dir


def is_admin():
    """检查当前程序是否以管理员权限运行"""
    try:
        # Windows 系统检查
        if os.name == 'nt':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        # Unix/Linux/macOS 系统检查
        else:
            return os.geteuid() == 0
    except:
        return False
