import markdown
from bs4 import BeautifulSoup
import json
import re
import os

def parse_markdown_to_json(markdown_file):
    with open(markdown_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Convert markdown to HTML
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize the JSON structure
    json_data = {
        "title": soup.h1.text if soup.h1 else "Untitled",
        "videos": []
    }
    
    # Find all video sections
    video_sections = soup.find_all('h2', string=re.compile(r'Video \d+[A-Z]:'))
    
    for section in video_sections:
        video = {
            "id": section.text.split(':')[0].split()[-1],
            "url": section.find_next('p').text,
            "content": "",
            "activities": []
        }
        
        # Extract content
        content_elem = section.find_next('p', string=True)
        if content_elem:
            video["content"] = content_elem.text
        
        # Extract activities
        activity_elem = content_elem.find_next_sibling()
        while activity_elem and activity_elem.name != 'h2':
            if activity_elem.name in ['ol', 'ul']:
                for item in activity_elem.find_all('li'):
                    video["activities"].append({
                        "type": "text_entry",
                        "instruction": item.text
                    })
            elif activity_elem.name == 'p' and activity_elem.strong:
                video["activities"].append({
                    "type": "text_entry",
                    "name": activity_elem.strong.text.lower().replace(' ', '_'),
                    "instruction": activity_elem.text.split(': ', 1)[-1]
                })
            activity_elem = activity_elem.find_next_sibling()
        
        json_data["videos"].append(video)
    
    return json_data

def process_markdown_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.md'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            
            json_data = parse_markdown_to_json(input_path)
            
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=2, ensure_ascii=False)
            
            print(f"Converted {filename} to JSON: {output_path}")

# Usage
input_directory = r"C:\Users\ASUS\Downloads\notiontojson\notion2json\markdown"
output_directory = r"C:\Users\ASUS\Downloads\notiontojson\notion2json\json"
process_markdown_files(input_directory, output_directory)