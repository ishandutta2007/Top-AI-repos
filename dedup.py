import re

def dedup_readme(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    prev_repo_info = None
    row_count = 1
    
    table_row_pattern = re.compile(r'^\|(\d+)(\|.*)')

    for line in lines:
        match = table_row_pattern.match(line)
        if match:
            # check for repo name and url
            repo_match = re.search(r'^\|\s*\[(.*?)\]\((.*?)\)\s*\|', match.group(2))
            if repo_match:
                repo_name = repo_match.group(1).strip()
                repo_url = repo_match.group(2).strip()
                repo_info = (repo_name, repo_url)
                
                if prev_repo_info == repo_info:
                    continue
                
                prev_repo_info = repo_info
                
            # fix numbering
            new_line = f"|{row_count}{match.group(2)}"
            if not new_line.endswith('\n'):
                new_line += '\n'
            out_lines.append(new_line)
            row_count += 1
        else:
            row_count = 1 # reset on non-table rows
            out_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

if __name__ == '__main__':
    dedup_readme(r'C:\Users\ishan\Documents\Projects\Top-AI-repos\README.md')
