from pywinauto import application


app = application.Application()
app.connect(title_re=".*메모장", class_name="Notepad")
app.UntitledNotepad.draw_outline()
app.UntitledNotepad.menu_select("편집 -> 바꾸기...")
app.바꾸기.취소.click()
app.UntitiledNotepad.Edit.type_keys("hello %s" % str(dir()), with_spaces=True)