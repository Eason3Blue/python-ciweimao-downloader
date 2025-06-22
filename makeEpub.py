import os
import uuid
import requests
import BuiltIn
from bs4 import BeautifulSoup
from ebooklib import epub
from urllib.parse import urlparse

def clean_html_with_images(raw_html: str, img_dir="images"):
    soup = BeautifulSoup(raw_html, 'html.parser')

    for span in soup.find_all('span'):
        span.decompose()

    image_items = []
    image_html_blocks = []

    for img_tag in soup.find_all('img'):
        src = img_tag.get('src') # type: ignore
        if not src:
            continue

        parsed = urlparse(src) # type: ignore
        filename = str(uuid.uuid4()) + os.path.splitext(parsed.path)[-1]
        epub_path = f"{img_dir}/{filename}"  # ✅ 正斜杠，适用于 HTML

        try:
            if parsed.scheme in ('http', 'https'):
                response = requests.get(src) # type: ignore
                if response.status_code == 200:
                    image_data = response.content
                else:
                    continue
            else:
                with open(src, 'rb') as f: # type: ignore
                    image_data = f.read()

            img_item = epub.EpubItem(uid=filename,
                                     file_name=epub_path,
                                     media_type=f'image/{filename.split(".")[-1]}',
                                     content=image_data)
            image_items.append(img_item)
            image_html_blocks.append(f'<div><img src="{epub_path}" /></div>')

        except Exception as e:
            print(f"[WARN] 图像 {src} 处理失败: {e}")
            continue

        img_tag.decompose()

    cleaned_paragraphs = [str(p.get_text()) for p in soup.find_all('p')]
    cleaned_text = '<br/>'.join(cleaned_paragraphs)
    full_html = f"<div>{cleaned_text}</div>" + ''.join(image_html_blocks)

    return full_html, image_items


def generate_epub(book: BuiltIn.ClassBook, output_path: str):
    epub_book = epub.EpubBook()

    # Set metadata
    epub_book.set_title(book.name or "Untitled Book")
    epub_book.add_author(book.author or "Unknown Author")

    # Set cover image safely
    if book.cover and isinstance(book.cover,bytes):
        epub_book.set_cover("cover.jpg", book.cover)
    else:
        print(f"[WARN] 封面图片文件不存在")

    spine = ['nav']
    epub_chapters = []

    for idx, chapter in enumerate(book.chapters):
        try:
            chapter_html, img_items = clean_html_with_images(chapter.raw)

            # 构造章节
            c = epub.EpubHtml(title=chapter.name,
                            file_name=f'chap_{idx + 1}.xhtml',
                            lang='zh')
            c.content = f"<h1>{chapter.name}</h1>{chapter_html}"
            epub_book.add_item(c)

            for img in img_items:
                    epub_book.add_item(img)
            epub_chapters.append(c)
            spine.append(c)  # type: ignore
        except Exception as e:
            print(f"[ERROR] 处理第 {idx + 1} 章时出错: {e}")

        # 添加 spine、导航
    epub_book.spine = spine
    epub_book.add_item(epub.EpubNcx())
    epub_book.add_item(epub.EpubNav())

    # ✅ 显式设置目录
    epub_book.toc = tuple(epub_chapters) # type: ignore

    # 写入 EPUB 文件
    try:
        epub.write_epub(output_path, epub_book, {})
        print(f"[INFO] EPUB 成功生成：{output_path}")
    except Exception as e:
        print(f"[ERROR] 写入 EPUB 失败: {e}")



# ✅ 示例用法
if __name__ == "__main__":
    sample_html = '''
        <p>This is a sample paragraph.</p>
        <p>Another one with <span>noise</span>.</p>
        <img src="img1.jpg"/>
        <img src="https://e1.kuangxiangit.com/uploads/allimg/c250510/10-05-25114833-25098.jpg"/>
    '''

    book = BuiltIn.ClassBook(
        name="Sample Image Book",
        author="Author Name",
        cover=bytes(),  # Should be a bytes object
        chapters=[
            BuiltIn.ClassChapter(raw=sample_html,name="c1",isFree=False),
            BuiltIn.ClassChapter(raw=sample_html,name="c2"),
            BuiltIn.ClassChapter(raw=sample_html,name="c3"),
            
        ]
    )

    generate_epub(book, "output.epub")
