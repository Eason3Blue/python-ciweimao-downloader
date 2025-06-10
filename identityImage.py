from PIL import Image
import numpy as np
from io import BytesIO
from paddleocr import PaddleOCR
from dataclasses import dataclass,field
from pathlib import Path
import io,json,cv2,ast
import BuiltIn

import cv2
import numpy as np
from PIL import Image

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

def image_to_text(chapter : BuiltIn.ClassChapter, lang='ch'):
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
        result = ocr.predict(input = chapter.content.imgPath)
        return result
    except Exception as e:
        print(f"OCR处理失败: {str(e)}")
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
        
        result = image_to_text(chapter)
        for res in result:
            res.save_to_json(f"{book.id}/json")
            res.save_to_img(f"{book.id}/ocrImg")
            textJson = res["rec_texts"]
        for texts in textJson: # type: ignore
            chapter.content.raw += texts+"\n"
    except Exception as e:
        chapter.content.raw = f"json 失败: {e}"
    return