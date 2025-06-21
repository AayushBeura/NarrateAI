import requests
import os
from typing import List, Dict
import logging
import time

class AudioProcessor:
    def __init__(self):
        self.murf_api_key = os.environ.get('MURF_API_KEY')
        if not self.murf_api_key:
            raise ValueError("MURF_API_KEY environment variable not set")
        
        self.murf_base_url = "https://api.murf.ai/v1"
        
        # Voice selection based on story theme
        self.theme_voices = {
            'adventure': 'en-US-davis',
            'mystery': 'en-US-cooper',
            'romance': 'en-US-natalie',
            'fantasy': 'en-US-ruby',
            'comedy': 'en-US-clint',
            'horror': 'en-US-cooper',
            'children': 'en-US-natalie'
        }
        
        logging.info("Audio Processor initialized successfully with Murf AI")
    
    def generate_emotional_audio(self, emotional_segments: List[Dict], output_path: str, theme: str = 'adventure'):
        """Generate emotional audio using Murf AI API"""
        try:
            voice_id = self.theme_voices.get(theme, 'en-US-davis')
            
            # Combine all text segments for single API call (more efficient)
            full_text = self._combine_segments_with_pauses(emotional_segments)
            
            # Determine dominant emotion for voice style
            dominant_emotion = self._get_dominant_emotion(emotional_segments)
            voice_style = self._get_voice_style_for_emotion(dominant_emotion)
            
            logging.info(f"Generating audio with voice: {voice_id}, style: {voice_style}")
            
            # Generate audio using Murf API
            audio_data = self._call_murf_api(
                text=full_text,
                voice_id=voice_id,
                style=voice_style
            )
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logging.info(f"Audio successfully generated: {output_path}")
            
        except Exception as e:
            logging.error(f"Error in generate_emotional_audio: {e}")
            raise
    
    def _combine_segments_with_pauses(self, segments: List[Dict]) -> str:
        """Combine text segments with appropriate pauses"""
        combined_text = ""
        
        for i, segment in enumerate(segments):
            combined_text += segment['text']
            
            # Add pauses between segments based on emotion
            if i < len(segments) - 1:  # Not the last segment
                emotion = segment.get('emotion', 'neutral')
                if emotion in ['sadness', 'fear']:
                    combined_text += " [pause 1s] "  # Longer pause for dramatic emotions
                else:
                    combined_text += " [pause 0.5s] "  # Standard pause
        
        return combined_text
    
    def _get_dominant_emotion(self, segments: List[Dict]) -> str:
        """Get the most common emotion from segments"""
        emotions = [seg.get('emotion', 'neutral') for seg in segments]
        return max(set(emotions), key=emotions.count)
    
    def _get_voice_style_for_emotion(self, emotion: str) -> str:
        """Map emotion to Murf voice style"""
        style_mapping = {
            'excitement': 'excited',
            'joy': 'excited',
            'happiness': 'excited',
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'terrified',
            'surprise': 'excited',
            'calm': 'calm',
            'mysterious': 'conversational',
            'neutral': 'conversational'
        }
        return style_mapping.get(emotion, 'conversational')
    
    def _call_murf_api(self, text: str, voice_id: str, style: str) -> bytes:
        """Make actual API call to Murf AI"""
        url = f"{self.murf_base_url}/speech/generate"
        
        payload = {
            "text": text,
            "voiceId": voice_id,
            "style": style,
            "format": "MP3",
            "sampleRate": 24000,
            "model": "GEN2",  # Use Gen2 for better quality
            "speed": self._get_speed_for_style(style),
            "pitch": self._get_pitch_for_style(style)
        }
        
        headers = {
            "api-key": self.murf_api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Murf API returns a URL to download the audio
                if 'audioFile' in result:
                    audio_url = result['audioFile']
                    # Download the audio file
                    audio_response = requests.get(audio_url, timeout=30)
                    if audio_response.status_code == 200:
                        return audio_response.content
                    else:
                        raise Exception(f"Failed to download audio: {audio_response.status_code}")
                else:
                    raise Exception("No audio file URL in Murf API response")
            else:
                error_msg = f"Murf API error: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            raise Exception("Murf API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error calling Murf API: {str(e)}")
    
    def _get_speed_for_style(self, style: str) -> int:
        """Get speed adjustment for different emotional styles"""
        speed_mapping = {
            'excited': 10,      # Slightly faster
            'sad': -15,         # Slower
            'angry': 5,         # Slightly faster
            'terrified': -10,   # Slower with tension
            'calm': -5,         # Slightly slower
            'conversational': 0 # Normal speed
        }
        return speed_mapping.get(style, 0)
    
    def _get_pitch_for_style(self, style: str) -> int:
        """Get pitch adjustment for different emotional styles"""
        pitch_mapping = {
            'excited': 15,      # Higher pitch
            'sad': -10,         # Lower pitch
            'angry': 10,        # Slightly higher
            'terrified': 20,    # Much higher
            'calm': -5,         # Slightly lower
            'conversational': 0 # Normal pitch
        }
        return pitch_mapping.get(style, 0)
