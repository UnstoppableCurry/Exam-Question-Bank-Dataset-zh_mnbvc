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


3.统计文件是否为试卷.
    [复现](./notebook/examination_paper_classifier/train-classifier.md)

    python examination_paper_classifier.py --input_dir="./docx" --csv_path="classifier.csv"
    以上指令会以"./docx"下所有的doc/docx/md文件进行"试卷"以及"试卷类型"的分类，结果会保存到"classifier.csv"中

    options:
    --input_dir 必填项, 输入目录
    --output_dir 输出目录，可不填，不填入代表不进行输出
    --model_url 模型下载链接，有默认值，如果填入，则此模型必须可由 joblib 进行加载
    --threshold 预测阈值，默认0.5，如果 output_dir 未填入，则此参数没有任何作用
    --just_by_file_name 是否仅仅通过文件名(0/1), 默认0
    --csv_path 保存的csv路径，默认"./classifier.csv"
    
    csv列名:
    -- file_path: str, 文件的输入路径
    -- target_path: str, 文件的输出输出路径，如果 output_dir 未填入或者预测值小于 threshold ，此字段等同于 file_path
    -- probability: float|None，模型的预测值
    -- type: str: [公务员|化学|医学|历史|地理|政治|数学|物理|生物|语文|理综|文综|other|None]，如果模型的预测值小于 threshold ，此字段为None

    注意事项*
    - 此脚本仅接受 doc,docx,md 文件
    - 在这个脚本中当提取文件的文本内容较少时，会采用根据文件名检测的策略，在这种情况下csv列名的 probability 为 None

3.1 试卷类型检测（非必要）
    python examination_paper_classifier.py --read_csv_file="./classifier.csv" --save_csv_file="classifier-category.csv" --threshold="0.5"

    此脚本不建议在生产使用，目前大部分类型是由文件路径提供

     options:
    --read_csv_file 必填项, 'examination_paper_category_classifier.py'所保存的csv路径地址
    --save_csv_file 输出文件，保存的csv路径地址
    --threshold 预测阈值，默认0.5，因为我们之检测文件是否为试卷是保存的 probabilitity ，此参数为预测试卷的 threshold

4.统计为试卷的文件中是否含有答案

    python 判断是否有答案.py
    output_csv_with_answers = 'rows_with_answers.csv' #含有答案的
    output_csv_without_answers = 'rows_without_answers.csv' #不含有答案的

5.含有答案的试卷进行切分-对齐尝试

    python 有答案试卷切分-对齐.py
     csv_file = 'rows_with_keywords.csv' #结果输出到 rows_with_keywords.csv

