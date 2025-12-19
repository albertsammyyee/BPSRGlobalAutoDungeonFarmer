import ctypes
import ctypes.wintypes
import threading
import win32gui
import sys
import os
import platform

# 检查系统和Python架构是否匹配
system_arch = platform.architecture()[0]
print(f"系统架构: {system_arch}, Python架构: {platform.architecture()[0]}")
if system_arch != platform.architecture()[0]:
    print("警告: Python架构与系统架构不匹配，这可能导致钩子失败！")
    print("请安装与系统匹配的Python版本（64位系统需要64位Python）")

# 定义Windows API常量
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
VK_1 = 0x31
WM_QUIT = 0x0012

# 加载系统库（使用明确的加载方式）
try:
    user32 = ctypes.WinDLL('user32.dll', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32.dll', use_last_error=True)
except OSError as e:
    print(f"加载系统库失败: {e}")
    print("可能缺少必要的系统组件，请检查系统完整性")
    sys.exit(1)

# 定义钩子回调函数类型
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('vkCode', ctypes.wintypes.DWORD),
        ('scanCode', ctypes.wintypes.DWORD),
        ('flags', ctypes.wintypes.DWORD),
        ('time', ctypes.wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


# 设置函数参数类型
user32.SetWindowsHookExW.argtypes = (
    ctypes.c_int,  # idHook
    HOOKPROC,  # lpfn
    ctypes.wintypes.HINSTANCE,  # hMod
    ctypes.wintypes.DWORD  # dwThreadId
)
user32.SetWindowsHookExW.restype = ctypes.wintypes.HHOOK

user32.CallNextHookEx.argtypes = (
    ctypes.wintypes.HHOOK, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM
)
user32.CallNextHookEx.restype = ctypes.c_long

user32.UnhookWindowsHookEx.argtypes = (ctypes.wintypes.HHOOK,)
user32.UnhookWindowsHookEx.restype = ctypes.c_bool

# 全局变量
g_hook = None
stop_flag = False
pos_x = 1465
pos_y = 1170
color_1 = 170


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


@HOOKPROC
def low_level_keyboard_handler(nCode, wParam, lParam):
    global stop_flag

    if nCode >= 0 and wParam == WM_KEYDOWN:
        try:
            kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT))[0]
            vk_code = kb_struct.vkCode

            # F12退出
            if vk_code == 123:
                stop_flag = True
                user32.PostThreadMessageW(threading.get_ident(), WM_QUIT, 0, 0)
                return 1

            # F11继续
            if vk_code == 122:
                stop_flag = False
                print("已继续检测")
                return 1

            # 处理1键
            if vk_code == VK_1:
                if not stop_flag:
                    pixel_color = get_pixel_color(pos_x, pos_y)
                    if pixel_color[0] < color_1:
                        print(f"阻止输入'1' (像素颜色: {pixel_color})")
                        return 1  # 阻止按键
                    else:
                        print(f"允许输入'1' (像素颜色: {pixel_color})")
                else:
                    print("检测已停止，允许输入'1'")
        except Exception as e:
            print(f"钩子处理错误: {e}")

    return user32.CallNextHookEx(g_hook, nCode, wParam, lParam)


def start_hook():
    global g_hook

    # 关键修复：使用更可靠的方式获取模块句柄
    h_module = None
    try:
        # 方法1: 尝试获取当前进程的模块句柄
        h_module = kernel32.GetModuleHandleW(None)
        if not h_module:
            print(f"方法1获取模块句柄失败，错误: {ctypes.get_last_error()}")

            # 方法2: 使用GetModuleHandleEx获取
            GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS = 0x00000004
            h_module = ctypes.wintypes.HMODULE()
            if not kernel32.GetModuleHandleExW(
                    GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
                    ctypes.c_wchar_p(sys.argv[0]),
                    ctypes.byref(h_module)
            ):
                print(f"方法2获取模块句柄失败，错误: {ctypes.get_last_error()}")

                # 方法3: 直接使用0作为模块句柄（最后尝试）
                h_module = 0
                print("使用0作为模块句柄进行最后尝试")

        # 设置钩子


        g_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, low_level_keyboard_handler, 0, 0)
        if not g_hook:
            err_code = ctypes.get_last_error()
            print(f"设置钩子失败: 错误代码 {err_code}")

            # 获取详细错误信息
            buf = ctypes.create_unicode_buffer(256)
            if kernel32.FormatMessageW(
                    0x1200,  # FORMAT_MESSAGE_FROM_SYSTEM
                    None,
                    err_code,
                    0,
                    buf,
                    ctypes.sizeof(buf),
                    None
            ):
                print(f"错误信息: {buf.value}")

            # 显示可能的解决方案
            print("\n可能的解决方案:")
            print("1. 确保使用与系统架构匹配的Python版本（64位系统用64位Python）")
            print("2. 以管理员身份运行程序")
            print("3. 安装Microsoft Visual C++ Redistributable")
            print("4. 修复系统文件: sfc /scannow")
            return

        print("钩子已安装，按下F12可停止并退出，按下F11则继续检测")

        # 消息循环
        msg = ctypes.wintypes.MSG()
        while not stop_flag:
            ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if ret == 0 or ret == -1:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    except Exception as e:
        print(f"钩子启动错误: {e}")
    finally:
        if g_hook:
            user32.UnhookWindowsHookEx(g_hook)
            g_hook = None
        print("钩子已卸载")


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

        # print("请输入目标图标的坐标：")
        # pos_x = int(input("x坐标："))
        # pos_y = int(input("y坐标："))
        print(f"坐标设置为：({pos_x},{pos_y})")

        # 在主线程中运行钩子（关键修复）
        start_hook()

    except KeyboardInterrupt:
        stop_flag = True
        if g_hook:
            user32.UnhookWindowsHookEx(g_hook)
        print("程序已终止")
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        sys.exit(0)
