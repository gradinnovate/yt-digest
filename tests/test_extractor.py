import os
import sys
import pytest
from pathlib import Path
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from lib.ffmpeg.extractor import FFmpegExtractor

# Store command line arguments before they're processed by pytest
_ORIGINAL_ARGS = sys.argv[1:]

def parse_args():
    # Use stored arguments instead of sys.argv
    parser = argparse.ArgumentParser(description='Test FFmpeg audio extraction')
    parser.add_argument('video_path', help='Path to the video file for testing')
    parser.add_argument('--output-dir', '-o', 
                       default=os.path.join(project_root, "tests", "test_data"),
                       help='Output directory for extracted audio')
    
    # Parse stored arguments
    if _ORIGINAL_ARGS:
        return parser.parse_args(_ORIGINAL_ARGS)
    else:
        # For running with pytest directly
        return parser.parse_args(['--help'])

class TestFFmpegExtractor:
    @pytest.fixture(scope="class")
    def setup_test(self):
        """Setup test environment"""
        try:
            args = parse_args()
            
            if args.video_path and not os.path.exists(args.video_path):
                pytest.skip(f"Video file not found: {args.video_path}")
                
            # Create output directory
            os.makedirs(args.output_dir, exist_ok=True)
            
            yield {
                'video_path': args.video_path,
                'output_dir': args.output_dir,
                'video_id': Path(args.video_path).stem  # Get filename without extension
            }
        except SystemExit:
            pytest.skip("No video path provided")
    
    def test_ffmpeg_initialization(self):
        """Test FFmpeg extractor initialization"""
        try:
            extractor = FFmpegExtractor()
            assert isinstance(extractor, FFmpegExtractor)
        except RuntimeError as e:
            pytest.skip(f"FFmpeg not installed: {str(e)}")
    
    def test_extract_audio(self, setup_test):
        """Test audio extraction from video"""
        if not setup_test:
            pytest.skip("Setup failed - no video path provided")
            
        extractor = FFmpegExtractor()
        video_path = setup_test['video_path']
        output_dir = setup_test['output_dir']
        video_id = setup_test['video_id']
        
        # Extract audio
        result = extractor.extract_audio(video_path, output_dir)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert all(key in result for key in ['video', 'audio', 'video_id'])
        
        # Verify paths
        assert os.path.exists(result['video'])
        assert os.path.exists(result['audio'])
        assert result['video_id'] == video_id
        
        # Verify audio file format
        audio_path = result['audio']
        assert audio_path.endswith('.mp3')
        
        # Verify file sizes
        assert os.path.getsize(audio_path) > 0
        
        print("\nExtraction Results:")
        print(f"Input video: {result['video']}")
        print(f"Output audio: {result['audio']}")
        print(f"Video ID: {result['video_id']}")

def main():
    # Parse arguments before running tests
    if len(_ORIGINAL_ARGS) < 1:
        print("Error: Please provide the path to the video file")
        print("Usage: python test_extractor.py <video_path> [--output-dir <dir>]")
        sys.exit(1)
    
    # Run the tests
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    main() 