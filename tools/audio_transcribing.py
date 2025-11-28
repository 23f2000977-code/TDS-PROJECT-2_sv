from langchain.tools import tool
import speech_recognition as sr
import os
import subprocess
import shutil

@tool
def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an MP3 or WAV audio file into text using Google's Web Speech API.
    Uses system ffmpeg directly, with NO pydub dependency.
    """
    try:
        # Resolve full path
        file_path = os.path.join("LLMFiles", file_path)
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"

        # Check if ffmpeg is installed
        if not shutil.which("ffmpeg"):
            return "Error: ffmpeg is not installed or not in PATH."

        # Determine output path
        if file_path.lower().endswith(".mp3"):
            wav_path = file_path.replace(".mp3", ".wav")
            
            # Use subprocess to convert MP3 -> WAV (16kHz, Mono)
            command = [
                "ffmpeg", "-y", "-i", file_path, 
                "-ac", "1", "-ar", "16000", 
                wav_path
            ]
            
            # Run conversion and capture errors
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error: FFmpeg conversion failed.\nStderr: {result.stderr}"
            
            final_path = wav_path
        else:
            final_path = file_path

        # Speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(final_path) as source:
            # Read the audio file
            audio_data = recognizer.record(source)
            try:
                # Transcribe
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Error: Audio was unclear or silent."
            except sr.RequestError as e:
                return f"Error: Google API error: {e}"

    except Exception as e:
        return f"Error processing audio: {str(e)}"