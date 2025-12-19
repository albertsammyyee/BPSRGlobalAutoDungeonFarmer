import time
from threading import Thread

import keyboard_playback
import global_config
from call_back_func import global_error_check, pre_operation_check, n6_click
from image_recognition import automation_tool


def select_target_careers():
    target_careers = input(
        "Is this for TN weapon farming? Enter a number (or press Enter to skip):\n1. Forest Whisperer\n2. Soul Musician\n3. Shield Knight\n4. Greatblade Guardian\n"
    )
    if target_careers:
        target_careers = int(target_careers)
        if target_careers == 1:
            global_config.target_careers = '森语者'
        elif target_careers == 2:
            global_config.target_careers = '灵魂乐手'
        elif target_careers == 3:
            global_config.target_careers = '盾'
        elif target_careers == 4:
            global_config.target_careers = '巨刃守护者'


def select_red_careers():
    origin_careers = int(input(
        "Choose your red class:\n1. Thunder Shadow Swordsman\n2. Azure Wind Knight\n3. Sharpshooter\n4. Ice Mage\n"
    ))
    if origin_careers == 1:
        global_config.red_careers = '雷影剑士'
    elif origin_careers == 2:
        global_config.red_careers = '青'
    elif origin_careers == 3:
        global_config.red_careers = '神射手'
    elif origin_careers == 4:
        global_config.red_careers = '冰魔导师'
    else:
        print("Please enter a valid number!\n")
        select_red_careers()


if __name__ == '__main__':
    import onnxruntime as ort

    global_config.automation_tool = automation_tool
    global_config.replay = keyboard_playback.recorder

    num_int = int(input(
        "Choose the dungeon to run:\n1. Tina(Broken)\n2. Kalamania\n3. Shadow Fortress(Broken)\n4. Goblin Nest(Broken)\n5. Dragon Scar(Broken)\n6. Giant Tower Ruins(Broken)\n7. Kalamania M6\n"
    ))

    if num_int == 1:
        global_config.script_json = global_config.get_image_path('resource/json/蒂娜.json')
        global_config.fb_time_out_sec = 300
    elif num_int == 2:
        global_config.script_json = global_config.get_image_path('resource/json/卡尼曼部落.json')
        global_config.fb_time_out_sec = 320
    elif num_int == 3:
        global_config.script_json = global_config.get_image_path('resource/json/暗影堡垒.json')
        select_target_careers()
        if global_config.target_careers:
            select_red_careers()
        global_config.fb_time_out_sec = 500
    elif num_int == 4:
        global_config.script_json = global_config.get_image_path('resource/json/哥布林巢穴.json')
        global_config.fb_time_out_sec = 360
    elif num_int == 5:
        global_config.script_json = global_config.get_image_path('resource/json/巨龙抓痕.json')
        global_config.fb_time_out_sec = 600
    elif num_int == 6:
        global_config.script_json = global_config.get_image_path('resource/json/巨塔遗迹.json')
        global_config.fb_time_out_sec = 540
    elif num_int == 7:
        global_config.script_json = global_config.get_image_path('resource/json/kalamaniam6.json')
        global_config.fb_time_out_sec = 360
        global_config.is_n6 = True
        global_config.img_info_arr[1].click_func = n6_click

    automation_tool.find_game_window()
    automation_tool.bring_window_to_front()
    automation_tool.start_monitoring(global_config.img_info_arr, global_config.ocr_info_arr.values())

    Thread(target=global_error_check, daemon=True).start()
    Thread(target=pre_operation_check, daemon=True).start()

    while True:
        time.sleep(200)
