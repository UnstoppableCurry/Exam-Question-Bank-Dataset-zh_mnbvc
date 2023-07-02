import os
import concurrent.futures
import pypandoc

def convert_docx_to_markdown(docx_file, markdown_folder, image_folder):
    try:
        # 构建Markdown文件名
        docx_filename = os.path.basename(docx_file)
        markdown_filename = os.path.splitext(docx_filename)[0] + ".md"
        markdown_file = os.path.join(markdown_folder, markdown_filename)

        # 创建图片文件夹
        os.makedirs(image_folder, exist_ok=True)

        # 配置Pandoc选项，将图片保存到指定的文件夹中
        pandoc_options = [
            f"--extract-media={image_folder}",
            "--wrap=none",
        ]

        # 使用pypandoc将.docx文件转换为Markdown，并使用外部图片链接
        output = pypandoc.convert_file(docx_file, 'md', extra_args=pandoc_options)

        # 将转换后的Markdown写入.md文件
        with open(markdown_file, 'w', encoding='utf-8') as file:
            file.write(output)

        print(f"转换完成：{docx_file} -> {markdown_file}")

    except Exception as e:
        print(f"转换错误：{docx_file} -> {e}")

def convert_docx_folder(docx_folder, markdown_folder, image_folder):
    # 获取.docx文件列表
    docx_files = [file for file in os.listdir(docx_folder) if file.endswith(".docx")]

    total_files = len(docx_files)
    completed_files = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交任务给线程池进行并行处理
        futures = []
        for docx_file in docx_files:
            docx_path = os.path.join(docx_folder, docx_file)
            future = executor.submit(convert_docx_to_markdown, docx_path, markdown_folder, image_folder)
            futures.append(future)

        # 获取任务的进度
        for future in concurrent.futures.as_completed(futures):
            completed_files += 1
            print(f"进度：{completed_files}/{total_files}")

# 调用函数进行转换

docx_folder = r'/www/dataset/MNBVC/docx_math' 
markdown_folder = r'/www/dataset/MNBVC/clear_data'  # 存放.md文件的文件夹路径
image_folder ="/www/dataset/MNBVC/image_folder"
convert_docx_folder(docx_folder, markdown_folder, image_folder)

