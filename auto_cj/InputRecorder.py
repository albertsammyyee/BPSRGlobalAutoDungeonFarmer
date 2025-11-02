import json
import time

from pynput import keyboard

from util import *


class InputRecorder:
    def __init__(self, file_name):
        self.pressed_map = {}
        self.recording = False
        self.recording_data = []
        self.start_time = 0
        self.file_name = file_name
        # 用于停止回放的事件
        self.recorded_data = []
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.is_interrupt = False
        # 热键定义
        self.toggle_record_key = keyboard.Key.f12  # F12开始/停止录制
        self.save_key = keyboard.Key.f10  # 保存录制
        self.interrupt_key = keyboard.Key.f8  # 终止录制


    def get_current_time(self):
        """获取相对于录制开始的时间"""
        return time.time() - self.start_time if self.start_time else 0

    def on_key_press(self, key):
        """键盘按键按下事件处理"""
        # 检查是否是控制键

        if key == self.toggle_record_key:
            self.toggle_recording()
            self.img = capture_window(app_name)
            return  # 修改：不返回False，让监听器继续工作

        if key == self.save_key and not self.recording:
            self.save_recording()
            self.is_interrupt = True
            return  # 修改：不返回False，让监听器继续工作
        if key == self.interrupt_key:
            self.is_interrupt = True
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
        print("开始录制... (再次按【F12】停止，按【F10】保存录制文件)")

    def stop_recording(self):
        """停止录制"""
        self.recording = False
        print(f"停止录制，共记录了 {len(self.recording_data)} 个事件")

    def save_recording(self):
        """保存录制数据到文件"""
        if not self.recording_data:
            print("没有可保存的录制数据")
            return
        curr_dir = get_exe_dir() + "/record"
        print(f"当前路径为{curr_dir}")
        if not os.path.exists(curr_dir):
            # 递归创建文件夹（若父目录不存在也会一并创建）
            os.makedirs(curr_dir, exist_ok=True)
            print(f"文件夹 '{curr_dir}' 创建成功")
        filename = f"{curr_dir}/{self.file_name}.json"
        img_name = f"{curr_dir}/{self.file_name}.png"
        final_record = self.transform_data(self.recording_data)
        try:
            with open(filename, 'w') as f:
                json.dump(final_record, f, indent=2)
            if self.img:
                self.img.save(img_name)
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
        print("按【F12】开始/停止录制，停止后再次按【F12】则清空之前的录制重新开始")
        print("录制停止后按【F10】保存录制")
        print("按【F8】跳出录制功能")
        # 启动监听器
        self.keyboard_listener.start()

        # 保持程序运行

        while True:
            time.sleep(1)
            if self.is_interrupt:
                print("终止录制")
                self.keyboard_listener.stop()
                break
