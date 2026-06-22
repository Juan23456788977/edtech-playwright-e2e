import re

with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/schools.html', 'r', encoding='utf-8') as f:
    html = f.read()

for match in re.finditer(r'<div class="role-option" data-instance-id="(\d+)".*?<strong>(.*?)</strong>', html, re.DOTALL):
    print(match.group(2).strip(), "-> ID:", match.group(1))
