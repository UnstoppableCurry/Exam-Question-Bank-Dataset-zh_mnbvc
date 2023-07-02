import os

image_folder_list = []
no_image_folder_list = []

# 遍历 clear_data 文件夹
folder_path = '/www/dataset/MNBVC/clear_data'  # 清理后的文件夹路径
for filename in os.listdir(folder_path):
    if filename.endswith('.md'):  # 仅处理 .md 文件
        file_path = os.path.join(folder_path, filename)
        
        # 读取文件内容
        with open(file_path, 'r') as file:
            content = file.read()
        
        # 判断文件内容是否包含 image_folder 字符
        if 'image_folder' in content:
            image_folder_list.append(file_path)
        else:
            no_image_folder_list.append(file_path)

# 统计列表长度
image_folder_count = len(image_folder_list)
no_image_folder_count = len(no_image_folder_list)

# 打印统计结果
print("包含图片的文件列表长度:", image_folder_count)
print("不包含图片的文件列表长度:", no_image_folder_count)

