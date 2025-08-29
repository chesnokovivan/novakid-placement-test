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
python generate_questions.py
```

### Run Application
```bash
streamlit run app.py
```

## Architecture

The system follows a modular architecture:

- **app.py**: Main Streamlit application entry point
- **config.py**: Central configuration including API keys, test parameters, and file paths
- **generate_questions.py**: One-time script to generate question bank using Google Gemini API
- **lib/adaptive_engine.py**: Core adaptive testing algorithm that adjusts difficulty based on performance
- **lib/question_renderer.py**: UI components for different question types in Streamlit
- **lib/analyzer.py**: Post-test analysis using LLM to provide detailed placement recommendations

### Data Structure

- **data/curriculum/**: JSON files defining Novakid levels, competencies, grammar topics, and vocabulary
- **data/questions.json**: Generated question bank organized by level (created by generate_questions.py)
- **data/test_results/**: Student test results (auto-created during tests)

### Adaptive Algorithm

The AdaptiveEngine uses a calibration phase (3 initial questions across levels) followed by adaptive selection based on performance windows. Level adjustments occur when accuracy consistently exceeds 80% (level up) or falls below 30% (level down).

## Key Configuration

- Uses Google Gemini 2.5 Pro API for question generation and analysis
- Test length: 15 questions with 5-question performance window
- Three question mechanics with level-based availability
- Results analyzed by LLM with rule-based fallback

## Dependencies

- **streamlit**: Web UI framework
- **google-genai**: Google Gemini API client
- **python-dotenv**: Environment variable management

Requires GEMINI_API_KEY in .env file for LLM functionality.