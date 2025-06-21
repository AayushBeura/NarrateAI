from flask import Blueprint, render_template, jsonify
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    services_status = {
        'status': 'healthy',
        'service': 'NarrateAI',
        'environment_vars': {
            'GEMINI_API_KEY': bool(os.environ.get('GEMINI_API_KEY')),
            'MURF_API_KEY': bool(os.environ.get('MURF_API_KEY'))
        }
    }
    return jsonify(services_status)

@main_bp.route('/about')
def about():
    return render_template('about.html')
