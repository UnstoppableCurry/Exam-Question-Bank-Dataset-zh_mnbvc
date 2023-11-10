import json
from collections import Counter
import matplotlib.pyplot as plt
from pathlib import Path
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True)

    args = parser.parse_args()

    input_path = Path(args.input_file)

    # 初始化计数器
    no_question_with_answer = 0
    no_answer_with_question = 0
    json_count=0
    picture_count = Counter()

    with open(input_path, 'r', encoding='utf-8') as file:
        for line in file:
            json_count += 1
            json_object = json.loads(line)
            len_question = len(json_object['question'])
            len_answer = len(json_object['answer'])
            if len_question == 0 and len_answer > 0:
                no_question_with_answer += 1
            elif len_question > 0 and len_answer == 0:
                no_answer_with_question += 1
            value = json_object['detail_data']['pic_count']
            if value is not None:
                picture_count[value] += 1

    plt.bar(picture_count.keys(), picture_count.values())
    plt.xlabel('num')
    plt.ylabel('count')
    plt.title(f'distribution of pic_num')
    plt.xticks(rotation=45)
    plt.show()


    categories = ['no question', 'no answer', 'all']
    values = [no_question_with_answer, no_answer_with_question, json_count]
    # 创建柱状图
    plt.bar(categories, values)

    # 添加标题和轴标签
    plt.title('analysis of batch')
    plt.xlabel('type')
    plt.ylabel('num')

    # 显示图表
    plt.show()