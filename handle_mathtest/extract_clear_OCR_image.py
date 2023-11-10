import zipfile
import os
def extract_and_rename_media(docx_path, output_folder):
    # Get the base name of the DOCX file (without the extension)
    docx_base_name = os.path.splitext(os.path.basename(docx_path))[0]

    # Create a specific output folder for this DOCX file
    docx_output_folder = os.path.join(output_folder, docx_base_name)
    if not os.path.exists(docx_output_folder):
        os.makedirs(docx_output_folder)

    # Open the DOCX file as a ZIP archive
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        # List all the files in the archive
        file_list = docx_zip.namelist()

        # Filter out the files in the 'word/media/' folder
        media_files = [f for f in file_list if f.startswith('word/media/')]

        # Extract and rename media files
        for idx, media_file in enumerate(media_files, start=1):
            # Create a new name for the media file
            _, extension = os.path.splitext(media_file)
            new_name = f"{docx_base_name}_image{idx}{extension}"
            new_path = os.path.join(docx_output_folder, new_name)

            # Extract and rename the media file
            with docx_zip.open(media_file) as source_file:
                with open(new_path, 'wb') as target_file:
                    target_file.write(source_file.read())

if __name__ == '__main__':
    # 用来解压docx获取文档里的图片
    docx_folder = ''
    output_folder = ''
    for docx_filename in os.listdir(docx_folder):
        if docx_filename.endswith('.docx'):
            docx_path = os.path.join(docx_folder, docx_filename)
            extract_and_rename_media(docx_path, output_folder)
