from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import joblib
import datasets
import re
import jieba
import argparse
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os

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



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder_path', type=str, help='需要检查的文件目录')
    parser.add_argument('--save_folder', type=str, help='保存文件的目录')

    args = parser.parse_args()

    folder_path = args.folder_path
    save_folder = args.folder_path

    test_paper_file_save_folder = os.path.join(save_folder, "test_paper")
    other_filer_save_folder = os.path.join(save_folder, "other")

    if not folder_path:
        raise ValueError("--folder_path argument need input")

    model = joblib.load("./notebook/TextClassifier-new-13m.pkl")

    raw_text_data_list = []
    file_name_list = []
    for file_name in folder_path:
        with open(file_name, "r") as f:
            raw_text_data_list.append(f.read())
            file_name_list.append(file_name)


    text_data_list = pre_process(raw_text_data_list)
    predictions = predict_with_threshold(model, text_data_list)

    for index, prediction in enumerate(predictions):
        save_folder = test_paper_file_save_folder

        if not prediction:
            save_folder = other_filer_save_folder

        save_local = os.path.join(save_folder, file_name_list[index])

        with open(save_local, "w") as f:
            f.write(raw_text_data_list[index])
        
            

