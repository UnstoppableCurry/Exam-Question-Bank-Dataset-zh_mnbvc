import csv
import re
from collections import Counter
import jieba

def count_word_frequency(words_list):
    # 创建一个空字典用于存储词频统计结果
    word_frequency = {}

    # 将所有分词结果合并为一个列表
    all_words = [word for words in words_list for word in words]

    # 统计词频
    word_counts = Counter(all_words)

    # 更新词频统计结果
    word_frequency.update(word_counts)

    # 按照词频从高到低排序
    sorted_result = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)

    return sorted_result


def extract_first_element_from_csv(csv_file):
    file_paths = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 确保行不为空
                file_path = re.sub(r'[^\w\s-]', '', row[0])  # 去除特殊字符
                file_paths.append(file_path.replace("docx_math", "").replace("docx", ""))

    return file_paths


# CSV文件路径
csv_file = 'index_to_filename.csv'

# 提取每行的第一个元素
file_paths = extract_first_element_from_csv(csv_file)

# 添加自定义词典

# 存储所有分词结果的列表
words_list = []

# 对每个元素进行分词处理，并保存到列表中
for file_path in file_paths:
    words = jieba.cut(file_path)
    words_list.append(list(words))

# 统计词频并按照词频从高到低排序
result = count_word_frequency(words_list)

# 输出词频统计结果
for word, count in result:
    if count <= 1:
        continue
    print(f"{word}: {count}")

