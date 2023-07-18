这份代码主要用于对文本数据进行分类。下面是关于该代码的详细说明。

## 依赖库

代码主要使用了以下Python库：

- joblib: 用于模型的保存和加载
- re: 用于正则表达式操作，移除或替换字符串中的特定模式
- jieba: 中文分词库，用于将句子分解为单个词语
- argparse: 用于从命令行解析参数
- os 和 glob: 用于处理文件和文件路径
- pathlib: 用于创建和管理文件路径
- requests: 下载模型
- pypandoc
- python-docx

## 主要功能

### 文本清洗

该代码定义了多个函数来清洗文本。主要的清洗步骤包括：

- 移除图片字符串（`remove_image_string`函数）
- 移除噪声字符（`remove_noise_character`函数）
- 对文本进行分词（`chinese_tokenizer`函数）

### 模型预测

`predict_with_threshold`函数用于对新的文本数据进行预测。


### 命令行参数解析

该代码还提供了命令行参数解析功能，通过`argparse`库实现。命令行参数主要包括输入目录、输出目录和模型文件的路径。

## 使用方式

在命令行中运行该代码，并按照参数提示输入相应的文件路径。例如：

```
python paper_markdown_text_classifier.py --input_dir='./docx' --output_dir='./examination_paper'
```

这会使用`./docx`目录中所有markdown文件作为输入数据，`./examination_paper`作为输出目录，并且这个目录中只存在预测是"试卷"类型的文件



usage: paper_markdown_text_classifier.py [-h] [--input_dir INPUT_DIR] [--output_dir OUTPUT_DIR] [--model_url MODEL_URL]
                                         [--threshold THRESHOLD]

options:
  --input_dir INPUT_DIR
                        输入目录
  --output_dir OUTPUT_DIR
                        输出目录
  --model_url MODEL_URL
                        模型下载链接
  --threshold THRESHOLD
                        预测阈值
                        默认0.5（调高效果也一样）

