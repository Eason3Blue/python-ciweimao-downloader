import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt(content,keys,access_key):

    if not content or not keys or not access_key:
        raise ValueError("Missing content, keys or accessKey")

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

# 使用示例
if __name__ == "__main__":
    # 示例参数（实际使用时需替换为真实数据）
    encrypted_content = "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"  # Base64 加密数据
    key_list = [
        "VKm5LW3+BnSEtnMaAVogLD2605q6+OKVWB7kgd/HSgQ=",
        "bTPcr8hquzf+EQdAp3ivod08Z8bfJWi/6xBCb507Tm0=",
        "zbW9Nh9yCxu9rnEGGF4rRxkSACbgWlvoBXG006c+YvU=",
        "94HGwwgGKlmSVv7c7PLdx04dTxowhmnvq7KIeJO1CqI=",
        "UD7ImxZBqfZBvvI3H9k3UDyYFGhvsz4Fgcs7Ch10lKQ=",
        "ZZTUaPOAl6ZG8oSoKU2wrz8idCuS/eZ+FeL9cqWw0nM=",
        "Wm7MT5nVRxuoSnHRVZrhwSw8QXOM98AF0UPXcYpEJIk=",
        "RkSodF/zNc8+xmnDFTB3v9EzF/OWvdg0x1ZrsVjJc8A=",
        "/w1cxx8cCU+rXvnVSx0lf7VoILxFSzTZq0YMQ3jROiU=",
        "Uc3QS0G8WRYv9LHm/aqki9uFBm7z2MbiJVtzgSakQ2c=",
        "Sj44lRCdH6IPYODtmnj3a9szlbXeojJVq6kIboIWoTw="
    ]  # Base64 密钥列表
    access_key = "RNXAhC4P"  # 访问密钥
    
    try:
        result = decrypt(encrypted_content, key_list, access_key)
        print("Decrypted Result:", result)
        with open("1.txt", "w", encoding="utf-8") as f:
            f.write(result)
    except Exception as e:
        print("Decryption failed:", str(e))