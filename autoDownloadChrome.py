import os
import zipfile
import requests
import shutil
from tqdm import tqdm
import urllib3
import sys

# 忽略 SSL 验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def remove_old_dirs():
    for folder in ["chrome", "chromedriver"]:
        if os.path.exists(folder):
            print(f"删除旧目录: {folder}")
            shutil.rmtree(folder)

def download_with_progress(url, output_path):
    response = requests.get(url, stream=True, verify=False)
    total = int(response.headers.get('content-length', 0))

    with open(output_path, 'wb') as file, tqdm(
        desc=os.path.basename(output_path),
        total=total,
        unit='B',
        unit_scale=True,
        unit_divisor=1024
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            bar.update(len(chunk))

def download_and_unzip_flat(url, extract_to):
    zip_path = os.path.join(extract_to, "temp.zip")
    os.makedirs(extract_to, exist_ok=True)
    print(f"下载: {url}")
    download_with_progress(url, zip_path)

    print(f"解压: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)

    # 将子文件夹下所有内容提升到根目录
    flatten_directory(extract_to)
    print(f"完成: {extract_to}\n")

def flatten_directory(root_dir):
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            for inner in os.listdir(item_path):
                src = os.path.join(item_path, inner)
                dst = os.path.join(root_dir, inner)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)
            shutil.rmtree(item_path)

def get_latest_version():
    url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    print(f"获取版本信息: {url}")
    response = requests.get(url, verify=False)
    data = response.json()
    stable = data["channels"]["Stable"]
    version = stable["version"]
    chrome_url = next(item["url"] for item in stable["downloads"]["chrome"] if item["platform"] == "win64")
    driver_url = next(item["url"] for item in stable["downloads"]["chromedriver"] if item["platform"] == "win64")
    return version, chrome_url, driver_url

def main():
    remove_old_dirs()

    version, chrome_url, driver_url = get_latest_version()
    print(f"\n最新稳定版版本号: {version}\n")

    download_and_unzip_flat(chrome_url, "chrome")
    download_and_unzip_flat(driver_url, "chromedriver")

    print("Chrome 路径应为: chrome/chrome.exe")
    print("Chromedriver 路径应为: chromedriver/chromedriver.exe")
    print("所有文件已下载并整理完成。")
