import json
import os.path
import subprocess
import time

import win32api
import win32con
import win32gui
from pynput import keyboard
from pynput.mouse import Controller


class PlayBack:
    def __init__(self, file_name,run_in_back=False):
        self.VK_A = 0x41
        self.VK_S = 0x53
        self.VK_D = 0x44
        self.VK_W = 0x57
        self.VK_F = 0x46
        self.run_in_back = run_in_back
        self.file_name = file_name
        self.stop_replay = True
        self.is_interrupt = False
        self.keyboard_listener = keyboard.Listener(on_press=self.on_hot_key_press)
        self.hwnd = win32gui.FindWindow(None, "星痕共鸣")
        if not self.hwnd:
            print("未找到星痕共鸣窗口！！！3秒后结束应用")
            time.sleep(3)
            exit()

    def load_recording(self, filename):
        """从文件加载录制数据"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载失败: {e}")
            return None

    def on_hot_key_press(self, key):
        if key == keyboard.Key.f8:
            print("终止回放")
            self.is_interrupt = True
        if key == keyboard.Key.f12:
            self.stop_replay = not self.stop_replay
            if self.stop_replay:
                print("暂停回放")
            else:
                print("开始回放")
                self.bring_window_to_front()
                if self.run_in_back:
                    win32api.PostMessage(self.hwnd, win32con.WM_ACTIVATE, 1, 0)

        if key == keyboard.Key.f9:

            img_path = self.file_name.replace(".json", ".png")
            if os.path.isfile(img_path):
                print("尝试打开图片")
                subprocess.run(f'start "" "{img_path}"', shell=True)
            else:
                print(f"图片文件不存在：{img_path}")

    def bring_window_to_front(self):
        """将游戏窗口置顶显示"""
        if not self.hwnd:
            print("未找到游戏窗口，无法置顶")
            return False
        try:
            # 确保窗口处于正常状态（非最小化）
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            # 将窗口置顶
            win32gui.SetForegroundWindow(self.hwnd)
        except Exception as e:
            pass
        time.sleep(0.5)  # 等待窗口置顶
        return True
    def start(self):
        """回放录制的数据"""
        data = self.load_recording(self.file_name)

        if not data:
            print("没有可回放的数据")
            return
        self.keyboard_listener.start()

        print("若使用后台回放，务必站好位置后打开ESC菜单再开始回放，且按F12后禁止点击游戏窗口！！！")
        print("按【F12】开始回放，再次按【F12】停止回放并重置进度")
        print("按【F9】可查看录制起始位置信息")
        print("按【F8】结束回放任务")

        while True:
            if self.is_interrupt:
                self.keyboard_listener.stop()
                return
            if self.stop_replay:
                time.sleep(0.5)
                continue

            self._replay(data)
    def _replay(self, data):
        """实际执行回放的方法"""
        keyboard_controller = keyboard.Controller()
        mouse = Controller()
        for event in data:
            if self.stop_replay or self.is_interrupt:
                return
            try:
                if event['type'] == 'key_press':
                    key = self._get_key(event['key'])
                    if not key:
                        continue
                    if self.run_in_back:
                        self.win32_keyboard_opt(key,event['type'])
                    else:
                        keyboard_controller.press(key)
                elif event['type'] == 'key_release':
                    key = self._get_key(event['key'])
                    if not key:
                        continue
                    if self.run_in_back:
                        self.win32_keyboard_opt(key,event['type'])
                    else:
                        keyboard_controller.release(key)
                elif event['type'] == 'scroll':
                    mouse.scroll(0, event['key'])
                elif event['type'] == 'sleep':
                    time.sleep(event['time'])
            except Exception as e:
                print(f"回放事件时出错: {e}")

    def win32_keyboard_opt(self, key_board,type):
        global curr_key

        if key_board == 'a' or key_board == 'A':
            curr_key = self.VK_A
        elif key_board == 's' or key_board == 'S':
            curr_key = self.VK_S
        elif key_board == 'd' or key_board == 'D':
            curr_key = self.VK_D
        elif key_board == 'w' or key_board == 'W':
            curr_key = self.VK_W
        elif key_board == 'f' or key_board == 'F':
            curr_key = self.VK_F
        else:
            return
        scan_code = win32api.MapVirtualKey(curr_key, 0)
        if type =='key_press':
            lParam_down = (scan_code << 16) | 0x00000001
            win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, curr_key, lParam_down)
        elif type == 'key_release':
            lParam_up = (scan_code << 16) | 0xC0000001
            win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, curr_key, lParam_up)
    def _get_key(self, key_str):
        """将按键字符串转换为pynput识别的按键对象"""
        # 特殊按键
        if key_str == 'Key.space':
            return keyboard.Key.space
        elif key_str == 'Key.enter':
            return keyboard.Key.enter
        elif key_str == 'Key.backspace':
            return keyboard.Key.backspace
        elif key_str == 'Key.tab':
            return keyboard.Key.tab
        elif key_str == 'Key.esc':
            return keyboard.Key.esc
        elif key_str == 'Key.shift':
            return keyboard.Key.shift
        elif key_str == 'Key.ctrl':
            return keyboard.Key.ctrl
        elif key_str == 'Key.alt':
            return keyboard.Key.alt
        elif key_str == 'Key.up':
            return keyboard.Key.up
        elif key_str == 'Key.down':
            return keyboard.Key.down
        elif key_str == 'Key.left':
            return keyboard.Key.left
        elif key_str == 'Key.right':
            return keyboard.Key.right

        # 普通字符按键
        if len(key_str) == 1:
            return key_str

        return None
