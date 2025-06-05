from pathlib import Path

def read_lines_if_exists(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"文件不存在：{file_path}")
        return []

    with open(path, 'r', encoding='utf-8') as f:
        readResponse = f.read()
    return readResponse
