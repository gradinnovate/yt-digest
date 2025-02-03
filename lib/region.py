from enum import Enum
from typing import Optional, Dict, ClassVar

class Region(Enum):
    """Region codes for different platforms"""
    
    # Common regions
    TAIWAN = "TW"
    HONG_KONG = "HK"
    JAPAN = "JP"
    KOREA = "KR"
    USA = "US"
    SINGAPORE = "SG"
    GLOBAL = "GLOBAL"
    
    def __str__(self) -> str:
        """Return the region code string"""
        return self.value
    
    @classmethod
    def from_code(cls, code: str) -> Optional['Region']:
        """
        Get Region enum from region code
        
        Args:
            code: Region code string (e.g., 'TW', 'US')
            
        Returns:
            Region enum if found, None otherwise
        """
        try:
            return cls(code.upper())
        except ValueError:
            return None
    
    def get_twitter_woeid(self) -> int:
        """Get Twitter WOEID for this region"""
        return _TWITTER_WOEID.get(self.value, _TWITTER_WOEID["GLOBAL"])
    
    def get_google_code(self) -> str:
        """Get Google Trends region code"""
        return _GOOGLE_TRENDS_CODE.get(self.value, _GOOGLE_TRENDS_CODE["GLOBAL"])
    
    def get_youtube_code(self) -> Optional[str]:
        """Get YouTube region code"""
        return _YOUTUBE_REGION_CODE.get(self.value, _YOUTUBE_REGION_CODE["GLOBAL"])
    
    @classmethod
    def get_supported_regions(cls) -> Dict[str, 'Region']:
        """
        Get all supported regions
        
        Returns:
            Dictionary of region codes to Region enums
        """
        return {region.value: region for region in cls}
    
    @classmethod
    def is_valid_code(cls, code: str) -> bool:
        """Check if a region code is valid"""
        return code.upper() in [region.value for region in cls]

# Platform-specific region mappings defined outside the class
_TWITTER_WOEID: Dict[str, int] = {
    "TW": 23424971,  # Taiwan
    "HK": 24865698,  # Hong Kong
    "JP": 23424856,  # Japan
    "KR": 23424868,  # South Korea
    "US": 23424977,  # United States
    "SG": 23424948,  # Singapore
    "GLOBAL": 1      # Worldwide
}

_GOOGLE_TRENDS_CODE: Dict[str, str] = {
    "TW": "TW",
    "HK": "HK",
    "JP": "JP",
    "KR": "KR",
    "US": "US",
    "SG": "SG",
    "GLOBAL": "WORLDWIDE"
}

_YOUTUBE_REGION_CODE: Dict[str, Optional[str]] = {
    "TW": "TW",
    "HK": "HK",
    "JP": "JP",
    "KR": "KR",
    "US": "US",
    "SG": "SG",
    "GLOBAL": None  # YouTube API uses None for global
}
