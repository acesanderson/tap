from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play
import argparse, sys


def play_mp3(mp3_file_path: str | Path):
    """
    Play an MP3 file using pydub.
    """
    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file_path)
    # Play the audio
    play(audio)


def main():
    parser = argparse.ArgumentParser(description="Play an MP3 file.")
    parser.add_argument("mp3_file", type=str, help="Path to the MP3 file to play.")
    args = parser.parse_args()
    # Detect if no input; if so, print help message and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    mp3_file_path = Path(args.mp3_file)
    if not mp3_file_path.is_file():
        print(f"Error: The file '{mp3_file_path}' does not exist.")
        return
    if mp3_file_path.suffix != ".mp3":
        raise FileError(f"Error: The file '{mp3_file_path}' is not an MP3 file.")
    play_mp3(mp3_file_path)


if __name__ == "__main__":
    main()
