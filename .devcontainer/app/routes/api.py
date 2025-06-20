from flask import Blueprint, request, jsonify, current_app, send_file
from app.services.story_generator import StoryGenerator
from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.audio_processor import AudioProcessor
from app.utils.validators import validate_story_request
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
            'error': 'AI services not properly initialized. Check API keys.'
        }), 500
    
    try:
        data = request.get_json()
        
        # Validate request data
        validation_error = validate_story_request(data)
        if validation_error:
            return jsonify({
                'success': False,
                'error': validation_error
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
        
        # Generate audio
        audio_filename = f"story_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], audio_filename)
        
        audio_processor.generate_emotional_audio(
            emotional_segments, 
            output_path=audio_path,
            theme=theme
        )
        
        logging.info(f"🎵 Audio generated: {audio_filename}")
        
        return jsonify({
            'success': True,
            'story': story_text,
            'audio_url': f'/static/audio/generated/{audio_filename}',
            'duration_estimate': f"{duration} minutes",
            'emotions_used': list(set([seg['emotion'] for seg in emotional_segments])),
            'segments_count': len(emotional_segments),
            'word_count': len(story_text.split())
        })
        
    except Exception as e:
        logging.error(f"❌ Error in generate_story: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@api_bp.route('/download-audio/<filename>')
def download_audio(filename):
    """Download generated audio file"""
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
