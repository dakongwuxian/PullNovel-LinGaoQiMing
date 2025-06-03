import os
from bs4 import BeautifulSoup

# 定义输入和输出文件夹路径
input_folder = r"C:\Users\David\Desktop\xian.wu\PythonVS\pull_novel_for_LinGaoQiMing\pull_novel_for_LinGaoQiMing\novel_txt"
# 输出文件夹与 input_folder 同级，文件夹名为 novel
output_folder = os.path.join(os.path.dirname(input_folder), "novel")

# 如果输出文件夹不存在，则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历 input_folder 中所有 txt 文件
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(".txt"):
        continue  # 忽略非 txt 文件

    input_file_path = os.path.join(input_folder, filename)
    with open(input_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(content, "html.parser")

    # 提取章节标题：位于 <h1> 标签中，取其文本
    h1_tag = soup.find("h1")
    if h1_tag:
        chapter_title = h1_tag.get_text(strip=True)
    else:
        print(f"文件 {filename} 中未找到 <h1> 标签，跳过。")
        continue

    # 提取小说文本：所有 <p> 标签中的内容，每个 <p> 提取后的文本末尾加一个换行符
    paragraphs = []
    p_tags = soup.find_all("p")
    for p in p_tags:
        p_text = p.get_text(strip=True)
        if p_text:
            paragraphs.append(p_text + "\n")

    # 构造新文件的内容：第一行为章节标题，后面是所有小说内容段落
    new_content = chapter_title + "\n\n"   # 标题后换两行
    new_content += "".join(paragraphs)

    # 构造新文件名：原文件名（去掉扩展名） + "-" + 章节标题 + ".txt"
    base_name = os.path.splitext(filename)[0]
    new_filename = f"{base_name}-{chapter_title}.txt"
    # 文件名中不能包含某些非法字符，进行替换（例如 \ / : * ? " < > |）
    invalid_chars = r'\/:*?"<>|'
    for char in invalid_chars:
        new_filename = new_filename.replace(char, "")
    
    output_file_path = os.path.join(output_folder, new_filename)
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"新文件保存成功：{output_file_path}")