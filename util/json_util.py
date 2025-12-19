import json


def edit_json_file(file_path):
    """
    读取JSON文件，应用修改，然后写回文件

    参数:
        file_path (str): JSON文件路径
        updates (dict): 要更新的键值对字典
    """
    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 应用修改
        data = edit_json(data)

        file_path = file_path.replace(".json","_replace.json")
        # 写回JSON文件，确保中文正常显示
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"成功更新JSON文件: {file_path}")
        return True

    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
    except json.JSONDecodeError:
        print(f"错误: 文件 {file_path} 不是有效的JSON格式")
    except Exception as e:
        print(f"发生错误: {str(e)}")

    return False
def edit_json(data):
    result = []
    pressed_map = {}
    for o in data:
        print(o)
        if o["type"]=="key_press":
            if o["key"] in pressed_map:
                continue
            else:
                pressed_map[o["key"]] = True
                print("插入",o)
                result.append(o)
        if o["type"] == "key_release" and o["key"] in pressed_map:
            del pressed_map[o["key"]]
            print("插入",o)
            result.append(o)
    return result

# 使用示例
if __name__ == "__main__":
    # 假设我们有一个名为data.json的文件
    file_path = "../resource/json/蒂娜.json"


    # 执行更新
    edit_json_file(file_path)
