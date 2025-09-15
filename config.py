import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv(override=True)

# API Configuration - use Streamlit secrets in production, fallback to env for local dev
try:
    # Production: Streamlit Community Cloud
    import streamlit as st
    GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
except (KeyError, AttributeError, ImportError):
    # Local development: .env file
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = 'gemini-2.5-pro'

# Test Configuration
QUESTIONS_PER_TEST = 15
CALIBRATION_QUESTIONS = 3
PERFORMANCE_WINDOW_SIZE = 5

# Adaptive Thresholds
LEVEL_UP_THRESHOLD = 0.8
LEVEL_DOWN_THRESHOLD = 0.4

# Mechanics for MVP
MVP_MECHANICS = [
    'multiple-choice-text-text',
    'word-pronunciation-practice',
    'image-single-choice-from-texts',
    'audio-single-choice-from-images',
    'sentence-pronunciation-practice',
    'sentence-scramble',
    'audio-category-sorting'
]

# Paths
DATA_DIR = 'data'
CURRICULUM_DIR = os.path.join(DATA_DIR, 'curriculum')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'questions.json')
RESULTS_DIR = os.path.join(DATA_DIR, 'test_results')