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

    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ol', 'li', 'a', 'iframe', 'strong']):
        if element.name == 'h1':
            if current_module:
                if current_lesson:
                    if current_page:
                        current_lesson["pages"].append(current_page)
                    current_module["lessons"].append(current_lesson)
                components.append(current_module)
            current_module = {
                "title": element.get_text(strip=True),
                "lessons": []
            }
            current_lesson = None
            current_page = None
        elif element.name == 'h2':
            if current_lesson:
                if current_page:
                    current_lesson["pages"].append(current_page)
                current_module["lessons"].append(current_lesson)
            current_lesson = {
                "title": element.get_text(strip=True),
                "pages": []
            }
            current_page = None
        elif element.name == 'h3':
            if current_page:
                current_lesson["pages"].append(current_page)
            current_page = {
                "title": element.get_text(strip=True),
                "components": []
            }
        elif element.name == 'p':
            if current_page is not None:
                current_page["components"].append({
                    'type': ComponentEnum.TEXT.value,
                    'content': {
                        'text': element.get_text(strip=True)
                    }
                })
        elif element.name == 'ol':
            if current_page is not None:
                list_items = [li.get_text(strip=True) for li in element.find_all('li')]
                current_page["components"].append({
                    'type': ComponentEnum.TEXT.value,
                    'content': {
                        'text': '\n'.join(list_items)
                    }
                })
        elif element.name == 'a':
            if current_page is not None:
                current_page["components"].append({
                    'type': ComponentEnum.VIDEO.value,
                    'content': {
                        'url': element['href']
                    }
                })
        elif element.name == 'iframe':
            if current_page is not None:
                current_page["components"].append({
                    'type': ComponentEnum.VIDEO.value,
                    'content': {
                        'url': element['src']
                    }
                })
        elif element.name == 'strong' and 'Activity:' in element.get_text(strip=True):
            # Attempt to parse the activity component
            activity_info = element.find_next('p')
            if activity_info:
                activity_dict = {'type': ComponentEnum.ACTIVITY.value, 'content': {}}
                activity_lines = activity_info.get_text(strip=True).split('\n')
                for line in activity_lines:
                    split_line = line.split(':', 1)
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
                current_page["components"].append(activity_dict)

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
