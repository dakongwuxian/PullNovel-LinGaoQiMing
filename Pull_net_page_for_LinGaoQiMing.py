import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# 禁用不安全的请求警告（仅用于测试环境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 各卷章节数统计
volumes = {
    0: 12,
    1: 47,
    2: 183,
    3: 382,
    4: 237,
    5: 472,
    6: 483,
    7: 110
}

output_dir = "novel_txt"
os.makedirs(output_dir, exist_ok=True)

base_url = "https://lingaoqiming.github.io"

# 创建全局 Session 对象，并设置重试策略
session = requests.Session()
retries = Retry(
    total=3,                 # 总共重试次数
    backoff_factor=1,        # 重试延时：1秒、2秒、4秒……
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 如果需要代理，请启用并设置正确的代理地址：
# proxies = {
#     "http": "http://100.98.146.3:8080",
#     "https": "http://100.98.146.3:8080"
# }
# session.proxies = proxies

def fetch_and_save(vol, chapter):
    """构造 URL，获取网页内容并保存到文件；若文件已存在则跳过"""
    chapter_str = f"{chapter:03d}"
    url = f"{base_url}/{vol}/{vol}-{chapter_str}00.html"
    filename = f"{vol}-{chapter_str}.txt"
    file_path = os.path.join(output_dir, filename)

    if os.path.exists(file_path):
        return f"{file_path} 已存在，跳过。"
    
    try:
        response = session.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            return f"保存成功：{file_path}"
        else:
            return f"获取失败，状态码 {response.status_code}：{url}"
    except Exception as e:
        return f"请求 {url} 时发生异常：{e}"

# 构造所有任务列表：每个任务对应一个卷的某一节
tasks = []
for vol in range(0, 8):
    num_chapters = volumes.get(vol, 0)
    for chapter in range(1, num_chapters + 1):
        tasks.append((vol, chapter))

# 使用线程池同时处理多个请求
max_workers = 10  # 根据需求调整线程数
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_task = {executor.submit(fetch_and_save, vol, chapter): (vol, chapter) for vol, chapter in tasks}
    for future in as_completed(future_to_task):
        result = future.result()
        print(result)
        # 可选：每个任务之间稍作延时，防止过快请求
        time.sleep(0.1)

print("全部任务完成。")