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
        # Use the current Gemini model instead of deprecated gemini-pro
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Word count estimates for different durations
        self.duration_word_counts = {
            1: 150,   # 1 minute
            3: 450,   # 3 minutes
            5: 750,   # 5 minutes
            10: 1500  # 10 minutes
        }
        
        logging.info("Story Generator initialized successfully with gemini-1.5-flash")
    
    def create_story(self, keywords: List[str], theme: str, target_duration: int, preferred_moods: List[str]) -> str:
        """Generate a story based on input parameters"""
        try:
            word_count = self.duration_word_counts.get(target_duration, 450)
            moods_text = ", ".join(preferred_moods)
            keywords_text = ", ".join(keywords)
            
            prompt = f"""
            Create an engaging {target_duration}-minute story (approximately {word_count} words) with the following specifications:
            
            Theme: {theme}
            Keywords to include: {keywords_text}
            Emotional moods to emphasize: {moods_text}
            Target word count: {word_count} words
            
            Requirements:
            1. Create clear emotional transitions that match the specified moods: {moods_text}
            2. Use vivid descriptions and engaging dialogue
            3. Include natural pauses and dramatic moments for audio narration
            4. Structure with a clear beginning, middle, and end
            5. Make it suitable for emotional text-to-speech narration
            6. Include emotional cues in parentheses like (excited), (whispered), (dramatically)
            7. Ensure all keywords are naturally integrated: {keywords_text}
            
            Write a captivating {theme} story that will sound amazing when narrated with emotional text-to-speech technology.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "Error: No story content generated"
                
        except Exception as e:
            logging.error(f"Error generating story: {e}")
            return f"Error generating story: {str(e)}"
