import yt_dlp
import os
import yaml
from typing import Dict, Optional
from urllib.parse import parse_qs, urlparse
from ..ffmpeg.extractor import FFmpegExtractor

class YouTubeDownloader:
    def __init__(self, config_path: str = "config.yaml"):
        # Load config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            yt_config = config['youtube']['download']
        
        self.output_dir = yt_config['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configure yt-dlp options from yaml config
        self.ydl_opts = {
            'format': yt_config['video']['format'],
            # Use video ID in filename
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'writesubtitles': yt_config['subtitles']['enabled'],
            'writeautomaticsub': yt_config['subtitles']['auto_generate'],
            'subtitleslangs': yt_config['subtitles']['languages'],
        }
        
        # Only add postprocessors if enabled
        if yt_config['video']['postprocess']['enabled']:
            self.ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
            self.ydl_opts['postprocessor_args'] = [
                '-vf', yt_config['video']['postprocess']['video_scale'],
                '-b:v', yt_config['video']['postprocess']['video_bitrate'],
                '-b:a', yt_config['video']['postprocess']['audio_bitrate'],
            ]
        
        self.ffmpeg = FFmpegExtractor()
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """Extract video ID from YouTube URL"""
        # Handle different URL formats
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed_url.path[1:]
        if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith(('/embed/', '/v/')):
                return parsed_url.path.split('/')[2]
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def download_video(self, url: str, extract_audio: bool = False) -> Dict[str, str]:
        """
        Download a YouTube video and optionally extract audio
        
        Args:
            url: YouTube video URL
            extract_audio: Whether to extract audio from video
            
        Returns:
            Dict containing paths to downloaded files and metadata
        """
        try:
            video_id = self.extract_video_id(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = os.path.join(self.output_dir, f"{video_id}.mp4")
                
                # Get subtitle paths if available
                subtitles = {}
                if info.get('requested_subtitles'):
                    for lang, sub_info in info['requested_subtitles'].items():
                        sub_path = os.path.join(self.output_dir, f"{video_id}.{lang}.vtt")
                        if os.path.exists(sub_path):
                            subtitles[lang] = sub_path
                
                result = {
                    'video': video_path,
                    'subtitles': subtitles,
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                    'description': info.get('description', ''),
                    'id': video_id
                }
                
                # Extract audio if requested
                if extract_audio:
                    audio_result = self.ffmpeg.extract_audio(video_path)
                    result['audio'] = audio_result['audio']
                
                return result
                
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")
    
    def download_captions(self, url: str) -> Dict[str, str]:
        """
        Download available captions for a YouTube video
        Returns a dictionary of language codes and caption file paths
        """
        try:
            video_id = self.extract_video_id(url)
            
            caption_opts = {
                **self.ydl_opts,
                'skip_download': True,  # Skip video download
                'writesubtitles': True,
                'writeautomaticsub': True,
            }
            
            with yt_dlp.YoutubeDL(caption_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                captions = {}
                if info.get('requested_subtitles'):
                    for lang, _ in info['requested_subtitles'].items():
                        caption_path = os.path.join(self.output_dir, f"{video_id}.{lang}.vtt")
                        if os.path.exists(caption_path):
                            captions[lang] = caption_path
                
                return captions
                
        except Exception as e:
            raise Exception(f"Failed to download captions: {str(e)}") 