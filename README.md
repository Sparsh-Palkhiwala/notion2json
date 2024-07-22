# Markdown to JSON Parser

This project is designed to convert structured markdown content into JSON format, suitable for use in applications requiring modular and organized data.

## Features

- **Parse Markdown**: Converts markdown files with special tags into structured JSON.
- **Component Support**: Handles various components like text, videos, and activities.
- **Activity Types**: Supports multiple activity types such as input, calendar, and checkbox.

## Markdown Structure

### Modules, Lessons, and Pages

- **Modules**: Represented by `# Module Title`
  - Contains attributes like color and icon.
- **Lessons**: Represented by `## Lesson Title`
  - Nested within modules.
- **Pages**: Represented by `### Page Title`
  - Contain various components.

### Components

#### Activities

Activities are marked with `::activity::` followed by the type.

Example:
```markdown
::activity:: input
<div>
label: How will you measure your progress?
variable: being_measurable
placeholder: I will plan my runs, where I will reach one more mile each day
</div>
```

### Videos
Links are parsed as video components:
```markdown
[Video Title](https://player.vimeo.com/video/123456789)
```


## Sample Markdown 
```markdown
# Habits

## Starting a New Habit

### Welcome

Welcome to the Habits Module!

::activity:: input
<div>
label: How will you measure your progress?
variable: being_measurable
placeholder: I will plan my runs, where I will reach one more mile each day
</div>

[Watch the Introduction Video](https://player.vimeo.com/video/123456789)

This guide will help you:

- Learn to incorporate the 5 components of habit formation.
- Track your habits using our habit tracker.
```

### Subsequent Json
```json
{
  "modules": [
    {
      "title": "Module Title",
      "color": "#8ED6ED",
      "icon": {
        "name": "Icon Name",
        "url": "Icon URL",
        "alt": "Icon Description"
      },
      "lessons": [
        {
          "title": "Lesson Title",
          "pages": [
            {
              "title": "Page Title",
              "components": [
                {
                  "type": "INPUT",
                  "content": {
                    "label": "How will you measure your progress?",
                    "variable": "being_measurable",
                    "placeholder": "I will plan my runs, where I will reach one more mile each day"
                  }
                },
                {
                  "type": "VIDEO",
                  "content": {
                    "url": "https://player.vimeo.com/video/123456789"
                  }
                },
                {
                  "type": "TEXT",
                  "content": {
                    "text": "Paragraph text goes here."
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}

```


