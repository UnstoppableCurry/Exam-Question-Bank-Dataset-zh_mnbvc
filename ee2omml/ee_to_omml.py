import argparse
import logging as log
import os
import time
from threading import Thread
import psutil
import pywinauto.keyboard
import pywinauto.mouse
import pywintypes
import tqdm
import win32com.client as win32
from pywinauto.application import Application
from win32com.client import constants
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


def get_word_process_id():
    """
    获取word的进程id
    Returns:
         int | None: word的pid
    """
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == 'WINWORD.EXE':
            return process.info['pid']
    return None


def dialog_handle(top_win):
    """
    转换公式对话框的点击处理
    Args:
        top_win: word顶层窗口对象
    """
    while True:
        time.sleep(0.5)
        try:
            checkbox = top_win.child_window(title_re=u'.*适用于所有公式', control_type="CheckBox")
            # 检查转换弹窗是否存在
            if checkbox.exists():
                checkbox.set_focus()
                pywinauto.keyboard.send_keys("{SPACE}")
                pywinauto.keyboard.send_keys("%y")
        except:
            continue


def create_md_file(docx_file):

    base_name = os.path.basename(docx_file)  # 获取文件名，包括扩展名
    file_name_without_extension = os.path.splitext(base_name)[0]  # 获取文件名，不带扩展名


    md_file_path = os.path.join(os.path.dirname(docx_file), '..', SAVE_DIR, file_name_without_extension + '.md')
    md_file_path = os.path.normpath(md_file_path)  # 标准化路径
    # 创建一个空的MD文件
    with open(md_file_path, 'w') as file:
        pass

    return md_file_path


def convert_docx_to_md(docx_file):
    md_file = create_md_file(docx_file)
    try:
        # 偷懒用了pandoc临时的位置，可以选择添加进path里
        subprocess.run(["C:\\Users\\Zhipeng\\AppData\\Local\\Pandoc\\pandoc.exe", docx_file, '-o', md_file], check=True)
        print(f"{docx_file} has been successfully converted to {md_file}")
    except subprocess.CalledProcessError:
        print("Pandoc conversion failed!")


    # # 文件路径
    # directory = os.path.dirname(md_file)
    #
    # with open(md_file, 'r', encoding='utf-8') as file:
    #     content = file.read()
    #     count = content.count('media')
    #
    # # 如果 "media" 的出现次数超过10
    # if count > 10:
    #     # 如果 "allpicture" 文件夹不存在，创建它
    #     allpicture_dir = os.path.join(directory, 'allpicture')
    #     if not os.path.exists(allpicture_dir):
    #         os.mkdir(allpicture_dir)
    #
    #     # 移动.md文件到 "allpicture" 文件夹
    #     shutil.move(md_file, allpicture_dir)
    #     shutil.move(docx_file, allpicture_dir)




if __name__ == '__main__':

    file_list = set(os.listdir(DOCX_DIR)) - set(os.listdir(SAVE_DIR))

    # 创建Word应用程序对象 and 显示窗口
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = True

    app = Application('uia').connect(process=get_word_process_id())

    # 启动一个守护线程在后台执行转换对话的点击动作
    dialog_handle_task = Thread(target=dialog_handle, args=(app.top_window(),))
    dialog_handle_task.setDaemon(True)
    dialog_handle_task.start()

    for fn in tqdm.tqdm(file_list, total=len(file_list)):
        # 打开Word文档
        try:
            doc = word.Documents.Open(os.path.join(DOCX_DIR, fn))
            # 其他处理文档的代码...
        except Exception as e:  # 捕获所有异常，也可以针对具体的异常进行捕获，如com_errors
            log.error(f"Error opening {fn}: {str(e)}")
            continue
        doc.Activate()
        # 旧版本公式在新版本word中会
        shapes = doc.InlineShapes

        # 检测公式
        for shape in shapes:
            if shape.Type == 1:
                try:
                    # 执行《全选文档》宏，需要手动打开word添加宏
                    word.Application.Run('SelectEntireDocument')
                    # 转换弹窗
                    shape.OLEFormat.DoVerb(0)
                except pywintypes.com_error as e:
                    # 预留出公式转换等待时长
                    time.sleep(8)
                    break
        # 保存文件
        word.ActiveDocument.SaveAs(os.path.join(SAVE_DIR, fn), FileFormat=constants.wdFormatXMLDocument)
        time.sleep(1)
        doc.Close(False)
        convert_docx_to_md(os.path.join(SAVE_DIR, fn))

    word.Quit()

# TODO: 添加全局宏，无权限异常 - pywintypes.com_error: (-2147352567, '发生意外。', (0, 'Microsoft Word',
#  '到 Visual Basic Project 的程序访问不被信任。', 'wdmain11.chm', 25548, -2146822220), None)
#   ----------------------------------------------------------------------------------------------
#   获取全局模板
#   global_template = word.NormalTemplate
#   VBA宏代码 - 全选文档
#   macro_code = '''\
#   Sub SelectEntireDocument()
#     Selection.WholeStory
#   End Sub'''
#   global_template.VBProject.VBComponents('ThisDocument').CodeModule.AddFromString(macro_code)