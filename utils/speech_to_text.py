import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_bytes):
    """
    Transcribe audio using IBM Watson Speech to Text.
    
    Args:
        audio_bytes: Audio file bytes (WAV format preferred)
        
    Returns:
        dict with 'text' key containing transcription,
        or 'error' key if transcription failed
    """
    try:
        # Get credentials
        try:
            api_key = st.secrets.get("SPEECH_TO_TEXT_API_KEY")
            url = st.secrets.get("SPEECH_TO_TEXT_URL", "https://api.us-south.speech-to-text.watson.cloud.ibm.com")
        except:
            api_key = os.environ.get("SPEECH_TO_TEXT_API_KEY")
            url = os.environ.get("SPEECH_TO_TEXT_URL", "https://api.us-south.speech-to-text.watson.cloud.ibm.com")
        
        if not api_key:
            return {"error": "Missing Speech to Text API credentials"}
        
        # Set up authenticator and service
        authenticator = IAMAuthenticator(api_key)
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_service_url(url)
        
        # Transcribe audio
        # The audio_bytes should be in a format Watson can handle (WAV, MP3, etc.)
        response = speech_to_text.recognize(
            audio=audio_bytes,
            content_type='audio/wav',
            model='en-US_BroadbandModel'
        ).get_result()
        
        # Extract transcript
        if response and 'results' in response and len(response['results']) > 0:
            transcript = ' '.join([
                result['alternatives'][0]['transcript']
                for result in response['results']
                if 'alternatives' in result and len(result['alternatives']) > 0
            ])
            return {"text": transcript.strip()}
        else:
            return {"error": "No speech detected in audio"}
            
    except Exception as e:
        return {"error": f"Error transcribing audio: {str(e)}"}
