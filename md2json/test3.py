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
            activity_dict = {'type': ComponentEnum.ACTIVITY.value, 'content': {}}
            i += 1
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
                i += 1
            if current_page is not None:
                current_page["components"].append(activity_dict)
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
input_markdown_file = r"C:\Users\ASUS\Downloads\notiontojson\notion2json\md2json\markdown\test3.md"
output_json_file = r"C:\Users\ASUS\Downloads\notiontojson\notion2json\md2json\output\test3.json"
convert_markdown_to_json(input_markdown_file, output_json_file)



"""
How the structure of the Markdown should be 
--------------------------------------------
# Module Title
Welcome to the module introduction.

## Lesson 1: Introduction to Markdown
Markdown is a lightweight markup language.

### Page 1: What is Markdown?
Markdown is a text-to-HTML conversion tool for web writers.

This is a simple paragraph explaining markdown.

::activity::
Label: Activity 1
Placeholder: Enter your answer here
Variable: activity1

- List item 1
- List item 2
- List item 3

[Watch this video](https://www.example.com/video)

<iframe src="https://www.youtube.com/embed/example"></iframe>

## Lesson 2: Markdown Syntax
Markdown uses plain text formatting.

### Page 1: Headers
Headers are created using the `#` symbol.

### Page 2: Links
Links can be created using `[link text](url)`.
--------------------------------------------------------------
What does the structure represent

# Module Title: This will create a new module.
## Lesson Title: This will create a new lesson within the current module.
### Page Title: This will create a new page within the current lesson.
This is a paragraph of text.: This will be parsed as a text component.
- Item 1 in an ordered list, - Item 2 in an ordered list: These list items will be parsed as text components.
[This is a video link](https://www.example.com/video): This will be parsed as a video component with the specified URL.
<iframe src="https://www.youtube.com/embed/example"></iframe>: This iframe will be parsed as a video component.
::activity:: followed by Label:, Placeholder:, and Variable:: This will be parsed as an activity component with the specified attributes.
"""
