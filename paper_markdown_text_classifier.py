from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import joblib
import re
import jieba
import argparse
import os
import glob
from pathlib import Path


def remove_image_string(input_string):
    pattern = r"!\[(.*?)\]\(.*?\)\{width=\".*?\" height=\".*?\"\}|!\[.*?\]\(.*?\)|\[.*?\]\{.*?\}"
    result = re.sub(pattern, "", input_string)
    return result


def remove_noise_character(input_string):
    pattern = r"[>*|image|data|media|png]"
    
    return re.sub(pattern, "", input_string)


def one_text_pre_process(text):
    precessed_text_split_lines = []
    
    for line in text.splitlines():
        remove_image_line = remove_image_string(line)

        if remove_image_line.strip() in ["", ">"]:
            continue

        remove_image_line = remove_noise_character(remove_image_line)
        precessed_text_split_lines.append(remove_image_line)
        
    return "\n".join(precessed_text_split_lines)


def pre_process(text_list):
    precessed_text_list = [one_text_pre_process(text) for text in text_list]
    return precessed_text_list


def dataset_map_pre_process(row):
    row["text"] = one_text_pre_process(row["text"])
    return row


def chinese_tokenizer(text):
    tokens = jieba.cut(text)
    return list(tokens)


def predict_with_threshold(model, X, threshold=0.9):
    probabilities = model.predict_proba(X)
    positive_probabilities = probabilities[:, 1]
    predictions = (positive_probabilities > threshold).astype(int)
    return predictions

def change_last_folder_name(path, new_folder_name):
    folders = path.split('/')
    last_folder = folders[-1]
    new_path = path.replace(last_folder, new_folder_name)
    return new_path

def get_file_content(file_local):
    with open(file_local, "r") as f:
        return f.read()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder_path', type=str, help='需要检查的文件目录')
    parser.add_argument('--save_folder', default=None, type=str, help='保存文件的目录')
    parser.add_argument('--save_other_file', default=0, type=int, help='是否保存非试卷的其他文件')
    parser.add_argument('--other_file_save_folder', default=None, type=str, help='不是试卷的其他文件保存文件的目录')


    args = parser.parse_args()

    folder_path = args.folder_path
    save_folder = args.save_folder
    other_file_save_folder = args.other_file_save_folder
    is_save_other_file = args.save_other_file


    if not folder_path:
        raise ValueError("--folder_path argument need input")

    if not save_folder:
        save_folder = change_last_folder_name(folder_path, "examination_paper")
        Path(save_folder).mkdir()
        
    if is_save_other_file and not other_file_save_folder:
        other_file_save_folder = change_last_folder_name(folder_path, "not_examination_paper")
        Path(other_file_save_folder).mkdir()

    model = joblib.load("./notebook/TextClassifier-new-13m.pkl")

    raw_text_data_list = []
    file_name_list = []


    for file_local in glob.glob(folder_path + '/' + "*.md"):
        file_content = get_file_content(file_local)
        raw_text_data_list.append(file_content)
        file_name_list.append(file_local.split('/')[-1])


    text_data_list = pre_process(raw_text_data_list)
    predictions = predict_with_threshold(model, text_data_list)

    for index, prediction in enumerate(predictions):
        if not prediction and not is_save_other_file:
            continue

        file_save_folder = save_folder

        if not prediction and is_save_other_file:
            file_save_folder = other_file_save_folder

        save_local = os.path.join(save_folder, file_name_list[index])

        with open(save_local, "w") as f:
            f.write(raw_text_data_list[index])
        
            

