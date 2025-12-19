import time
from threading import Thread

import keyboard_playback
import global_config
from call_back_func import global_error_check,pre_operation_check,n6_click
from image_recognition import automation_tool


def select_target_careers():
    target_careers =input(
        "是否为给TN职业刷武器，请输入数字(不填默认否)：1.森语者 2.灵魂乐手 3.神盾骑士 4.巨刃守护者\r\n")
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
    origin_careers = int(input("选择一个你拥有的红职，请输入数字：1.雷影剑士 2.青岚骑士 3.神射手 4.冰魔导师\r\n"))
    if origin_careers == 1:
        global_config.red_careers = '雷影剑士'
    elif origin_careers == 2:
        global_config.red_careers = '青'
    elif origin_careers == 3:
        global_config.red_careers = '神射手'
    elif origin_careers == 4:
        global_config.red_careers = '冰魔导师'
    else:
        print("请输入对应数字！\r\n")
        select_red_careers()

if __name__ == '__main__':

    import onnxruntime as ort
    # 查看可用的执行 providers
    # print(ort.get_available_providers())
    global_config.automation_tool = automation_tool
    global_config.replay = keyboard_playback.recorder

    num_int = int(input("请输入数字: 1.蒂娜 2.卡尼曼 3.暗影堡垒 4.哥布林巢穴 5.巨龙抓痕 6.巨塔遗迹 7.n6卡尼曼\r\n"))
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
        global_config.script_json = global_config.get_image_path('resource/json/n6卡尼曼部落.json')
        global_config.fb_time_out_sec = 360
        global_config.is_n6 = True
        global_config.img_info_arr[1].click_func = n6_click

    # 可选：滚动后等待一段时间


    automation_tool.find_game_window()
    automation_tool.bring_window_to_front()
    automation_tool.start_monitoring(global_config.img_info_arr,global_config.ocr_info_arr.values())

    Thread(target=global_error_check, daemon=True).start()
    Thread(target=pre_operation_check, daemon=True).start()
    while True:
        time.sleep(200)
