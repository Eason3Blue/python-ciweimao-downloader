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

def slice_image_fast(image:bytes, chapter:BuiltIn.ClassChapter,  max_len: int):
    # 从 bytes 转为 numpy 一维数组
    nparr = np.frombuffer(image, np.uint8)

    # 解码为灰度图，等效于 cv2.IMREAD_GRAYSCALE
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

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
    for i in range(len(cuts) - 1):
        if long_axis == 0:
            cropped = img[cuts[i]:cuts[i+1], :]
        else:
            cropped = img[:, cuts[i]:cuts[i+1]]

        success, encoded_img = cv2.imencode('.jpg', img)
        if not success:
            raise ValueError("图像编码失败")
        chapter.img.append(encoded_img.tobytes())
    return
