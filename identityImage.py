from PIL import Image
import numpy as np
from io import BytesIO
from paddleocr import PaddleOCR
from pathlib import Path
import io,cv2
import BuiltIn
import os
from bisect import bisect_right
from typing import List

#将图片转为黑白
def filter_black_white_cv(image: Image.Image) -> Image.Image:
    """使用 OpenCV 提高速度"""
    np_img = np.array(image.convert("RGB"))

    # 分别提取黑/白掩码
    black_mask = cv2.inRange(np_img, (0, 0, 0), (129, 129, 129)) # type: ignore
    white_mask = cv2.inRange(np_img, (221, 221, 221), (255, 255, 255)) # type: ignore

    # 合并两种掩码
    mask = cv2.bitwise_or(black_mask, white_mask)

    # 创建空白图像（默认白）
    result = np.full_like(np_img, 255)

    # 将黑色像素保留
    result[black_mask == 255] = [0, 0, 0]
    # 白色区域自然保留

    return Image.fromarray(result)

#将图片分割
def slice_image_fast(image_path: str, save_dir: str, max_len: int = 3890) -> List[str]:
    os.makedirs(save_dir, exist_ok=True)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    long_axis = 0 if h > w else 1
    length = h if long_axis == 0 else w

    # 快速二值化（白为255，黑为0）
    binary = np.where(img > 200, 255, 0).astype(np.uint8)

    # 计算黑色像素投影
    projection = np.count_nonzero(binary == 0, axis=1 if long_axis == 0 else 0)

    # 获取所有白缝索引（全白的行或列）
    white_gaps = np.flatnonzero(projection == 0)

    # 初始化切点
    cuts = [0]
    current = 0

    while current + max_len < length:
        target = current + max_len
        idx = bisect_right(white_gaps, target) - 1
        if idx <= 0 or white_gaps[idx] <= current + 100:
            # 没有合适的白缝，只能强切
            next_cut = target
        else:
            next_cut = white_gaps[idx]
        cuts.append(next_cut)
        current = next_cut

    cuts.append(length)

    # 切割图像
    saved_paths = []
    for i in range(len(cuts) - 1):
        if long_axis == 0:
            cropped = img[cuts[i]:cuts[i+1], :]
        else:
            cropped = img[:, cuts[i]:cuts[i+1]]

        out_path = os.path.join(save_dir, f'slice_{i:03d}.png')
        cv2.imwrite(out_path, cropped)
        saved_paths.append(out_path)

    return saved_paths

def image_to_text(imgPath:str, lang='ch'):
    """
    使用 PaddleOCR 提取图片中的文字
    """
    try:
        # 初始化OCR
        ocr = PaddleOCR(
            text_detection_model_dir='./paddlex\\official_models\\PP-OCRv5_mobile_det',
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_dir='./paddlex\\official_models\\PP-OCRv5_mobile_rec',
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False)
        # 执行OCR
        result = ocr.predict(input = imgPath)
        return result
    except Exception as e:
        print(f"    OCR处理失败: {str(e)}")
        return []

def process_image_bytes_to_chapter(chapter : BuiltIn.ClassChapter, book : BuiltIn.ClassBook) -> None:
    try:
        image = Image.open(BytesIO(chapter.content.img))
        img_byte_arr = io.BytesIO()
        pimage = filter_black_white_cv(image)
        pimage.save(img_byte_arr, format='PNG')
        chapter.content.img =  img_byte_arr.getvalue()
        with open(Path(chapter.content.imgPath),"wb") as f:
            f.write(chapter.content.img)
        
        print("     正在分割图片...")
        contentImgs = list()
        contentImgs = slice_image_fast(
            chapter.content.imgPath,
            f"{chapter.content.imgDir}/sliced/{chapter.countId}",
            3890)
        print(f"    分割完成，共{len(contentImgs)}张图片，正在识别...")
        
        j = 0
        for imgPath in contentImgs:
            j += 1
            textBoxesJson = textJson = list()
            result = image_to_text(imgPath)
            for res in result:
                # res.save_to_json(f"{book.path}/json")
                # res.save_to_img(f"{book.path}/ocrImg")
                textJson = res["rec_texts"]
                textBoxesJson = res["rec_boxes"]
            
            i = 0
            for texts in textJson:
                textBoxes = textBoxesJson[i]
                x = textBoxes[0]
                if x > 60 and x <120:
                    chapter.content.raw += "\n"+texts
                else:
                    chapter.content.raw += texts
                i += 1
            print(f"    第{j}张图片识别成功")
    except Exception as e:
        chapter.content.raw = f"失败: {e}"
    return
