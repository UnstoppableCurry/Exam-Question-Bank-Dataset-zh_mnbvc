import math
import json
from pathlib import Path
import argparse
import pandas as pd
import csv
from tqdm import tqdm
import re

from examination_paper_classifier import extract_text
from examination_paper_classifier import read_processed_file_path

# 创建Path对象，代表当前脚本所在的目录
current_directory = Path(__file__).parent

# 构建关键字json文件的路径
json_file_path = current_directory / "data" / "category_keywords.json"

CLASSIFY_KEYWORDS = None

if not json_file_path.exists():
    raise FileNotFoundError("默认的词频分析json未找到")

with json_file_path.open("r") as file:
    CLASSIFY_KEYWORDS = json.load(file)


def starts_with_number_and_punctuation(text):
    pattern = r"^\d+[.,;:!?。，；：！？、]"
    match = re.match(pattern, text)
    return match is not None


def judgment_paper_category_by_path(file_path):
    """
    根据提供的文件路径判断文件类型。

    这个函数会遍历所有定义的类别以及其对应的关键字，查找关键字在文件路径中最后出现的位置。
    函数会返回最后出现位置最靠后的类别作为文件的类型。

    如果没有找到任何类别的关键字，那么函数会返回None。

    参数：
    file_path: str
        文件的路径。

    返回：
    str 或 None
        文件的类别，如果找不到匹配的类别则返回None。
    """
    # 从CLASSIFY_KEYWORDS中获取所有的类别
    paper_types = [item["category"] for item in CLASSIFY_KEYWORDS]
    
    # 初始化每个类别的最后出现的位置为-1
    last_occurrence = {paper_type[0]: -1 for paper_type in paper_types}

    # 遍历每个类别和它的关键字
    for paper_type in paper_types:
        for keyword in paper_type:
            # 找到这个关键字在文件路径中最后出现的位置
            index = file_path.rfind(keyword)
            # 如果这个关键字出现的位置比当前记录的位置更靠后
            if index > last_occurrence[paper_type[0]]:
                # 更新这个类别的最后出现的位置
                last_occurrence[paper_type[0]] = index

    # 找到最后出现的位置最靠后的类别
    max_index_paper_type = max(last_occurrence, key=last_occurrence.get)

    # 如果最后出现的位置是-1，说明没有找到任何类别
    if last_occurrence[max_index_paper_type] == -1:
        return None
    else:
        # 否则返回找到的类别
        return max_index_paper_type


def classify_paper_type(file_content, file_path=None, gap=0.05, min_total=5, debug=False):
    # 首先通过路径判断
    if file_path:
        category = judgment_paper_category_by_path(str(file_path))
        if category:
            return category

    # 检测文件第一行是否出现category
    first_line_content =  file_content.split("\n", 1)[0]
    # 优先先检测一下是否直接以题目开始
    if not starts_with_number_and_punctuation(first_line_content):
        for item in CLASSIFY_KEYWORDS:
            keywords = item["category"]
            if any([keyword in first_line_content for keyword in keywords]):
                return keywords[0]

    # Create a dictionary to store keyword counts for each category
    category_counts = {}

    for item in CLASSIFY_KEYWORDS:
        keywords = item["category"] + item["keywords"]
        count = sum(file_content.count(keyword) for keyword in keywords)
        category_counts[item["category"][0]] = count

    # Sort the categories by their counts in descending order
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    if debug:
        print(sorted_categories)

    # 检查出现最多的和次多的差距是否过小，如果过小则认为无法区分
    if len(sorted_categories) > 1 and sorted_categories[0][1] - sorted_categories[1][1] <= math.ceil(sorted_categories[0][1] * gap):
        return "indefinable"
    else:
        if sorted_categories[0][1] <= min_total:
            return "indefinable"
        return sorted_categories[0][0]
    

def process(save_csv_file, read_csv_file, threshold=0.5):
    all_file_df = pd.read_csv(read_csv_file, usecols=['file_path', 'target_path', 'probability'])

    # 将这列的数据类型转化成float
    all_file_df['probability'] = pd.to_numeric(all_file_df['probability'])
    
    positive_df = all_file_df[all_file_df['probability'] > threshold]

    # 读取已经处理完毕的文件原始路径
    existing_files = read_processed_file_path(save_csv_file)
    # 过滤掉已经处理完毕的的数据
    positive_df = positive_df[~positive_df['file_path'].isin(existing_files)]

    with open(save_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['file_path', 'target_path', 'probability', "categorie"]  # 列名
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 如果csv文件为空则将列名写入表头
        if not Path(save_csv_file).stat().st_size:
            writer.writeheader()

        with tqdm(total=positive_df.shape[0]) as pbar:
            for _, row in positive_df.iterrows():
                file_path = Path(row["file_path"])

                # textract不支持Pathlib，所以这里必须要把file_path再次转化成str
                text = extract_text(str(file_path), file_path.suffix)

                categorie = classify_paper_type(text, file_path=file_path)

                row["categorie"] = categorie
            
                writer.writerow(row.to_dict())

                pbar.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--read_csv_file', type=str, required=True, help="'examination_paper_category_classifier.py'所保存的csv路径地址")
    parser.add_argument('--save_csv_file', type=str, default="./category_classifier.csv", help="保存的csv路径地址")
    parser.add_argument('--threshold', default=0.5, type=float, help='因为我们之检测文件是否为试卷是保存的 probabilitity ，此参数为预测试卷的 threshold')

    args = parser.parse_args()

    process(args.save_csv_file, args.read_csv_file, args.threshold)




