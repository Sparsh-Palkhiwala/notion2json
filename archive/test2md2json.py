import json
import re
from markdown import markdown
from bs4 import BeautifulSoup
from enum import Enum

class ComponentEnum(Enum):
    VIDEO = "VIDEO"
    TEXT = "TEXT"
    INPUT = "INPUT"
    HABIT = "HABIT"
    CHECKBOX = "CHECKBOX"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    CALENDAR = "CALENDAR"

# Helper function to convert markdown to HTML
def markdown_to_html(md):
    return markdown(md)

# Helper function to parse HTML to JSON structure
def parse_html_to_json(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    components = []

    for element in soup.find_all(['p', 'ol', 'li', 'div', 'a']):
        if element.name == 'p':
            components.append({
                'type': ComponentEnum.TEXT.value,
                'content': {
                    'text': element.get_text(strip=True)
                }
            })
        elif element.name == 'ol':
            list_items = [li.get_text(strip=True) for li in element.find_all('li')]
            components.append({
                'type': ComponentEnum.TEXT.value,
                'content': {
                    'text': '\n'.join(list_items)
                }
            })
        elif element.name == 'a':
            components.append({
                'type': ComponentEnum.VIDEO.value,
                'content': {
                    'url': element['href']
                }
            })

    return components

# Function to read markdown content from a file
def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to write JSON content to a file
def write_json_file(json_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2)

# Function to extract headings and their hierarchy from markdown content
def extract_headings(markdown_content):
    headings = []
    lines = markdown_content.split('\n')
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((level, title))
    return headings

# Function to build a nested structure based on headings
def build_structure(headings):
    root = {"title": "", "lessons": []}
    stack = [root]
    
    for level, title in headings:
        while len(stack) > level:
            stack.pop()
        
        current = {
            "title": title,
            "pages": [] if level == 2 else None,
            "components": [] if level > 2 else None
        }
        
        if level == 1:
            stack[-1]["lessons"].append(current)
        elif level == 2:
            stack[-1]["pages"].append(current)
        else:
            stack[-1]["components"].append(current)
        
        stack.append(current)
    
    return root["lessons"]

# Main function to convert markdown file to JSON
def convert_markdown_to_json(input_file_path, output_file_path):
    # Read the markdown content from the file
    markdown_content = read_markdown_file(input_file_path)

    # Extract headings and build structure
    headings = extract_headings(markdown_content)
    structure = build_structure(headings)
    
    # Convert markdown to HTML
    html_content = markdown_to_html(markdown_content)

    # Parse HTML to JSON structure
    components = parse_html_to_json(html_content)

    # Assign components to the last level of structure
    for lesson in structure:
        for page in lesson.get("pages", []):
            if "components" in page:
                page["components"].extend(components)

    # Write the resulting JSON to the output file
    write_json_file(structure, output_file_path)

# Usage example
input_markdown_file = "C:\\Users\\ASUS\\Downloads\\notiontojson\\notion2json\\example.md"
output_json_file = 'path_to_your_output_file.json'
convert_markdown_to_json(input_markdown_file, output_json_file)
