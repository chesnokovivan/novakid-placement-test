import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
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
    'image-single-choice-from-texts'
]

# Paths
DATA_DIR = 'data'
CURRICULUM_DIR = os.path.join(DATA_DIR, 'curriculum')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'questions.json')
RESULTS_DIR = os.path.join(DATA_DIR, 'test_results')