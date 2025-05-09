// Function to add copy buttons to code blocks
function addCopyButtons() {
  // Add copy buttons to all code blocks
  var codeBlocks = document.querySelectorAll('pre, div.highlight pre, .rst-content pre, code.literal-block');

  codeBlocks.forEach(function(codeBlock) {
    // Skip if already has a header
    if (codeBlock.parentNode.querySelector('.code-header')) {
      return;
    }

    // Try to determine the language
    var language = "code";

    // Check for class-based language indicators
    if (codeBlock.className) {
      var classNames = codeBlock.className.split(' ');
      for (var i = 0; i < classNames.length; i++) {
        // Check common class patterns for language identification
        if (classNames[i].startsWith('language-')) {
          language = classNames[i].replace('language-', '');
          break;
        } else if (classNames[i].startsWith('lang-')) {
          language = classNames[i].replace('lang-', '');
          break;
        } else if (/^(html|css|js|ts|python|java|cpp|c|csharp|ruby|go|rust|php|swift|kotlin|bash|shell|powershell|sql)$/i.test(classNames[i])) {
          language = classNames[i].toLowerCase();
          break;
        }
      }
    }

    // Check parent elements for language hints
    if (language === "code") {
      var parent = codeBlock.parentNode;
      while (parent && parent.tagName && parent.tagName.toLowerCase() !== 'body') {
        if (parent.className && parent.className.includes('language-')) {
          var parentClasses = parent.className.split(' ');
          for (var j = 0; j < parentClasses.length; j++) {
            if (parentClasses[j].startsWith('language-')) {
              language = parentClasses[j].replace('language-', '');
              break;
            }
          }
          if (language !== "code") break;
        }
        parent = parent.parentNode;
      }
    }

    // Check for data attributes
    if (language === "code" && codeBlock.dataset && codeBlock.dataset.language) {
      language = codeBlock.dataset.language;
    }

    // Format the language name to be more readable
    if (language !== "code") {
      // Capitalize first letter and format common language names
      switch (language.toLowerCase()) {
        case 'js': language = 'JavaScript'; break;
        case 'ts': language = 'TypeScript'; break;
        case 'py': language = 'Python'; break;
        case 'rb': language = 'Ruby'; break;
        case 'cs': language = 'C#'; break;
        case 'cpp': language = 'C++'; break;
        case 'sh': language = 'Shell'; break;
        case 'md': language = 'Markdown'; break;
        case 'yml': case 'yaml': language = 'YAML'; break;
        case 'json': language = 'JSON'; break;
        case 'html': language = 'HTML'; break;
        case 'css': language = 'CSS'; break;
        case 'sql': language = 'SQL'; break;
        case 'text': language = ''; break;
        default:
          // Capitalize first letter
          language = language.charAt(0).toUpperCase() + language.slice(1);
      }
    }

    // Create header div
    var headerDiv = document.createElement('div');
    headerDiv.className = 'code-header';
    headerDiv.style.display = 'flex';
    headerDiv.style.justifyContent = 'space-between';
    headerDiv.style.alignItems = 'center';
    headerDiv.style.padding = '4px 10px'; // Match CSS: smaller padding
    headerDiv.style.backgroundColor = '#eaeaea';
    headerDiv.style.borderTopLeftRadius = '8px';
    headerDiv.style.borderTopRightRadius = '8px';
    headerDiv.style.borderBottom = '1px solid #e1e4e5';

    // Create language label
    var languageLabel = document.createElement('span');
    languageLabel.className = 'code-language';
    // Only display language if it's explicitly set (not "code")
    languageLabel.textContent = language === "code" ? "" : language;
    languageLabel.style.fontFamily = 'monospace';
    languageLabel.style.fontSize = '0.75em'; // Match CSS: smaller font size
    languageLabel.style.fontWeight = 'normal'; // Match CSS: normal instead of bold
    languageLabel.style.color = '#666'; // Match CSS: lighter color

    // Create copy button
    var button = document.createElement('button');
    button.className = 'copy-button';
    button.title = 'Copy to clipboard';
    button.style.display = 'flex';
    button.style.alignItems = 'center';
    button.style.gap = '5px';
    button.style.padding = '3px 8px'; // Match CSS: smaller padding
    button.style.border = 'none';
    button.style.borderRadius = '4px';
    button.style.backgroundColor = '#eaeaea';
    button.style.cursor = 'pointer';
    button.style.transition = 'background-color 0.2s';
    button.style.fontSize = '0.8em'; // Match CSS: smaller font size
    button.style.color = '#555'; // Match CSS: lighter color

    // Add hover effect
    button.addEventListener('mouseover', function() {
      button.style.backgroundColor = '#d0d0d0'; // Darker on hover
    });

    button.addEventListener('mouseout', function() {
      button.style.backgroundColor = '#eaeaea'; // Back to normal
    });

    // Create icon span
    var iconSpan = document.createElement('span');
    iconSpan.className = 'copy-icon';
    iconSpan.innerHTML = '📋'; // Clipboard icon

    // Create text span
    var textSpan = document.createElement('span');
    textSpan.className = 'copy-text';
    textSpan.textContent = 'Copy';

    // Add icon and text to button
    button.appendChild(iconSpan);
    button.appendChild(textSpan);

    // Add language label and button to header
    headerDiv.appendChild(languageLabel);
    headerDiv.appendChild(button);

    // Create a wrapper div if needed
    var wrapper = codeBlock.parentNode;
    if (wrapper.nodeName.toLowerCase() !== 'div' || !wrapper.classList.contains('code-wrapper')) {
      wrapper = document.createElement('div');
      wrapper.className = 'code-wrapper';
      wrapper.style.position = 'relative';
      wrapper.style.marginBottom = '1.5em';
      wrapper.style.borderRadius = '8px';
      wrapper.style.overflow = 'hidden';
      // No box shadow to avoid border appearance
      codeBlock.parentNode.insertBefore(wrapper, codeBlock);
      wrapper.appendChild(codeBlock);
    }

    // Style the code block
    codeBlock.style.margin = '0';
    codeBlock.style.borderTopLeftRadius = '0';
    codeBlock.style.borderTopRightRadius = '0';
    codeBlock.style.borderBottomLeftRadius = '8px';
    codeBlock.style.borderBottomRightRadius = '8px';
    codeBlock.style.backgroundColor = '#f8f8f8'; // Light background color
    codeBlock.style.padding = '12px';
    codeBlock.style.border = 'none'; // Ensure no border on the code block

    // Add header before code block
    wrapper.insertBefore(headerDiv, codeBlock);

    // Add click event
    button.addEventListener('click', function() {
      // Get the text content
      var text = codeBlock.textContent;

      // Create a temporary textarea element
      var textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'absolute';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);

      // Select the text and copy it
      textarea.select();
      document.execCommand('copy');

      // Remove the textarea
      document.body.removeChild(textarea);

      // Change icon to checkmark
      iconSpan.innerHTML = '✓'; // Checkmark icon

      // Reset icon after a delay
      setTimeout(function() {
        iconSpan.innerHTML = '📋'; // Back to clipboard icon
      }, 2000);
    });
  });
}

// Run when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', addCopyButtons);

// Also run when the window is fully loaded (as a fallback)
window.addEventListener('load', addCopyButtons);

// For readthedocs theme which might load content dynamically
// Run periodically to catch any new code blocks
setInterval(addCopyButtons, 2000);
