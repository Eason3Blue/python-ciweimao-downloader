import numpy as np
from io import BytesIO
from paddleocr import PaddleOCR
from pathlib import Path
import cv2
import BuiltIn
from bisect import bisect_right
from typing import List

def slice_image_fast(image: bytes, chapter: BuiltIn.ClassChapter, max_len: int, grayscale: bool = False):
    nparr = np.frombuffer(image, np.uint8)

    decode_flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imdecode(nparr, decode_flag)

    if img is None:
        raise ValueError("图像解码失败")

    # 分析用灰度图
    img_gray = img if grayscale else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if img_gray.shape[0] < 600:
        print("此章节内容很少，登录状态可能掉了，也有可能你还未购买。")
        chapter.isWrong = True
    if img_gray.shape[0] == 28:
        print("重试")
        return False

    h, w = img_gray.shape
    long_axis = 0 if h > w else 1
    length = h if long_axis == 0 else w

    binary = np.where(img_gray > 200, 255, 0).astype(np.uint8)
    projection = np.count_nonzero(binary == 0, axis=1 if long_axis == 0 else 0)
    white_gaps = np.flatnonzero(projection == 0)

    cuts = [0]
    current = 0
    while current + max_len < length:
        target = current + max_len
        idx = bisect_right(white_gaps, target) - 1
        if idx <= 0 or white_gaps[idx] <= current + 100:
            next_cut = target
        else:
            next_cut = white_gaps[idx]
        cuts.append(next_cut)
        current = next_cut
    cuts.append(length)

    count = 1
    for i in range(len(cuts) - 1):
        if long_axis == 0:
            cropped = img[cuts[i]:cuts[i+1], :]
        else:
            cropped = img[:, cuts[i]:cuts[i+1]]

        success, encoded_img = cv2.imencode('.jpg', cropped)
        if not success:
            raise ValueError("图像编码失败")
        Path(f"{chapter.content.imgDir}/sliced/{chapter.countId}/").mkdir(parents=True, exist_ok=True)
        with open(Path(f"{chapter.content.imgDir}/sliced/{chapter.countId}/{count}.jpg"), "wb") as f:
            f.write(encoded_img.tobytes())
        chapter.content.raw += f"<img src='{chapter.content.imgDir}/sliced/{chapter.countId}/{count}.jpg'>"
        count += 1
    return
