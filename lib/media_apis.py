# Media API integrations for real images and audio
import requests
import streamlit as st
from typing import Optional

# API Configuration - use Streamlit secrets in production, fallback to hardcoded for local dev
try:
    # Production: Streamlit Community Cloud
    UNSPLASH_CLIENT_ID = st.secrets["unsplash"]["access_key"]
    AUDIO_API_BASE = st.secrets["novakid_tts"]["base_url"]
except (KeyError, AttributeError):
    # Local development: fallback to current values
    UNSPLASH_CLIENT_ID = "xwkWSFRdhZdVuEu7VrzlW4Qp3RsMDexu7oMvTFcYitA"
    AUDIO_API_BASE = "https://cdn.novakidschool.com/api/0/text_to_speech"

@st.cache_data(ttl=3600)
def get_unsplash_image(query: str) -> Optional[str]:
    """Get image URL from Unsplash API"""
    try:
        url = f"https://api.unsplash.com/search/photos"
        params = {
            "page": 1,
            "client_id": UNSPLASH_CLIENT_ID,
            "query": query,
            "per_page": 1
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["regular"]
        return None
        
    except Exception as e:
        st.warning(f"Could not load image: {e}")
        return None

def get_audio_url(text: str, voice: str = "Brian") -> str:
    """Get audio URL from Novakid TTS API"""
    return f"{AUDIO_API_BASE}?text={requests.utils.quote(text)}&voice={voice}"