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
        doc = word.Documents.Open(os.path.join(DOCX_DIR, fn))
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
        doc.Close(False)

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
