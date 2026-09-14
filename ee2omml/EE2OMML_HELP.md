# EE_TO_OMML
旧版本word中的 **ee (equation editor 3.0)** 格式的数学公式转换**omml（Office Math Markup Language)** 格式
# 环境
以下为开发使用版本

| Application | Version |
|-------------|---------|
| python      | 3.11.*  |
| word        | 2016 +  |

# 使用
1. 打开word添加VAB宏，注意宏的位置为**所有文档**

![img.png](images/img.png)
```vba
Sub SelectEntireDocument()
    Selection.WholeStory
End Sub
```
2. 安装依赖
```bash
pip install psutil pywinauto tqdm pywin32
```
3. 执行脚本，输入参数源文档和保存转换后的文件的**目录绝对路径**
```bash
python ee_to_omml.py 'abs_source_dir' 'abs_target_dir'
```
# HELP
```bash
python ee_to_omml.py --help
```