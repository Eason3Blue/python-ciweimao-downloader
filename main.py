import getLogin
import makeEpub
import getBookDetail
from pathlib import Path
import json, time
from dataclasses import dataclass, field

@dataclass
class ClassBook:
    url: str = field(default_factory=str)
    id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    author: str = field(default_factory=str)
    content: list = field(default_factory=list)
    cover: bytes = field(default_factory=bytes)
    status: bool = False
@dataclass
class ClassAccess:
    url: str = "https://www.ciweimao.com/chapter/ajax_get_session_code"
    data: dict = field(default_factory=dict)
    resp: object = field(default_factory=object)
    json: object = field(default_factory=object)
    key: str = field(default_factory=str)
@dataclass
class ClassContent:
    url: str = "https://www.ciweimao.com/chapter/get_book_chapter_detail_info"
    data: dict = field(default_factory=dict)
    resp: object = field(default_factory=object)
    json: object = field(default_factory=object)
    keys: dict = field(default_factory=dict)
    raw: str = field(default_factory=str)
    status: bool = False
@dataclass
class ClassChapter:
    id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    url: str = field(default_factory=str)
    accessKey: ClassAccess = field(default_factory=ClassAccess)
    content: ClassContent = field(default_factory=ClassContent)

expireTime = 0

if __name__ == "__main__":
    #读取缓存
    path = Path('./accountCookies.json')
    if not path.exists():
        print(f"文件不存在：{path}")
        cacheReadResponse = False
    else:
        with open(path, "r", encoding='utf-8') as f:
            cacheReadResponse = f.read()
    if(cacheReadResponse != False):
        accountCookies = json.loads(cacheReadResponse)
        expireTime     = float(accountCookies["expireTime"])
    if(cacheReadResponse == False):
        print("未检测到缓存，正在登录...")
        accountCookies = getLogin.getLogin()
    elif(time.time() >= expireTime):
        print("Session超时，正在重新登录...")
        accountCookies = getLogin.getLogin()
    with open(path, "w", encoding='utf-8') as f:
        f.write(json.dumps(accountCookies))
    print(f"ci_session  = {accountCookies['ci_session']} \n",
          f"login_token = {accountCookies['login_token']}\n",
          f"user_id     = {accountCookies['user_id']}\n",
          f"reader_id   = {accountCookies['reader_id']}")
    
    book = ClassBook()
    while(True):
        book.url = input("输入小说链接(https://example.com): ")
        book.id = int(book.url.split("/")[-1])
        print("book_id: " + str(book.id))
        if(book.id < 1e8):
            print("输入错误，请重新输入")
            continue  
    
        getBookDetail.getName(accountCookies,book)
        if(book == False):
            print("书籍不存在或未通过审核")
            continue
        dirPath = Path(book.name)
        dirPath.mkdir(parents=True, exist_ok=True)
        coverImg = book.cover
        with open(dirPath / "cover.jpg", "wb") as f:
            f.write(coverImg)
        
        getBookDetail.getContent(accountCookies,book)
        count = 1
        chapters = []
        for title,url in book.content:
            chapter  = ClassChapter()
            chapter.id = url.split("/")[-1]
            chapter.url = url
            path = Path(dirPath / f"{str(count)}{title}.html")
            if not path.exists():
                print(f"进行第{count}章下载，标题:{title}")
                getBookDetail.getChapter(accountCookies,chapter)
                print("下载完成")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(chapter.content.raw)
            else:
                print(f"第{count}章已经下载，跳过")
                with open(path, "r", encoding="utf-8") as f:
                    chapter.content.raw = f.read()
            chapters.append(ClassChapter(name = title,content = ClassContent(raw= chapter.content.raw)))
            count += 1
        makeEpub.create_epub(book.name, book.author, chapters, book.cover, f"./{book.name}/epub/", f"./{book.name}/epub/output")
        print("合并完成")
        input("回车进入下一轮下载..")
