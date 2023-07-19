import joblib
import re
import jieba
import argparse
import os   
import glob
import requests
from tqdm import tqdm
import shutil
from docx import Document
from pathlib import Path

def remove_image_string(input_string):
    """
    从输入字符串中移除图片字符串。
    
    参数:
    input_string (str): 原始字符串。
    
    返回:
    result (str): 移除图片字符串后的结果。
    """
    pattern = r"!\[(.*?)\]\(.*?\)\{width=\".*?\" height=\".*?\"\}|!\[.*?\]\(.*?\)|\[.*?\]\{.*?\}"
    result = re.sub(pattern, "", input_string)
    return result


def remove_noise_character(input_string):
    """
    从输入字符串中移除噪声字符。
    
    参数:
    input_string (str): 原始字符串。
    
    返回:
    result (str): 移除噪声字符后的结果。
    """
    pattern = r"[>*|image|data|media|png]"
    return re.sub(pattern, "", input_string)


def one_text_pre_process(text):
    """
    对单个文本进行预处理。
    
    参数:
    text (str): 需要预处理的文本。
    
    返回:
    precessed_text_split_lines (str): 预处理后的文本。
    """
    precessed_text_split_lines = []
    
    for line in text.splitlines():
        remove_image_line = remove_image_string(line)

        if remove_image_line.strip() in ["", ">"]:
            continue

        remove_image_line = remove_noise_character(remove_image_line)
        precessed_text_split_lines.append(remove_image_line)
        
    return "\n".join(precessed_text_split_lines)


def pre_process(text_list):
    """
    对文本列表进行预处理。
    
    参数:
    text_list (list): 需要预处理的文本列表。
    
    返回:
    precessed_text_list (list): 预处理后的文本列表。
    """
    precessed_text_list = [one_text_pre_process(text) for text in text_list]
    return precessed_text_list


def dataset_map_pre_process(row):
    """
    对数据集的一行进行预处理。
    
    参数:
    row (dict): 需要预处理的数据行，字典形式。
    
    返回:
    row (dict): 预处理后的数据行，字典形式。
    """
    row["text"] = one_text_pre_process(row["text"])
    return row


def chinese_tokenizer(text):
    """
    对中文文本进行分词。
    
    参数:
    text (str): 需要分词的文本。
    
    返回:
    tokens (list): 分词后的词语列表。
    """
    tokens = jieba.cut(text)
    return list(tokens)


def predict_with_threshold(model, X, threshold=0.5):
    """
    对模型进行带阈值的预测。
    
    参数:
    model (object): 需要预测的模型。
    X (array-like): 需要预测的数据。
    threshold (float): 预测阈值，默认为0.9。
    
    返回:
    predictions (array-like): 预测结果。
    """
    probabilities = model.predict_proba(X)
    positive_probabilities = probabilities[:, 1]
    predictions = (positive_probabilities > threshold).astype(int)
    return predictions


def change_last_folder_name(path, new_folder_name):
    """
    修改路径中的最后一个文件夹名。
    
    参数:
    path (str): 原始路径。
    new_folder_name (str): 新的文件夹名。
    
    返回:
    new_path (str): 修改后的路径。
    """
    folders = path.split('/')
    last_folder = folders[-1]
    new_path = path.replace(last_folder, new_folder_name)
    return new_path


def get_file_content(file_local):
    """
    获取文件内容。
    
    参数:
    file_local (str): 文件的本地路径。
    
    返回:
    content (str): 文件内容。
    """
    with open(file_local, "r") as f:
        return f.read()


def download_model(*, model_name, download_url):
    """
    从指定的URL下载模型并使用给定的模型名称保存。

    参数：
        model_name (str): 要下载的模型的名称。
        download_url (str): 要下载模型的URL。
    """

    # 检查模型是否已存在
    if os.path.exists(model_name):
        return

    temp_model_name = model_name + ".tmp"

    # 检查是否存在临时模型文件
    if os.path.exists(temp_model_name):
        initial_position = os.path.getsize(temp_model_name)
    else:
        initial_position = 0

    try:
        # 设置请求头部信息，用于断点续传
        headers = {'Range': f'bytes={initial_position}-'}
        response = requests.get(download_url, headers=headers, stream=True)

        # 检查响应的状态码
        response.raise_for_status()

        # 从响应头部信息获取总文件大小
        total_size = int(response.headers.get('content-range').split('/')[1])

        # 创建进度条并设置初始值为已下载的文件大小
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, initial=initial_position)

        with open(temp_model_name, 'ab') as f:
            for data in response.iter_content(chunk_size=1024):
                progress_bar.update(len(data))
                f.write(data)

        progress_bar.close()

        # 检查下载是否完成
        if total_size != 0 and progress_bar.n != total_size:
            print("错误：下载过程中出现问题。")

        # 将临时模型文件重命名为指定的模型名称
        os.rename(temp_model_name, model_name)
    except:
        # 如果出现异常，抛出异常并中断下载过程
        raise


def extract_text_from_docx(file_path):
    """
    解析一个docx中的文字，没有图片标签等噪点
    """
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + ' '
    return text


def detect_language(text):
    """
    解析一段文字是否为中文
    """
    chinese_count = 0
    english_count = 0
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            chinese_count += 1
        elif 'a' <= char.lower() <= 'z':
            english_count += 1
            
    if chinese_count > english_count:
        return 'Chinese'
    elif english_count > chinese_count:
        return 'English'
    else:
        return 'Unknown'


def move_files(input_dir, output_dir, threshold, model):
    if os.path.exists(input_dir) == False:
        raise ValueError('输入目录不存在')
    if os.path.abspath(input_dir) == os.path.abspath(output_dir):
        raise ValueError('输入目录和输出目录不能相同')

    os.makedirs(output_dir, exist_ok=True)
    
    # 文件名后缀
    file_pattern = ".docx"
    
    # 遍历一个文件夹下所有docx文件
    for root, _, files in os.walk(input_dir):
        for file in files:
            
            if not file.endswith(file_pattern):
                continue

            file_local = os.path.join(root, file)

            # widnwos下的目录和ubuntu不一样
            if "\\" in file_local:
                file_local = file_local.replace("\\","/")

            target_dir = os.path.join(output_dir, os.path.relpath(root, input_dir))
            target_file = os.path.join(target_dir, file_local.split("/")[-1])

            if os.path.exists(target_file):
                continue
   
            try:
                # 存在一些无法解析的字符集的文件会报错
                docx_text = extract_text_from_docx(file_local)
                # 如果不是中文
                if detect_language(docx_text) != "Chinese":
                    print("1")
                    continue
            except: 
                continue

            # 一个和多个文件速度没差
            predict = predict_with_threshold(model, [one_text_pre_process(docx_text)], threshold)[0]

            # 0/1 => False/True
            if predict:
                Path(target_dir).mkdir(exist_ok=True)
                shutil.copy(file_local, target_file)

            # print(f"{file_local} success")
   

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True, help="输入目录")
    parser.add_argument('--output_dir', type=str, required=True, help="输出目录")
    parser.add_argument('--model_url', default="https://huggingface.co/datasets/ranWang/test_paper_textClassifier/resolve/main/TextClassifier-13m.pkl", type=str, help='模型下载链接')
    parser.add_argument('--threshold', default=0.5, type=float, help='预测阈值')
    
    args = parser.parse_args()

    model_file_name = "TextClassifier.pkl"
    download_model(model_name=model_file_name, download_url=args.model_url)
    model = joblib.load(model_file_name)
    
    move_files(args.input_dir, args.output_dir, args.threshold, model)



            

