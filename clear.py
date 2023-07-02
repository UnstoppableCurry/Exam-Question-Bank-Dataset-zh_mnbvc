import os
import docx
import docx2txt

def read_document(file_path, file_extension):
    if file_extension == ".docx":
        text = docx2txt.process(file_path)
    elif file_extension == ".doc":
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text

def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(file)
            file_extension = os.path.splitext(file)[1].lower()

            if file_extension in [".docx", ".doc"]:
                text = read_document(file_path, file_extension)
                print(f"Content of {file_path}:\n{text}\n")
            else:
                print(f"Skipping unsupported file format: {file_path}")

directory_path = "/www/dataset/MNBVC/docx_math"
process_directory(directory_path)
