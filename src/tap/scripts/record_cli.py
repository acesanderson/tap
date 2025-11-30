from datetime import datetime
from pydub import AudioSegment
import pyaudio, wave, threading, os, sys


class AudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self):
        """Start recording audio"""
        self.frames = []
        self.recording = True

        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            print("🔴 Recording started... Press Enter to stop recording.")

            # Record in a separate thread
            def record():
                while self.recording:
                    try:
                        data = self.stream.read(self.chunk, exception_on_overflow=False)
                        self.frames.append(data)
                    except Exception as e:
                        print(f"Error during recording: {e}")
                        break

            record_thread = threading.Thread(target=record)
            record_thread.daemon = True
            record_thread.start()

            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            print("Make sure your microphone is accessible and try again.")
            return False

    def stop_recording(self):
        """Stop recording audio"""
        if self.recording:
            self.recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            print("⏹️  Recording stopped.")
            return True
        return False

    def save_recording(self, filename=None):
        """Save the recorded audio as WAV first, then convert to MP3"""
        if not self.frames:
            print("No audio data to save.")
            return None

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}"

        # Ensure we have the full path
        if not filename.endswith(".mp3"):
            filename += ".mp3"

        # First save as WAV (temporary)
        temp_wav = filename.replace(".mp3", ".wav")

        try:
            # Save WAV file
            wf = wave.open(temp_wav, "wb")
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(self.frames))
            wf.close()

            # Convert WAV to MP3
            audio_segment = AudioSegment.from_wav(temp_wav)
            audio_segment.export(filename, format="mp3", bitrate="192k")

            # Remove temporary WAV file
            os.remove(temp_wav)

            print(f"💾 Recording saved as: {filename}")
            return filename

        except Exception as e:
            print(f"Error saving recording: {e}")
            return None

    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()


def main():
    print("🎙️  AudioMemos Clone - Command Line Audio Recorder")
    print("=" * 50)

    recorder = AudioRecorder()

    try:
        while True:
            print("\nOptions:")
            print("1. Start new recording")
            print("2. Exit")

            choice = input("\nSelect option (1-2): ").strip()

            if choice == "1":
                # Confirm recording start
                confirm = input("Ready to start recording? (y/n): ").strip().lower()
                if confirm in ["y", "yes"]:
                    if recorder.start_recording():
                        # Wait for user to press Enter to stop
                        input()  # This blocks until user presses Enter

                        if recorder.stop_recording():
                            # Ask for filename
                            custom_name = input(
                                "Enter filename (or press Enter for auto-generated): "
                            ).strip()
                            filename = custom_name if custom_name else None

                            saved_file = recorder.save_recording(filename)
                            if saved_file:
                                print(f"✅ Successfully saved: {saved_file}")
                    else:
                        print("❌ Failed to start recording.")
                else:
                    print("Recording cancelled.")

            elif choice == "2":
                print("👋 Goodbye!")
                break
            else:
                print("Invalid option. Please select 1 or 2.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Recording interrupted by user.")
        recorder.stop_recording()

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

    finally:
        recorder.cleanup()


if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pyaudio
        import pydub
    except ImportError as e:
        print("❌ Missing required packages!")
        print("Please install required packages:")
        print("pip install pyaudio pydub")
        print("\nFor macOS, you might also need:")
        print("brew install portaudio")
        print("brew install ffmpeg")
        sys.exit(1)

    main()
