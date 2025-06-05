from bs4 import BeautifulSoup
import requests
import decrypt
import json
import time

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

def getContent(cookies,ID):
    url = "https://www.ciweimao.com/chapter/get_chapter_list_in_chapter_detail"
    headers = defaultHeaders
    headers.update({
        "Referer": url})
    data = {
        "book_id": ID,
        "chapter_id": "0",
        "orderby": "0"
    }
    response = requests.post(url, cookies=cookies,headers=headers,data=data)
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

def getName(cookies,url):
    headers = defaultHeaders
    headers.update({
        "Referer": url})
    response = requests.get(url, cookies=cookies,headers=headers)
    if(response.status_code != 200):
        return False
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

def getChapter(cookies,ID):
    url = f"https://www.ciweimao.com/chapter/{ID}"
    headers = defaultHeaders
    headers.update({
        "Referer": url})

    accessKeyUrl = "https://www.ciweimao.com/chapter/ajax_get_session_code"
    accessKeyHeaders = headers
    accessKeyData = {
        "chapter_id": ID
    }
    accessKeyResponse = requests.post(accessKeyUrl,data=accessKeyData,cookies=cookies,headers=accessKeyHeaders)
    accessKeyJson = json.loads(accessKeyResponse.text)
    accessKey = accessKeyJson.get("chapter_access_key")

    chapterUrl = "https://www.ciweimao.com/chapter/get_book_chapter_detail_info"
    chapterHeaders = headers
    chapterData = accessKeyData
    chapterData.update({"chapter_access_key": accessKey})
    
    chapterResponse = requests.post(chapterUrl,data=chapterData,cookies=cookies,headers=chapterHeaders)
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
