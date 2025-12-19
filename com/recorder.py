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

        self.stop_replay = False
        self.recorded_data = []
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )

        self.toggle_record_key = keyboard.Key.f12  # Start/stop recording
        self.save_key = keyboard.Key.f10  # Save recording

    def get_current_time(self):
        return time.time() - self.start_time if self.start_time else 0

    def on_key_press(self, key):
        if key == self.toggle_record_key:
            self.toggle_recording()
            return

        if key == self.save_key and not self.recording:
            self.save_recording()
            return

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
                'type': 'key_release',
                'key': key_str,
                'time': self.get_current_time()
            })
            self.recording_data.append({
                'type': 'key_release',
                'key': key_str,
                'time': self.get_current_time()
            })

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.recording_data = []
        self.start_time = time.time()
        print("Recording started... (Press F12 again to stop, F10 to save)")

    def stop_recording(self):
        self.recording = False
        print(f"Recording stopped. {len(self.recording_data)} events recorded.")

    def save_recording(self, filename=None):
        if not self.recording_data:
            print("No recording data to save.")
            return

        if not filename:
            save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resource', 'json'))
            os.makedirs(save_dir, exist_ok=True)
            filename = os.path.join(save_dir, 'n6卡尼曼部落.json')

        final_record = self.transform_data(self.recording_data)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_record, f, indent=2)
            print(f"Recording saved to {filename}")
        except Exception as e:
            print(f"Save failed: {e}")

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
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Load failed: {e}")
            return None

    def on_f98_press(self, key):
        if key == keyboard.Key.f9:
            self.stop_replay = not self.stop_replay
        if key == keyboard.Key.f8:
            sys.exit(0)

    def start_replay(self, filename=None):
        if self.replaying:
            print("Already replaying...")
            return

        keyboard.Listener(on_press=self.on_f98_press).start()
        data = self.load_recording(filename) if filename else self.recording_data

        if not data:
            print("No data to replay.")
            return

        self.replaying = True
        self.stop_replay = False
        print("Replaying... (F9 to pause, F8 to stop and output executed commands)")
        Thread(target=self._replay, args=(data,), daemon=True).start()

    def _replay(self, data):
        keyboard_controller = keyboard.Controller()
        stopped = False
        for event in data:
            if self.stop_replay:
                stopped = True
                print("Paused replay. Executed so far:")
                print(self.recorded_data)
                while self.stop_replay:
                    time.sleep(1)
            if stopped:
                print("Resuming replay. Clearing log.")
                stopped = False
                self.recorded_data.clear()

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
                print(f"Replay error: {e}")
            self.recorded_data.append(event)

        self.replaying = False
        print("Replay finished.")

    def _get_key(self, key_str):
        special_keys = {
            'Key.space': keyboard.Key.space,
            'Key.enter': keyboard.Key.enter,
            'Key.backspace': keyboard.Key.backspace,
            'Key.tab': keyboard.Key.tab,
            'Key.esc': keyboard.Key.esc,
            'Key.shift': keyboard.Key.shift,
            'Key.ctrl': keyboard.Key.ctrl,
            'Key.alt': keyboard.Key.alt,
            'Key.up': keyboard.Key.up,
            'Key.down': keyboard.Key.down,
            'Key.left': keyboard.Key.left,
            'Key.right': keyboard.Key.right
        }
        if key_str in special_keys:
            return special_keys[key_str]
        if len(key_str) == 1:
            return key_str
        return None

    def start(self):
        print("Recorder running.")
        print("F12 = Start/Stop recording")
        print("F10 = Save")
        print("ESC = Exit")
        self.keyboard_listener.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
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
