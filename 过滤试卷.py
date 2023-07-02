import csv
import re

def extract_rows_with_keywords(csv_file, keywords):
    rows_with_keywords = []
    rows_without_keywords = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 确保行不为空
                file_path = re.sub(r'[^\w\s-]', '', row[0])  # 去除特殊字符
                file_path = file_path.replace("docx_math", "").replace("docx", "")
                if any(keyword in file_path for keyword in keywords):
                    rows_with_keywords.append(row)
                else:
                    rows_without_keywords.append(row)

    return rows_with_keywords, rows_without_keywords

# CSV文件路径
csv_file = 'index_to_filename.csv'

# 关键字列表
keywords = ['考试', '试卷', '卷', '试题', '试']

# 提取含有关键字和不含关键字的行
rows_with_keywords, rows_without_keywords = extract_rows_with_keywords(csv_file, keywords)

# 保存含有关键字的行到新的CSV文件
output_csv_with_keywords = 'rows_with_keywords.csv'
with open(output_csv_with_keywords, 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows_with_keywords)

print(f"Rows with keywords saved to '{output_csv_with_keywords}' successfully.")

# 保存不含关键字的行到新的CSV文件
output_csv_without_keywords = 'rows_without_keywords.csv'
with open(output_csv_without_keywords, 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows_without_keywords)

print(f"Rows without keywords saved to '{output_csv_without_keywords}' successfully.")

