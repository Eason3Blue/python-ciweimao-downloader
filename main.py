import getLogin
import autoDownloadChrome
import makeEpub
import BuiltIn
import makeRequest
import requests
import random
import getBookDetail
from pathlib import Path
import json, time

expireTime = 2147483647

if __name__ == "__main__":
    chromePath = Path("./chrome\\chrome.exe")
    chromeDriverPath = Path('./chromedriver\\chromedriver.exe')
    if chromePath.exists() == False or chromeDriverPath.exists() == False :
        print("未下载chrome，正在下载中...")
        autoDownloadChrome.main()
    
    #读取Cookies缓存
    path = Path('./accountCookies.json')
    try:
        with open(path, "r", encoding='utf-8') as f:
            cacheReadResponse = f.read()
        BuiltIn.accountCookies = json.loads(cacheReadResponse)
        expireTime     = float(BuiltIn.accountCookies["expireTime"])
    except:
        print("未检测到缓存，正在登录...")
        getLogin.getLogin()
    
    if(time.time() >= expireTime): #若token超时
        print("登录信息超时，正在重新登录...")
        getLogin.getLogin()
    
    with open(path, "w", encoding='utf-8') as f: #写入缓存
        f.write(json.dumps(BuiltIn.accountCookies))
    
    BuiltIn.session.cookies = requests.utils.cookiejar_from_dict(BuiltIn.accountCookies)
    makeRequest.getSession(BuiltIn.session)
    
    with open(path, "w", encoding='utf-8') as f: #写入缓存
        f.write(json.dumps(BuiltIn.accountCookies))
    
    #告知用户
    print("")
    print(f"login_token = {BuiltIn.accountCookies['login_token']}\n",
          f"user_id     = {BuiltIn.accountCookies['user_id']}\n",
          f"reader_id   = {BuiltIn.accountCookies['reader_id']}")
    
    #读取设备缓存
    path = Path('./deviceInfo.json')
    try:
        with open(path, "r", encoding='utf-8') as f:
            cacheReadResponse = f.read()
            responJson = json.loads(cacheReadResponse)
            BuiltIn.deviceInfo = responJson
    except:
        print(f"文件不存在：{path}")
        #没有缓存
        while(True):
            print("现在输入你的设备信息")
            needCache = height = weight = point = "wdf"
            
            height = int(input("     长："))
            weight = int(input("     宽："))
            point = int(input("     字号："))
            needCache = str(input("     是否要保存以上信息（y/其他）："))
            
            if (isinstance(height,int) and isinstance(weight,int) and isinstance(point,int) and isinstance(needCache,str)):
                break
            else:
                print("输入无效")
        
        BuiltIn.deviceInfo['height'] = height
        BuiltIn.deviceInfo['weight'] = weight
        BuiltIn.deviceInfo['point'] = point
        if(needCache == 'y'):
            path = Path('./deviceInfo.json')
            with open(path, "w", encoding='utf-8') as f:
                f.write(json.dumps(BuiltIn.deviceInfo))
                    
    #告知用户
    print("")
    print(f"长  = {BuiltIn.deviceInfo['height']}\n",
          f"宽  = {BuiltIn.deviceInfo['weight']}\n",
          f"字号 = {BuiltIn.deviceInfo['point']}")
    
    
    while(True): #下载流程
        #获得书本信息
        book = BuiltIn.ClassBook()
        book.url = input("输入小说链接(https://example.com): ")
        book.id = int(book.url.split("/")[-1])
        print("book_id: " + str(book.id))
        if(book.id < 1e8):
            print("输入错误，请重新输入")
            continue  
        getBookDetail.getName(book)
        if(book.status == False):
            print("书籍不存在或未通过审核，或者刺猬猫服务器宕机（有时真的会发生）")
            continue
        print(f"bookName: {book.name}")
        book.path = f"./book/{str(book.id)}"
        Path(book.path).mkdir(parents=True, exist_ok=True)
        Path(f"{book.path}/img").mkdir(parents=True, exist_ok=True)
        Path(f"{book.path}/img/sliced").mkdir(parents=True, exist_ok=True)
        Path(f"{book.path}/epub").mkdir(parents=True, exist_ok=True)
        
        #放置书本封面
        with open(Path(book.path) / "cover.jpg", "wb") as f:
            f.write(book.cover)
        
        #获得书本目录
        getBookDetail.getContent(book)
        
        #开始下载章节
        count = 1
        for chapter in book.content:
            #定义单章节
            chapter.id = chapter.url.split("/")[-1]
            chapter.countId = count
            path = Path(Path(book.path) / f"{str(count)} {chapter.name}.html")
            
            if not path.exists():
                print(f"进行第{count}章下载，标题:{chapter.name}")
                #伪装
                headers = BuiltIn.defaultHeaders.copy()
                headers["Referer"] = chapter.url
                BuiltIn.session.get(url=chapter.url,headers=headers)
                
                if chapter.isFree == True:
                    getBookDetail.getChapter(chapter)
                else:
                    t = random.random()
                    print(f"睡眠{t}秒")
                    time.sleep(random.random())
                    getBookDetail.getPaidChapter(chapter,book,BuiltIn.deviceInfo)
                print("下载完成")
                
                with open(path, "w", encoding="utf-8") as f:
                    f.write(chapter.content.raw)
            else: #读取已下载章节
                print(f"第{count}章已经下载，跳过")
                with open(path, "r", encoding="utf-8") as f:
                    chapter.content.raw = f.read()
            chapter.raw = chapter.content.raw
            book.chapters.append(chapter)
            count += 1
        with open(path, "w", encoding='utf-8') as f: #写入缓存
            f.write(json.dumps(BuiltIn.accountCookies))
        makeEpub.generate_epub(book, f"{book.path}/epub/{book.name}.epub")
        print("合并完成")
        input("回车进入下一轮下载..")
