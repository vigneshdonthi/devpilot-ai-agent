import requests

from langchain_core.tools import tool


def parse_github_url(repo_url: str):
    """Extract the owner and repository name from a GitHub URL."""

    repo_url = repo_url.rstrip("/")

    parts = repo_url.split("/")

    if len(parts) < 2:
        return None, None

    owner = parts[-2]
    repo = parts[-1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    return owner, repo


def get_default_branch(owner: str, repo: str, headers: dict):
    """Get the default branch of a GitHub repository."""

    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:
        return None

    data = response.json()

    return data.get("default_branch", "main")


@tool
def get_github_repo_info(repo_url: str) -> str:
    """Get metadata, languages, and recent open issues for a public GitHub repository."""

    owner, repo = parse_github_url(repo_url)

    if not owner or not repo:
        return "Invalid GitHub repository URL."

    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    try:

        # -----------------------------
        # Repository metadata
        # -----------------------------

        repo_response = requests.get(
            base_url,
            headers=headers,
            timeout=10
        )

        if repo_response.status_code == 404:
            return "Repository not found or repository is private."

        if repo_response.status_code != 200:
            return (
                "GitHub repository request failed with status "
                f"{repo_response.status_code}"
            )

        repo_data = repo_response.json()

        # -----------------------------
        # Languages
        # -----------------------------

        languages_response = requests.get(
            f"{base_url}/languages",
            headers=headers,
            timeout=10
        )

        languages = {}

        if languages_response.status_code == 200:
            languages = languages_response.json()

        # -----------------------------
        # Recent issues
        # -----------------------------

        issues_response = requests.get(
            f"{base_url}/issues",
            headers=headers,
            params={
                "state": "open",
                "per_page": 5
            },
            timeout=10
        )

        issues = []

        if issues_response.status_code == 200:

            for issue in issues_response.json():

                # GitHub issues endpoint also returns pull requests
                if "pull_request" in issue:
                    continue

                issue_number = issue.get("number")
                issue_title = issue.get("title")

                issues.append(
                    f"#{issue_number} - {issue_title}"
                )

        language_names = list(languages.keys())

        report = f"""
GitHub Repository Report
------------------------

Repository:
{repo_data.get("full_name")}

Description:
{repo_data.get("description") or "No description"}

Primary Language:
{repo_data.get("language") or "Unknown"}

Languages:
{", ".join(language_names) if language_names else "Unknown"}

Stars:
{repo_data.get("stargazers_count", 0)}

Forks:
{repo_data.get("forks_count", 0)}

Open Issues Count:
{repo_data.get("open_issues_count", 0)}

Default Branch:
{repo_data.get("default_branch")}

Last Updated:
{repo_data.get("updated_at")}

Recent Open Issues:
{chr(10).join("- " + issue for issue in issues) if issues else "None found"}
"""

        return report.strip()

    except requests.RequestException as e:
        return f"GitHub connection error: {str(e)}"

    except Exception as e:
        return f"GitHub repository analysis failed: {str(e)}"


@tool
def get_github_repo_tree(repo_url: str) -> str:
    """Get the file structure of a public GitHub repository so files can be discovered before reading them."""

    owner, repo = parse_github_url(repo_url)

    if not owner or not repo:
        return "Invalid GitHub repository URL."

    headers = {
        "Accept": "application/vnd.github+json"
    }

    try:

        # -----------------------------
        # Find default branch
        # -----------------------------

        default_branch = get_default_branch(
            owner,
            repo,
            headers
        )

        if not default_branch:
            return "Unable to determine repository default branch."

        # -----------------------------
        # Request Git tree
        # -----------------------------

        tree_url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/git/trees/{default_branch}"
        )

        response = requests.get(
            tree_url,
            headers=headers,
            params={
                "recursive": "1"
            },
            timeout=15
        )

        if response.status_code == 404:
            return "Repository tree not found."

        if response.status_code != 200:
            return (
                "GitHub tree request failed with status "
                f"{response.status_code}"
            )

        data = response.json()

        files = []

        # -----------------------------
        # Extract files
        # -----------------------------

        for item in data.get("tree", []):

            if item.get("type") == "blob":

                path = item.get("path")

                if path:
                    files.append(path)

        if not files:
            return "No files found in the repository."

        # Avoid sending huge repositories to the LLM
        max_files = 300

        displayed_files = files[:max_files]

        file_list = "\n".join(
            f"- {file}"
            for file in displayed_files
        )

        report = f"""
GitHub Repository Tree
----------------------

Repository:
{owner}/{repo}

Default Branch:
{default_branch}

Total Files:
{len(files)}

Files:
{file_list}
"""

        if len(files) > max_files:
            report += (
                f"\n\nOnly the first {max_files} files "
                f"are shown out of {len(files)}."
            )

        return report.strip()

    except requests.RequestException as e:
        return f"GitHub connection error: {str(e)}"

    except Exception as e:
        return f"GitHub tree analysis failed: {str(e)}"


@tool
def read_github_file(
    repo_url: str,
    file_path: str
) -> str:
    """Read the contents of a specific text or source-code file from a public GitHub repository."""

    owner, repo = parse_github_url(repo_url)

    if not owner or not repo:
        return "Invalid GitHub repository URL."

    headers = {
        "Accept": "application/vnd.github.raw+json"
    }

    try:

        # -----------------------------
        # Find default branch
        # -----------------------------

        metadata_headers = {
            "Accept": "application/vnd.github+json"
        }

        default_branch = get_default_branch(
            owner,
            repo,
            metadata_headers
        )

        if not default_branch:
            return "Unable to determine repository default branch."

        # -----------------------------
        # Request file
        # -----------------------------

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{file_path}"
        )

        response = requests.get(
            url,
            headers=headers,
            params={
                "ref": default_branch
            },
            timeout=15
        )

        if response.status_code == 404:
            return f"File not found: {file_path}"

        if response.status_code != 200:
            return (
                "GitHub file request failed with status "
                f"{response.status_code}"
            )

        content = response.text

        # -----------------------------
        # Protect the LLM context
        # -----------------------------

        max_characters = 20_000

        truncated = False

        if len(content) > max_characters:

            content = content[:max_characters]

            truncated = True

        report = f"""
GitHub File
-----------

Repository:
{owner}/{repo}

Branch:
{default_branch}

File:
{file_path}

Content:

{content}
"""

        if truncated:
            report += (
                "\n\nWARNING: File was truncated because "
                "it exceeded 20,000 characters."
            )

        return report.strip()

    except requests.RequestException as e:
        return f"GitHub connection error: {str(e)}"

    except Exception as e:
        return f"GitHub file reading failed: {str(e)}"