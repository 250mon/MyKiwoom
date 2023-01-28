# Kiwoom software needs to be upgraded daily or weekly
# for version handling

# This file takes care of the whole process of version upgrade
# from login to upgrade
# It needs to be run daily or weekly

# Because auto login is enabled, 'connect' command gets a connection to
# Kiwoom server silently except the following VersionUpgrade

import os
import os.path
import win32gui
import win32con
import win32api
import time
import multiprocessing as mp
from operator import methodcaller, itemgetter
from login_window import LoginWindow


LOGIN_FILE = "C:/OpenAPI/system/Autologin.dat"
LOGIN_FILE_TMP = "C:/OpenAPI/system/Autologin.tmp"

class VersionUpgrade():

    def __init__(self, config_path):
        self.queue = mp.Manager().Queue()
        # getting id, passwd, cert
        self.id = None
        self.pw = None
        self.cert = None
        self._get_idpw(config_path)

        # start login window subprocess
        self.login_window = None

    # tool for get_idpw
    def _config_reader(self, file_name):
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

    # get idpwd from config file
    def _get_idpw(self, config_path):
        options = self._config_reader(config_path)
        self.id = options['id']
        self.pw = options['password']
        # if cert is not given, it runs in simulation mode
        self.cert = options.get('cert', None)

    # start login window process
    def start_login_window(self):
        self.login_window = mp.Process(target=LoginWindow, name="Login Window Process", args= (self.queue,), daemon=True)
        self.login_window.start()

    #################################
    # auto login on and off
    #################################
    def turn_off_autologin(self):
        if os.path.isfile(LOGIN_FILE):
            os.rename(LOGIN_FILE, LOGIN_FILE_TMP)

    def turn_on_autologin(self):
        if os.path.isfile(LOGIN_FILE_TMP):
            os.rename(LOGIN_FILE_TMP, LOGIN_FILE)

    #################################
    # functions for manual login
    #################################
    # JY added
    def _getWindowList(self):
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
    def find_window(self, title):
        try:
            hwnd = win32gui.FindWindow(None, title)

            if hwnd == 0:
                win_list = self._getWindowList()
                # try to find handle of the window whose name contains title
                mapped_hwnd = map(itemgetter(1), filter(lambda x: title in x[0], win_list))
                for handle in mapped_hwnd:
                    hwnd = handle
                    break

            return hwnd

        except:
            print("Exception occured while getting hwnd")
            exit(1)

    def enter_keys(self, hwnd, data):
        win32api.SendMessage(hwnd, win32con.EM_SETSEL, 0, -1)
        win32api.SendMessage(hwnd, win32con.EM_REPLACESEL, 0, data)
        win32api.Sleep(300)

    def click_button(self, btn_hwnd):
        win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
        win32api.Sleep(100)
        win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONUP, 0, 0)
        win32api.Sleep(300)

    def left_click(self, x, y, hwnd):
        lParam = win32api.MAKELONG(x, y)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

    def double_click(self, x, y, hwnd):
        self.left_click(x, y, hwnd)
        self.left_click(x, y, hwnd)
        win32api.Sleep(300)


    def close_window(self, title, secs=5):
        hwnd = self.find_window(title)
        if hwnd != 0:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            print("{} secs sleep ...".format(secs))
            time.sleep(secs)

    def wait_secs(self, msg, secs=10):
        while secs > 0:
            time.sleep(1)
            print(f"{msg} waiting: {secs}")
            secs = secs - 1

    def manual_login(self):
        print("수동 로그인 함수 호출")

        while True:
            caption = "OPEN API Login"
            hwnd = self.find_window(caption)

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
        if self.cert is None:
            if win32gui.IsWindowEnabled(win32gui.GetDlgItem(hwnd, 0x3EA)):
                self.click_button(win32gui.GetDlgItem(hwnd, 0x3ED))
        else:
            if not win32gui.IsWindowEnabled(win32gui.GetDlgItem(hwnd, 0x3EA)):
                self.click_button(win32gui.GetDlgItem(hwnd, 0x3ED))


        self.double_click(15, 15, edit_id)
        self.enter_keys(edit_id, self.id)
        time.sleep(0.5)

        self.double_click(15, 15, edit_pass)
        self.enter_keys(edit_pass, self.pw)
        time.sleep(0.5)

        if self.cert is not None:
            self.double_click(15, 15, edit_cert)
            self.enter_keys(edit_cert, self.cert)
            time.sleep(0.5)

        self.click_button(btn_login)

    def check_version_upgrade(self):
        secs_cnt = 0
        while True:
            time.sleep(1)
            remain_secs = 120 - secs_cnt
            print(f"로그인 대기: {remain_secs}")

            # 버전처리 경고창 확인
            hwnd = self.find_window("opstarter")
            if hwnd != 0:
                try:
                    static_hwnd = win32gui.GetDlgItem(hwnd, 0xFFFF)
                    text = win32gui.GetWindowText(static_hwnd)
                    if '버전처리' in text:
                        while self.login_window.is_alive():
                            self.login_window.kill()
                            time.sleep(1)

                        self.click_button(win32gui.GetDlgItem(hwnd, 0x2))
                        secs_cnt = 90      # 버전처리이면 30초 후 종료
                except:
                    pass

            # 업그레이드 확인창
            hwnd = self.find_window("업그레이드 확인")
            if hwnd != 0:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

            # 버전처리가 있는 경우의 종료
            if secs_cnt > 120:
                break

            # 버전처리가 없는 경우의 종료
            if not self.queue.empty():
                data = self.queue.get()
                break

            secs_cnt += 1

        print("버전처리 완료")



if __name__ == "__main__":

    user = VersionUpgrade("../config")
    # 자동 로그인 오프
    user.turn_off_autologin()
    # open up the login window
    user.start_login_window()
    # manual login
    user.manual_login()
    # check version and upgrade
    user.check_version_upgrade()
    # 자동 로그인 온
    user.turn_on_autologin()