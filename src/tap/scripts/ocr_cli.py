from PIL import Image
from io import BytesIO
import argparse
import pytesseract
import base64
from rich.console import Console

console = Console()


def grab_image_from_clipboard() -> str | None:
    """
    Attempt to grab image from clipboard; return tuple of mime_type and base64.
    """
    import os

    if "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ:
        console.print("Image paste not available over SSH.", style="red")
        return

    import warnings
    from PIL import ImageGrab
    import base64
    import io

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress PIL warnings
        image = ImageGrab.grabclipboard()

    if image:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        # Save for next query
        console.print("Image captured!", style="green")
        # Build our ImageMessage
        return img_base64
    else:
        console.print("No image detected.", style="red")
        import sys

        sys.exit()


def grab_image_from_file(image_file: str) -> str | None:
    """
    Attempt to grab image from a file; return base64 encoded string.
    """
    import os

    if not os.path.exists(image_file):
        console.print(f"File {image_file} does not exist.", style="red")
        return None

    with open(image_file, "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()
        console.print("Image loaded from file!", style="green")
        return img_base64


def extract_text_from_base64(base64_string):
    # Remove data URL prefix if present
    if base64_string.startswith("data:image"):
        base64_string = base64_string.split(",")[1]

    # Decode base64 to bytes
    image_bytes = base64.b64decode(base64_string)

    # Convert bytes to PIL Image
    image = Image.open(BytesIO(image_bytes))

    # Extract text using pytesseract
    text = pytesseract.image_to_string(image)

    return text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="OCR from clipboard or base64 string. Default is clipboard."
    )
    # add an imagefile positional required argument
    parser.add_argument(
        "filename",
        nargs="?",
        help="Path to an image file to perform OCR on. If not provided, will use clipboard.",
    )
    args = parser.parse_args()

    if args.filename:
        image_content = grab_image_from_file(args.filename)
    else:
        image_content = grab_image_from_clipboard()
    if image_content:
        extracted_text = extract_text_from_base64(image_content)
        print(extracted_text)


if __name__ == "__main__":
    main()
