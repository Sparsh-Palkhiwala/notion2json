import json
import markdown
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
    ACTIVITY = "ACTIVITY"

def parse_markdown_to_json(markdown_content, input_file_name):
    html_content = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html_content, 'html.parser')
    components = []

    current_module = None
    current_lesson = None
    current_page = None

    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ol', 'li', 'a', 'iframe', 'div']):
        if element.name == 'h1':
            if current_module:
                components.append(current_module)
            current_module = {
                "title": element.get_text(strip=True),
                "lessons": []
            }
        elif element.name == 'h2':
            if current_lesson:
                current_module["lessons"].append(current_lesson)
            current_lesson = {
                "title": element.get_text(strip=True),
                "pages": []
            }
        elif element.name == 'h3':
            if current_page:
                current_lesson["pages"].append(current_page)
            current_page = {
                "title": element.get_text(strip=True),
                "components": []
            }
        elif element.name == 'p' and element.get_text(strip=True).startswith('::activity::'):
            if current_page is not None:
                activity_type = element.get_text(strip=True).split('::')[2].strip()
                activity_info = element.find_next('div')
                if activity_info:
                    activity_lines = activity_info.get_text(strip=True).split('\n')
                    activity_content = {}
                    for line in activity_lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            activity_content[key.strip().lower()] = value.strip()
                    current_page["components"].append({
                        'type': ComponentEnum.ACTIVITY.value,
                        'content': {
                            'type': activity_type,
                            **activity_content
                        }
                    })
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
input_markdown_file = r"C:\Users\ASUS\Downloads\notiontojson\notion2json\md2json\markdown\Setting_Smart_Goals_1.md"
output_json_file = r"C:\Users\ASUS\Downloads\notiontojson\notion2json\md2json\output\Setting_Smart_Goals_1.json"
convert_markdown_to_json(input_markdown_file, output_json_file)
