import csv
import os
import json
import re
import concurrent.futures

def split_file_contents(file_content):
    # Define the splitting pattern
    pattern = r'\d+\.|一|二|三|四|五|六|七|八|九|十|百|千|万|亿|\.'
    
    # Split the file content based on the pattern
    elements = re.split(pattern, file_content)
    
    return elements

def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        
        # Split the file content into elements
        elements = split_file_contents(file_content)
        
        # Save the elements as JSON lines
        with open("结果.json", 'a', encoding='utf-8') as json_file:
            for element in elements:
                json_object = {'element': element}
                json_line = json.dumps(json_object, ensure_ascii=False)
                json_file.write(json_line + '\n')

def process_rows_with_keywords(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        file_paths = [os.path.join('../clear_data/', row[1].replace(".docx",".md")) for row in reader if row]
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_file, file_paths)

# CSV file path
csv_file = 'rows_with_keywords.csv'

# Process the rows with keywords
process_rows_with_keywords(csv_file)

