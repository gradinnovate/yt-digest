from pathlib import Path
import logging
import speech_recognition as sr

class Transcriber:
    """Audio transcription using speech recognition"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.recognizer = sr.Recognizer()
    
    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            with sr.AudioFile(str(audio_path)) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {e}")
            raise 