from __future__ import annotations

from PIL import Image
from io import BytesIO
from pathlib import Path
import argparse
import pytesseract
import base64
from rich.console import Console

console = Console()

VLM_MODEL = "minicpm-v:latest"
VLM_PROMPT = """\
Look at this image. First determine what type of image it is, then respond accordingly:

- Text / document / screenshot with text: extract all text verbatim, preserving structure and layout
- Chart, graph, or diagram: describe what it shows — axes, labels, key data points, and the main insight
- Table: extract the data as a markdown table
- Photo or natural image: describe what you see in detail
- Map: describe the geography, locations, and any labels
- UI screenshot or interface: describe the layout and content of the interface
- Icon or logo: identify and describe it

Respond with only the extracted content or description. No preamble, no labels, no explanation of what you did.\
"""


def grab_image_from_clipboard() -> str | None:
    """
    Attempt to grab image from clipboard; return base64 PNG string.
    """
    import os

    if "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ:
        console.print("Image paste not available over SSH.", style="red")
        return

    import warnings
    from PIL import ImageGrab
    import io

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress PIL warnings
        image = ImageGrab.grabclipboard()

    if image:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        console.print("Image captured!", style="green")
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


def extract_text_from_base64(base64_string: str) -> str:
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


def describe_image_with_vlm(image_content) -> str:
    """Send image to VLM via Headwater and return the response text."""
    from conduit.domain.message.message import UserMessage, TextContent
    from conduit.domain.request.request import GenerationRequest
    from conduit.domain.request.generation_params import GenerationParams
    from conduit.domain.config.conduit_options import ConduitOptions
    from headwater_client.client.headwater_client import HeadwaterClient

    text_content = TextContent(text=VLM_PROMPT)
    user_message = UserMessage(content=[image_content, text_content])
    params = GenerationParams.defaults(VLM_MODEL)
    options = ConduitOptions(project_name="ocr")
    request = GenerationRequest(
        messages=[user_message],
        params=params,
        options=options,
    )
    client = HeadwaterClient()
    response = client.conduit.query_generate(request)
    return str(response)


def main():
    parser = argparse.ArgumentParser(
        description="OCR from clipboard or file. Default uses Tesseract; --llm sends to VLM."
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help="Path to an image file. If not provided, uses clipboard.",
    )
    parser.add_argument(
        "--llm",
        "-l",
        action="store_true",
        help=f"Use VLM ({VLM_MODEL}) via Headwater instead of Tesseract.",
    )
    args = parser.parse_args()

    if args.llm:
        from conduit.domain.message.message import ImageContent

        if args.filename:
            img = ImageContent.from_file(args.filename)
        else:
            b64 = grab_image_from_clipboard()
            if not b64:
                return
            img = ImageContent(url=f"data:image/png;base64,{b64}")
        print(describe_image_with_vlm(img))
    else:
        if args.filename:
            image_content = grab_image_from_file(args.filename)
        else:
            image_content = grab_image_from_clipboard()
        if image_content:
            extracted_text = extract_text_from_base64(image_content)
            print(extracted_text)


if __name__ == "__main__":
    main()
