def parse_duration(duration: str) -> int:
    """Convert ISO 8601 duration to seconds
    
    Args:
        duration: Duration string in ISO 8601 format (e.g. 'PT1H2M10S')
        
    Returns:
        Duration in seconds
        
    Examples:
        >>> parse_duration('PT7M32S')
        452
        >>> parse_duration('PT1H2M10S')
        3730
    """
    # Remove PT from start
    duration = duration.replace('PT', '')
    seconds = 0
    
    # Handle hours
    if 'H' in duration:
        hours, duration = duration.split('H')
        seconds += int(hours) * 3600
    
    # Handle minutes
    if 'M' in duration:
        minutes, duration = duration.split('M')
        seconds += int(minutes) * 60
    
    # Handle seconds
    if 'S' in duration:
        s, _ = duration.split('S')
        seconds += int(s)
    
    return seconds
