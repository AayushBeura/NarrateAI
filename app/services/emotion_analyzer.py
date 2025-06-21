import logging
from typing import List, Dict
import re

class EmotionAnalyzer:
    def __init__(self):
        # Simplified version without transformers to avoid NumPy issues
        logging.info("Emotion Analyzer initialized successfully (simplified version)")
        
        # Mapping emotions to Murf AI voice styles
        self.emotion_to_murf_style = {
            'joy': 'excited',
            'happiness': 'excited',
            'excitement': 'excited',
            'sadness': 'sad',
            'sad': 'sad',
            'anger': 'angry',
            'angry': 'angry',
            'fear': 'terrified',
            'scared': 'terrified',
            'surprise': 'excited',
            'neutral': 'conversational',
            'calm': 'calm',
            'peaceful': 'calm',
            'mysterious': 'conversational',
            'dramatic': 'conversational'
        }
    
    def analyze_story_emotions(self, story_text: str, preferred_moods: List[str]) -> List[Dict]:
        """Analyze emotions in story text using rule-based approach"""
        # Split story into sentences
        sentences = re.split(r'[.!?]+', story_text)
        emotional_segments = []
        
        # Use preferred moods in rotation for simplicity
        mood_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            # Extract emotional cues from parentheses
            emotional_cues = re.findall(r'\((.*?)\)', sentence)
            clean_sentence = re.sub(r'\([^)]*\)', '', sentence).strip()
            
            if emotional_cues:
                # Use explicit emotional cue
                emotion = emotional_cues[0].lower()
                confidence = 0.9
            else:
                # Use preferred moods in rotation
                if preferred_moods:
                    emotion = preferred_moods[mood_index % len(preferred_moods)]
                    mood_index += 1
                else:
                    emotion = 'neutral'
                confidence = 0.7
            
            murf_style = self.emotion_to_murf_style.get(emotion, 'conversational')
            
            emotional_segments.append({
                'text': clean_sentence,
                'emotion': emotion,
                'murf_style': murf_style,
                'confidence': confidence
            })
        
        return emotional_segments
