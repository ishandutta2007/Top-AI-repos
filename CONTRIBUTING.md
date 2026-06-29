# Contributing to Top AI Repos

Thank you for your interest in contributing to Top-AI-repos! This guide will help you understand the project structure, how to use the utility scripts to maintain the repository, and the guidelines for submitting your changes.

---

## 🛠️ Repository Scripts & Roles

This repository uses several Python scripts and one PowerShell script to automate data consistency, table sorting, serial updates, and contributor stats in [README.md](/README.md).

Here is a breakdown of each script's role and how to run it:

### 1. Table Sorting
* **File:** [sort_table.py](/sort_table.py)
* **Role:** Fetches the latest star counts for each GitHub repository in the list using the GitHub API, sorts the table rows in descending order based on star counts, updates the serial numbers, and caches results locally in `star_cache.json` (valid for 24 hours).
* **Environment variables:** Needs `VITE_GITHUB_TOKEN` defined in a `.env` file (copied from `.env.example`) to avoid GitHub API rate-limiting.
* **How to run:**
  ```powershell
  python sort_table.py
  ```

### 2. Consistency Checking
* **Files:** [check_table.py](/check_table.py) and [check_repo_link_vs_user_link_inconsistencies.py](/check_repo_link_vs_user_link_inconsistencies.py)
* **Role:** Parses the README table and verifies that the `Repo_Stars` and `User_Stars` badge URLs/hrefs match the owner and repository names specified in the main `Repo` column.
* **How to run:**
  ```powershell
  python check_table.py
  # or
  python check_repo_link_vs_user_link_inconsistencies.py
  ```

### 3. Fixing Serial Numbers
* **Files:** [fix_serials.py](/fix_serials.py) & [fix_serials.ps1](/fix_serials.ps1)
* **Role:** Ensures the sequential row IDs (first column) in the markdown table start from `1` and increase incrementally without gaps.
* **How to run:**
  ```powershell
  python fix_serials.py
  # or in PowerShell
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File fix_serials.ps1
  ```

### 4. Updating Contributors
* **File:** [update_contributors.py](/update_contributors.py)
* **Role:** Fetches project contributors via the GitHub API and updates the grid of contributor avatar images under the `## 👥 Contributors` section in [README.md](/README.md).
* **How to run:**
  ```powershell
  python update_contributors.py
  ```

---

## 📋 General Contribution Guidelines

1. **Adding/Editing Repositories:**
   * Open [README.md](/README.md) and append or modify the target row inside the Markdown table.
   * Make sure to follow the existing row structure:
     `| ID | Repo | Repo_Stars | User_Stars | Description | Core Technology |`
   * Run [check_table.py](/check_table.py) to verify links and badges.
   * Run [sort_table.py](/sort_table.py) to sort the table by star counts.
   * Run [fix_serials.py](/fix_serials.py) to clean up the numbering.

2. **Commit Guidelines:**
   * Keep commits focused and descriptive (e.g., `feat: add new AI repo X`, `docs: fix typo in README`).
   * Verify scripts run without errors prior to committing.

---

## 🌐 SaaS Products Pricing Info

This project interacts with the following SaaS platforms. Refer to their pricing details and free tier limits below:

| SaaS Product | Pricing Model | Free Tier Details / Limits |
| :--- | :--- | :--- |
| **GitHub** | Freemium | Free for public/private repositories. Unauthenticated API: 60 requests/hr. Authenticated API: 5,000 requests/hr. |
| **Heroku** (custom-icon-badges) | Paid | No free tier available. Pricing starts at $5/month for basic dynos. |
| **Cloudflare Workers** (github-star-counter) | Freemium | Free tier includes 100,000 requests/day. Paid starts at $5/month. |
