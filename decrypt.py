import base64
import BuiltIn
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decryptFree(content,keys,access_key):

    if not content or not keys or not access_key:
        raise ValueError("Missing content, keys or access")

    t = len(keys)
    o = list(access_key)
    m = len(o)

    # 选出两个密钥索引
    k = [
        keys[ord(o[m - 1]) % t],
        keys[ord(o[0]) % t]
    ]

    n = content
    for i in range(len(k)):
        n = base64.b64decode(n)  # base64 解码
        iv = n[:16]
        encrypted_data = n[16:]

        # 解密
        cipher = AES.new(base64.b64decode(k[i]), AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)

        if i < len(k) - 1:
            n = base64.b64decode(base64.b64encode(decrypted))  # 中间过程继续处理
        else:
            n = unpad(decrypted, AES.block_size)

    return n.decode('utf-8')

from dataclasses import dataclass,field

def decryptImgId(access : BuiltIn.ClassAccess):
    imageCode = access.json["image_code"] # type: ignore
    accessKey = access.json["access_key"] # type: ignore
    keys = access.json["encryt_keys"] # type: ignore
    access.key = accessKey

    # --- 解析 access_key 并选择两个密钥 ---
    key1 = keys[ord(accessKey[-1]) % len(keys)]
    key2 = keys[ord(accessKey[0]) % len(keys)]

    # --- 执行 AES 解密两轮 ---
    def aes_decrypt(encrypted_data_b64, key_b64):
        encrypted_data = base64.b64decode(encrypted_data_b64)
        key = base64.b64decode(key_b64)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        return decrypted

    # 先解密两轮
    step1 = aes_decrypt(imageCode, key1)
    step1_base64 = base64.b64decode(base64.b64encode(step1))  # 模拟中间 base64 encode/decode 操作
    step2 = aes_decrypt(step1_base64, key2)
    final_result = unpad(step2, AES.block_size)

    access.imgId = final_result.decode()
    return
