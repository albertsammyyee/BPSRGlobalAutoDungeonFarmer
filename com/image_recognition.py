from datetime import datetime
from random import random

import cv2
import numpy as np
import pyautogui
import win32gui
import win32con
import time
import os
import mss
import mss.tools
from ctypes import windll, byref, wintypes
from threading import Thread
import global_config as global_config
from util.util import print_log
from rapidocr_onnxruntime import RapidOCR


class GameAutomationTool:
    def __init__(self, window_title=None, target_resolution=(1920, 1080)):
        """
        初始化游戏自动化工具
        :param window_title: 游戏窗口标题（支持部分匹配）
        :param target_resolution: 目标游戏分辨率，默认1920x1080
        """
        self.window_title = window_title
        self.target_resolution = target_resolution
        self.ocr = RapidOCR()
        # 窗口信息
        self.hwnd = None  # 窗口句柄
        self.client_rect = None  # 客户区坐标 (left, top, right, bottom)
        self.client_size = None  # 客户区大小 (width, height)
        self.fb_num = 0  # 客户区大小 (width, height)

        # 运行状态
        self.running = False
        self.monitoring = False
        self.in_fb = False

        # 配置pyautogui
        pyautogui.FAILSAFE = True  # 启用安全模式，鼠标移到角落可终止程序
        pyautogui.PAUSE = 0.2  # 操作间的暂停时间

    def find_game_window(self):
        """查找并定位游戏窗口，获取客户区信息"""

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.window_title in title:
                    extra.append(hwnd)

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            self.hwnd = windows[0]
            window_title = win32gui.GetWindowText(self.hwnd)
            print_log(f"已找到游戏窗口: {window_title}")

            # 获取客户区信息（实际游戏内容区域）
            rect = wintypes.RECT()
            windll.user32.GetClientRect(self.hwnd, byref(rect))
            screen_left, screen_top = win32gui.ClientToScreen(self.hwnd, (rect.left, rect.top))
            screen_right, screen_bottom = win32gui.ClientToScreen(self.hwnd, (rect.right, rect.bottom))

            self.client_rect = (screen_left, screen_top, screen_right, screen_bottom)
            self.client_size = (screen_right - screen_left, screen_bottom - screen_top)

            print_log(f"客户区位置: {self.client_rect}")
            print_log(f"客户区大小: {self.client_size[0]}x{self.client_size[1]}")

            # 检查分辨率是否符合预期
            if self.client_size != self.target_resolution:
                print_log(f"警告: 客户区大小与目标分辨率不符 ({self.target_resolution[0]}x{self.target_resolution[1]})")

            return True
        else:
            print_log(f"未找到标题包含 '{self.window_title}' 的窗口")
            return False

    def bring_window_to_front(self):
        """将游戏窗口置顶显示"""
        if not self.hwnd:
            print_log("未找到游戏窗口，无法置顶")
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

    def ocr_check(self, sub_left=0, sub_top=0, width=0, height=0):
        left, top, right, bottom = self.client_rect
        img = self.capture_game_window(sub_left, sub_top, width, height)
        result, _ = self.ocr(img)
        arr = []
        if not result:
            return []
        # cv2.imwrite("aaa.png", img)
        for box, text, confidence in result:
            abs_left = sub_left + left + box[0][0]
            abs_top = sub_top + top + box[0][1]
            width = box[2][0] - box[0][0]
            height = box[2][1] - box[0][1]
            arr.append((text, (abs_left, abs_top, width, height)))
            # print(f"文本: {text}, 坐标: {(abs_left, abs_top, width, height)}, 置信度: {confidence}")
        return arr

    def capture_game_window(self, sub_left=0, sub_top=0, width=0, height=0):
        """
        捕获游戏窗口内容（解决黑屏问题）
        :return: OpenCV格式图像 (ndarray) 或 None
        """
        if not self.client_rect:
            print_log("未获取到客户区信息，无法捕获窗口")
            return None

        left, top, right, bottom = self.client_rect
        if width == 0:
            width = right - left
            height = bottom - top
        left = left + sub_left
        top = top + sub_top
        # 方法1：使用MSS库捕获（推荐，适用于硬件加速窗口）
        try:
            with mss.mss() as sct:
                # 定义捕获区域
                monitor = {"top": top, "left": left, "width": width, "height": height}
                # 捕获图像
                sct_img = sct.grab(monitor)
                # 转换为OpenCV格式
                img = np.array(sct_img)
                # 转换颜色空间 (BGRA -> BGR)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                return img
        except Exception as e:
            print_log(f"MSS捕获失败: {str(e)}，尝试备用方案")

        # 方法2：使用pyautogui区域截图（备用方案）
        try:
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            return img
        except Exception as e:
            print_log(f"备用方案捕获失败: {str(e)}")
            return None

    def find_image_in_game(self, target_image_path, game_img, threshold=0.8):
        """
        在游戏窗口中查找目标图像
        :param target_image_path: 目标图像路径
        :param threshold: 匹配阈值（0-1）
        :return: 找到的位置列表 [(x, y, width, height), ...]
        """
        # 捕获游戏窗口图像

        # 检查目标图像是否存在
        if not os.path.exists(target_image_path):
            print_log(f"错误: 目标图像 '{target_image_path}' 不存在")
            return []

        # 读取目标图像
        target_img = cv2.imread(target_image_path)
        if target_img is None:
            print_log(f"错误: 无法读取目标图像 '{target_image_path}'")
            return []

        # 获取图像尺寸
        target_height, target_width = target_img.shape[:2]
        game_height, game_width = game_img.shape[:2]

        # 检查目标图像是否过大
        if target_width > game_width or target_height > game_height:
            print_log("错误: 目标图像大于游戏窗口尺寸")
            return []

        # 执行模板匹配
        result = cv2.matchTemplate(game_img, target_img, cv2.TM_CCOEFF_NORMED)

        # 提取匹配位置
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))  # 转换为(x, y)格式

        # 去重相邻结果
        unique_locations = []
        seen = set()
        for (x, y) in locations:
            # 对位置进行分组去重（减少重复识别）
            key = (round(x / 20) * 20, round(y / 20) * 20)
            if key not in seen:
                seen.add(key)
                unique_locations.append((x, y, target_width, target_height))

        return unique_locations

    def get_win_pos(self):
        return  self.client_rect[0],self.client_rect[1]
    def click_position(self, x, y, duration=0.1, button='left',is_abs_pos=False):
        """
        点击游戏窗口内的指定位置
        :param x, y: 相对于游戏窗口客户区的坐标
        :param duration: 鼠标移动时间（秒）
        :param button: 点击的按键（'left', 'right', 'middle'）
        :return: 是否点击成功
        """
        if not self.client_rect:
            print_log("未获取到客户区信息，无法点击")
            return False
        screen_x =  x
        screen_y =  y
        if not is_abs_pos:
            # 转换为屏幕绝对坐标
            screen_x = self.client_rect[0] + x
            screen_y = self.client_rect[1] + y


        # 移动鼠标并点击
        try:
            pyautogui.moveTo(screen_x, screen_y, duration=duration)
            pyautogui.click(button=button)
            print_log(f"已点击位置: 屏幕坐标({screen_x}, {screen_y})")
            return True
        except Exception as e:
            print_log(f"点击失败: {str(e)}")
            return False

    def find_img(self, target_image_path, game_img, threshold=0.8):
        """
        查找图像并点击
        :param target_image_path: 目标图像路径
        :param threshold: 匹配阈值
        :param click_center: 是否点击图像中心
        :param wait_time: 点击后等待时间（秒）
        :return: 是否成功点击
        """
        # 查找目标图像
        return self.find_image_in_game(target_image_path, game_img, threshold)

    def start_monitoring(self, img_info_arr, ocr_info_arr):
        """
        开始持续监控并点击目标图像
        :param img_info_arr:
        :param target_image_path: 目标图像路径
        :param interval: 检查间隔（秒）
        :param threshold: 匹配阈值
        """
        self.monitoring = True
        self.running = True

        def monitor_loop():
            while self.running:

                game_img = self.capture_game_window()
                if game_img is None:
                    print_log("截图画面失败")
                    time.sleep(5)
                    continue
                try:
                    if not self.monitoring:
                        time.sleep(5)
                        continue
                    for img_info in img_info_arr:
                        # 校验当前状态是否需要检测此图片
                        if img_info.check_when_status and global_config.global_status not in img_info.check_when_status:
                            continue
                        if "yueka" in img_info.path and not self.is_between_450_510():
                            continue
                        positions = self.find_img(img_info.path, game_img, img_info.threshold)
                        if positions:
                            print_log(f"找到图片{img_info.path}")
                            self.click_pos(positions, img_info.click_func)
                            if img_info.status_change_to:
                                print_log(f"change global_status from {global_config.global_status} to {img_info.status_change_to}")
                                global_config.global_status = img_info.status_change_to
                            if img_info.call_back:
                                img_info.call_back()
                            # 检测成功的情况下，需要重新截图
                            game_img = self.capture_game_window()
                        # else:
                        #     print_log(f"未找到图片{img_info.path}")
                    for ocr_info in ocr_info_arr:
                        if not ocr_info.check_when_status or global_config.global_status in ocr_info.check_when_status:
                            ocr_info.is_match(self.ocr_check(*ocr_info.pos))
                except Exception as e:
                    print_log(e)
                # 等待间隔时间
                time.sleep(0.5)

        # 在新线程中运行监控
        Thread(target=monitor_loop, daemon=True).start()

    def click_pos(self, positions, click_func=None):

        # 取第一个匹配位置
        x, y, w, h = positions[0]

        # 计算点击坐标
        if click_func is None:
            click_x = x + w // 2
            click_y = y + h // 2
        else:
            click_x, click_y = click_func(x, y, w, h)
        if click_x != 0:
            # 执行点击
            self.click_position(click_x, click_y)
        time.sleep(0.5)

    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        self.monitoring = False
        print_log("已停止监控")

    def is_between_450_510(self):
        # 获取当前时间
        now = datetime.now()

        # 提取当前小时和分钟
        current_hour = now.hour
        current_minute = now.minute

        # 计算当前时间的总分钟数（便于比较）
        current_total_minutes = current_hour * 60 + current_minute

        # 目标时间段的总分钟数
        start_total_minutes = 4 * 60 + 50  # 4:50
        end_total_minutes = 5 * 60 + 10  # 5:10

        # 判断当前时间是否在目标时间段内
        return start_total_minutes <= current_total_minutes <= end_total_minutes


# 配置参数
GAME_WINDOW_TITLE = "星痕共鸣"  # 替换为你的游戏窗口标题（支持部分匹配）

# 初始化工具
automation_tool = GameAutomationTool(
    window_title=GAME_WINDOW_TITLE,
    target_resolution=(1920, 1080)
)
