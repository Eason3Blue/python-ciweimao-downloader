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
    session.cookies.update(requests.utils.cookiejar_from_dict({"ci_session": match.group(1)})) # type: ignore
    return
