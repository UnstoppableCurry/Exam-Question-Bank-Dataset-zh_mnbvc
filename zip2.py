import zipfile
import os
import csv
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_file(zf, info, target_path, lock):
    with zf.open(info, 'r') as file, open(target_path, 'wb') as target:
        target.write(file.read())

    with lock:
        print(f"解压完成: {target_path}")

def unzip_file_with_original_format(zip_file_path, dest_path, index_csv_path, encoding='cp437', max_workers=5):
    with zipfile.ZipFile(zip_file_path, 'r') as zf:
        # 创建 CSV 文件并写入文件名映射
        with open(index_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['original_filename', 'new_filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # 使用多线程解压文件
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                lock = threading.Lock()
                futures = []

                for index, info in enumerate(zf.infolist()):
                    decoded_filepath = info.filename.encode('cp437').decode(encoding)
                    target_filename = f"{index}.docx"
                    target_path = os.path.join(dest_path, target_filename)

                    # 如果是目录，跳过创建文件
                    if target_path.endswith('/'):
                        continue

                    # 如果是文件，先创建所在目录
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)

                    # 提交解压任务到线程池
                    future = executor.submit(extract_file, zf, info, target_path, lock)
                    futures.append(future)

                    # 将原始文件名和新文件名写入 CSV 文件
                    writer.writerow({'original_filename': decoded_filepath, 'new_filename': target_filename})

                # 等待所有任务完成
                for future in as_completed(futures):
                    future.result()

if __name__ == "__main__":
    zip_file_path = '../docx_math.zip'  # 替换为你的 zip 文件路径
    dest_path = '../docx_math'  # 替换为你想解压到的目标文件夹路径
    index_csv_path = 'index_to_filename.csv'  # 替换为你想存储索引到文件名映射的 CSV 文件路径
    unzip_file_with_original_format(zip_file_path, dest_path, index_csv_path, encoding='gbk')

