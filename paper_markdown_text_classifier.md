这份代码主要用于对文本数据进行分类。下面是关于该代码的详细说明。

## 主要功能


### 命令行参数解析

该代码还提供了命令行参数解析功能，通过`argparse`库实现。命令行参数主要包括输入目录、输出目录和模型文件的路径。

## 使用方式

在命令行中运行该代码，并按照参数提示输入相应的文件路径。例如：

```
python paper_markdown_text_classifier.py --input_dir='./docx' --output_dir='./examination_paper'
```

这会使用`./docx`目录中所有markdown文件作为输入数据，`./examination_paper`作为输出目录，并且这个目录中只存在预测是"试卷"类型的文件,
此外在脚本运行目录会出现"move_log.log"和"file_name_classification.log"两个文件，

move_log.log可在notebook/validation_results解析并查看分类的具体情况和使用文件名推断的预测错误
file_name_classification用于标记这些文件中那些是使用文件名来推断的


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

