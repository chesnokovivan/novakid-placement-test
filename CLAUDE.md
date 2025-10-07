# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered adaptive English placement test for Novakid (EdTech). Determines student proficiency levels (0-5, CEFR-mapped) through 7 question mechanics with real-time difficulty adjustment.

## Development Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

### Question Bank Generation
```bash
python3 generate_questions.py
```

### Run Application
```bash
streamlit run app.py
# IMPORTANT: DO NOT RUN AUTOMATICALLY. USER RUNS MANUALLY.
```

### Deployment
Streamlit Community Cloud configuration:
- `.streamlit/config.toml` - Kid-friendly theme (coral #FF6B6B)
- Auto-deploy on git push to main
- Secrets: GEMINI_API_KEY, Unsplash, Novakid TTS
- See `DEPLOYMENT.md` for setup

## Architecture

### Core Modules
- **app.py**: Main Streamlit UI with kid-friendly results screen
- **config.py**: Central config (API keys, test parameters, paths)
- **generate_questions.py**: Question bank generator (Gemini API)
- **lib/adaptive_engine.py**: Adaptive algorithm with momentum system
- **lib/question_renderer.py**: 7 mechanic renderers with session state deduplication
- **lib/media_apis.py**: Unsplash images + Novakid TTS integration
- **lib/analyzer.py**: LLM-powered post-test analysis

### Data Structure
- **data/curriculum/**: Novakid levels, competencies, grammar, vocab (JSON)
- **data/questions.json**: Generated question bank by level
- **data/test_results/**: Test results (gitignored, auto-created)

## Question Mechanics (7 Types)

1. **word-pronunciation-practice**: Word + phonetic + image + TTS → speech (75% sim success)
2. **sentence-pronunciation-practice**: Sentence + phonetic + image + TTS → speech
3. **audio-single-choice-from-images**: TTS audio → select image (4 options)
4. **audio-category-sorting**: Multiple TTS → sort into categories (60% pass threshold)
5. **image-single-choice-from-texts**: Image → select text (4 options)
6. **multiple-choice-text-text**: Grammar sentence → select option
7. **sentence-scramble**: Drag-drop words to form sentence

Level 0 = audio only; Levels 1-5 = progressive unlock

## Adaptive Algorithm (lib/adaptive_engine.py)

### Calibration (Q1-3): Tests levels 0, 1, 2 sequentially with category balance (50/50 audio/text)

### Adaptive Phase (Q4-15)
**Momentum System** (-2.0 to +2.0): +0.3 on correct, -0.5 on wrong; tracks consecutive successes

**Level Adjustments** (2Q cooldown):
- Up: 90%+ (4+ consecutive) or 75%+ (3+ consecutive) → +1 level
- Early L5: 85%+ at L4 (2+ consecutive, Q≤10) → Level 5
- Down: 30%- → -1 level (L5 protected: needs 3 of last 4 wrong)

**Progressive Exploration**: Early (±1) → Mid (±2) → End-test ceiling push (85%+ overall)
**Category Balance**: 50/50 audio/text via coin-flip | **Diversity**: Avoids last 2 mechanics
**Windows**: 5Q recent accuracy, 3Q for adjustments, full history for confidence

## UI Features

**Question Rendering**: Session state flags prevent media re-rendering | Unsplash images + Novakid TTS | Large buttons, clear fonts | Image description fallbacks

**Results Screen**: Celebration UI with emojis/badges | Color-coded level badges (0-5) | Skill stars (Vocab/Pronunciation/Grammar) | Kid-friendly language

## Dependencies

- **streamlit**: Web framework
- **google-genai**: Gemini 2.5 Pro API
- **python-dotenv**: Env management
- **requests**: Media API calls

Requires `GEMINI_API_KEY` in `.env`