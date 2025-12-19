import json
import sys
import time
from pynput import mouse, keyboard
from threading import Thread
import os


class InputRecorder:
    def __init__(self):
        self.pressed_map = {}
        self.recording = False
        self.recording_data = []
        self.start_time = 0
        self.replaying = False

        # 用于停止回放的事件
        self.stop_replay = False
        self.recorded_data = []
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )

        # 热键定义
        self.toggle_record_key = keyboard.Key.f12  # F12开始/停止录制
        self.save_key = keyboard.Key.f10  # 保存录制

    def get_current_time(self):
        """获取相对于录制开始的时间"""
        return time.time() - self.start_time if self.start_time else 0

    def on_key_press(self, key):
        """键盘按键按下事件处理"""
        # 检查是否是控制键

        if key == self.toggle_record_key:
            self.toggle_recording()
            return  # 修改：不返回False，让监听器继续工作

        if key == self.save_key and not self.recording:
            self.save_recording()
            return  # 修改：不返回False，让监听器继续工作

        if self.recording:
            try:
                key_str = key.char

            except AttributeError:
                key_str = str(key)
            if key_str in self.pressed_map:
                return
            else:
                self.pressed_map[key_str] = True
            print({
                'type': 'key_press',
                'key': key_str,
                'time': self.get_current_time()
            })
            self.recording_data.append({
                'type': 'key_press',
                'key': key_str,
                'time': self.get_current_time()
            })

    def on_key_release(self, key):
        """键盘按键释放事件处理"""
        if self.recording:

            try:
                key_str = key.char
            except AttributeError:

                key_str = str(key)

            if key_str in self.pressed_map:
                del self.pressed_map[key_str]
            else:
                return
            print({
                'type': 'key_press',
                'key': key_str,
                'time': self.get_current_time()
            })
            self.recording_data.append({
                'type': 'key_release',
                'key': key_str,
                'time': self.get_current_time()
            })

    def toggle_recording(self):
        """切换录制状态"""
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """开始录制"""
        self.recording = True
        self.recording_data = []
        self.start_time = time.time()
        print("开始录制... (再次按F12停止，按F10保存录制文件)")

    def stop_recording(self):
        """停止录制"""
        self.recording = False
        print(f"停止录制，共记录了 {len(self.recording_data)} 个事件")

    def save_recording(self, filename=None):
        """保存录制数据到文件"""
        if not self.recording_data:
            print("没有可保存的录制数据")
            return
        print(os.path.abspath(__file__))
        if not filename:
            filename = f"{os.path.abspath(__file__).replace("recorder.py", "")}/../recorder/recording_{int(time.time())}.json"
        final_record = self.transform_data(self.recording_data)
        try:
            with open(filename, 'w') as f:
                json.dump(final_record, f, indent=2)
            print(f"录制数据已保存到 {filename}")
        except Exception as e:
            print(f"保存失败: {e}")

    def transform_data(self, datas):
        result = []
        last_time = 0
        for data in datas:
            curr_time = data['time']
            result.append({
                "type": 'sleep',
                "time": curr_time - last_time
            })
            result.append({
                "type": data['type'],
                "key": data['key']
            })

            last_time = curr_time
        return result

    def load_recording(self, filename):
        """从文件加载录制数据"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载失败: {e}")
            return None

    def on_f98_press(self, key):
        if key == keyboard.Key.f9:
            self.stop_replay = not self.stop_replay

        if key == keyboard.Key.f8:
            sys.exit(0)

    def start_replay(self, filename=None):
        """回放录制的数据"""
        if self.replaying:
            print("正在回放中...")
            return
        keyboard.Listener(
            on_press=self.on_f98_press
        ).start()
        # 如果指定了文件名，则加载文件；否则使用当前录制的数据
        data = self.load_recording(filename) if filename else self.recording_data

        if not data:
            print("没有可回放的数据")
            return

        self.replaying = True
        self.stop_replay = False
        print("开始回放... (按F9可暂停,F8结束进程,并输出已执行指令)")
        Thread(target=self._replay, args=(data,), daemon=True).start()

    def _replay(self, data):
        """实际执行回放的方法"""

        keyboard_controller = keyboard.Controller()
        stopped = False
        for event in data:
            if self.stop_replay:
                stopped = True
                print("暂停回放，输出已回放数据：")
                print(self.recorded_data)
                while self.stop_replay:
                    time.sleep(1)
            if stopped == True:
                print("继续回放，清空已输出得数据：")
                stopped = False
                self.recorded_data.clear()

            # 执行事件
            try:
                if event['type'] == 'key_press':
                    key = self._get_key(event['key'])
                    if key:
                        keyboard_controller.press(key)

                elif event['type'] == 'key_release':
                    key = self._get_key(event['key'])
                    if key:
                        keyboard_controller.release(key)
                elif event['type'] == 'sleep':
                    time.sleep(event['time'])

            except Exception as e:
                print(f"回放事件时出错: {e}")
            self.recorded_data.append(event)
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

    def start(self):
        """启动监听器"""
        print("输入录制器已启动")
        print("按F12开始/停止录制")
        print("录制停止时按F10保存录制")
        print("按ESC退出程序")

        # 启动监听器
        self.keyboard_listener.start()

        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("程序退出")
            self.keyboard_listener.stop()


def transfer_old_json(input, output):
    recorder = InputRecorder()
    with open(input, 'r', encoding='utf-8') as file:
        data = json.load(file)
        with open(output, 'w') as f:
            json.dump(recorder.transform_data(data), f, indent=2)


if __name__ == "__main__":
    recorder = InputRecorder()
    recorder.start()
    time.sleep(10000)
