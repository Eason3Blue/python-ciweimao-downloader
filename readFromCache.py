from pathlib import Path

def read(filePath):
    path = Path(filePath)
    if not path.exists():
        print(f"文件不存在：{filePath}")
        return []

    with open(path, 'r', encoding='utf-8') as f:
        readResponse = f.read()
    return readResponse
