from contex.database.obsidian.obsidian_path import get_obsidian_path
import os

OBSIDIAN_PATH = get_obsidian_path()


def get_titles() -> list[str]:
    # Go through Obsidian vault folder and get all file names for *.md files, without the .md extension
    titles = []
    for root, dirs, files in os.walk(OBSIDIAN_PATH):
        for file in files:
            if file.endswith(".md"):
                titles.append(os.path.splitext(file)[0])

    titles = sorted(titles)
    return titles
