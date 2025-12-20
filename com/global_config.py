import datetime
import os
import sys
import time

import click_func as cf
from call_back_func import press_f, begin_fb_loop, change_to_outer_fb, leave_team, press_esc

# Global status codes
# 0. Initialization
# 1. Preparing to enter dungeon
# 2. Inside dungeon
# 3. Pre-entry actions before dungeon
# 4. Global exception occurred
# 5. Character died
# 6. Another global exception
global_status = 0

# Tools and runtime states
automation_tool = None
replay = None
fb_times = 0
fb_time_out_times = 0
fb_time_out_sec = 300
last_fb_start_time = time.time()

# Career settings before dungeon
target_careers = None
red_careers = None

# Whether this is the n6 dungeon
is_n6 = False

def get_image_path(relative_path):
    """
    Get the absolute path to an image file, compatible with both
    development and packaged environments (e.g. PyInstaller).

    Args:
        relative_path: Path relative to the project root,
                       e.g., "images/logo.png" or "resources/background.jpg"
    """
    try:
        # For PyInstaller: extracted to a temp directory
        base_path = sys._MEIPASS
    except AttributeError:
        # For development: use script location
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)

# Default JSON script path
script_json = get_image_path('resource/json/蒂娜.json')

def print_log(str):
    print(f"{datetime.now()}:{str}")

# Image matcher with optional click behavior and state change
class img_info:
    def __init__(self, path, click_func=None, call_back=None, status_change_to=None, interval=3, threshold=0.95,
                 check_when_status=None):
        self.path = path
        self.click_func = click_func
        self.call_back = call_back
        self.status_change_to = status_change_to
        self.interval = interval
        self.threshold = threshold
        self.check_when_status = check_when_status

# Image detection rules
img_info_arr = [
    img_info(get_image_path("resource/img/change_to_single.png"), click_func=cf.change_to_single, status_change_to=1,
             check_when_status=[1, 2]),
    img_info(get_image_path("resource/img/gotoFb.png"), click_func=cf.gotoFb, status_change_to=1, threshold=0.9,
             check_when_status=[1, 2]),
    img_info(get_image_path("resource/img/trigger_fb.png"), click_func=None, status_change_to=2, check_when_status=[2]),
    img_info(get_image_path("resource/img/win.png"), click_func=None, status_change_to=0, check_when_status=[2],
             threshold=0.9),
    img_info(get_image_path("resource/img/die.png"), click_func=cf.qilai, status_change_to=None,
             threshold=0.7),
    img_info(get_image_path("resource/img/esc.png"), click_func=press_esc,
             threshold=0.88),
]

# OCR matcher with optional callback
class ocr_info:
    def __init__(self, match_str, pos, operation=None, check_when_status=None, need_pos=False):
        self.match_str = match_str
        self.pos = pos
        self.operation = operation
        self.check_when_status = check_when_status
        self.need_pos = need_pos

    def is_match(self, results):
        if results:
            for result in results:
                ocr_str, pos = result
                if self.match_str in ocr_str:
                    if self.need_pos:
                        self.operation(pos)
                    else:
                        self.operation()
        return False

# OCR detection rules
ocr_info_arr = {
    # "Dungeon Entrance": Detect if the "F" key prompt appears (used to enter dungeon)
    "dungeon_entry": ocr_info("F", (1371, 534, 280, 80), operation=press_f, check_when_status=[1]),
    
    # "Inside Dungeon": Detect if "Leave" appears in menu (confirm we are in)
    "inside_dungeon": ocr_info("Leave", (39, 226, 296, 33), operation=begin_fb_loop, check_when_status=[1]),

    # "Outside Dungeon": Detect if we are back in town (Asterleeds)
    "outside_dungeon": ocr_info("Asterleeds", (41, 228, 83, 26), operation=change_to_outer_fb, check_when_status=[2]),

    # "Not Left Party": Detect if too many party members remain
    "not_left_party": ocr_info("超过2人", (721, 265, 476, 50), operation=leave_team, check_when_status=[1, 3]),
    # Means: "More than 2 players in team, cannot enter this mode"
}
