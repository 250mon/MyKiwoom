from pywinauto import application


app = application.Application()
app.start("Notepad.exe")
app.UntitledNotepad.draw_outline()
app.UntitledNotepad.menu_select("편집 -> 바꾸기...")
app.바꾸기.취소.click()
app.UntitiledNotepad.Edit.type_keys("hello %s" % str(dir()), with_spaces=True)
#app.UntitledNotepad.menu_select("파일 -> 끝내기")
#app['메모장']['저장 안 함'].click()
#app.메모장.Button2.click()