import requests
import os
from typing import List, Dict
import logging
import re

class AudioProcessor:
    def __init__(self):
        self.murf_api_key = os.environ.get('MURF_API_KEY')
        if not self.murf_api_key:
            raise ValueError("MURF_API_KEY environment variable not set")
        
        self.murf_base_url = "https://api.murf.ai/v1"
        
        # Safe fallback voices
        self.fallback_voices = [
            'en-US-cooper',
            'en-US-hazel', 
            'en-US-natalie',
            'en-US-davis',
            'en-US-ruby'
        ]
        
        logging.info("Enhanced Audio Processor initialized for storytelling")
    
    def generate_emotional_audio(self, emotional_segments: List[Dict], output_path: str, theme: str = 'adventure'):
        """Generate highly emotional storytelling audio"""
        try:
            # Get available voices and select the best one
            available_voices = self._get_available_voices()
            voice_id = self._select_best_voice(theme, available_voices)
            
            logging.info(f"Using voice ID: {voice_id} for theme: {theme}")
            
            # Process segments for storytelling
            processed_segments = self._enhance_segments_for_storytelling(emotional_segments, theme)
            
            # Generate audio with storytelling techniques
            audio_data = self._generate_storytelling_audio(
                segments=processed_segments,
                voice_id=voice_id,
                theme=theme
            )
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logging.info(f"Emotional storytelling audio generated: {output_path}")
            
        except Exception as e:
            logging.error(f"Error in generate_emotional_audio: {e}")
            raise
    
    def _get_available_voices(self) -> List[Dict]:
        """Get list of available voices from Murf API with better error handling"""
        try:
            url = f"{self.murf_base_url}/speech/voices"
            headers = {
                "api-key": self.murf_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                voices_data = response.json()
                
                # Handle different response formats
                if isinstance(voices_data, list):
                    voices = voices_data
                elif isinstance(voices_data, dict):
                    voices = voices_data.get('voices', voices_data.get('data', []))
                else:
                    logging.warning(f"Unexpected voices response format: {type(voices_data)}")
                    return []
                
                logging.info(f"Retrieved {len(voices)} available voices")
                return voices if isinstance(voices, list) else []
            else:
                logging.error(f"Failed to get voices: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Error getting available voices: {e}")
            return []
    
    def _select_best_voice(self, theme: str, available_voices: List[Dict]) -> str:
        """Select the best available voice for the theme"""
        if not available_voices:
            logging.info("Using fallback voice selection")
            return self.fallback_voices[0]
        
        # Extract voice IDs from available voices with flexible key handling
        voice_ids = []
        for voice in available_voices:
            if isinstance(voice, dict):
                voice_id = voice.get('voiceId') or voice.get('id') or voice.get('name')
                if voice_id:
                    voice_ids.append(voice_id)
            elif isinstance(voice, str):
                voice_ids.append(voice)
        
        if not voice_ids:
            logging.warning("No voice IDs found, using fallback")
            return self.fallback_voices[0]
        
        # Theme preferences
        theme_preferences = {
            'adventure': ['cooper', 'davis', 'marcus', 'male'],
            'mystery': ['cooper', 'davis', 'male'],
            'romance': ['hazel', 'natalie', 'sarah', 'female'],
            'fantasy': ['hazel', 'ruby', 'natalie', 'female'],
            'comedy': ['cooper', 'clint', 'male'],
            'horror': ['cooper', 'davis', 'male'],
            'children': ['hazel', 'natalie', 'sarah', 'female']
        }
        
        preferred_names = theme_preferences.get(theme, ['cooper'])
        
        # Find the first available voice that matches our preference
        for pref_name in preferred_names:
            for voice_id in voice_ids:
                if pref_name.lower() in str(voice_id).lower():
                    logging.info(f"Selected voice {voice_id} for theme {theme}")
                    return voice_id
        
        # If no preference match, return the first English voice
        for voice_id in voice_ids:
            if 'en' in str(voice_id).lower():
                logging.info(f"Using fallback English voice {voice_id} for theme {theme}")
                return voice_id
        
        # Ultimate fallback
        selected_voice = voice_ids[0] if voice_ids else self.fallback_voices[0]
        logging.info(f"Using ultimate fallback voice {selected_voice}")
        return selected_voice
    
    def _enhance_segments_for_storytelling(self, segments: List[Dict], theme: str) -> List[Dict]:
        """Enhance text segments with storytelling elements"""
        enhanced_segments = []
        
        for i, segment in enumerate(segments):
            text = segment['text']
            emotion = segment.get('emotion', 'neutral')
            
            # Clean text AGGRESSIVELY
            enhanced_text = self._clean_text_completely(text)
            
            enhanced_segments.append({
                'text': enhanced_text,
                'emotion': emotion,
                'murf_style': self._get_advanced_voice_style(emotion, theme),
                'speed': self._get_dynamic_speed(emotion, i, len(segments)),
                'pitch': self._get_dynamic_pitch(emotion, theme),
                'emphasis': self._get_emphasis_level(emotion),
                'pause_after': self._get_dramatic_pause(emotion, i, len(segments))
            })
        
        return enhanced_segments
    
    def _clean_text_completely(self, text: str) -> str:
        """AGGRESSIVELY clean text for TTS - remove ALL problematic content"""
        
        # Step 1: Remove ALL types of brackets and their content
        text = re.sub(r'\([^)]*\)', '', text)  # Remove (anything)
        text = re.sub(r'\[[^]]*\]', '', text)  # Remove [anything]
        text = re.sub(r'\{[^}]*\}', '', text)  # Remove {anything}
        text = re.sub(r'<[^>]*>', '', text)    # Remove <anything>
        
        # Step 2: Remove ALL emphasis markers
        text = re.sub(r'\*+([^*]*)\*+', r'\1', text)  # Remove *emphasis*
        text = re.sub(r'_+([^_]*)_+', r'\1', text)    # Remove _emphasis_
        text = re.sub(r'`+([^`]*)`+', r'\1', text)    # Remove `code`
        
        # Step 3: Fix stutters BEFORE other processing
        def fix_stutter(match):
            letter = match.group(1).lower()
            word = match.group(2)
            
            # Convert single letters to sounds
            letter_sounds = {
                'w': 'wuh', 'b': 'buh', 'c': 'cuh', 'd': 'duh', 'f': 'fuh',
                'g': 'guh', 'h': 'huh', 'j': 'juh', 'k': 'kuh', 'l': 'luh',
                'm': 'muh', 'n': 'nuh', 'p': 'puh', 'r': 'ruh', 's': 'suh',
                't': 'tuh', 'v': 'vuh', 'x': 'xuh', 'z': 'zuh'
            }
            
            sound = letter_sounds.get(letter, letter)
            return f"{sound} {word}"
        
        # Fix stutters like "w-who" -> "wuh who"
        text = re.sub(r'\b([a-zA-Z])-([a-zA-Z]\w*)', fix_stutter, text)
        
        # Step 4: Fix abbreviations
        abbreviations = {
            'Dr.': 'Doctor', 'Mr.': 'Mister', 'Mrs.': 'Missus', 'Ms.': 'Miss',
            'Prof.': 'Professor', 'St.': 'Saint', 'Ave.': 'Avenue', 'Rd.': 'Road',
            'Jr.': 'Junior', 'Sr.': 'Senior', 'Inc.': 'Incorporated',
            'Ltd.': 'Limited', 'Corp.': 'Corporation', 'Co.': 'Company',
            'etc.': 'etcetera', 'vs.': 'versus', 'e.g.': 'for example',
            'i.e.': 'that is', 'A.M.': 'A M', 'P.M.': 'P M'
        }
        
        for abbrev, full in abbreviations.items():
            text = text.replace(abbrev, full)
            text = text.replace(abbrev.lower(), full.lower())
            text = text.replace(abbrev.upper(), full.upper())
        
        # Step 5: Fix ellipsis and multiple dots - CONVERT TO PERIODS
        text = re.sub(r'\.{2,}', '.', text)  # Multiple dots -> single dot
        text = re.sub(r'…+', '.', text)      # Unicode ellipsis -> period
        
        # Step 6: Ensure proper sentence structure
        # Split by periods and rebuild with proper spacing
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Rebuild with proper periods and spacing
        clean_sentences = []
        for sentence in sentences:
            if sentence:
                # Ensure sentence starts with capital letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                clean_sentences.append(sentence)
        
        # Join with periods and spaces
        text = '. '.join(clean_sentences)
        
        # Add final period if needed
        if text and not text.endswith('.'):
            text += '.'
        
        # Step 7: Clean up spacing
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces -> single space
        text = text.strip()
        
        # Step 8: Final check - remove any remaining problematic characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)  # Keep only letters, numbers, spaces, basic punctuation
        
        return text
    
    def _get_advanced_voice_style(self, emotion: str, theme: str) -> str:
        """Get voice style for emotion"""
        
        style_mapping = {
            'excitement': 'excited',
            'joy': 'cheerful',
            'happiness': 'cheerful',
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'terrified',
            'surprise': 'excited',
            'calm': 'calm',
            'mysterious': 'conversational',
            'neutral': 'conversational'
        }
        
        return style_mapping.get(emotion, 'conversational')
    
    def _get_dynamic_speed(self, emotion: str, position: int, total: int) -> float:
        """Get dynamic speed for emotion and story position"""
        
        base_speeds = {
            'excitement': 1.1, 'fear': 0.9, 'sadness': 0.8, 'anger': 1.0,
            'joy': 1.1, 'mysterious': 0.9, 'calm': 0.95, 'surprise': 1.2, 'neutral': 1.0
        }
        
        return base_speeds.get(emotion, 1.0)
    
    def _get_dynamic_pitch(self, emotion: str, theme: str) -> float:
        """Get dynamic pitch for emotion"""
        
        pitch_map = {
            'excitement': 1.1, 'joy': 1.05, 'fear': 1.2, 'surprise': 1.3,
            'anger': 1.05, 'sadness': 0.95, 'mysterious': 0.95, 'calm': 1.0, 'neutral': 1.0
        }
        
        return pitch_map.get(emotion, 1.0)
    
    def _get_emphasis_level(self, emotion: str) -> str:
        """Get emphasis level for emotional delivery"""
        
        emphasis_levels = {
            'excitement': 'strong', 'anger': 'strong', 'fear': 'moderate', 'surprise': 'strong',
            'joy': 'moderate', 'sadness': 'reduced', 'mysterious': 'moderate', 'calm': 'none', 'neutral': 'none'
        }
        
        return emphasis_levels.get(emotion, 'none')
    
    def _get_dramatic_pause(self, emotion: str, position: int, total: int) -> float:
        """Get pause duration after segment"""
        
        base_pauses = {
            'sadness': 1.2, 'mysterious': 1.0, 'fear': 0.8, 'excitement': 0.3,
            'joy': 0.4, 'anger': 0.3, 'surprise': 0.5, 'calm': 0.6, 'neutral': 0.5
        }
        
        return base_pauses.get(emotion, 0.5)
    
    def _generate_storytelling_audio(self, segments: List[Dict], voice_id: str, theme: str) -> bytes:
        """Generate audio with storytelling techniques"""
        
        # Combine all segments into one clean text
        full_text = ""
        
        for i, segment in enumerate(segments):
            text = segment['text']
            if text:
                full_text += text
                if i < len(segments) - 1:
                    full_text += " "
        
        # Final cleaning
        full_text = self._clean_text_completely(full_text)
        
        # Get dominant emotion
        emotions = [seg.get('emotion', 'neutral') for seg in segments]
        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        # Calculate average parameters
        avg_speed = sum(seg.get('speed', 1.0) for seg in segments) / len(segments)
        avg_pitch = sum(seg.get('pitch', 1.0) for seg in segments) / len(segments)
        
        return self._call_murf_api(
            text=full_text,
            voice_id=voice_id,
            style=self._get_advanced_voice_style(dominant_emotion, theme),
            rate=avg_speed,
            pitch=avg_pitch
        )
    
    def _call_murf_api(self, text: str, voice_id: str, style: str, rate: float = 1.0, pitch: float = 1.0) -> bytes:
        """Call Murf API with proper parameters"""
        
        url = f"{self.murf_base_url}/speech/generate"
        
        payload = {
            "text": text,
            "voiceId": voice_id,
            "format": "MP3",
            "sampleRate": 24000
        }
        
        if style and style != 'conversational':
            payload["style"] = style
        
        if rate != 1.0:
            payload["rate"] = rate
        
        if pitch != 1.0:
            payload["pitch"] = pitch
        
        headers = {
            "api-key": self.murf_api_key,
            "Content-Type": "application/json"
        }
        
        try:
            logging.info(f"Generating CLEAN audio - Text preview: {text[:100]}...")
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                audio_url = None
                if isinstance(result, dict):
                    audio_url = (result.get('audioFile') or 
                               result.get('audio_url') or 
                               result.get('url') or 
                               result.get('downloadUrl'))
                
                if audio_url:
                    audio_response = requests.get(audio_url, timeout=60)
                    if audio_response.status_code == 200:
                        logging.info("CLEAN audio generated successfully")
                        return audio_response.content
                    else:
                        raise Exception(f"Failed to download audio: {audio_response.status_code}")
                else:
                    if hasattr(response, 'content') and len(response.content) > 1000:
                        return response.content
                    else:
                        raise Exception("No audio data in response")
            else:
                error_msg = f"Murf API error: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            raise Exception("Murf API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
