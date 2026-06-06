import requests
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("VITE_GITHUB_TOKEN")

def get_repo_info(repo_slug):
    url = f"https://api.github.com/repos/{repo_slug}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            "name": data["name"],
            "owner": data["owner"]["login"],
            "language": data["language"] or "Markdown",
            "description": data["description"] or "",
            "year": data["created_at"][:4]
        }
    return None

def add_repo_to_readme(slug):
    info = get_repo_info(slug)
    if not info:
        print(f"Failed to fetch info for {slug}")
        return

    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the bullet point link
    bullet_link = f"- https://github.com/{slug}"
    content = content.replace(bullet_link, "")

    table_end_marker = "## 👥 Contributors"
    split_content = content.split(table_end_marker)
    
    if len(split_content) < 2:
        print("Error: Could not find table end marker.")
        return

    table_part = split_content[0].strip()
    rest_part = table_end_marker + split_content[1]

    repo_link = f"[{info['name']}](https://github.com/{slug})"
    repo_stars = f'<a href="https://github.com/{slug}"><img alt="total stars" title="Total stars on GitHub" src="https://custom-icon-badges.herokuapp.com/github/stars/{slug}?logo=star&color=55960c&labelColor=488207&label=Stars&style=for-the-badge&query=%24.stars&url=https://api.github.com/repos/{slug}"/></a>'
    user_stars = f'<a href="https://github.com/{info["owner"]}?tab=repositories&sort=stargazers"> <img alt="total stars" title="Total stars on GitHub" src="https://custom-icon-badges.herokuapp.com/badge/dynamic/json?logo=star&color=55960c&labelColor=488207&label=Stars&style=for-the-badge&query=%24.stars&url=https://api.github-star-counter.workers.dev/user/{info["owner"]}"/></a>'
    
    new_row = f"| | {repo_link} | {repo_stars} | {user_stars} | {info['language']} | {info['description']} | {info['year']} |"
    
    updated_table = table_part + "\n" + new_row + "\n\n"
    final_content = updated_table + rest_part

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Added {slug} to README.md and removed its bullet point.")

if __name__ == "__main__":
    add_repo_to_readme("f/prompts.chat")
