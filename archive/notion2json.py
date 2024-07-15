import json
import markdown
import argparse
from typing import List, Dict, Any

def custom_notion_parser(text: str) -> List[Dict[str, Any]]:
    """Parse Notion text and return a list of structured components."""
    components = []
    lines = text.split('\n')
    current_block = []

    for line in lines:
        if line.startswith('{ACTIVITY:') or line.startswith('{ICON:'):
            if current_block:
                components.append({
                    "type": ComponentEnum.TEXT,
                    "content": {"text": markdown.markdown('\n'.join(current_block))}
                })
                current_block = []
            
            if line.startswith('{ACTIVITY:'):
                components.append({
                    "type": ComponentEnum.ACTIVITY,
                    "content": {"text": line.strip('{}').split(':', 1)[1].strip()}
                })
            else:  # ICON
                components.append({
                    "type": ComponentEnum.ICON,
                    "content": {"text": line.strip('{}').split(':', 1)[1].strip()}
                })
        else:
            current_block.append(line)

    if current_block:
        components.append({
            "type": ComponentEnum.TEXT,
            "content": {"text": markdown.markdown('\n'.join(current_block))}
        })

    return components

def convert_notion_to_json(text: str, title: str) -> str:
    """Convert Notion text to a JSON string."""
    components = custom_notion_parser(text)
    
    json_data = {
        "title": title,
        "components": components
    }
    
    return json.dumps(json_data, indent=2)

class ComponentEnum:
    TEXT = "TEXT"
    ACTIVITY = "ACTIVITY"
    ICON = "ICON"

def main():
    parser = argparse.ArgumentParser(description="Convert Notion export to JSON")
    parser.add_argument("input_file", help="Path to the Notion export file")
    parser.add_argument("output_file", help="Path for the output JSON file")
    parser.add_argument("--title", default="Untitled", help="Title for the document")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as file:
            notion_text = file.read()

        json_output = convert_notion_to_json(notion_text, args.title)

        with open(args.output_file, 'w', encoding='utf-8') as file:
            file.write(json_output)

        print(f"Conversion successful. JSON saved to {args.output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
