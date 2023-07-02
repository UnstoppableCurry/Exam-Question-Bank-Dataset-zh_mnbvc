import csv
import re
import os

def check_keywords_in_row(row, keywords):
    file_path = row[0]
    if any(keyword in file_path for keyword in keywords):
        return True
    return False

def check_keywords_in_file(file_path, keywords):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_text = file.read()
        if any(keyword in file_text for keyword in keywords):
            return True
    return False

def process_rows_with_keywords(csv_file, keywords, output_csv_with_answers, output_csv_without_answers):
    rows_with_answers = []
    rows_without_answers = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 确保行不为空
                if check_keywords_in_row(row, keywords):
                    rows_with_answers.append(row)
                else:
                    file_path = os.path.join('../clear_data/', row[1])
                    if os.path.exists(file_path) and check_keywords_in_file(file_path, keywords):
                        rows_with_answers.append(row)
                    else:
                        rows_without_answers.append(row)

    with open(output_csv_with_answers, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows_with_answers)

    with open(output_csv_without_answers, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows_without_answers)

    print(f"Rows with answers saved to '{output_csv_with_answers}' successfully.")
    print(f"Rows without answers saved to '{output_csv_without_answers}' successfully.")

# CSV文件路径
csv_file = 'rows_with_keywords.csv'

# 关键字列表
keywords = ['答', '解', '解析', '答案']

# 输出CSV文件路径
output_csv_with_answers = 'rows_with_answers.csv'
output_csv_without_answers = 'rows_without_answers.csv'

# 处理含有关键字的行
process_rows_with_keywords(csv_file, keywords, output_csv_with_answers, output_csv_without_answers)

