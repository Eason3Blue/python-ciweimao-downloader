from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def getLogin():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.ciweimao.com/signup/login")
    input("请登录后按回车")
    cookies = driver.get_cookies()
    driver.quit()
    
    for cookie in cookies:
        if cookie['name'] == 'ci_session':
            accountSession = cookie['value']
        elif cookie['name'] == 'login_token':
            accountLoginToken = cookie['value']
        elif cookie['name'] == 'user_id':
            accountUserID = cookie['value']
        elif cookie['name'] == 'reader_id':
                accountReaderID = cookie['value']
    cookies = {
        "ci_session" : accountSession,
        "login_token": accountLoginToken,
        "user_id"    : accountUserID,
        "reader_id"  : accountReaderID,
        "expireTime" : str(time.time() + 7200)
    }
    return cookies
