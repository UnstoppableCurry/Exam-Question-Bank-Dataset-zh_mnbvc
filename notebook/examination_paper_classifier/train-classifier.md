# 复现试卷分类

## 结构

### 训练说明
测试数据：https://pan.baidu.com/s/12sc5oqNr3KU1_x6c9mcNuA?pwd=x93b 
这份数据中存在1w左右的试卷

### create_datasets.ipynb
创建训练集
最终训练集:https://huggingface.co/datasets/ranWang/test_paper_textClassifier

### train_examination_paper_classifier.ipynb
训练模型的 notebook
最终训练出来的模型:https://huggingface.co/datasets/ranWang/test_paper_textClassifier/blob/main/TextClassifie-full-final.pkl

使用此模型在 examination_paper_classifier.py 脚本中预测[训练说明中的文件](#训练说明)的试卷总数为10400