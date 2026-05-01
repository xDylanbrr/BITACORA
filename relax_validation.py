import os

file_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Relax MO validation to allow more zeros (as seen in user screenshot)
content = content.replace('function isValidMO(v) { return /^MO\\d{10}-\\d{4}$/.test(v || \'\'); }', 
                          'function isValidMO(v) { return /^MO\\d{8,15}-\\d{4}$/.test(v || \'\'); }')

# Relax Item validation
content = content.replace('return /^PTC\\d{5}$/.test(String(v || \'\').trim().toUpperCase());', 
                          'return /^PTC\\d{4,8}$/.test(String(v || \'\').trim().toUpperCase());')

# Fix isValidMOByArea too
import re
content = re.sub(r'return new RegExp\(`\^MO000000\\\\d{4}-\$\{AREA_SUFFIX\[area\]\}\$`\)', 
                 r'return new RegExp(`^MO\\d{8,15}-${AREA_SUFFIX[area]}$`)', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated validation rules in app.js")
