import ctypes.wintypes
import random
import sys
import time

import win32gui
from pynput import keyboard


def get_pixel_color(x, y):
    try:
        hdc = win32gui.GetDC(0)
        color = win32gui.GetPixel(hdc, x, y)
        win32gui.ReleaseDC(0, hdc)
        r = color & 0xff
        g = (color >> 8) & 0xff
        b = (color >> 16) & 0xff
        return (r, g, b)
    except Exception as e:
        print(f"获取像素颜色错误: {e}")
        return (255, 255, 255)


start = False
def on_hot_key_press(key):
    global start
    if key == keyboard.Key.f12:
        start = not start
        print(f"当前状态为{start}")


if __name__ == '__main__':
    try:
        # 强制检查管理员权限
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            is_admin = False

        if not is_admin:
            print("错误: 程序必须以管理员权限运行！")
            # 尝试自动重启为管理员
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        keyboard.Listener(
            on_press=on_hot_key_press
        ).start()
        keyboard_controller = keyboard.Controller()
        print(f"重新启动")
        i = 0
        while True:
            if start:
                i = i+1
                if i%10==0:
                    r, g, b = get_pixel_color(1290,1270)
                    if r>250 and g>250 and b>250:
                        print("点击5")
                        keyboard_controller.press("5")
                        time.sleep(0.1)
                        keyboard_controller.release("5")
                r, g, b = get_pixel_color(1170, 1250)
                if r>100:
                    print("点击3")
                    keyboard_controller.press("3")
                    time.sleep(0.05)
                    keyboard_controller.release("3")
            else:
                time.sleep(0.5)

    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        sys.exit(0)
