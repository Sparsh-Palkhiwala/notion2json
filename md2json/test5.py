import json
import mistune
from enum import Enum
from bs4 import BeautifulSoup

class ComponentEnum(Enum):
    VIDEO = "VIDEO"
    TEXT = "TEXT"
    ACTIVITY = "ACTIVITY"
    INPUT = "INPUT"
    HABIT = "HABIT"
    CHECKBOX = "CHECKBOX"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    CALENDAR = "CALENDAR"

def parse_markdown_to_json(markdown_content, input_file_name):
    html_content = mistune.markdown(markdown_content)
    soup = BeautifulSoup(html_content, 'html.parser')
    components = []

    current_module = None
    current_lesson = None
    current_page = None

    lines = markdown_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('# '):
            if current_module:
                if current_lesson:
                    if current_page:
                        current_lesson["pages"].append(current_page)
                    current_module["lessons"].append(current_lesson)
                components.append(current_module)
            current_module = {
                "title": line[2:].strip(),
                "lessons": []
            }
            current_lesson = None
            current_page = None
        elif line.startswith('## '):
            if current_lesson:
                if current_page:
                    current_lesson["pages"].append(current_page)
                current_module["lessons"].append(current_lesson)
            current_lesson = {
                "title": line[3:].strip(),
                "pages": []
            }
            current_page = None
        elif line.startswith('### '):
            if current_page:
                current_lesson["pages"].append(current_page)
            current_page = {
                "title": line[4:].strip(),
                "components": []
            }
        elif line.startswith('::activity::'):
            activity_type = line.split('::activity::')[1]
            activity_dict = {'type': ComponentEnum.ACTIVITY.value, 'content': {'type': activity_type}}
            i += 1
            options = []
            while i < len(lines) and lines[i].strip() != '':
                activity_line = lines[i].strip()
                split_line = activity_line.split(':', 1)
                if len(split_line) == 2:
                    key, value = split_line
                    key = key.strip().lower()
                    value = value.strip()
                    if key == 'label':
                        activity_dict['content']['label'] = value
                    elif key == 'placeholder':
                        activity_dict['content']['placeholder'] = value
                    elif key == 'variable':
                        activity_dict['content']['variable'] = value
                    elif key == 'options':
                        options.append(value)
                i += 1
            if options:
                activity_dict['content']['options'] = options
            if current_page is not None:
                current_page["components"].append(activity_dict)
        elif line.startswith('[') and '](' in line:
            # Handle markdown links (potential video links)
            link_text = line.split('[', 1)[1].split(']', 1)[0]
            link_url = line.split('](', 1)[1].split(')', 1)[0]
            if 'video' in link_text.lower():
                if current_page is not None:
                    current_page["components"].append({
                        'type': ComponentEnum.VIDEO.value,
                        'content': {
                            'url': link_url
                        }
                    })
            else:
                if current_page is not None:
                    current_page["components"].append({
                        'type': ComponentEnum.TEXT.value,
                        'content': {
                            'text': line
                        }
                    })
        elif line.startswith('<iframe') and 'src=' in line:
            # Handle embedded videos
            soup = BeautifulSoup(line, 'html.parser')
            iframe = soup.find('iframe')
            if iframe and iframe.get('src'):
                if current_page is not None:
                    current_page["components"].append({
                        'type': ComponentEnum.VIDEO.value,
                        'content': {
                            'url': iframe['src']
                        }
                    })
        else:
            if current_page is not None:
                if line:
                    current_page["components"].append({
                        'type': ComponentEnum.TEXT.value,
                        'content': {
                            'text': line
                        }
                    })
        
        i += 1

    if current_page:
        current_lesson["pages"].append(current_page)
    if current_lesson:
        current_module["lessons"].append(current_lesson)
    if current_module:
        components.append(current_module)

    # Define the JSON structure
    modules = [
        {
            "title": input_file_name,
            "color": "#8ED6ED",
            "iconUrl": "some_icon_url",  # Update with actual icon URL
            "lessons": [
                {
                    "title": input_file_name,
                    "color": "#8ED6ED",
                    "iconUrl": "some_icon_url",  # Update with actual icon URL
                    "pages": [
                        {
                            "title": input_file_name,
                            "components": components
                        }
                    ]
                }
            ]
        }
    ]

    return modules

def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_json_file(json_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2)

def convert_markdown_to_json(input_file_path, output_file_path):
    markdown_content = read_markdown_file(input_file_path)
    input_file_name = input_file_path.split('/')[-1]
    json_data = parse_markdown_to_json(markdown_content, input_file_name)
    write_json_file(json_data, output_file_path)

# Usage example
input_markdown_file = '/content/drive/MyDrive/notion2json2/test2.md'
output_json_file = '/content/drive/MyDrive/notion2json2/test2.json'
convert_markdown_to_json(input_markdown_file, output_json_file)
