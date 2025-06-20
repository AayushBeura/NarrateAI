import requests
import os
from typing import List, Dict
from pydub import AudioSegment
import io
import logging

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
        
        logging.info("Audio Processor initialized successfully")
    
    def generate_emotional_audio(self, emotional_segments: List[Dict], output_path: str, theme: str = 'adventure'):
        """Generate emotional audio from text segments"""
        try:
            audio_segments = []
            voice_id = self.theme_voices.get(theme, 'en-US-davis')
            
            for i, segment in enumerate(emotional_segments):
                try:
                    logging.info(f"Processing segment {i+1}/{len(emotional_segments)}: {segment['emotion']}")
                    
                    # For demo purposes, create a simple TTS simulation
                    # In production, replace this with actual Murf API calls
                    audio_data = self._simulate_tts_generation(
                        text=segment['text'],
                        style=segment['murf_style'],
                        voice_id=voice_id
                    )
                    
                    if audio_data:
                        audio_segments.append(audio_data)
                        
                except Exception as e:
                    logging.error(f"Error generating audio for segment {i}: {e}")
                    continue
            
            # Combine all audio segments
            if audio_segments:
                self._combine_audio_segments(audio_segments, output_path)
                logging.info(f"Audio successfully generated: {output_path}")
            else:
                raise Exception("No audio segments were generated successfully")
                
        except Exception as e:
            logging.error(f"Error in generate_emotional_audio: {e}")
            raise
    
    def _simulate_tts_generation(self, text: str, style: str, voice_id: str) -> bytes:
        """Simulate TTS generation - replace with actual Murf API call in production"""
        # This is a placeholder for the actual Murf API call
        # For demo purposes, we'll create a simple audio file
        
        # In production, use this structure:
        """
        url = f"{self.murf_base_url}/speech/generate"
        
        payload = {
            "text": text,
            "voice_id": voice_id,
            "style": style,
            "speed": self._get_speed_for_style(style),
            "pitch": self._get_pitch_for_style(style),
            "format": "mp3",
            "sample_rate": 24000
        }
        
        headers = {
            "Authorization": f"Bearer {self.murf_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Murf API error: {response.status_code} - {response.text}")
        """
        
        # For demo: create a simple silent audio segment
        duration_ms = len(text) * 50  # Rough estimate: 50ms per character
        silent_audio = AudioSegment.silent(duration=duration_ms)
        
        # Export to bytes
        buffer = io.BytesIO()
        silent_audio.export(buffer, format="mp3")
        return buffer.getvalue()
    
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
    
    def _combine_audio_segments(self, audio_segments: List[bytes], output_path: str):
        """Combine multiple audio segments into a single file"""
        try:
            combined = AudioSegment.empty()
            
            for i, audio_data in enumerate(audio_segments):
                try:
                    segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
                    
                    # Add a small pause between segments
                    if i > 0:
                        pause = AudioSegment.silent(duration=500)  # 0.5 second pause
                        combined += pause
                    
                    combined += segment
                    
                except Exception as e:
                    logging.error(f"Error processing audio segment {i}: {e}")
                    continue
            
            # Export the combined audio
            combined.export(output_path, format="mp3", bitrate="128k")
            
        except Exception as e:
            logging.error(f"Error combining audio segments: {e}")
            raise
