import re
import requests
import os
import time
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv("VITE_GITHUB_TOKEN")
CACHE_FILE = "star_cache.json"
CACHE_EXPIRATION_HOURS = 24

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        print(f"Error saving cache: {e}")

# Global cache object
star_cache = load_cache()

def get_github_stars(repo_slug):
    """Fetches the star count for a given GitHub repository slug with caching."""
    now = datetime.now()
    
    # Check cache first
    if repo_slug in star_cache:
        cached_data = star_cache[repo_slug]
        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        if now - cached_time < timedelta(hours=CACHE_EXPIRATION_HOURS):
            # print(f"Using cached stars for {repo_slug}: {cached_data['stars']}")
            return cached_data['stars']

    api_url = f"https://api.github.com/repos/{repo_slug}"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        stars = data.get("stargazers_count", 0)
        
        # Update cache
        star_cache[repo_slug] = {
            'stars': stars,
            'timestamp': now.isoformat()
        }
        return stars
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stars for {repo_slug}: {e}")
        # Return cached value if available even if expired, as fallback
        if repo_slug in star_cache:
            return star_cache[repo_slug]['stars']
        return -1  # Return -1 to indicate an error, will be sorted to the bottom

def sort_markdown_table(markdown_content):
    # Find the table header and separator
    header_match = re.search(r'\|<ins>#</ins>[^\n]*\n', markdown_content)
    separator_match = re.search(r'\|---[^\n]*\n', markdown_content)

    if not header_match or not separator_match:
        print("Table header or separator not found.")
        return markdown_content

    # Content before the table starts at the beginning of the file and ends at the start of the header line.
    content_before_table = markdown_content[:header_match.start()]

    # The table block starts at header_match.start() and ends at table_body_end_index.
    # We need to find the end of the table body.
    table_body_start_index = separator_match.end()
    search_start_for_next_heading = table_body_start_index
    next_heading_match = re.search(r'\n##', markdown_content[search_start_for_next_heading:])
    
    if next_heading_match:
        table_body_end_index = search_start_for_next_heading + next_heading_match.start()
    else:
        table_body_end_index = len(markdown_content) # If no next heading, table goes to end of file

    # Content after the table starts from table_body_end_index to the end of the file.
    content_after_table = markdown_content[table_body_end_index:]

    # Extract the original header line and separator line to reconstruct the new table block
    original_header_line = markdown_content[header_match.start():header_match.end()]
    original_separator_line = markdown_content[separator_match.start():separator_match.end()]

    # Extract table body rows
    table_body_raw = markdown_content[separator_match.end():table_body_end_index].strip()
    rows = table_body_raw.split('\n')
    
    parsed_repos = []

    # Regex to extract repo slug from the Repo_Stars column's img src
    repo_slug_regex = re.compile(r'src="https://custom-icon-badges.herokuapp.com/github/stars/([^/]+/[^?]+)\?')

    for i, row in enumerate(rows):
        if not row.strip():
            continue

        cols = row.split('|')
        if len(cols) < 7:
            print(f"Skipping malformed row (not enough columns): {row}")
            continue

        repo_stars_column_content = cols[3] # This is the content of the Repo_Stars column

        repo_slug = None
        slug_match = repo_slug_regex.search(repo_stars_column_content)
        if slug_match:
            repo_slug = slug_match.group(1)
        else:
            # Fallback: try to get from the main repo link in the second column (cols[2])
            repo_link_match = re.search(r'\[.*?\]\((https://github.com/([^/]+/[^)]+))\)', cols[2])
            if repo_link_match:
                repo_slug = repo_link_match.group(2)

        stars = 0
        if repo_slug:
            stars = get_github_stars(repo_slug)
            print(f"Fetched stars for {repo_slug}: {stars}")
            time.sleep(0.1) # Be kind to the API, 5000 requests/hour limit with token
        else:
            print(f"Could not extract repo slug from row: {row}")

        parsed_repos.append({'original_row': row, 'stars': stars, 'repo_slug': repo_slug})

    # Sort by stars in descending order
    parsed_repos.sort(key=lambda x: x['stars'], reverse=True)

    # Reconstruct the table body with updated numbering
    sorted_rows = []
    for i, repo_data in enumerate(parsed_repos):
        original_row = repo_data['original_row']
        cols = original_row.split('|')
        if len(cols) > 1:
            cols[1] = str(i + 1) # Update the number
            sorted_rows.append('|'.join(cols))
        else:
            sorted_rows.append(original_row)

    new_table_body = "\n".join(sorted_rows)
    
    # Construct the new full table block
    new_full_table_block = original_header_line + original_separator_line + "\n" + new_table_body + "\n"

    # Construct the full new markdown content
    new_markdown_content = content_before_table + new_full_table_block + content_after_table

    return new_markdown_content

# Main execution
file_path = r"C:\Users\ishan\Documents\Projects\Top-AI-repos\README.md"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

updated_content = sort_markdown_table(content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)

save_cache(star_cache)
print("Table sorting complete. Check README.md")