import google.generativeai as genai
import os
from typing import List
import logging

class StoryGenerator:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.duration_word_counts = {
            1: 150, 3: 450, 5: 750, 10: 1500
        }
        
        logging.info("Enhanced Story Generator initialized for emotional storytelling")
    
    def create_story(self, keywords: List[str], theme: str, target_duration: int, preferred_moods: List[str]) -> str:
        """Generate an emotionally rich story optimized for audio narration"""
        try:
            word_count = self.duration_word_counts.get(target_duration, 450)
            moods_text = ", ".join(preferred_moods)
            keywords_text = ", ".join(keywords)
            
            prompt = f"""
            Create a HIGHLY EMOTIONAL and DRAMATIC {target_duration}-minute story (approximately {word_count} words) optimized for storytelling narration:
            
            STORY REQUIREMENTS:
            - Theme: {theme}
            - Keywords to weave naturally: {keywords_text}
            - Emotional journey: {moods_text}
            - Target length: {word_count} words
            
            STORYTELLING REQUIREMENTS FOR AUDIO NARRATION:
            1. Write with DRAMATIC PACING - vary sentence lengths for rhythm
            2. Include EMOTIONAL DIALOGUE with clear character voices
            3. Use VIVID, SENSORY descriptions that paint pictures
            4. Create EMOTIONAL PEAKS AND VALLEYS throughout
            5. Add natural storytelling phrases like "But then...", "Suddenly...", "In that moment..."
            6. Include DRAMATIC PAUSES with ellipses (...) where appropriate
            7. Use EMOTIONAL INTENSIFIERS: whispered secrets, thunderous roars, gentle touches
            8. Create CLIFFHANGER MOMENTS that build tension
            9. End with a SATISFYING, EMOTIONAL RESOLUTION
            
            EMOTIONAL GUIDANCE:
            - Start with scene-setting in a {preferred_moods[0] if preferred_moods else 'mysterious'} tone
            - Build emotional intensity through the middle
            - Include moments of {', '.join(preferred_moods)} throughout
            - Create emotional contrasts (quiet moments before dramatic ones)
            - End with emotional satisfaction and closure
            
            DIALOGUE AND CHARACTER REQUIREMENTS:
            - Include meaningful dialogue that reveals character emotions
            - Use emotional tags: (whispered), (shouted), (trembling voice), (with tears)
            - Create distinct character voices and personalities
            - Show emotions through actions, not just words
            
            Write this as if you're a master storyteller performing for an audience. Make every sentence count for emotional impact and audio delivery.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                story = response.text.strip()
                # Enhance the story further for audio
                return self._enhance_for_audio_narration(story, preferred_moods, theme)
            else:
                return "Error: No story content generated"
                
        except Exception as e:
            logging.error(f"Error generating story: {e}")
            return f"Error generating story: {str(e)}"
    
    def _enhance_for_audio_narration(self, story: str, moods: List[str], theme: str) -> str:
        """Add additional enhancements for better audio narration"""
        
        # Add emotional stage directions
        story = self._add_emotional_cues(story, moods)
        
        # Enhance dramatic moments
        story = self._enhance_dramatic_moments(story, theme)
        
        # Add natural storytelling flow
        story = self._add_storytelling_flow(story)
        
        return story
    
    def _add_emotional_cues(self, story: str, moods: List[str]) -> str:
        """Add emotional cues for better TTS interpretation"""
        
        # Add emotional context to dialogue
        import re
        
        # Find dialogue and add emotional context
        dialogue_pattern = r'"([^"]*)"'
        
        def add_emotion_to_dialogue(match):
            dialogue = match.group(1)
            # Choose appropriate emotion based on content and mood
            if any(word in dialogue.lower() for word in ['help', 'scared', 'afraid']):
                return f'"(trembling) {dialogue}"'
            elif any(word in dialogue.lower() for word in ['amazing', 'wonderful', 'incredible']):
                return f'"(excited) {dialogue}"'
            elif any(word in dialogue.lower() for word in ['whisper', 'secret', 'quietly']):
                return f'"(whispered) {dialogue}"'
            else:
                return f'"(emotionally) {dialogue}"'
        
        story = re.sub(dialogue_pattern, add_emotion_to_dialogue, story)
        
        return story
    
    def _enhance_dramatic_moments(self, story: str, theme: str) -> str:
        """Enhance dramatic moments based on theme"""
        
        dramatic_enhancers = {
            'adventure': ['Suddenly', 'Without warning', 'In that heart-stopping moment'],
            'mystery': ['In the shadows', 'A chill ran down', 'Something wasn\'t right'],
            'romance': ['Their eyes met', 'Time seemed to stop', 'In that tender moment'],
            'horror': ['The darkness crept', 'A blood-curdling', 'Terror gripped'],
            'fantasy': ['Magic filled the air', 'The ancient power', 'Mystical forces']
        }
        
        # This is a simplified enhancement - in a full implementation,
        # you'd use more sophisticated NLP to identify and enhance dramatic moments
        
        return story
    
    def _add_storytelling_flow(self, story: str) -> str:
        """Add natural storytelling transitions and flow"""
        
        # Add storytelling transitions
        transitions = [
            'But our story doesn\'t end there...',
            'Little did they know...',
            'As fate would have it...',
            'In the distance...',
            'Meanwhile...'
        ]
        
        # This would be enhanced with more sophisticated story analysis
        # For now, we return the story as-is
        
        return story
