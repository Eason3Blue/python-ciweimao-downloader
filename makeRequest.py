import requests
import BuiltIn
import re

def getSession(session : requests.Session):
    """
    获得ci_session
    """
    url = "https://www.ciweimao.com"
    headers = BuiltIn.defaultHeaders.copy()
    resp = session.get(url=url,headers=headers)
    respHeader = resp.headers.get('Set-Cookie', '')
    match = re.search(r'ci_session=([^;]+)', respHeader)
    if match:
        session.cookies.update(requests.utils.cookiejar_from_dict({"ci_session": match.group(1)})) # type: ignore
    return

def myRequest(session:requests.Session, url:str, headers:dict,method:str, data:dict = {}) -> requests.Response:
    if (method == "post"):
        resp = session.post(url=url,
                             data=data,
                             headers=headers)
    elif (method == "get"):
        resp = session.get(url=url,
                             params=data,
                             headers=headers)
    else:
        raise SyntaxError
    respHeader = resp.headers.get('Set-Cookie', '')
    match = re.search(r'ci_session=([^;]+)', respHeader)
    if match:
        session.cookies.update(requests.utils.cookiejar_from_dict({"ci_session": match.group(1)})) # type: ignore
    match = re.search(r'login_token=([^;]+)', respHeader)
    if match:
        session.cookies.update(requests.utils.cookiejar_from_dict({"login_token": match.group(1)})) # type: ignore
    match = re.search(r'user_id=([^;]+)', respHeader)
    if match:
        session.cookies.update(requests.utils.cookiejar_from_dict({"user_id": match.group(1)})) # type: ignore
    match = re.search(r'reader_id=([^;]+)', respHeader)
    if match:
        session.cookies.update(requests.utils.cookiejar_from_dict({"reader_id": match.group(1)})) # type: ignore
    
    return resp