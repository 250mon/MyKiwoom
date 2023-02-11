import os.path
import subprocess
from kiwoom_version.util import *

CUR_PATH = os.getcwd()


def manual_login(user_id, user_pw):
    print("수동 로그인 함수 호출")
    hwnd = find_window("Open API Login")
    edit_id = win32gui.GetDlgItem(hwnd, 0x3E8)
    edit_pass = win32gui.GetDlgItem(hwnd, 0x3E9)
    button = win32gui.GetDlgItem(hwnd, 0x1)

    enter_keys(edit_id, user_id)
    enter_keys(edit_pass, user_pw)
    click_button(button)


def check_version():
    try:
        hwnd = find_window("opstarter")
        if hwnd != 0:
            static_hwnd = win32gui.GetDlgItem(hwnd, 0xFFFF)
            text = win32gui.GetWindowText(static_hwnd)
            if '버전처리를' in text:
                button = win32gui.GetDlgItem(hwnd, 0x2)
                click_button(button)
                click_button(button)
    except:
        pass


def check_upgrade():
    try:
        hwnd = find_window("업그레이드 확인")
        if hwnd != 0:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    except:
        pass


if __name__ == "__main__":
    f = open("user.txt")
    lines = f.readlines()
    user_id = lines[0].strip()
    user_pw = lines[1].strip()
    f.close()

    # 자동 로그인 파일 삭제 
    login_info = "C:/OpenAPI/system/Autologin.dat"
    if os.path.isfile(login_info):
        os.remove("C:/OpenAPI/system/Autologin.dat")

    # To bypass UAC
    os.environ.update({"__COMPAT_LAYER": "RUnAsInvoker"})

    # 버전처리
    proc = subprocess.Popen(f"{CUR_PATH}/login/KiwoomAPI.exe", shell=True)
    wait_secs("버전처리", 10)

    # 수동 로그인 
    manual_login(user_id, user_pw)
    wait_secs("로그인", 90)

    # 프로그램 종료
    proc.kill()
    close_window("Kiwoom Login", secs=10)

    # check version
    check_version()
    wait_secs("버전처리", 20)

    # check upgrade 
    check_upgrade()
    wait_secs("업그레이드", 10)
