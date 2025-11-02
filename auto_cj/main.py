import traceback

from InputRecorder import InputRecorder
from PlayBack import PlayBack
from util import *


def selection():
    while True:
        try:
            num = input("请输入数字: 1.录制新的采集 2.回放录制 3.回放录制(后台运行)\r\n")
            if num == "1":
                file_name = input("请输入录制的文件名称\r\n")

                recorder = InputRecorder(file_name)
                recorder.start()
            elif num == "2" or num == "3":
                dir_path = get_exe_dir() + "/record"
                files = list_file(dir_path, "json")
                while True:
                    try:
                        file_index = int(input("请输入需要回放的文件序号\r\n"))
                        play_back = PlayBack(f"{dir_path}/{files[file_index]}", num == "3")
                        break
                    except:
                        traceback.print_exc()
                        print("输入序号有误")
                play_back.start()
            else:
                print("输入有误,请重新输入")
        except Exception as e:
            traceback.print_exc()  # 直接打印到控制台
            print("输入有误,请重新输入")


if __name__ == "__main__":
# pyinstaller -F -p G:\xhgm_script\AutoFuckBKLGetDress\auto_cj .\main.py
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
    selection()
