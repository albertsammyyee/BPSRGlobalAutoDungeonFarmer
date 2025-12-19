import ctypes
import os
import sys
import time
import threading
from subprocess import Popen, PIPE

from pynput import keyboard
from pynput.keyboard import Controller, Key

# 初始化键盘控制器
keyboard_controller = Controller()

# 状态变量
running = False
shift_pressed = False
doRush = False
w_pressed = 0
last_rush_time = time.time()-30


def on_press(key):
    global running, doRush, last_rush_time

    # 按下V键切换运行状态
    try:
        if key.char == 'v' or key.char == 'V':  # 同时支持大小写V
            if not running:
                print("脚本已启动 (再次按V停止)")
                running = True
                # 在新线程中执行操作，避免阻塞监听器
                threading.Thread(target=start_operation, daemon=True).start()
            else:
                print("脚本已停止")
                running = False
        if key.char == 'z' or key.char == 'Z':  # 同时支持大小写V
            print(doRush)
            if running and not doRush:
                print("开启冲刺")
                doRush = True
                last_rush_time = time.time()
            else:
                print("脚本已停止")
                running = False
        if key == Key.f10:
            while w_pressed > 0:
                keyboard_controller.release('w')
                w_pressed = w_pressed - 1
    except AttributeError:
        # 忽略特殊按键
        pass


def on_release(key):
    # 如果需要可以在这里处理按键释放事件
    pass


def start_operation():
    global running, shift_pressed, w_pressed, doRush

    # 按住W
    keyboard_controller.press('w')
    w_pressed = w_pressed + 1
    time.sleep(0.05)

    # 按住Shift
    keyboard_controller.press(Key.shift)
    shift_pressed = True
    time.sleep(0.05)  # 短暂延迟确保按键被正确识别
    keyboard_controller.release(Key.shift)
    # 循环按空格直到停止信号
    while running:
        # 按下并释放空格
        keyboard_controller.press(Key.space)
        time.sleep(0.05)  # 空格按下的时间
        while w_pressed > 0:
            keyboard_controller.release('w')
            w_pressed = w_pressed - 1
        time.sleep(0.08)
        keyboard_controller.press('w')
        w_pressed = w_pressed + 1
        keyboard_controller.release(Key.space)
        time.sleep(0.65)  # 空格释放后的间隔
        if doRush:
            time.sleep(0.2)
            keyboard_controller.press('e')
            time.sleep(0.05)
            keyboard_controller.release('e')
            time.sleep(1.2)
            keyboard_controller.press('e')
            time.sleep(0.05)
            keyboard_controller.release('e')
            time.sleep(1.6)
            keyboard_controller.release(Key.shift)
            time.sleep(0.1)
            keyboard_controller.press(Key.shift)
            time.sleep(0.1)
            keyboard_controller.press(Key.shift)
            doRush = False
            print("冲刺结束")

    # 停止后释放所有按键
    while w_pressed > 1:
        keyboard_controller.release('w')
        w_pressed = w_pressed - 1

    if shift_pressed:
        keyboard_controller.release(Key.shift)
        shift_pressed = False


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


if __name__ == "__main__":
    if not is_admin():
        print("当前不是以管理员权限运行")
        print("正在请求管理员权限...")

        # 尝试提升权限
        if run_as_admin():
            print("权限提升成功，程序将以管理员权限重新运行")
            # 注意：提升权限后，原进程会继续运行，这里可以选择退出
            sys.exit(0)
        else:
            print("无法获取管理员权限，程序可能无法正常运行")
    else:
        print("程序正在以管理员权限运行")
        # 在这里编写需要管理员权限的代码
    print("键盘控制脚本就绪")
    print("按V键开始马拉松，再次按V键停止跳跃（但是人物还是会往前跑），按Z键衔接双E")
    print("开局前先把Z键的幻想下了，然后冲刺使用E键，马拉松过程中只需要冲刺CD好就按一下Z即可")

    # 启动键盘监听器 我
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
