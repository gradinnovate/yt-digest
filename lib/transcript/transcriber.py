import os
import torch
from typing import Dict, Optional, List
from pathlib import Path
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

class Transcriber:
    def __init__(self, model_dir: str = "iic/SenseVoiceSmall"):
        """
        Initialize transcriber with SenseVoice model
        
        Args:
            model_dir: Path to the model directory or model name
        """
        try:
            # Auto detect best available device
            device = self._detect_device()
            print(f"Using device: {device}")
            
            self.model = AutoModel(
                model=model_dir,
                trust_remote_code=True,
                remote_code="./model.py",
                vad_model="fsmn-vad",
                vad_kwargs={"max_single_segment_time": 30000},
                disable_update=True,
                device=device
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize transcriber: {str(e)}")
    
    @staticmethod
    def _detect_device() -> str:
        """
        Detect the best available device for model inference
        
        Returns:
            str: 'mps' for Apple Silicon, 'cuda' for NVIDIA GPU, 'cpu' for CPU
        """
        if torch.backends.mps.is_available():
            return "mps"  # Apple Silicon GPU
        elif torch.cuda.is_available():
            return "cuda"  # NVIDIA GPU
        else:
            return "cpu"   # CPU fallback
    
    def transcribe(self, 
                  audio_path: str, 
                  language: str = "auto",
                  batch_size_s: int = 60,
                  merge_length_s: int = 15) -> Dict[str, any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code ('auto', 'zh', 'en', 'yue', 'ja', 'ko')
            batch_size_s: Batch size in seconds
            merge_length_s: Length for merging segments in seconds
            
        Returns:
            Dictionary containing transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Generate transcription
            result = self.model.generate(
                input=audio_path,
                cache={},
                language=language,
                use_itn=True,
                batch_size_s=batch_size_s,
                merge_vad=True,
                merge_length_s=merge_length_s
            )
            
            # Post-process the text
            processed_text = rich_transcription_postprocess(result[0]["text"])
            
            # Get segments if available
            segments = result[0].get("segments", [])
            
            return {
                'text': processed_text,
                'segments': segments,
                'language': result[0].get("lang", language),
                'audio_path': audio_path,
                'file_name': Path(audio_path).name
            }
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def transcribe_batch(self, 
                        audio_files: List[str], 
                        language: str = "auto") -> List[Dict[str, any]]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_files: List of paths to audio files
            language: Language code ('auto', 'zh', 'en', 'yue', 'ja', 'ko')
            
        Returns:
            List of transcription results
        """
        results = []
        for audio_path in audio_files:
            try:
                result = self.transcribe(audio_path, language)
                results.append(result)
            except Exception as e:
                print(f"Failed to transcribe {audio_path}: {str(e)}")
                results.append({
                    'error': str(e),
                    'audio_path': audio_path,
                    'file_name': Path(audio_path).name
                })
        return results 