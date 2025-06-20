from transformers import pipeline
import re
from typing import List, Dict
import logging

class EmotionAnalyzer:
    def __init__(self):
        try:
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1  # Use CPU for better compatibility
            )
            logging.info("Emotion Analyzer initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing emotion analyzer: {e}")
            self.emotion_classifier = None
        
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
        """Analyze emotions in story text and return segments with emotion data"""
        if not self.emotion_classifier:
            # Fallback to simple emotion assignment
            return self._fallback_emotion_analysis(story_text, preferred_moods)
        
        # Split story into sentences
        sentences = re.split(r'[.!?]+', story_text)
        emotional_segments = []
        
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
                # Use AI emotion detection
                try:
                    emotion_result = self.emotion_classifier(sentence)[0]
                    emotion = emotion_result['label'].lower()
                    confidence = emotion_result['score']
                except Exception as e:
                    logging.warning(f"Error in emotion classification: {e}")
                    emotion = 'neutral'
                    confidence = 0.5
            
            # Bias towards preferred moods
            if preferred_moods and emotion not in preferred_moods:
                emotion = self._select_best_mood(emotion, preferred_moods)
            
            murf_style = self.emotion_to_murf_style.get(emotion, 'conversational')
            
            emotional_segments.append({
                'text': clean_sentence,
                'emotion': emotion,
                'murf_style': murf_style,
                'confidence': confidence
            })
        
        return emotional_segments
    
    def _fallback_emotion_analysis(self, story_text: str, preferred_moods: List[str]) -> List[Dict]:
        """Fallback emotion analysis when AI model is not available"""
        sentences = re.split(r'[.!?]+', story_text)
        emotional_segments = []
        default_mood = preferred_moods[0] if preferred_moods else 'neutral'
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            emotional_segments.append({
                'text': sentence,
                'emotion': default_mood,
                'murf_style': self.emotion_to_murf_style.get(default_mood, 'conversational'),
                'confidence': 0.7
            })
        
        return emotional_segments
    
    def _select_best_mood(self, detected_emotion: str, preferred_moods: List[str]) -> str:
        """Select the best mood from preferred moods based on detected emotion"""
        emotion_families = {
            'positive': ['joy', 'happiness', 'excitement', 'calm'],
            'negative': ['sadness', 'anger', 'fear'],
            'neutral': ['neutral', 'surprise']
        }
        
        for mood in preferred_moods:
            for family, emotions in emotion_families.items():
                if mood in emotions and detected_emotion in emotions:
                    return mood
        
        return preferred_moods[0]  # Default to first preferred mood
