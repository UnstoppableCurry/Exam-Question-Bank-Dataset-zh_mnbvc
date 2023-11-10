import os
import argparse
import logging as log
import subprocess
import shutil
log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s (%(funcName)s:%(lineno)d) - %(message)s')

# 命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('docx_dir', type=str, help='未处理的文件所在目录绝对路径')
parser.add_argument('save_dir', type=str, help='处理后的文件保存目录绝对路径')
args = parser.parse_args()

DOCX_DIR = args.docx_dir
SAVE_DIR = args.save_dir

if not os.path.isdir(SAVE_DIR):
    os.makedirs(SAVE_DIR)

log.info('源文件目录：' + DOCX_DIR)
log.info('保存目录：' + SAVE_DIR)
def create_md_file(docx_file):

    base_name = os.path.basename(docx_file)  # 获取文件名，包括扩展名
    file_name_without_extension = os.path.splitext(base_name)[0]  # 获取文件名，不带扩展名


    md_file_path = os.path.join(os.path.dirname(docx_file), '../..', SAVE_DIR, file_name_without_extension + '.md')
    md_file_path = os.path.normpath(md_file_path)  # 标准化路径
    # 创建一个空的MD文件
    with open(md_file_path, 'w') as file:
        pass

    return md_file_path


def convert_docx_to_md_and_count(docx_file):
    md_file = create_md_file(docx_file)
    try:
        # 偷懒用了pandoc临时的位置，可以选择添加进path里
        subprocess.run(["your\\path\\to\\pandoc.exe", docx_file, '-o', md_file], check=True)
        print(f"{docx_file} has been successfully converted to {md_file}")
    except subprocess.CalledProcessError:
        print("Pandoc conversion failed!")

    directory = os.path.dirname(md_file)

    with open(md_file, 'r', encoding='utf-8') as file:
        content = file.read()
        count = content.count('media')

    # 如果 "media" 的出现次数超过10
    if count > 10:

        picture10_dir = os.path.join(directory, 'picture10')
        if not os.path.exists(picture10_dir):
            os.mkdir(picture10_dir)

        shutil.move(md_file, picture10_dir)
        shutil.move(docx_file, picture10_dir)


if __name__ == '__main__':
    #对文档进行区分，将图片数量较多的单独清出来
    file_list = set(os.listdir(DOCX_DIR)) - set(os.listdir(SAVE_DIR))
    for fn in file_list:
        convert_docx_to_md_and_count(os.path.join(DOCX_DIR, fn))