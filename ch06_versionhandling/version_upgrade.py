import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import pythoncom
import win32gui
import win32con
import win32api
import time
import multiprocessing as mp
from operator import methodcaller, itemgetter


#################################
# auto login on and off
#################################

LOGIN_FILE = "C:/OpenAPI/system/Autologin.dat"
LOGIN_FILE_TMP = "C:/OpenAPI/system/Autologin.tmp"

def turn_off_autologin():
    if os.path.isfile(LOGIN_FILE):
        os.rename(LOGIN_FILE, LOGIN_FILE_TMP)

def turn_on_autologin():
    if os.path.isfile(LOGIN_FILE_TMP):
        os.rename(LOGIN_FILE_TMP, LOGIN_FILE)


#################################
# manual login functions
#################################

# JY added
def _getWindowList():
    def callback(hwnd, hwnd_list: list):
        title = win32gui.GetWindowText(hwnd)
        # if win32gui.IsWindowEnabled() and win32gui.IsWindowVisible() and title:
        #     hwnd_list.append((title, hwnd))
        hwnd_list.append((title, hwnd))
        return True
    windows_list = []
    # EnumWindows() works like map(), iterating the windows by applying callback
    win32gui.EnumWindows(callback, windows_list)
    return windows_list

# JY edited
def find_window(title):
    try:
        hwnd = win32gui.FindWindow(None, title)

        if hwnd == 0:
            win_list = _getWindowList()
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


def left_click(x, y, hwnd):
    lParam = win32api.MAKELONG(x, y)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)


def double_click(x, y, hwnd):
    left_click(x, y, hwnd)
    left_click(x, y, hwnd)
    win32api.Sleep(300)


# JY added
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


#################################
# login window
#################################

class MyWindow(QMainWindow):
    app = QApplication(sys.argv)

    def __init__(self, q):
        super().__init__()
        self.login_status = False
        self.q = q
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.slot_login)
        self.login()


    def login(self):
        self.ocx.dynamicCall("commConnect()")
        while not self.login_status:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.0001)


    def slot_login(self, err_code):
        self.login_status = True
        print("login is complete")
        self.q.put('a')


def version(user_id, user_pw, user_cert=None):
    q = mp.Queue()

    turn_off_autologin()

    sub_proc = mp.Process(target=MyWindow, name="Sub Process", args= (q,), daemon=True)
    sub_proc.start()

    # manual login
    while True:
        caption = "OPEN API Login"
        hwnd = find_window(caption)

        if hwnd == 0:
            print("Waiting for login window...")
            time.sleep(1)
            continue
        else:
            break

    time.sleep(2)
    edit_id   = win32gui.GetDlgItem(hwnd, 0x3E8)
    edit_pass = win32gui.GetDlgItem(hwnd, 0x3E9)
    edit_cert = win32gui.GetDlgItem(hwnd, 0x3EA)
    btn_login = win32gui.GetDlgItem(hwnd, 0x1)

    # if there is no cert, click on the check box '모의투자접속'
    if user_cert is None:
        if win32gui.IsWindowEnabled(win32gui.GetDlgItem(hwnd, 0x3EA)):
            click_button(win32gui.GetDlgItem(hwnd, 0x3ED))
    else:
        if not win32gui.IsWindowEnabled(win32gui.GetDlgItem(hwnd, 0x3EA)):
            click_button(win32gui.GetDlgItem(hwnd, 0x3ED))

    double_click(15, 15, edit_id)
    enter_keys(edit_id, user_id)
    time.sleep(0.5)

    double_click(15, 15, edit_pass)
    enter_keys(edit_pass, user_pw)
    time.sleep(0.5)

    if user_cert is not None:
        double_click(15, 15, edit_cert)
        enter_keys(edit_cert, user_cert)
        time.sleep(0.5)

    click_button(btn_login)

    # check version and upgrade
    secs_cnt = 0
    while True:
        time.sleep(1)
        remain_secs = 120 - secs_cnt
        print(f"로그인 대기: {remain_secs}")

        # 버전처리 경고창 확인
        hwnd = find_window("opstarter")
        if hwnd != 0:
            try:
                static_hwnd = win32gui.GetDlgItem(hwnd, 0xFFFF)
                text = win32gui.GetWindowText(static_hwnd)
                if '버전처리' in text:
                    while sub_proc.is_alive():
                        sub_proc.kill()
                        time.sleep(1)

                    click_button(win32gui.GetDlgItem(hwnd, 0x2))
                    secs_cnt = 90      # 버전처리이면 30초 후 종료
            except:
                pass

        # 업그레이드 확인창
        hwnd = find_window("업그레이드 확인")
        if hwnd != 0:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

        # 버전처리가 있는 경우의 종료
        if secs_cnt > 120:
            break

        # 버전처리가 없는 경우의 종료
        if not q.empty():
            data = q.get()
            break

        secs_cnt += 1

    print("버전처리 완료")

    # 자동 로그인 재설정
    turn_on_autologin()


if __name__ == "__main__":
    options = config_reader("../config")
    id = options['id']
    password = options['password']
    cert = options['cert']

    version(id, password, cert)