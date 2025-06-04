from pathlib import Path
import getBookDetail

def main(session, logintoken, user_id, reader_id,book_id):
    result = getBookDetail.getName(session,logintoken,user_id,reader_id,book_id)
    name = result[0]
    dirPath = Path(name)
    dirPath.mkdir(parents=True, exist_ok=True)
    img = result[1]
    with open(dirPath / "cover.jpg", "wb") as f:
        f.write(img)
    
    content = getBookDetail.getContent(session,logintoken,user_id,reader_id,book_id)
    count = 1
    result = ""
    for title, chapterID in content:
        print("进行第",count,"章下载，标题:",title," ChapterID: ",chapterID)
        result += title + "\n" + getBookDetail.getChapter(session,logintoken,user_id,reader_id,chapterID)
        count += 1
        print("下载完成")
    with open(dirPath / (name + ".html"), "w", encoding="utf-8") as f:
        f.write(result)

import time
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
    print(main(ci_session,login_token,user_id,reader_id,"100047661"))