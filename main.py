import getBookself
import getLogin
import readFromCache
import time
import getBookDetail
import download

ci_session = None
login_token = None
reader_id = None
user_id = None
ci_session = None
exTimest = 0

lines = readFromCache.read_lines_if_exists('./cached.passport')
if(len(lines) > 0):
    login_token = lines[0]
    reader_id = lines[1]
    user_id = lines[2]
    exTimest = lines[3]
    ci_session = lines[4]
print("Debug: ",login_token,"\n",reader_id,"\n",user_id,"\n",exTimest,"\n",ci_session)
if (time.time() > float(exTimest) or len(lines) == 0): 
	loginData = getLogin.getLogin()
	for cookie in loginData:
		if cookie['name'] == 'login_token':
			login_token = cookie['value']
		if cookie['name'] == 'reader_id':
			reader_id = cookie['value']
		if cookie['name'] == 'user_id':
			user_id = cookie['value']
		if cookie['name'] == 'ci_session':
			ci_session = cookie['value']
	print("Debug: ",login_token,"\n",reader_id,"\n",user_id,"\n")
	# 在 Python 中打开文件并使用 utf-8 编码
	data = data = login_token + "\n" + reader_id + "\n" + user_id + "\n" + str(int(time.time() + 7200)) + "\n" + ci_session

	with open("cached.passport", "w", encoding="utf-8") as f:
		f.write(data)

# bookself = getBookself.getBookself(ci_session,login_token,user_id,reader_id)

# print(bookself)
book_id = input("输入一个小说id: ")
download.main(ci_session,login_token,user_id,reader_id,book_id)
# content = getBookDetail.getBookDetail(ci_session,login_token,user_id,reader_id,book_id)
# # print(content)
# for title, link in content:
#     print(f"章节标题: {title}, 链接: {link}")
