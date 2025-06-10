import os
import BuiltIn
import mimetypes
import requests
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from ebooklib import epub
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

ALLOWED_IMAGE_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'
}

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
    name: str = field(default_factory=str)
    access: ClassAccess = field(default_factory=ClassAccess)
    content: ClassContent = field(default_factory=ClassContent)

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({"User-Agent": "Mozilla/5.0 (EPUBBot/1.0)"})
    return session

def safe_filename(content, original_name):
    ext = os.path.splitext(original_name)[1] or '.jpg'
    name_hash = hashlib.md5(content).hexdigest()[:8]
    return f"{name_hash}{ext}"

def download_image(img_src, base_path, session=None):
    try:
        session = session or create_session()
        Path(base_path).mkdir(parents=True, exist_ok=True)
        if img_src.startswith(('http://', 'https://')):
            response = session.get(img_src, timeout=10)
            response.raise_for_status()
            return response.content, safe_filename(response.content, os.path.basename(img_src))
        else:
            full_path = (Path(base_path) / img_src).resolve()
            Path(full_path.parent).mkdir(parents=True, exist_ok=True)
            try:
                full_path.relative_to(Path(base_path).resolve())
            except ValueError:
                raise ValueError(f"Attempted to access restricted path: {full_path}")
            content = full_path.read_bytes()
            return content, safe_filename(content, full_path.name)
    except Exception as e:
        print(f"Failed to download {img_src}: {str(e)}")
        raise

def process_html(html, book, base_path, session, image_cache):
    Path(base_path).mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(html, 'lxml')
    for img in soup.find_all('img'):
        src = img.get('src') # type: ignore
        if not src:
            continue
        try:
            if src in image_cache:
                img['src'] = image_cache[src] # type: ignore
                continue
            img_data, filename = download_image(src, base_path, session)
            media_type, _ = mimetypes.guess_type(filename)
            if not media_type:
                media_type = 'image/jpeg'
            if media_type not in ALLOWED_IMAGE_TYPES:
                raise ValueError(f"Unsupported image type: {media_type}")
            img_id = f"img_{hashlib.md5(img_data).hexdigest()[:8]}"
            Path(base_path, "images").mkdir(parents=True, exist_ok=True)
            image_item = epub.EpubItem(
                uid=img_id,
                file_name=f"images/{filename}",
                media_type=media_type,
                content=img_data
            )
            book.add_item(image_item)
            new_src = f"images/{filename}"
            img['src'] = new_src # type: ignore
            image_cache[src] = new_src
        except Exception as e:
            print(f"Skipping image {src}: {str(e)}")
            img['src'] = f"FAILED:{src}" # type: ignore
    return str(soup)

def create_epub(originBook : BuiltIn.ClassBook, output_path):
    try:
        title = originBook.name
        author = originBook.author
        chapters = originBook.chapters.copy()
        cover = originBook.cover
        base_path = output_path
        
        Path(output_path).mkdir(parents=True, exist_ok=True)
        output_file = Path(output_path) / f"{title}.epub"
        Path(output_file.parent).mkdir(parents=True, exist_ok=True)

        book = epub.EpubBook()
        book.set_title(title)
        book.add_author(author)
        book.set_cover("cover.jpg", cover)

        spine = []
        toc = []
        image_cache = {}
        session = create_session()

        for idx, chapter in enumerate(chapters, start=1):
            if not chapter.content.raw.strip():
                continue
            processed_html = process_html(
                chapter.content.raw, book, base_path, session, image_cache
            )
            file_name = f'chap_{idx}.xhtml'
            epub_chapter = epub.EpubHtml(
                title=chapter.name,
                file_name=file_name,
                content=processed_html,
                lang='zh'
            )
            book.add_item(epub_chapter)
            spine.append(epub_chapter)
            toc.append(epub.Link(file_name, chapter.name, f'chap_{idx}'))

        if not spine:
            print("No valid chapters to write.")
            return

        book.toc = toc
        book.spine = ['nav'] + spine
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub(str(output_file), book)
        print(f'✅ EPUB 已创建: {output_file}')
    except Exception as e:
        print(f"写入 EPUB 文件时出错：{e}")
