import os
import sys
import pytest
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from lib.transcript.transcriber import Transcriber

# Store command line arguments before they're processed by pytest
_ORIGINAL_ARGS = sys.argv[1:]

def parse_args():
    parser = argparse.ArgumentParser(description='Test audio transcription')
    parser.add_argument('audio_path', help='Path to the audio file for testing')
    parser.add_argument('--language', '-l', 
                       choices=['auto', 'zh', 'en', 'yue', 'ja', 'ko'],
                       default='auto',
                       help='Language for transcription')
    
    # Parse stored arguments
    if _ORIGINAL_ARGS:
        return parser.parse_args(_ORIGINAL_ARGS)
    else:
        # For running with pytest directly
        return parser.parse_args(['--help'])

class TestTranscriber:
    @pytest.fixture(scope="class")
    def setup_test(self):
        """Setup test environment"""
        try:
            args = parse_args()
            
            if args.audio_path and not os.path.exists(args.audio_path):
                pytest.skip(f"Audio file not found: {args.audio_path}")
            
            yield {
                'audio_path': args.audio_path,
                'language': args.language
            }
        except SystemExit:
            pytest.skip("No audio path provided")
    
    @pytest.fixture(scope="class")
    def transcriber(self):
        """Initialize transcriber"""
        try:
            transcriber = Transcriber()
            print("\nInitialized transcriber successfully")
            return transcriber
        except Exception as e:
            pytest.skip(f"Failed to initialize transcriber: {str(e)}")
    
    def test_device_detection(self, transcriber):
        """Test device detection"""
        device = transcriber._detect_device()
        assert device in ['mps', 'cuda', 'cpu']
        print(f"\nUsing device: {device}")
    
    def test_transcribe(self, transcriber, setup_test):
        """Test transcription with specified language"""
        if not setup_test:
            pytest.skip("Setup failed - no audio path provided")
        
        audio_path = setup_test['audio_path']
        language = setup_test['language']
        
        # Show progress
        print(f"\nStarting transcription:")
        print(f"Audio file: {audio_path}")
        print(f"Language: {language}")
        
        # Perform transcription
        result = transcriber.transcribe(audio_path, language=language)
        
        # Basic validation
        assert isinstance(result, dict)
        assert 'text' in result
        assert len(result['text']) > 0
        
        # Print results
        print("\n" + "="*80)
        print("TRANSCRIPTION RESULTS")
        print("="*80)
        print(f"Input file: {result['file_name']}")
        print(f"Detected language: {result['language']}")
        print("\nTranscribed text:")
        print("-"*80)
        print(result['text'])
        print("-"*80)
        
        if result.get('segments'):
            print("\nSegments:")
            for i, segment in enumerate(result['segments'], 1):
                print(f"\nSegment {i}:")
                for key, value in segment.items():
                    print(f"{key}: {value}")
        
        return result  # Return result for potential further use

def run_transcription_test():
    """Run transcription test directly"""
    if len(_ORIGINAL_ARGS) < 1:
        print("Error: Please provide the path to the audio file")
        print("Usage: python test_transcriber.py <audio_path> [--language <lang>]")
        sys.exit(1)
    
    args = parse_args()
    
    try:
        # Initialize transcriber
        transcriber = Transcriber()
        print(f"\nInitialized transcriber")
        
        # Show device info
        device = transcriber._detect_device()
        print(f"Using device: {device}")
        
        # Perform transcription
        print(f"\nTranscribing: {args.audio_path}")
        result = transcriber.transcribe(args.audio_path, args.language)
        
        # Print results
        print("\n" + "="*80)
        print("TRANSCRIPTION RESULTS")
        print("="*80)
        print(f"Input file: {result['file_name']}")
        print(f"Detected language: {result['language']}")
        print("\nTranscribed text:")
        print("-"*80)
        print(result['text'])
        print("-"*80)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if "--pytest" in sys.argv:
        # Run with pytest
        pytest.main([__file__, "-v", "--capture=no"])
    else:
        # Run transcription directly
        run_transcription_test() 