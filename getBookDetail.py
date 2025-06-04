from bs4 import BeautifulSoup
import requests
import decrypt
import json
import time

def getContent(session, logintoken, user_id, reader_id,book_id):
    url = "https://www.ciweimao.com/chapter/get_chapter_list_in_chapter_detail"
    cookie = {
        "ci_session": session,
        "login_token": logintoken,
        "user_id": user_id,
        "reader_id": reader_id
    }
    data = {
        "book_id": book_id,
        "chapter_id": "0",
        "orderby": "0"
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }
    response = requests.post(url, cookies=cookie,headers=headers,data=data)
    return extract_chapter_info(response.text)

def extract_chapter_info(text):
    soup = BeautifulSoup(text, 'html.parser')

    chapters = []
    for a_tag in soup.find_all('a', href=True):
        # 获取链接文本和链接地址
        text = a_tag.get_text(strip=True)
        url = a_tag['href']

        # 检查是否为有效的章节链接
        # 通过识别链接中的 URL 模式来过滤非章节链接
        if text and url.startswith("https://www.ciweimao.com/chapter/"):
            chapters.append((text, url.split("/")[-1]))

    return chapters

def getName(session, logintoken, user_id, reader_id,book_id):
    url = "https://www.ciweimao.com/book/"+str(book_id)
    cookie = {
        "ci_session": session,
        "login_token": logintoken,
        "user_id": user_id,
        "reader_id": reader_id
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }
    response = requests.post(url, cookies=cookie,headers=headers)
    return extract_name_and_cover(response.text)

def extract_name_and_cover(text):
    soup = BeautifulSoup(text, 'html.parser')

    # 提取小说标题
    title_tag = soup.find('h1', class_='title')
    title = title_tag.find(text=True, recursive=False).strip()
    
    # 提取图片URL
    img_tag = soup.find('img', {'alt': title})
    img_url = img_tag['src'] if img_tag else None

    result = ["Hello","World"]
    result[0] = title
    result[1] = requests.get(img_url).content
    return result

import readFromCache
if __name__ == "__main__":
    lines = readFromCache.read_lines_if_exists('./cached.passport')
    if(len(lines) > 0):
        login_token = lines[0]
        reader_id = lines[1]
        user_id = lines[2]
        exTimest = lines[3]
        ci_session = lines[4]
    print("Debug: ",login_token,"\n",reader_id,"\n",user_id,"\n",exTimest,"\n",ci_session)
    print(getName(ci_session,login_token,user_id,reader_id,"100434343"))
    

def getChapter(session, logintoken, user_id, reader_id,chapter_id):
    cookie = {
        "ci_session": session,
        "login_token": logintoken,
        "user_id": user_id,
        "reader_id": reader_id
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",  # 模拟浏览器请求
        "Referer": f"https://www.ciweimao.com/chapter/{chapter_id}",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    accessKeyUrl = "https://www.ciweimao.com/chapter/ajax_get_session_code"
    accessKeyData = {
        "chapter_id": chapter_id
    }
    accessKeyResponse = requests.post(accessKeyUrl,data=accessKeyData,cookies=cookie,headers=headers)
    accessKeyJson = json.loads(accessKeyResponse.text)
    accessKey = accessKeyJson.get("chapter_access_key")
    chapterUrl = "https://www.ciweimao.com/chapter/get_book_chapter_detail_info"
    chapterData = {
        "chapter_id": chapter_id,
        "chapter_access_key": accessKey
    }
    chapterResponse = requests.post(chapterUrl,data=chapterData,cookies=cookie,headers=headers)
    chapterJson = json.loads(chapterResponse.text)
    status = chapterJson.get("code")
    if(status != 100000):
        return chapterJson['tip']
    keys = chapterJson.get("encryt_keys")
    content = chapterJson.get("chapter_content")
    return decrypt.decrypt(content,keys,accessKey)

def pureChapter(text):
    soup = BeautifulSoup(text, 'html.parser')
    for span in soup.find_all('span'):
        span.decompose()  # 彻底删除标签和内容
    return soup.prettify()
