import traceback
from datetime import datetime



def print_log(str):
    if isinstance(str, Exception):
        traceback.print_exc()

        # 也可以将堆栈信息捕获为字符串（便于日志记录）
        str = traceback.format_exc()
    print(f"{datetime.now()}:{str}")

# if __name__ == '__main__':
#     ocr = RapidOCR()
#     result = ocr("C:\\Users\\233715\\Desktop\\收藏夹新协议\\123.png")
#     print(result)