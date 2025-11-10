"""
GitHub repository processing for the Flatten tool.
Handles fetching and flattening GitHub repositories into XML format.
"""

import os
import zipfile
from io import BytesIO
from typing import Iterator, Tuple
import requests

from siphon.ingestion.github.flatten_xml import (
    package_to_xml,
    should_exclude_path,
    should_include_file,
)


def parse_github_url(github_url: str) -> tuple[str, dict]:
    """
    Convert a GitHub URL to a zipball API URL with better error handling.
    Also retrieve metadata through GH API.
    """
    parts = github_url.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL format")

    owner = parts[-2]
    repo = parts[-1]

    from github import Github
    import os

    # Initialize GitHub API client
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo_obj = g.get_repo(f"{owner}/{repo}")
    # Extract metadata

    metadata = {
        # Standard online metadata
        "url": repo_obj.url,
        "domain": "github.com",
        "title": f"{owner}/{repo}",
        "published_date": int(repo_obj.created_at.timestamp()),
        # GitHub-specific
        "stars": repo_obj.stargazers_count,
        "language": repo_obj.language,
        "topics": repo_obj.topics,
        "description": repo_obj.description,
        "updated_at": int(repo_obj.updated_at.timestamp()),
        "pushed_at": int(repo_obj.pushed_at.timestamp()),
        "size": repo_obj.size,
    }

    # First try to get the default branch
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    try:
        # Get repository info to find default branch
        repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(repo_info_url, headers=headers)

        if response.status_code == 200:
            repo_data = response.json()
            default_branch = repo_data.get("default_branch", "main")
        else:
            print(
                f"Warning: Could not get repo info (status {response.status_code}), defaulting to 'main'"
            )
            default_branch = "main"
    except Exception as e:
        print(f"Warning: Error getting repo info: {e}, defaulting to 'main'")
        default_branch = "main"

    zipball_url = (
        f"https://api.github.com/repos/{owner}/{repo}/zipball/{default_branch}"
    )
    print(f"Using zipball URL: {zipball_url}")

    return zipball_url, metadata


def download_github_repo(repo_url: str) -> zipfile.ZipFile:
    """
    Download a GitHub repository as a zip file with better error handling.
    """
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    print(f"Downloading from: {repo_url}")
    print(f"Using token: {'Yes' if token else 'No'}")

    response = requests.get(repo_url, headers=headers)

    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")

    if response.status_code == 401:
        print("401 Unauthorized - possible causes:")
        print("1. Token expired or invalid")
        print("2. Repository is private and token lacks access")
        print("3. Token doesn't have 'repo' scope")
        raise Exception(f"Authentication failed. Check your GitHub token permissions.")
    elif response.status_code == 404:
        raise Exception(
            f"Repository not found. Check if repository exists and is accessible."
        )
    elif response.status_code != 200:
        raise Exception(
            f"Failed to fetch repository: {response.status_code} - {response.text}"
        )

    zip_data = BytesIO(response.content)
    return zipfile.ZipFile(zip_data, "r")


def get_repo_name_from_zip(zip_file: zipfile.ZipFile) -> str:
    """Extract the repository name from the zip file structure."""
    file_list = zip_file.namelist()
    if file_list:
        # GitHub adds a hash prefix like "repo-abc123/"
        repo_name = file_list[0].split("/")[0]
        # Clean up the repo name (remove hash suffix)
        if "-" in repo_name:
            repo_name = repo_name.split("-")[0]
        return repo_name
    return "unknown_repo"


def get_github_file_iterator(zip_file: zipfile.ZipFile) -> callable:
    """
    Return a function that iterates over files in a GitHub zip file.

    Args:
        zip_file: ZipFile object to iterate over

    Returns:
        Function that yields (file_path, filename) tuples
    """

    def iterator() -> Iterator[Tuple[str, str]]:
        file_list = zip_file.namelist()

        for file_path in file_list:
            # Skip directories (they end with /)
            if file_path.endswith("/"):
                continue

            # Skip excluded paths
            if should_exclude_path(file_path):
                continue

            # Extract filename
            filename = file_path.split("/")[-1]

            # Include only desired file types
            if should_include_file(filename):
                # Remove the GitHub repo prefix (first directory component)
                path_parts = file_path.split("/")
                if len(path_parts) > 1:
                    clean_path = "/".join(path_parts[1:])
                else:
                    clean_path = file_path

                yield (clean_path, filename)

    return iterator


def create_github_file_reader(zip_file: zipfile.ZipFile) -> callable:
    """
    Create a file reader function for GitHub zip files.

    Args:
        zip_file: ZipFile object to read from

    Returns:
        Function that reads file content by clean path
    """
    # Build mapping from clean paths to zip paths
    path_mapping = {}
    file_list = zip_file.namelist()

    for zip_path in file_list:
        if not zip_path.endswith("/"):
            path_parts = zip_path.split("/")
            if len(path_parts) > 1:
                clean_path = "/".join(path_parts[1:])
                path_mapping[clean_path] = zip_path

    def file_reader(clean_path: str) -> str:
        """Read file content from zip using clean path."""
        zip_path = path_mapping.get(clean_path, clean_path)
        with zip_file.open(zip_path) as f:
            return f.read().decode("utf-8")

    return file_reader


def flatten_github_repo(github_url: str) -> tuple[str, dict]:
    """
    Flatten a GitHub repository into XML format.

    Args:
        github_url: GitHub repository URL

    Returns:
        A tuple of:
            XML string representation of the repository
            Metadata dictionary with keys: url, domain, title, published_date

    Raises:
        Exception: If the repository cannot be fetched or processed
    """
    # Convert URL to API endpoint
    repo_url, metadata = parse_github_url(github_url)

    # Download and process the repository
    with download_github_repo(repo_url) as zip_file:
        # Extract project name
        project_name = get_repo_name_from_zip(zip_file)

        # Create iterator and reader functions
        path_iterator = get_github_file_iterator(zip_file)
        file_reader = create_github_file_reader(zip_file)

        # Generate XML
        return package_to_xml(project_name, file_reader, path_iterator), metadata
