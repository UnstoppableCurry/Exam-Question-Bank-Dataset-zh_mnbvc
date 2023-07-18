这份代码主要用于对文本数据进行分类。下面是关于该代码的详细说明。

## 依赖库

代码主要使用了以下Python库：

- sklearn: 用于模型训练和预测
- joblib: 用于模型的保存和加载
- re: 用于正则表达式操作，移除或替换字符串中的特定模式
- jieba: 中文分词库，用于将句子分解为单个词语
- argparse: 用于从命令行解析参数
- os 和 glob: 用于处理文件和文件路径
- pathlib: 用于创建和管理文件路径

## 主要功能

### 文本清洗

该代码定义了多个函数来清洗文本。主要的清洗步骤包括：

- 移除图片字符串（`remove_image_string`函数）
- 移除噪声字符（`remove_noise_character`函数）
- 对文本进行分词（`cut_words`函数）

### 模型预测

`predict_with_threshold`函数用于对新的文本数据进行预测。


### 命令行参数解析

该代码还提供了命令行参数解析功能，通过`argparse`库实现。命令行参数主要包括输入文件、输出文件和模型文件的路径。

## 使用方式

在命令行中运行该代码，并按照参数提示输入相应的文件路径。例如：

```
python paper_markdown_text_classifier.py --folder_path='./markdown' --save_folder='./examination_paper_markdone'
```

这会使用`./markdown`目录中所有markdown文件作为输入数据，`./examination_paper_markdone`作为输出目录，并且这个目录中只存在预测是"试卷"类型的md文档。


usage: paper_markdown_text_classifier.py [-h] [--folder_path FOLDER_PATH] [--save_folder SAVE_FOLDER] [--save_other_file SAVE_OTHER_FILE]
                                         [--other_file_save_folder OTHER_FILE_SAVE_FOLDER]

options:
  --folder_path FOLDER_PATH
                        需要检查的文件目录
  --save_folder SAVE_FOLDER
                        保存文件的目录
                        默认：FOLDER_PATH相对路径的examination_paper
  --save_other_file SAVE_OTHER_FILE
                        是否保存非试卷的其他文件 0 or 1
                        默认：0
  --other_file_save_folder OTHER_FILE_SAVE_FOLDER
                        不是试卷的其他文件保存文件的目录
                        默认：FOLDER_PATH相对路径的not_examination_paper