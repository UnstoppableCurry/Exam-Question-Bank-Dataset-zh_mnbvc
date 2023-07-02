import os

# 将中文部分替换为你想要的文件路径。
filepath = r'/www/dataset/MNBVC/docx_math/'
destination_path = r'/www/dataset/MNBVC/clear_data/'

# 检查转换后文件所在文件夹是否存在，不存在则创建。
if os.path.exists(destination_path):
    pass
else:
    os.makedirs(destination_path)

# os.listdir 命令列出待转换文件所在文件夹中所有文件的名称，包含 .xxx 后缀
file_names = os.listdir(filepath)

for file_name in file_names:

    # .rfind('.')，从左往右直到最后一个 . 的位置。
    index = file_name.rfind('.')

    # index == -1 即不存在 . 符号。
    if index != -1:

        # 将不带后缀的文件名储存到另一变量中。
        file_name_nosuffix = file_name[:index]

        # os.system 命令调用系统命令行。Linux 和 Mac 可能需要将 \ 替换为 /.
        os.system(f'pandoc {filepath}\{file_name} -f docx -t markdown -s -o {destination_path}\{file_name_nosuffix}.md')
