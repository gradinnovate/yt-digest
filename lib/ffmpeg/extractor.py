import subprocess
import os
from typing import Dict, Optional

class FFmpegExtractor:
    def __init__(self):
        """
        Initialize FFmpeg extractor
        Raises RuntimeError if ffmpeg is not installed
        """
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("FFmpeg is not installed. Please install FFmpeg first.")

    def extract_audio(self, video_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save extracted audio (default: same as video)
            
        Returns:
            Dict containing paths to the original video and extracted audio
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Get directory and filename
        video_dir = os.path.dirname(video_path)
        video_id = os.path.splitext(os.path.basename(video_path))[0]
        
        # Use provided output directory or video directory
        output_dir = output_dir or video_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output audio path
        audio_path = os.path.join(output_dir, f"{video_id}.mp3")
        
        try:
            # Extract audio using FFmpeg
            command = [
                'ffmpeg',
                '-i', video_path,  # Input video
                '-vn',  # Disable video
                '-acodec', 'libmp3lame',  # Use MP3 codec
                '-q:a', '4',  # Audio quality (0-9, lower is better)
                '-y',  # Overwrite output file
                audio_path
            ]
            
            # Run FFmpeg command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not os.path.exists(audio_path):
                raise RuntimeError("Audio extraction failed: Output file not created")
            
            return {
                'video': video_path,
                'audio': audio_path,
                'video_id': video_id
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg error: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio: {str(e)}")
