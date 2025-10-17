import json
import os
import time
from threading import Thread

from pynput import keyboard
from pynput.mouse import Controller, Button

json_file_name = 'recording_1755429068.json'
class InputRecorder:
    def __init__(self):
        self.recording = False
        self.recording_data = []
        self.replaying = False
        # 用于停止回放的事件
        self.stop_replay = False
        self.recorded_data = []



    def load_recording(self, filename):
        """从文件加载录制数据"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载失败: {e}")
            return None

    def start_replay(self, filename=None):
        """回放录制的数据"""
        if self.replaying:
            print("正在回放中...")
            return

        # 如果指定了文件名，则加载文件；否则使用当前录制的数据
        data = self.load_recording(filename) if filename else self.recording_data

        if not data:
            print("没有可回放的数据")
            return
        self.replaying = True
        Thread(target=self._replay, args=(data,), daemon=True).start()

    def _replay(self, data):
        """实际执行回放的方法"""
        keyboard_controller = keyboard.Controller()
        mouse = Controller()

        for event in data:
            if not self.replaying:
                print("中断回放...")
                return
            # 执行事件
            try:
                # print(event)
                if event['type'] == 'key_press':
                    key = self._get_key(event['key'])
                    if key:
                        keyboard_controller.press(key)

                elif event['type'] == 'key_release':
                    key = self._get_key(event['key'])
                    if key:
                        keyboard_controller.release(key)
                elif event['type'] == 'mouse_click':
                    mouse.press(Button.left)  # 按下左键
                    time.sleep(event['time'])  # 短暂延迟，模拟实际点击时长
                    mouse.release(Button.left)  # 释放左键
                elif event['type'] == 'sleep':
                    time.sleep(event['time'])
                elif event['type'] == 'scroll':
                    mouse.scroll(0, event['key'])
            except Exception as e:
                print(f"回放事件时出错: {e}")

        self.replaying = False
        print("回放结束")



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


recorder = InputRecorder()
