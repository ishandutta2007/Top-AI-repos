import requests
import os
from dotenv import load_dotenv

# Load environment variables (ensure VITE_GITHUB_TOKEN is set in .env)
load_dotenv()
GITHUB_TOKEN = os.getenv("VITE_GITHUB_TOKEN")


def get_repo_contributors(repo_slug):
    """Fetch all contributors from the GitHub API."""
    url = f"https://api.github.com/repos/{repo_slug}/contributors?per_page=100"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    contributors = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching contributors: {response.status_code}")
            break
        contributors.extend(response.json())
        if "next" in response.links:
            url = response.links["next"]["url"]
        else:
            url = None
    return contributors


def update_readme(repo_slug, contributors):
    """Generate HTML and update the README.md file."""
    # Generate HTML for contributors with fixed-size avatars
    html_output = []
    for c in contributors:
        login = c["login"]
        avatar = c["avatar_url"]
        html_url = c["html_url"]
        # Use img tag with explicit width and height for consistency
        html_output.append(
            f'<a href="{html_url}"><img src="{avatar}&s=32" width="32" height="32" alt="{login}" /></a>'
        )

    contributor_wall = "\n".join(html_output)

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # Define markers for the contributors section
    # Note: These markers should exist in your README.md
    start_marker = (
        "A huge thank you to everyone who has contributed to this project!\n\n"
    )
    header = "## 👥 Contributors"

    # Try to find the section to replace
    start_index = readme.find(start_marker)
    if start_index == -1:
        # Try finding just the header if the marker was lost
        h_index = readme.find(header)
        if h_index != -1:
            start_index = h_index + len(header)
            # Add the thank you note back in
            contributor_wall = (
                "\n\nA huge thank you to everyone who has contributed to this project!\n\n"
                + contributor_wall
            )
        else:
            print("Error: Could not find '## 👥 Contributors' header in README.md")
            return

    # Find where the next section starts to avoid deleting too much
    next_section = "### 🤔 Questions?"
    end_index = readme.find(next_section)

    if start_index != -1 and end_index != -1:
        # Build the new README content
        new_readme = readme[
            : start_index
            + (len(start_marker) if "A huge thank you" in start_marker else 0)
        ]
        new_readme += contributor_wall
        new_readme += "\n\n" + readme[end_index:]

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
        print(f"Successfully updated README.md with {len(contributors)} contributors.")
    else:
        print(f"Error: Could not find markers. Start: {start_index}, End: {end_index}")


if __name__ == "__main__":
    REPO = "ishandutta2007/Top-AI-repos"
    print(f"Updating contributors for {REPO}...")

    all_contributors = get_repo_contributors(REPO)
    if all_contributors:
        update_readme(REPO, all_contributors)
    else:
        print("No contributors found or error occurred.")
