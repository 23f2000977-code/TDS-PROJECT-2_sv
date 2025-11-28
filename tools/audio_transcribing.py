from langchain.tools import tool
import speech_recognition as sr
import os
import subprocess

@tool
def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an MP3 or WAV audio file into text using Google's Web Speech API.
    Handles conversion using system FFmpeg directly for stability.
    """
    try:
        # Resolve full path
        file_path = os.path.join("LLMFiles", file_path)
        
        # Determine paths
        if file_path.lower().endswith(".mp3"):
            wav_path = file_path.replace(".mp3", ".wav")
            
            # --- ROBUST CONVERSION START ---
            # We use subprocess directly to avoid pydub path issues
            print(f"Converting {file_path} to {wav_path}...")
            command = [
                "ffmpeg", "-y", "-i", file_path, 
                "-ac", "1", "-ar", "16000", # Convert to Mono, 16kHz (optimal for speech recognition)
                wav_path
            ]
            
            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                return "Error: FFmpeg failed to convert audio. Is ffmpeg installed?"
            except FileNotFoundError:
                return "Error: FFmpeg not found in system PATH."
            
            final_path = wav_path
        else:
            final_path = file_path

        # Speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(final_path) as source:
            audio_data = recognizer.record(source)
            # Use show_all=True to debug if needed, but default is fine
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return "Error: Speech was unintelligible."
            except sr.RequestError as e:
                return f"Error: API unavailable: {e}"

        # Clean up wav file if we created it
        if final_path != file_path and os.path.exists(final_path):
            os.remove(final_path)

        return text
    except Exception as e:
        return f"Error occurred: {e}"