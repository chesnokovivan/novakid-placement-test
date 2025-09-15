# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered English placement test system for Novakid (EdTech company). The system uses adaptive testing to determine student English proficiency levels (0-5, mapped to CEFR) through three question mechanics: multiple choice grammar, word pronunciation practice, and image-text matching.

## Development Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

### Question Bank Generation
```bash
python3 generate_questions.py
```

### Run Application Locally
```bash
streamlit run app.py

IMPORTANT: DO NOT RUN THE APP AUTOMATICALLY. I WILL DO IT MANUALLY IN OTHER TERMINAL.
```

### Deployment
The application is configured for deployment on Streamlit Community Cloud:

**Live App**: Available at production URL once deployed via GitHub integration
**Deployment Config**:
- `.streamlit/config.toml` - Kid-friendly theme with coral primary color (#FF6B6B)
- Automatic deployment on git push to main branch
- Secrets management via Streamlit Cloud dashboard (GEMINI_API_KEY, Unsplash, Novakid TTS)
- Zero-cost hosting on free tier

**Deployment Guide**: See `DEPLOYMENT.md` for complete setup instructions

## Architecture

The system follows a modular architecture:

- **app.py**: Main Streamlit application with kid-friendly UI and results screen
- **config.py**: Central configuration including API keys, test parameters, and file paths
- **generate_questions.py**: One-time script to generate question bank using Google Gemini API
- **lib/adaptive_engine.py**: Core adaptive testing algorithm that adjusts difficulty based on performance
- **lib/question_renderer.py**: UI components for different question types with duplicate media rendering fixes
- **lib/media_apis.py**: Integration with Unsplash (images) and Novakid TTS (audio) APIs
- **lib/analyzer.py**: Post-test analysis using LLM to provide detailed placement recommendations

### Data Structure

- **data/curriculum/**: JSON files defining Novakid levels, competencies, grammar topics, and vocabulary
- **data/questions.json**: Generated question bank organized by level (created by generate_questions.py)
- **data/test_results/**: Student test results (auto-created during tests, excluded from git via .gitignore)
- **.streamlit/config.toml**: Streamlit deployment configuration with kid-friendly theme
- **DEPLOYMENT.md**: Complete Streamlit Community Cloud deployment guide

### Adaptive Algorithm

The AdaptiveEngine uses a calibration phase (3 randomized questions across levels with mechanic diversity) followed by performance-responsive adaptive selection. Features include:

- **Category Balance:** 50/50 audio vs text mechanic distribution via coin-flip selection
- **Mechanic Diversity:** Tracks recent question types to prevent boring streaks
- **Dynamic Exploration:** High performers (90%+) get expanded level range testing  
- **Aggressive Progression:** Perfect performance (100% over 4+ questions) triggers 2-level jumps
- **Ceiling Exploration:** End-test push ensures advanced students get Level 5 assessment
- **Standard Adjustments:** 80% accuracy (level up), 30% accuracy (level down)

This ensures proper placement from beginners to advanced students while maintaining engaging variety and balanced question types.

## Key Configuration

- Uses Google Gemini 2.5 Pro API for question generation and analysis
- Test length: 15 questions with 5-question performance window
- Three question mechanics with level-based availability
- Results analyzed by LLM with rule-based fallback
- Real media integration: Unsplash API for images, Novakid TTS for audio
- Kid-friendly UI with colorful themes and celebration elements

## UI Features

### Question Rendering
- **Media Integration**: Real images from Unsplash API, audio from Novakid TTS
- **Duplicate Prevention**: Session state flags prevent media re-rendering on button clicks
- **Responsive Design**: Large buttons and clear fonts optimized for children
- **Visual Feedback**: Immediate feedback with colorful success/error messages

### Results Screen
- **Celebration Design**: Big emojis, colorful badges, and achievement unlocks
- **Level Visualization**: Color-coded level badges (Level 0-5) with gradient backgrounds
- **Skill Assessment**: Star ratings and achievement badges for Vocabulary, Pronunciation, Grammar
- **Kid-Friendly Language**: Technical analysis transformed into encouraging, age-appropriate descriptions
- **Visual Progress**: Animated progress bars showing test performance

## Dependencies

- **streamlit**: Web UI framework
- **google-genai**: Google Gemini API client
- **python-dotenv**: Environment variable management
- **requests**: HTTP requests for media APIs

Requires GEMINI_API_KEY in .env file for LLM functionality.

## Media APIs

- **Unsplash API**: Provides real images for vocabulary questions (CLIENT_ID configured in lib/media_apis.py)
- **Novakid TTS API**: Generates pronunciation audio for target words