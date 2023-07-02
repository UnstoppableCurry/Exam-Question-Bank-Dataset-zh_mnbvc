import sys
import subprocess
from pathlib import Path
import shutil

def process_files(folder_path, output_folder_path):
    folder_path = Path(folder_path)
    output_folder_path = Path(output_folder_path)
    output_folder_path.mkdir(exist_ok=True)

    success_count = 0
    failed_files = []

    for file in folder_path.glob('*.*'):
        if file.suffix in ['.doc', '.docx']:
            try:
                md_file = output_folder_path / file.with_suffix('.md').name
                subprocess.check_call(['pandoc', '-s', str(file), '-o', str(md_file)])
                success_count += 1
            except Exception as e:
                print(f"Error processing {file}: {e}")
                failed_files.append(file)

    return success_count, failed_files

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python process_doc_files.py <input_folder_path> <output_folder_path>")
        sys.exit(1)

    success_count, failed_files = process_files(sys.argv[1], sys.argv[2])

    print(f"Successfully converted {success_count} files.")
    print(f"Failed to convert {len(failed_files)} files:")
    for file in failed_files:
        print(f"  - {file}")
