from flask import Blueprint, request, jsonify, current_app
from app.services.story_generator import StoryGenerator
from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.audio_processor import AudioProcessor
import os
import uuid
import logging

api_bp = Blueprint('api', __name__)

# Initialize services with error handling
try:
    story_gen = StoryGenerator()
    emotion_analyzer = EmotionAnalyzer()
    audio_processor = AudioProcessor()
    logging.info("✅ All AI services initialized successfully")
except Exception as e:
    logging.error(f"❌ Error initializing AI services: {e}")
    story_gen = None
    emotion_analyzer = None
    audio_processor = None

@api_bp.route('/generate-story', methods=['POST'])
def generate_story():
    """Generate an emotional story with TTS"""
    if not all([story_gen, emotion_analyzer, audio_processor]):
        return jsonify({
            'success': False,
            'error': 'AI services not properly initialized. Check API keys and dependencies.'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        keywords = data.get('keywords', [])
        theme = data.get('theme', 'adventure')
        duration = int(data.get('duration', 3))
        moods = data.get('moods', ['neutral'])
        
        logging.info(f"🎬 Generating story: {keywords}, {theme}, {duration}min, {moods}")
        
        # Generate story
        story_text = story_gen.create_story(
            keywords=keywords,
            theme=theme,
            target_duration=duration,
            preferred_moods=moods
        )
        
        if not story_text or "Error" in story_text:
            return jsonify({
                'success': False,
                'error': 'Failed to generate story. Please try again.'
            }), 500
        
        logging.info("📝 Story generated successfully")
        
        # Analyze emotions
        emotional_segments = emotion_analyzer.analyze_story_emotions(
            story_text, 
            preferred_moods=moods
        )
        
        logging.info(f"🎭 Emotions analyzed: {len(emotional_segments)} segments")
        
        # Generate audio with Murf AI
        audio_filename = f"story_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], audio_filename)
        
        try:
            logging.info("🎵 Starting audio generation...")
            audio_processor.generate_emotional_audio(
                emotional_segments, 
                output_path=audio_path,
                theme=theme
            )
            audio_url = f'/static/audio/generated/{audio_filename}'
            logging.info(f"🎵 Audio generated successfully: {audio_filename}")
        except Exception as audio_error:
            logging.error(f"Audio generation failed: {audio_error}")
            # Return story without audio if audio generation fails
            audio_url = None
        
        return jsonify({
            'success': True,
            'story': story_text,
            'audio_url': audio_url,
            'duration_estimate': f"{duration} minutes",
            'emotions_used': list(set([seg['emotion'] for seg in emotional_segments])),
            'segments_count': len(emotional_segments),
            'word_count': len(story_text.split()),
            'message': 'Story and audio generated successfully!' if audio_url else 'Story generated successfully! Audio generation failed.'
        })
        
    except Exception as e:
        logging.error(f"❌ Error in generate_story: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500
