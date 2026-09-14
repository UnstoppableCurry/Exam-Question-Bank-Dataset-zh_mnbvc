import os
import shutil

# 定义要处理的文件夹路径
folder_path = ""

# 定义子文件夹的名称
math_folder = 'math fold'


# 创建子文件夹
os.makedirs(os.path.join(folder_path, math_folder), exist_ok=True)
keywords = ['数', '奥数','形', '概率','方程', '加', '减', '乘', '除', '指数', '图', '度','弧','等式','线','计算']

# 列出文件夹中的所有文件
for filename in os.listdir(folder_path):
    if any(keyword in filename for keyword in keywords):
        # 移动文件到数学文件夹下
        shutil.move(os.path.join(folder_path, filename), os.path.join(folder_path, math_folder, filename))
