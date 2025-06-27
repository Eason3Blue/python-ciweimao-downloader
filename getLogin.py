from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import BuiltIn

def getLogin():
    chrome_driver_path = "chromedriver/chromedriver.exe"
    chrome_binary_path = "chrome/chrome.exe"  # 指定浏览器路径
    options = Options()
    options.add_argument("--start-maximized")

    options.binary_location = chrome_binary_path

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.ciweimao.com/signup/login")
    input("登录成功后，按回车继续...")
    
    cookies = driver.get_cookies()
    driver.quit()
    
    accountSession = accountLoginToken = accountReaderID = accountUserID = ""
    
    for cookie in cookies:
        if cookie['name'] == 'login_token':
            accountLoginToken = cookie['value']
        elif cookie['name'] == 'user_id':
            accountUserID = cookie['value']
        elif cookie['name'] == 'reader_id':
                accountReaderID = cookie['value']
        elif cookie['name'] == 'ci_session':
                accountSession = cookie['value']
    BuiltIn.accountCookies = {
        "ci_session": accountSession,
        "login_token": accountLoginToken,
        "user_id"    : accountUserID,
        "reader_id"  : accountReaderID,
        "expireTime" : str(time.time() + 604800)
    }
    return
