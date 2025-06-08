from bs4 import BeautifulSoup
import requests
import decrypt
import json
from dataclasses import dataclass,field

defaultHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Origin": "https://www.ciweimao.com",
    "Priority": "u=0, i"
}
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
    url: str = field(default_factory=str)
    accessKey: ClassAccess = field(default_factory=ClassAccess)
    content: ClassContent = field(default_factory=ClassContent)


def getContent(cookies,book : ClassBook):
    url = "https://www.ciweimao.com/chapter/get_chapter_list_in_chapter_detail"
    headers = defaultHeaders.copy()
    headers.update({
        "Referer": url})
    data = {
        "book_id": book.id,
        "chapter_id": "0",
        "orderby": "0"
    }
    response = requests.post(url, cookies=cookies,headers=headers,data=data)
    soup = BeautifulSoup(response.text, "html.parser")

    for a_tag in soup.find_all("a", href=True):
        # 获取链接文本和链接地址
        text = a_tag.get_text(strip=True)
        url = a_tag["href"]

        # 检查是否为有效的章节链接
        # 通过识别链接中的 URL 模式来过滤非章节链接
        if text and url.startswith("https://www.ciweimao.com/chapter/"):
            book.content.append((text, url))
    return

def getName(cookies,book : ClassBook):
    headers = defaultHeaders.copy()
    headers["Referer"] = book.url
    response = requests.get(book.url, cookies=cookies,headers=headers)
    if(response.status_code != 200):
        book.status = False
        return
    soup = BeautifulSoup(response.text, "html.parser")
    
    title = soup.find("meta", property="og:novel:book_name")["content"]
    author = soup.find("meta", property="og:novel:author")["content"]
    coverUrl = soup.find("meta", property="og:image")["content"]  
    book.name = title
    book.author = author  
    book.cover= requests.get(coverUrl).content
    return

def getChapter(cookies,chapter : ClassChapter):
    headers = defaultHeaders.copy()
    headers["Referer"] = chapter.url

    chapter.accessKey.data = {
        "chapter_id": chapter.id
    }
    chapter.accessKey.key = json.loads(requests.post(chapter.accessKey.url,data=chapter.accessKey.data,cookies=cookies,headers=headers).text).get("chapter_access_key")

    chapter.content.data = chapter.accessKey.data.copy()
    chapter.content.data["chapter_access_key"] = chapter.accessKey.key
    chapter.content.json = json.loads(requests.post(
        chapter.content.url,
        data=chapter.content.data,
        cookies=cookies,
        headers=headers).text)
    chapter.content.status = chapter.content.json["code"]
    if(chapter.content.status != 1e5):
        return chapter.content.json["tip"]
    chapter.content.raw = pureChapter(decrypt.decrypt(
        chapter.content.json["chapter_content"],
        chapter.content.json["encryt_keys"],
        chapter.accessKey.key))
    return

def pureChapter(text):
    soup = BeautifulSoup(text, "html.parser")
    for span in soup.find_all("span"):
        span.decompose()  # 彻底删除标签和内容
    return soup.prettify()
