import re
import sys

def check_table_consistency(file_path='README.md'):
    """
    Checks the consistency of the GitHub repository table in a Markdown file.
    Verifies that 'Repo_Stars' and 'User_Stars' columns correctly link to the 
    repository and owner specified in the 'Repo' column.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Find the table rows: |ID| Repo | Repo_Stars | User_Stars | ...
    # Flexible regex to handle varying whitespace
    table_pattern = re.compile(r'^\|(\d+)\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
    rows = table_pattern.findall(content)

    if not rows:
        print("No table rows found matching the expected pattern.")
        return

    print(f"--- Checking {len(rows)} rows in {file_path} ---")
    mismatches = 0

    for row_id, repo_col, repo_stars_col, user_stars_col in rows:
        # Extract repo owner and name from Repo column: [Name](https://github.com/owner/repo)
        repo_match = re.search(r'https://github\.com/([^/]+)/([^/)]+)', repo_col)
        if not repo_match:
            continue
        
        owner = repo_match.group(1).lower().rstrip('/')
        repo_name = repo_match.group(2).lower().rstrip('/')

        # --- Check Repo_Stars column ---
        # 1. Check anchor tag href
        href_match = re.search(r'href="https://github\.com/([^/"]+)/?([^/"]+)?"', repo_stars_col)
        if href_match:
            h_owner = href_match.group(1).lower()
            h_repo = href_match.group(2).lower() if href_match.group(2) else ""
            if h_owner != owner or (h_repo and h_repo != repo_name):
                 print(f"Row {row_id}: [Repo_Stars] href mismatch. Expected {owner}/{repo_name}, found {h_owner}/{h_repo}")
                 mismatches += 1

        # 2. Check badge API URL
        badge_url_match = re.search(r'url=https://api\.github\.com/repos/([^/&"]+)/([^/&"]+)', repo_stars_col)
        if badge_url_match:
            b_owner, b_repo = badge_url_match.groups()
            if b_owner.lower() != owner or b_repo.lower() != repo_name:
                print(f"Row {row_id}: [Repo_Stars] badge API mismatch. Expected {owner}/{repo_name}, found {b_owner}/{b_repo}")
                mismatches += 1

        # --- Check User_Stars column ---
        # 1. Check anchor tag href
        u_href_match = re.search(r'href="https://github\.com/(?:orgs/)?([^/?"]+)', user_stars_col)
        if u_href_match:
            u_owner = u_href_match.group(1).lower()
            if u_owner != owner:
                print(f"Row {row_id}: [User_Stars] href mismatch. Expected owner {owner}, found {u_owner}")
                mismatches += 1

        # 2. Check badge API URL
        u_badge_url_match = re.search(r'url=https://api\.github-star-counter\.workers\.dev/user/([^/&"]+)', user_stars_col)
        if u_badge_url_match:
            u_b_owner = u_badge_url_match.group(1).lower()
            if u_b_owner != owner:
                print(f"Row {row_id}: [User_Stars] badge API mismatch. Expected owner {owner}, found {u_b_owner}")
                mismatches += 1

    if mismatches == 0:
        print("Success: No inconsistencies found!")
    else:
        print(f"Finished: Found {mismatches} inconsistencies.")

if __name__ == "__main__":
    check_table_consistency()
