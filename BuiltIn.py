from dataclasses import dataclass,field
import requests
@dataclass
class ClassAccess:
    url: str = "https://www.ciweimao.com/chapter/ajax_get_session_code"
    data: dict = field(default_factory=dict)
    resp: object = field(default_factory=object)
    json: object = field(default_factory=object)
    key: str = field(default_factory=str)
    imgId: str = field(default_factory=str)
@dataclass
class ClassContent:
    url: str = "https://www.ciweimao.com/chapter/get_book_chapter_detail_info"
    data: dict = field(default_factory=dict)
    resp: object = field(default_factory=object)
    json: object = field(default_factory=object)
    keys: dict = field(default_factory=dict)
    raw: str = field(default_factory=str)
    img: bytes = field(default_factory=bytes)
    imgPath: str = field(default_factory=str)
    imgDir: str = field(default_factory=str)
    imgsJson: object = field(default_factory=object)
    imgs: list = field(default_factory=list)
    status: bool = True
@dataclass
class ClassChapter:
    id: int = field(default_factory=int)
    countId: int = field(default_factory=int)
    name: str = field(default_factory=str)
    url: str = field(default_factory=str)
    raw: str = field(default_factory=str)
    img: list = field(default_factory=list)
    isFree: bool = True
    isWrong: bool = False
    access: ClassAccess = field(default_factory=ClassAccess)
    content: ClassContent = field(default_factory=ClassContent)
@dataclass
class ClassBook:
    url: str = field(default_factory=str)
    id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    author: str = field(default_factory=str)
    content: list = field(default_factory=list)
    chapters: list = field(default_factory=list)
    cover: bytes = field(default_factory=bytes)
    path: str = field(default_factory=str)
    status: bool = True
    
defaultHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

accountCookies = {
    "ci_session" : "",
    "login_token": "",
    "user_id"    : "",
    "reader_id"  : "",
    "expireTime" : ""
}

deviceInfo = {
    'height' : 0,
    'weight' : 0,
    'point'  : 0,
    'needCache' : 'no' 
}

session = requests.Session()
