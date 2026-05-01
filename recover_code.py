import os

log_path = r'C:\Users\hilar\.gemini\antigravity\brain\1b1e70cc-1f79-49e6-8770-e45d2fb50ab7\.system_generated\logs\overview.txt'

if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    start_tag = 'function renderHistoryRecords()'
    pos = content.rfind(start_tag) # Find the LAST occurrence
    if pos != -1:
        print(content[pos:pos+5000])
    else:
        print("COULD NOT FIND function renderHistoryRecords in logs")
else:
    print("LOG PATH NOT FOUND")
