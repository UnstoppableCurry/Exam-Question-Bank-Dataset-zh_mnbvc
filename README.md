# Exam-Question-Bank-Dataset-zh
通用考试题库数据集  选择 填空 简答
# 处理流程
1.格式转换 所有.doc 转为.docx 格式

2.格式对齐 所有.docx文件 转为markdown格式 文件中的图片公式等需要解码的统一存在资源文件夹内

3.统计文件是否为试卷

4.统计试卷中是否还有答案

5.有答案的试卷进行切分-对齐

# 代码使用

1.centos 系统下,解压xxx.zip 数据集， 解压含有中文字符的文件会乱码。请使用zip2.py
 python zip2.py
    zip_file_path = '../docx_math.zip'  # 替换为你的 zip 文件路径
    dest_path = '../docx_math'  # 替换为你想解压到的目标文件夹路径
    index_csv_path = 'index_to_filename.csv'  # 替换为你想存储索引到文件名映射的 CSV 文件路径


2.将所有.docx 文件转为 markdown格式  静态资源保存在静态文件夹
 python docx2markdown2.py  
     
    docx_folder = r'/www/dataset/MNBVC/docx_math' 
    markdown_folder = r'/www/dataset/MNBVC/clear_data'  # 存放.md文件的文件夹路径
    image_folder ="/www/dataset/MNBVC/image_folder"

3.

1.docx, doc, word to text (pandoc)  使用规则对word文档进行每道题-答案的切分

2.question segmentation, alignment
