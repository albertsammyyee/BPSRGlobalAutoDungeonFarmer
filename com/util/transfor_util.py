import json


def get_format_operation(filename):
    result_arr = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            # 找到最后一个"-"的位置
            last_dash = line.rfind("-")
            # 找到第一个"("的位置
            first_paren = line.find("(")

            # 提取中间的内容并去除前后空格
            result = line[last_dash + 1:first_paren].strip()
            name = result.split("：")[0].strip()
            target = result.split("：")[1].replace("毫秒","").strip()
            if name=="释放键":
                name = "key_release"
            if name=="按下键":
                name = "key_press"
            if name == "等待":
                target = int(target)/1000
            result_arr.append((name,target))
    return result_arr
def transfer_to_mine(result_arr):
    time = 0
    result = []
    for operation in result_arr:
        name = operation[0]
        target = operation[1]
        if name=="key_release" or name=="key_press":
            if target == "space" or target=="shift":
                target = "Key."+target
            result.append({
                "type": name,
                "key": target,
                "time": time
            })
        else:
            time = time+target
    with open("../哥布林巢穴.json", 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
    return result


if __name__ == '__main__':
    transfer_to_mine(get_format_operation("a.txt"))