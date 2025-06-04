import getLogin
import readFromCache
import time
import getBookDetail
from pathlib import Path

expireTime = 0
accountSession = accountLoginToken = accountUserID = accountReaderID = None

if __name__ == "__main__":
    #读取缓存
    cacheReadResponse = readFromCache.read('./accountCookies.cached')
    if(len(cacheReadResponse) > 0):
        accountCookies = eval(cacheReadResponse[0])
        expireTime     = float(cacheReadResponse[1])
    if(time.time() >= expireTime):
        print("Session超时，正在重新登录...")
        if(len(cacheReadResponse) == 0):
            print("未检测到缓存，正在登录...")
        responseCookies = getLogin.getLogin() #调用Chrome获取Cookies
        for cookie in responseCookies:
            if cookie['name'] == 'ci_session':
                accountSession = cookie['value']
            elif cookie['name'] == 'login_token':
                accountLoginToken = cookie['value']
            elif cookie['name'] == 'user_id':
                accountUserID = cookie['value']
            elif cookie['name'] == 'reader_id':
                accountReaderID = cookie['value']
        with open("accountCookies.cached", "w", encoding="utf-8") as f: #写入缓存
            accountCookies = {
                "ci_session" : accountSession,
                "login_token": accountLoginToken,
                "user_id"    :accountUserID,
                "reader_id"  : accountReaderID
            }
            f.write(str(accountCookies) + "\n" + str(time.time() + 7200))

    for key,value in accountCookies.items():
        print(key + ": " + value)
    
    while(True):
        bookURL = input("输入小说链接(https://example.com): ")
        bookID = int(bookURL.split("/")[-1])
        print("book_id: " + str(bookID))
        if(bookID < 1e8):
            print("输入错误，请重新输入")
            continue  
    
        bookAbout = getBookDetail.getName(accountCookies,bookURL)
        if(bookAbout == False):
            print("书籍不存在或未通过审核")
            continue
        bookName = bookAbout[0]
        dirPath = Path(bookName)
        dirPath.mkdir(parents=True, exist_ok=True)
        coverImg = bookAbout[1]
        with open(dirPath / "cover.jpg", "wb") as f:
            f.write(coverImg)
        
        bookContent = getBookDetail.getContent(accountCookies,bookID)
        count = 1
        for chapterTitle, chapterID in bookContent:
            print("进行第",count,"章下载，标题:",chapterTitle," ChapterID: ",chapterID)
            chapterContent = chapterTitle + "\n" + getBookDetail.getChapter(accountCookies,chapterID)
            print("下载完成")
            with open(dirPath / (str(count) + ".html"), "w", encoding="utf-8") as f:
                f.write(chapterContent)
            count += 1
