import joblib
import re
import jieba
import argparse
import os   
import glob
from pathlib import Path
import requests
from tqdm import tqdm


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


def download_model(*,model_name, download_url):
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




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder_path', type=str, help='需要检查的文件目录')
    parser.add_argument('--save_folder', default=None, type=str, help='保存文件的目录')
    parser.add_argument('--save_other_file', default=0, type=int, help='是否保存非试卷的其他文件')
    parser.add_argument('--other_file_save_folder', default=None, type=str, help='不是试卷的其他文件保存文件的目录')
    parser.add_argument('--model_url', default="https://huggingface.co/datasets/ranWang/test_paper_textClassifier/blob/main/TextClassifier-13m.pkl", type=str, help='模型下载链接')
    parser.add_argument('--threshold', default=0.5, type=float, help='预测阈值')
    
    args = parser.parse_args()

    folder_path = args.folder_path
    save_folder = args.save_folder
    other_file_save_folder = args.other_file_save_folder
    is_save_other_file = args.save_other_file
    model_url = args.model_url
    threshold = args.threshold

    if not folder_path:
        raise ValueError("--folder_path argument need input")

    if not save_folder:
        save_folder = change_last_folder_name(folder_path, "examination_paper")
        
    Path(save_folder).mkdir()
        
    if is_save_other_file and not other_file_save_folder:
        other_file_save_folder = change_last_folder_name(folder_path, "not_examination_paper")
        Path(other_file_save_folder).mkdir()

    model_file_name = "TextClassifier.pkl"

    download_model(model_name=model_file_name, download_url=model_url)
    model = joblib.load(model_file_name)


    raw_text_data_list = []
    file_name_list = []

    for file_local in glob.glob(folder_path + '/' + "*.md"):
        file_content = get_file_content(file_local)
        raw_text_data_list.append(file_content)
        file_name_list.append(file_local.split('/')[-1])


    text_data_list = pre_process(raw_text_data_list)
    predictions = predict_with_threshold(model, text_data_list, threshold)
    
    for index, prediction in enumerate(predictions):
        # 如果选择不保存其他文件，并且预测文件类型结果为"其他"
        if not prediction and not is_save_other_file:
            continue

        file_save_folder = save_folder

        if not prediction and is_save_other_file:
            file_save_folder = other_file_save_folder

        save_local = os.path.join(file_save_folder, file_name_list[index])

        with open(save_local, "w") as f:
            f.write(raw_text_data_list[index])
        
            

