import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt(content,keys,access_key):
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
