import win32gui
import win32con
import win32api
import time
from operator import methodcaller, itemgetter


# def window_enumeration_handler(hwnd, top_windows):
#     top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
#
#
# def enum_windows():
#     windows = []
#     win32gui.EnumWindows(window_enumeration_handler, windows)
#     return windows
#
#
# def find_window(caption):
#     hwnd = win32gui.FindWindow(None, caption)
#     if hwnd == 0:
#         windows = enum_windows()
#         for handle, title in windows:
#             if caption in title:
#                 hwnd = handle
#                 break
#     return hwnd

# My version of find_window
def getWindowList():
    def callback(hwnd, hwnd_list: list):
        title = win32gui.GetWindowText(hwnd)
        if win32gui.IsWindowEnabled() and win32gui.IsWindowVisible() and title:
            hwnd_list.append((title, hwnd))
        return True
    windows_list = []
    # EnumWindows() works like map(), iterating the windows by applying callback
    win32gui.EnumWindows(callback, windows_list)
    return windows_list

def find_window(title):
    try:
        hwnd = win32gui.FindWindow(None, title)

        if hwnd == 0:
            win_list = getWindowList()
            # try to find handle of the window whose name contains title
            mapped_hwnd = map(itemgetter(1), filter(lambda x: title in x[0], win_list) )
            for handle in mapped_hwnd:
                hwnd = handle
                break

        return hwnd

    except:
        print("Exception occured while getting hwnd")
        exit(1)


def enter_keys(hwnd, data):
    win32api.SendMessage(hwnd, win32con.EM_SETSEL, 0, -1)
    win32api.SendMessage(hwnd, win32con.EM_REPLACESEL, 0, data)
    win32api.Sleep(300)


def click_button(btn_hwnd):
    win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
    win32api.Sleep(100)
    win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONUP, 0, 0)
    win32api.Sleep(300)


def config_reader(file_name):
    with open(file_name, "r", encoding='utf-8') as fd:
        # strip lines
        lines = map(methodcaller("strip"), fd.readlines())
        # filtering lines starting with '#' or blank lines
        lines_filtered = filter(lambda l: l and not l.startswith("#"), lines)
        # parsing
        lines_dict_iter = map(methodcaller("split", ";"), lines_filtered)
        # converting list to dict
        options = dict(lines_dict_iter)
    return options


if __name__ == "__main__":
    caption = "Open API Login"
    hwnd = find_window(caption)

    edit_id = win32gui.GetDlgItem(hwnd, 0x3E8)
    edit_pass = win32gui.GetDlgItem(hwnd, 0x3E9)
    edit_cert = win32gui.GetDlgItem(hwnd, 0x3EA)
    btn_login = win32gui.GetDlgItem(hwnd, 0x1)

    options = config_reader("../config")
    id = options['id']
    password = options['password']
    cert = options['cert']

    enter_keys(edit_id, id)
    enter_keys(edit_pass, password)
    enter_keys(edit_cert, cert)
    click_button(btn_login)