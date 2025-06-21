import os
import requests

def check_murf_voices():
    api_key = os.environ.get('MURF_API_KEY')
    if not api_key:
        print("❌ MURF_API_KEY not set")
        return
    
    url = "https://api.murf.ai/v1/speech/voices"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            voices_data = response.json()
            
            # Handle both list and dict responses
            if isinstance(voices_data, list):
                voices = voices_data
            elif isinstance(voices_data, dict):
                voices = voices_data.get('voices', voices_data.get('data', []))
            else:
                print(f"❌ Unexpected response format: {type(voices_data)}")
                return
            
            print(f"✅ Found {len(voices)} available voices:")
            print(f"Response type: {type(voices_data)}")
            print(f"First voice structure: {voices[0] if voices else 'No voices'}")
            
            print("\nEnglish voices:")
            
            for voice in voices:
                if isinstance(voice, dict):
                    voice_id = voice.get('voiceId') or voice.get('id') or voice.get('name', 'Unknown')
                    language = voice.get('language') or voice.get('lang', 'Unknown')
                    styles = voice.get('styles', voice.get('availableStyles', []))
                    
                    if 'en' in str(voice_id).lower() or 'english' in str(language).lower():
                        print(f"  - {voice_id} ({language}) - Styles: {styles}")
                else:
                    print(f"  - Unexpected voice format: {voice}")
            
            print(f"\nFirst 5 voice IDs for reference:")
            for i, voice in enumerate(voices[:5]):
                if isinstance(voice, dict):
                    voice_id = voice.get('voiceId') or voice.get('id') or voice.get('name', 'Unknown')
                    print(f"  {i+1}. {voice_id}")
                else:
                    print(f"  {i+1}. {voice}")
                
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_murf_voices()
