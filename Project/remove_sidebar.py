import os
import glob
import re

html_files = glob.glob('*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this file has a sidebar (ml-64 inside flex-1)
    if 'class="flex-1 ml-64"' in content or 'ml-64' in content:
        # Regex to remove the aside block
        # The block starts with <aside and ends with </aside>
        # We need to be careful not to remove other things if they exist, but there's usually only one aside
        new_content = re.sub(r'\n*[ \t]*<aside.*?fixed left-0 top-\[72px\].*?</aside>\n*', '\n', content, flags=re.DOTALL)
        
        # Another pattern just in case it's slightly different
        if new_content == content:
           new_content = re.sub(r'\n*[ \t]*<!-- Fixed Left Sidebar.*?</aside>\n*', '\n', content, flags=re.DOTALL)
           
        # Replace the flex-1 ml-64 with flex-1
        new_content = new_content.replace('class="flex-1 ml-64"', 'class="flex-1"')
        
        # If there's an empty line left by the removed sidebar comment, we can clean it up
        new_content = re.sub(r'<!-- Fixed Left Sidebar.*?-->\n*', '', new_content, flags=re.DOTALL)

        if new_content != content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Removed sidebar from {file}")
