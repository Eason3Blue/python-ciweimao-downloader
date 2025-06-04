from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def getLogin():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.ciweimao.com/signup/login")
    input("请登录后按回车")
    return driver.get_cookies()


import time
if __name__ == "__main__":
    loginData = getLogin()
    for cookie in loginData:
        if cookie['name'] == 'login_token':
            login_token = cookie['value']
        if cookie['name'] == 'reader_id':
            reader_id = cookie['value']
        if cookie['name'] == 'user_id':
            user_id = cookie['value']
        if cookie['name'] == 'ci_session':
            ci_session = cookie['value']
    print("Debug: ",login_token,"\n",reader_id,"\n",user_id,"\n")
    # 在 Python 中打开文件并使用 utf-8 编码
    data = data = login_token + "\n" + reader_id + "\n" + user_id + "\n" + str(int(time.time() + 7200)) + "\n" + ci_session

    with open("cached.passport", "w", encoding="utf-8") as f:
        f.write(data)
