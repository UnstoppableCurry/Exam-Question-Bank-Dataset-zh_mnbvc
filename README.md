# Exam-Question-Bank-Dataset-zh
通用考试题库数据集  选择 填空 简答
# 处理流程
1.格式转换 所有.doc 转为.docx 格式

2.格式对齐 所有.docx文件 转为markdown格式 文件中的图片公式等需要解码的统一存在资源文件夹内

3.统计文件是否为试卷

4.统计试卷中是否还有答案

5.有答案的试卷进行切分-对齐

# 代码使用
0.环境安装
   
    pip install pypandoc  #centos系统要提前安装好pandoc，pypandoc这个库只是一个封装调用api

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

3.统计文件是否为试卷
  3.1 统计试卷词频分布
  3.2 通过获得词频分布，对文档进行过过滤
    - 一个实例 [paper_markdown_text_classifier](./paper_markdown_text_classifier.md)
                     
    python 统计是否为试卷.py  #打印输出词频获得分布
    
    python 过滤试卷.py  #将结果存储到csv中
    output_csv_with_keywords = 'rows_with_keywords.csv' # 保存含有关键字的行到新的CSV文件
    output_csv_without_keywords = 'rows_without_keywords.csv' # 保存不含关键字的行到新的CSV文件



4.统计为试卷的文件中是否含有答案

    python 判断是否有答案.py
    output_csv_with_answers = 'rows_with_answers.csv' #含有答案的
    output_csv_without_answers = 'rows_without_answers.csv' #不含有答案的

5.含有答案的试卷进行切分-对齐尝试

    python 有答案试卷切分-对齐.py
     csv_file = 'rows_with_keywords.csv' #结果输出到 rows_with_keywords.csv

