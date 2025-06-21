from typing import Dict, List, Optional

def validate_story_request(data: Dict) -> Optional[str]:
    """Validate story generation request data"""
    if not data:
        return "No data provided"
    
    # Validate keywords
    keywords = data.get('keywords', [])
    if not keywords or not isinstance(keywords, list):
        return "Keywords must be provided as a list"
    
    if len(keywords) == 0:
        return "At least one keyword is required"
    
    if len(keywords) > 10:
        return "Maximum 10 keywords allowed"
    
    # Validate theme
    valid_themes = ['adventure', 'mystery', 'romance', 'fantasy', 'comedy', 'horror', 'children']
    theme = data.get('theme', 'adventure')
    if theme not in valid_themes:
        return f"Theme must be one of: {', '.join(valid_themes)}"
    
    # Validate duration
    valid_durations = [1, 3, 5, 10]
    duration = data.get('duration', 3)
    try:
        duration = int(duration)
        if duration not in valid_durations:
            return f"Duration must be one of: {', '.join(map(str, valid_durations))} minutes"
    except (ValueError, TypeError):
        return "Duration must be a valid integer"
    
    # Validate moods
    valid_moods = ['excitement', 'joy', 'sadness', 'anger', 'fear', 'surprise', 'calm', 'mysterious', 'neutral']
    moods = data.get('moods', ['neutral'])
    if not isinstance(moods, list):
        return "Moods must be provided as a list"
    
    if len(moods) == 0:
        return "At least one mood is required"
    
    for mood in moods:
        if mood not in valid_moods:
            return f"Invalid mood '{mood}'. Valid moods: {', '.join(valid_moods)}"
    
    return None  # No validation errors

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove any characters that aren't alphanumeric, dash, underscore, or dot
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return sanitized[:100]  # Limit length
