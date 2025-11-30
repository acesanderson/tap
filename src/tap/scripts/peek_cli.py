import argparse
from pathlib import Path


def display_image_file(filename: str | Path):
    """
    Display a base64-encoded image using chafa.
    Your mileage may vary depending on the terminal and chafa version.
    """
    # Coerce to Path
    if isinstance(filename, str):
        filename = Path(filename)

    import subprocess, base64, os

    if not filename.exists():
        raise FileNotFoundError(f"File {filename} does not exist.")

    # Read binary image file and convert to base64
    with open(filename, "rb") as file:  # Note the "rb" for binary mode
        image_data = file.read()

    try:
        cmd = ["chafa", "-"]

        # If in tmux or SSH, force text mode for consistency
        if (
            os.environ.get("TMUX")
            or os.environ.get("SSH_CLIENT")
            or os.environ.get("SSH_CONNECTION")
        ):
            cmd.extend(["--format", "symbols", "--symbols", "block"])
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(input=image_data)
    except Exception as e:
        print(f"Error displaying image: {e}")


def test_display_image_file():
    from siphon.tests.fixtures.example_files import example_image_file

    display_image_file(example_image_file)


def main():
    parser = argparse.ArgumentParser(
        description="Display a base64-encoded image using chafa."
    )
    parser.add_argument(
        "filename", help="Path to the file containing the base64 image content."
    )
    args = parser.parse_args()

    filename = args.filename

    display_image_file(filename)


if __name__ == "__main__":
    # test_display_image_file()
    main()
