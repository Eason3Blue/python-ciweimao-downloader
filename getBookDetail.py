import requests
import decrypt
import identityImage
import json,time
import BuiltIn
import getSession
from dataclasses import dataclass,field
from bs4 import BeautifulSoup

def getContent(book : BuiltIn.ClassBook):
    
    url = "https://www.ciweimao.com/chapter/get_chapter_list_in_chapter_detail"
    
    headers = BuiltIn.defaultHeaders.copy()
    headers.update({
        "Referer": url})
    
    data = {
        "book_id": book.id,
        "chapter_id": "0",
        "orderby": "0"
    }
    
    response = requests.post(url,headers=headers,data=data)

    soup = BeautifulSoup(response.text, "html.parser")
    
    for li in soup.select("ul.book-chapter-list li"):
        a_tag = li.find("a", href=True)
        if not a_tag:
            continue

        url = a_tag["href"] # type: ignore
        # 提取章节文本，排除 <i> 图标标签
        title = ''.join([str(x) for x in a_tag.contents if not getattr(x, 'name', None)]) # type: ignore
        is_locked = a_tag.find("i", class_="icon-lock") is not None # type: ignore
        if is_locked : isFree = False 
        else: isFree = True
        book.content.append(BuiltIn.ClassChapter(name=title,url=url,isFree=isFree)) # type: ignore
    return

def getName(book : BuiltIn.ClassBook):
    session = BuiltIn.session
    
    headers = BuiltIn.defaultHeaders.copy()
    headers["Referer"] = book.url
    
    response = session.get(book.url,headers=headers)
    if(response.status_code != 200):
        book.status = False
        return
    soup = BeautifulSoup(response.text, "html.parser")
    
    title = soup.find("meta", property="og:novel:book_name")["content"] # type: ignore
    author = soup.find("meta", property="og:novel:author")["content"] # type: ignore
    coverUrl = soup.find("meta", property="og:image")["content"]   # type: ignore
    book.name = title # type: ignore
    book.author = author   # type: ignore
    book.cover= requests.get(coverUrl).content # type: ignore
    return

def getPaidChapter(chapter : BuiltIn.ClassChapter, book : BuiltIn.ClassBook):
    #取得图片id
    session = BuiltIn.session
    
    chapter.access.url = "https://www.ciweimao.com/chapter/ajax_get_image_session_code"
    
    headers = BuiltIn.defaultHeaders.copy()
    headers["Referer"] = chapter.url
    chapter.access.data = {}
    
    chapter.access.resp = session.post(
        url = chapter.access.url,
        headers = headers
    )
    chapter.access.json = json.loads(chapter.access.resp.text)
    decrypt.decryptImgId(chapter.access)

    #取得图片
    chapter.content.url = "https://www.ciweimao.com/chapter/book_chapter_image"
    chapter.content.data = {
        "chapter_id": chapter.id,
        "area_width": 1080,
        "font": "undefined",
        "font_size": 48,
        "image_code": chapter.access.imgId,
        "bg_color_name": "white",
        "text_color_name": "white"
    }
    
    chapter.content.resp = session.get(
        url = chapter.content.url,
        headers = headers,
        params = chapter.content.data)
    chapter.content.img = chapter.content.resp.content
    
    print("章节内容下载完成，正在OCR识别中...")
    
    #转存图片
    from pathlib import Path
    imgDir = f"{book.path}/img"
    imgDirPath = Path(imgDir)
    imgDirPath.mkdir(parents=True, exist_ok=True)
    chapter.content.imgDir = imgDir
    imgPath = f"{book.path}/img/{chapter.countId}.jpg"
    
    with open(Path(imgPath),"wb") as f:
        f.write(chapter.content.img)
    
    chapter.content.imgPath = imgPath
    identityImage.process_image_bytes_to_chapter(chapter, book)
    
    print("正在检测是否有附加图片中...")
    imgsUrl = "https://www.ciweimao.com/chapter/chapter_image_tsukkomi_list"
    imgsData = {
        "chapter_id": chapter.id,
        "area_width": 871,
        "font_size":48
    }
    chapter.content.imgsJson = json.loads(session.post(url = imgsUrl, headers = headers, data = imgsData).text)
    paths = []
    def find_paths(obj):
        if isinstance(obj, dict):
            if 'path' in obj:
                paths.append(obj['path'])
            for value in obj.values():
                find_paths(value)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                find_paths(item)
    find_paths(chapter.content.imgsJson["imageInfoMaps"]) # type: ignore
    for url in paths:
        chapter.content.imgs.append(url)
    return

def getChapter(chapter : BuiltIn.ClassChapter):
    #获得AccessKey
    session = BuiltIn.session
    
    headers = BuiltIn.defaultHeaders.copy()
    headers["Referer"] = chapter.url

    chapter.access.data = {
        "chapter_id": chapter.id
    }
    
    chapter.access.key = json.loads(session.post(
        url=chapter.access.url,
        data=chapter.access.data,
        headers=headers).text).get("chapter_access_key")

    #获得章节内容
    chapter.content.data = chapter.access.data.copy()
    chapter.content.data["chapter_access_key"] = chapter.access.key
    chapter.content.json = json.loads(session.post(
        url=chapter.content.url,
        data=chapter.content.data,
        headers=headers).text)
    chapter.content.status = chapter.content.json["code"] # type: ignore
    
    if(chapter.content.status == 400001):
        print(chapter.content.json["tip"]) # type: ignore
        chapter.content.raw = chapter.content.json["tip"] # type: ignore
        return
    chapter.content.raw = pureChapter(decrypt.decryptFree(
        chapter.content.json["chapter_content"], # type: ignore
        chapter.content.json["encryt_keys"], # type: ignore
        chapter.access.key))
    return

def pureChapter(text):
    soup = BeautifulSoup(text, "html.parser")
    for span in soup.find_all("span"):
        span.decompose()  # 彻底删除标签和内容
    return soup.prettify()
