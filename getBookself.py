import requests
from bs4 import BeautifulSoup

def getBookself(session, logintoken, user_id, reader_id):
    url = "https://www.ciweimao.com/bookshelf/my_book_shelf"
    cookie = {
		"ci_session": session,
		"login_token": logintoken,
		"user_id": user_id,
		"reader_id": reader_id
	}
    headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
	}
    response = requests.get(url, cookies=cookie,headers=headers)
    return extract_book_titles_and_links(response.text)

def extract_book_titles_and_links(content):
    soup = BeautifulSoup(content, 'html.parser')

    result = []

    # 查找所有书籍标题所在的 h3 元素
    for h3 in soup.find_all('h3', class_='title'):
        a_tag = h3.find('a')
        if a_tag and a_tag.get('href') and a_tag.text.strip():
            title = a_tag.text.strip()
            url = a_tag['href']
            result.append((title, url))

    return result
