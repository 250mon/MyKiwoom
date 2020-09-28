from pywinauto import application


app = application.Application()
app.connect(title_re="*.컨트롤", class_name="Credential Dialog Xaml Host")
app.Button1.click()