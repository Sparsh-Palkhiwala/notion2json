const fs = require('fs');
const path = require('path');
const marked = require('marked');

// Define your types and enums here
const ComponentEnum = {
  VIDEO: 'VIDEO',
  TEXT: 'TEXT',
  INPUT: 'INPUT',
  HABIT: 'HABIT'
};

// Function to parse the markdown and convert it to the desired format
function convertMarkdownToModules(markdownContent) {
  const tokens = marked.lexer(markdownContent);
  const modules = [];
  let currentModule = null;
  let currentLesson = null;
  let currentPage = null;

  tokens.forEach(token => {
    switch (token.type) {
      case 'heading':
        if (token.depth === 1) {
          // New module
          if (currentModule) modules.push(currentModule);
          currentModule = {
            title: token.text,
            color: '',
            iconUrl: '',
            lessons: []
          };
        } else if (token.depth === 2) {
          // New lesson
          if (currentLesson) currentModule.lessons.push(currentLesson);
          currentLesson = {
            title: token.text,
            color: '',
            iconUrl: '',
            pages: []
          };
        } else if (token.depth === 3) {
          // New page
          if (currentPage) currentLesson.pages.push(currentPage);
          currentPage = {
            title: token.text,
            components: []
          };
        }
        break;
      case 'paragraph':
        if (currentPage) {
          if (token.text.startsWith('{icon}')) {
            currentPage.components.push({
              type: ComponentEnum.TEXT,
              content: { text: `<div class="icon"><p>${token.text.replace('{icon}', '').trim()}</p></div>` }
            });
          } else if (token.text.startsWith('{activity}')) {
            currentPage.components.push({
              type: ComponentEnum.TEXT,
              content: { text: `<div class="activity"><p>${token.text.replace('{activity}', '').trim()}</p></div>` }
            });
          } else {
            currentPage.components.push({
              type: ComponentEnum.TEXT,
              content: { text: `<div><p>${token.text}</p></div>` }
            });
          }
        }
        break;
      case 'list':
        if (currentPage) {
          const items = token.items.map(item => `<li>${item.text}</li>`).join('');
          currentPage.components.push({
            type: ComponentEnum.TEXT,
            content: { text: `<div><ol>${items}</ol></div>` }
          });
        }
        break;
      // Add more cases as needed to handle other Markdown structures
    }
  });

  if (currentPage) currentLesson.pages.push(currentPage);
  if (currentLesson) currentModule.lessons.push(currentLesson);
  if (currentModule) modules.push(currentModule);

  return modules;
}

// Load your markdown file
const markdownPath = path.join(__dirname, 'testmd.md');  //change path to the markdown here
const markdownContent = fs.readFileSync(markdownPath, 'utf-8');

// Convert the markdown to modules format
const modules = convertMarkdownToModules(markdownContent);

// Output the result
const inputFileName = path.basename(markdownPath, path.extname(markdownPath));
const outputPath = path.join(__dirname, `${inputFileName}_output.json`);     //name of the output file that will come out 
fs.writeFileSync(outputPath, JSON.stringify(modules, null, 2), 'utf-8');

console.log(`Modules have been saved to ${outputPath}`);
