def change_to_single(x, y, w, h):
    click_x = x + 2
    click_y = y + h // 2
    return click_x, click_y


def gotoFb(x, y, w, h):
    click_x = x + 1.5 * w
    click_y = y + h // 2
    return click_x, click_y

def qilai(x, y, w, h):
    return 1691, 950



def p(x, y, w, h):
    click_x = x + w - 20
    click_y = y + h // 2
    return click_x, click_y


def no_click(x, y, w, h):
    return 0, 0

