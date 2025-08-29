# Novakid Adaptive Placement Test - Complete Implementation Guide

## Project Overview
An AI-powered English placement test for Novakid (EdTech company) that automatically adapts to student responses and determines their level (0-5). This is a text-based prototype using Streamlit UI and Google Gemini API.

## Project Structure
```
placement-test/
├── requirements.txt
├── generate_questions.py      # One-time question bank generator
├── app.py                     # Main Streamlit application
├── config.py                  # Configuration and constants
├── data/
│   ├── curriculum/
│   │   ├── novakid_levels.json
│   │   ├── competencies.json
│   │   ├── grammar.json
│   │   └── vocabulary.json
│   ├── questions.json         # Generated question bank
│   └── test_results/          # Student test results (created automatically)
└── lib/
    ├── __init__.py
    ├── adaptive_engine.py     # Adaptive test logic
    ├── question_renderer.py   # UI components for questions
    └── analyzer.py           # Post-test analysis with LLM
```

## Step 1: Setup and Dependencies

### requirements.txt
```txt
streamlit==1.47.1
google-genai>=1.32.0
python-dotenv==1.0.0
```

### Installation
```bash
pip install -r requirements.txt
```

### Environment Setup
Create `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
```

## Step 2: Configuration and Data Files

### config.py
```python
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
```

### data/curriculum/novakid_levels.json
```json
{
  "levels": [
    {
      "novakid_level": 0,
      "cefr_mapping": "pre-A1",
      "description": "Complete beginner",
      "mechanics": ["word-pronunciation-practice"]
    },
    {
      "novakid_level": 1,
      "cefr_mapping": "A1",
      "description": "Basic vocabulary and simple phrases",
      "mechanics": ["word-pronunciation-practice", "image-single-choice-from-texts"]
    },
    {
      "novakid_level": 2,
      "cefr_mapping": "A1+",
      "description": "Expanded vocabulary and basic grammar",
      "mechanics": ["word-pronunciation-practice", "image-single-choice-from-texts", "multiple-choice-text-text"]
    },
    {
      "novakid_level": 3,
      "cefr_mapping": "A2",
      "description": "Simple conversations and grammar",
      "mechanics": ["word-pronunciation-practice", "image-single-choice-from-texts", "multiple-choice-text-text"]
    },
    {
      "novakid_level": 4,
      "cefr_mapping": "B1",
      "description": "Complex sentences and varied vocabulary",
      "mechanics": ["word-pronunciation-practice", "image-single-choice-from-texts", "multiple-choice-text-text"]
    },
    {
      "novakid_level": 5,
      "cefr_mapping": "B2",
      "description": "Fluent communication and complex grammar",
      "mechanics": ["word-pronunciation-practice", "image-single-choice-from-texts", "multiple-choice-text-text"]
    }
  ],
  "mechanic_details": {
    "multiple-choice-text-text": {
      "min_level": 2,
      "skills": ["Grammar", "Reading"],
      "description": "Choose correct word to fill the gap"
    },
    "word-pronunciation-practice": {
      "min_level": 0,
      "skills": ["Speaking", "Pronunciation"],
      "description": "Practice pronouncing words"
    },
    "image-single-choice-from-texts": {
      "min_level": 1,
      "skills": ["Reading", "Vocabulary Recognition"],
      "description": "Choose text that matches image"
    }
  }
}
```

### data/curriculum/competencies.json
```json
[
  {"novakid_level": 0, "skill": "Vocabulary", "can_do": "Identify basic classroom objects", "complexity": 0.1},
  {"novakid_level": 0, "skill": "Vocabulary", "can_do": "Name primary colors", "complexity": 0.2},
  {"novakid_level": 0, "skill": "Speaking", "can_do": "Pronounce simple CVC words", "complexity": 0.2},
  {"novakid_level": 1, "skill": "Vocabulary", "can_do": "Name family members", "complexity": 0.3},
  {"novakid_level": 1, "skill": "Speaking", "can_do": "Introduce themselves with name and age", "complexity": 0.3},
  {"novakid_level": 1, "skill": "Reading", "can_do": "Match words to pictures", "complexity": 0.3},
  {"novakid_level": 2, "skill": "Grammar", "can_do": "Use present simple correctly", "complexity": 0.4},
  {"novakid_level": 2, "skill": "Reading", "can_do": "Understand simple sentences", "complexity": 0.4},
  {"novakid_level": 3, "skill": "Grammar", "can_do": "Use past simple tense", "complexity": 0.5},
  {"novakid_level": 3, "skill": "Speaking", "can_do": "Describe daily routines", "complexity": 0.5},
  {"novakid_level": 4, "skill": "Grammar", "can_do": "Use present perfect tense", "complexity": 0.6},
  {"novakid_level": 4, "skill": "Reading", "can_do": "Understand short paragraphs", "complexity": 0.6},
  {"novakid_level": 5, "skill": "Grammar", "can_do": "Use conditional sentences", "complexity": 0.7},
  {"novakid_level": 5, "skill": "Speaking", "can_do": "Express opinions fluently", "complexity": 0.7}
]
```

### data/curriculum/grammar.json
```json
[
  {"novakid_level": 0, "topic": "be verb", "examples": "I am, you are, he is", "complexity": 0.1},
  {"novakid_level": 1, "topic": "present simple", "examples": "I like, she likes, we play", "complexity": 0.3},
  {"novakid_level": 2, "topic": "articles", "examples": "a cat, an apple, the sun", "complexity": 0.4},
  {"novakid_level": 2, "topic": "plural forms", "examples": "cats, children, feet", "complexity": 0.4},
  {"novakid_level": 3, "topic": "past simple", "examples": "went, played, was/were", "complexity": 0.5},
  {"novakid_level": 3, "topic": "comparatives", "examples": "bigger, more beautiful", "complexity": 0.5},
  {"novakid_level": 4, "topic": "present perfect", "examples": "have done, has been", "complexity": 0.6},
  {"novakid_level": 4, "topic": "modal verbs", "examples": "can, should, must", "complexity": 0.6},
  {"novakid_level": 5, "topic": "conditionals", "examples": "if...then, would have", "complexity": 0.7},
  {"novakid_level": 5, "topic": "passive voice", "examples": "is done, was made", "complexity": 0.7}
]
```

### data/curriculum/vocabulary.json
```json
[
  {"novakid_level": 0, "topic": "colors", "words": "red, blue, yellow, green", "complexity": 0.1},
  {"novakid_level": 0, "topic": "numbers", "words": "one, two, three, four, five", "complexity": 0.1},
  {"novakid_level": 0, "topic": "classroom", "words": "pen, book, desk, chair", "complexity": 0.2},
  {"novakid_level": 1, "topic": "family", "words": "mother, father, sister, brother", "complexity": 0.3},
  {"novakid_level": 1, "topic": "animals", "words": "cat, dog, bird, fish", "complexity": 0.3},
  {"novakid_level": 1, "topic": "food", "words": "apple, bread, milk, water", "complexity": 0.3},
  {"novakid_level": 2, "topic": "daily activities", "words": "wake up, brush teeth, go to school", "complexity": 0.4},
  {"novakid_level": 2, "topic": "emotions", "words": "happy, sad, angry, excited", "complexity": 0.4},
  {"novakid_level": 3, "topic": "hobbies", "words": "reading, swimming, playing guitar", "complexity": 0.5},
  {"novakid_level": 3, "topic": "weather", "words": "sunny, rainy, cloudy, windy", "complexity": 0.5},
  {"novakid_level": 4, "topic": "professions", "words": "doctor, teacher, engineer, artist", "complexity": 0.6},
  {"novakid_level": 4, "topic": "environment", "words": "pollution, recycling, conservation", "complexity": 0.6},
  {"novakid_level": 5, "topic": "abstract concepts", "words": "democracy, justice, innovation", "complexity": 0.7},
  {"novakid_level": 5, "topic": "idioms", "words": "piece of cake, break the ice", "complexity": 0.7}
]
```

## Step 3: Question Generation Script

### generate_questions.py
```python
import json
import os
from google import genai
from config import GEMINI_API_KEY, MODEL_NAME, CURRICULUM_DIR, QUESTIONS_FILE, MVP_MECHANICS

client = genai.Client(api_key=GEMINI_API_KEY)

def load_curriculum_data():
    """Load all curriculum JSON files"""
    with open(os.path.join(CURRICULUM_DIR, 'novakid_levels.json')) as f:
        levels = json.load(f)
    with open(os.path.join(CURRICULUM_DIR, 'competencies.json')) as f:
        competencies = json.load(f)
    with open(os.path.join(CURRICULUM_DIR, 'grammar.json')) as f:
        grammar = json.load(f)
    with open(os.path.join(CURRICULUM_DIR, 'vocabulary.json')) as f:
        vocabulary = json.load(f)
    return levels, competencies, grammar, vocabulary

def generate_questions_prompt(level, mechanic, curriculum_data):
    """Create prompt for question generation"""
    levels, competencies, grammar, vocabulary = curriculum_data
    
    # Filter data for specific level
    level_competencies = [c for c in competencies if c['novakid_level'] == level]
    level_grammar = [g for g in grammar if g['novakid_level'] == level]
    level_vocabulary = [v for v in vocabulary if v['novakid_level'] == level]
    
    prompt = f"""You are an ESL curriculum expert creating placement test questions for children aged 4-12.

LEVEL: Novakid Level {level} ({levels['levels'][level]['cefr_mapping']})
MECHANIC: {mechanic}

CURRICULUM DATA:
Competencies: {json.dumps(level_competencies[:5])}
Grammar: {json.dumps(level_grammar[:5])}
Vocabulary: {json.dumps(level_vocabulary[:5])}

Generate exactly 10 questions for {mechanic} mechanic at Novakid Level {level}.

QUESTION FORMATS BY MECHANIC:

For 'multiple-choice-text-text':
{{
  "id": "L{level}_MC_001",
  "mechanic": "multiple-choice-text-text",
  "sentence": "She ___ to school every day.",
  "options": ["go", "goes", "going", "went"],
  "correct_answer": 1,
  "skill": "Grammar",
  "difficulty": 0.3,
  "grammar_point": "present simple third person"
}}

For 'word-pronunciation-practice':
{{
  "id": "L{level}_WP_001",
  "mechanic": "word-pronunciation-practice",
  "target_word": "elephant",
  "phonetic": "/ˈelɪfənt/",
  "image_description": "Large gray animal with trunk",
  "skill": "Pronunciation",
  "difficulty": 0.2,
  "word_type": "noun"
}}

For 'image-single-choice-from-texts':
{{
  "id": "L{level}_IS_001",
  "mechanic": "image-single-choice-from-texts",
  "image_description": "Clock showing 3:00",
  "options": ["three o'clock", "four o'clock", "half past three", "quarter to three"],
  "correct_answer": 0,
  "skill": "Vocabulary Recognition",
  "difficulty": 0.3,
  "topic": "telling time"
}}

Requirements:
- Age-appropriate vocabulary and topics
- Gradually increasing difficulty within the level
- Clear, unambiguous correct answers
- Varied topics to maintain engagement

Return ONLY a valid JSON array with 10 questions. No additional text."""

    return prompt

def generate_questions():
    """Generate questions for all levels and mechanics"""
    curriculum_data = load_curriculum_data()
    levels, _, _, _ = curriculum_data
    
    all_questions = {}
    
    for level in range(6):  # Levels 0-5
        level_questions = []
        level_mechanics = []
        
        # Determine which mechanics are available for this level
        if level >= 0:
            level_mechanics.append('word-pronunciation-practice')
        if level >= 1:
            level_mechanics.append('image-single-choice-from-texts')
        if level >= 2:
            level_mechanics.append('multiple-choice-text-text')
        
        for mechanic in level_mechanics:
            if mechanic not in MVP_MECHANICS:
                continue
                
            print(f"Generating questions for Level {level}, Mechanic: {mechanic}")
            
            prompt = generate_questions_prompt(level, mechanic, curriculum_data)
            
            try:
                response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                questions_text = response.text.strip()
                
                # Clean up response - remove markdown if present
                if '```json' in questions_text:
                    questions_text = questions_text.split('```json')[1].split('```')[0]
                elif '```' in questions_text:
                    questions_text = questions_text.split('```')[1].split('```')[0]
                
                questions = json.loads(questions_text)
                level_questions.extend(questions)
                print(f"  Generated {len(questions)} questions")
                
            except Exception as e:
                print(f"  Error generating questions: {e}")
                # Fallback: create sample questions manually
                level_questions.extend(create_fallback_questions(level, mechanic))
        
        all_questions[str(level)] = level_questions
    
    # Save generated questions
    os.makedirs(os.path.dirname(QUESTIONS_FILE), exist_ok=True)
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(all_questions, f, indent=2)
    
    print(f"\nGenerated {sum(len(q) for q in all_questions.values())} total questions")
    print(f"Saved to {QUESTIONS_FILE}")

def create_fallback_questions(level, mechanic):
    """Create sample questions if generation fails"""
    fallback = []
    
    if mechanic == 'multiple-choice-text-text':
        fallback = [
            {
                "id": f"L{level}_MC_FALLBACK_001",
                "mechanic": "multiple-choice-text-text",
                "sentence": "I ___ a student.",
                "options": ["am", "is", "are", "be"],
                "correct_answer": 0,
                "skill": "Grammar",
                "difficulty": 0.2,
                "grammar_point": "be verb"
            }
        ]
    elif mechanic == 'word-pronunciation-practice':
        fallback = [
            {
                "id": f"L{level}_WP_FALLBACK_001",
                "mechanic": "word-pronunciation-practice",
                "target_word": "cat",
                "phonetic": "/kæt/",
                "image_description": "Small furry pet animal",
                "skill": "Pronunciation",
                "difficulty": 0.1,
                "word_type": "noun"
            }
        ]
    elif mechanic == 'image-single-choice-from-texts':
        fallback = [
            {
                "id": f"L{level}_IS_FALLBACK_001",
                "mechanic": "image-single-choice-from-texts",
                "image_description": "Red round fruit",
                "options": ["apple", "banana", "orange", "grape"],
                "correct_answer": 0,
                "skill": "Vocabulary Recognition",
                "difficulty": 0.2,
                "topic": "fruits"
            }
        ]
    
    return fallback

if __name__ == "__main__":
    print("Starting question generation...")
    generate_questions()
```

## Step 4: Adaptive Engine

### lib/adaptive_engine.py
```python
import json
import random
from typing import Dict, List, Optional

class AdaptiveEngine:
    """Simple adaptive testing engine with deterministic rules"""
    
    def __init__(self, questions_file: str):
        with open(questions_file) as f:
            self.question_bank = json.load(f)
        
        self.current_level = 1  # Start at Level 1
        self.performance_window = []  # Track last N answers
        self.used_questions = set()  # Track used question IDs
        self.question_history = []  # Full test history
        self.calibration_complete = False
        self.calibration_count = 0
        
        # Mechanic availability by level
        self.mechanic_availability = {
            0: ['word-pronunciation-practice'],
            1: ['word-pronunciation-practice', 'image-single-choice-from-texts'],
            2: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text'],
            3: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text'],
            4: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text'],
            5: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text']
        }
    
    def get_next_question(self) -> Optional[Dict]:
        """Get the next question based on adaptive logic"""
        
        # Calibration phase: start with easy questions from multiple levels
        if not self.calibration_complete:
            question = self._get_calibration_question()
            if question:
                return question
        
        # Adaptive phase: select from appropriate level
        available_levels = self._get_available_levels()
        available_mechanics = self.mechanic_availability[self.current_level]
        
        # Try to find unused question
        for level in available_levels:
            level_questions = self.question_bank.get(str(level), [])
            
            # Filter by available mechanics and unused questions
            candidates = [
                q for q in level_questions 
                if q['mechanic'] in available_mechanics 
                and q['id'] not in self.used_questions
            ]
            
            if candidates:
                # Select question with some randomization
                question = random.choice(candidates[:5])  # Pick from top 5 candidates
                self.used_questions.add(question['id'])
                question['assigned_level'] = level
                return question
        
        return None
    
    def _get_calibration_question(self) -> Optional[Dict]:
        """Get calibration questions from different levels"""
        calibration_levels = [0, 1, 2]  # Test multiple levels initially
        
        if self.calibration_count < 3:
            level = calibration_levels[self.calibration_count]
            level_questions = self.question_bank.get(str(level), [])
            
            # Use only simple mechanics for calibration
            calibration_mechanics = ['word-pronunciation-practice', 'image-single-choice-from-texts']
            candidates = [
                q for q in level_questions 
                if q['mechanic'] in calibration_mechanics 
                and q['id'] not in self.used_questions
            ]
            
            if candidates:
                question = candidates[0]
                self.used_questions.add(question['id'])
                question['assigned_level'] = level
                question['is_calibration'] = True
                self.calibration_count += 1
                
                if self.calibration_count >= 3:
                    self.calibration_complete = True
                
                return question
        
        self.calibration_complete = True
        return None
    
    def _get_available_levels(self) -> List[int]:
        """Get pool of levels to select from based on performance"""
        base_levels = [self.current_level]
        
        # Add adjacent levels based on recent performance
        if len(self.performance_window) >= 2:
            recent_accuracy = sum(self.performance_window[-2:]) / 2
            
            if recent_accuracy >= 0.75 and self.current_level < 5:
                base_levels.append(self.current_level + 1)
            elif recent_accuracy <= 0.25 and self.current_level > 0:
                base_levels.append(self.current_level - 1)
        
        # Always include one level above and below for variety
        if self.current_level > 0 and (self.current_level - 1) not in base_levels:
            base_levels.append(self.current_level - 1)
        if self.current_level < 5 and (self.current_level + 1) not in base_levels:
            base_levels.append(self.current_level + 1)
        
        return sorted(base_levels)
    
    def update_performance(self, question_id: str, correct: bool, response_time: float = 0):
        """Update performance tracking and adjust level"""
        
        # Add to history
        self.question_history.append({
            'question_id': question_id,
            'correct': correct,
            'response_time': response_time,
            'level': self.current_level
        })
        
        # Update performance window
        self.performance_window.append(1 if correct else 0)
        if len(self.performance_window) > 5:
            self.performance_window.pop(0)
        
        # Adjust level based on performance
        if len(self.performance_window) >= 3:
            recent_accuracy = sum(self.performance_window[-3:]) / 3
            
            if recent_accuracy >= 0.8 and self.current_level < 5:
                self.current_level += 1
                print(f"Level increased to {self.current_level}")
            elif recent_accuracy <= 0.3 and self.current_level > 0:
                self.current_level -= 1
                print(f"Level decreased to {self.current_level}")
    
    def get_estimated_level(self) -> Dict:
        """Get current estimated level with confidence"""
        if not self.question_history:
            return {'level': 1, 'confidence': 0.0}
        
        # Calculate overall accuracy
        total_correct = sum(1 for h in self.question_history if h['correct'])
        accuracy = total_correct / len(self.question_history)
        
        # Confidence based on number of questions and consistency
        confidence = min(len(self.question_history) / 15, 1.0) * accuracy
        
        return {
            'level': self.current_level,
            'confidence': confidence,
            'accuracy': accuracy,
            'questions_answered': len(self.question_history)
        }
```

## Step 5: Question Renderer

### lib/question_renderer.py
```python
import streamlit as st
from typing import Dict, Optional

def render_question(question: Dict, question_number: int) -> Optional[any]:
    """Render question based on mechanic type"""
    
    mechanic = question['mechanic']
    
    st.markdown(f"### Question {question_number}")
    
    if mechanic == 'multiple-choice-text-text':
        return render_multiple_choice(question)
    elif mechanic == 'word-pronunciation-practice':
        return render_pronunciation(question)
    elif mechanic == 'image-single-choice-from-texts':
        return render_image_choice(question)
    else:
        st.error(f"Unknown mechanic: {mechanic}")
        return None

def render_multiple_choice(question: Dict) -> Optional[int]:
    """Render multiple choice grammar question"""
    st.write("**Fill in the blank:**")
    st.info(question['sentence'])
    
    # Create radio buttons for options
    selected = st.radio(
        "Choose the correct answer:",
        options=range(len(question['options'])),
        format_func=lambda x: f"{chr(65+x)}) {question['options'][x]}",
        key=f"mc_{question['id']}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Submit", type="primary", key=f"submit_{question['id']}"):
            return selected
    
    return None

def render_pronunciation(question: Dict) -> Optional[bool]:
    """Render word pronunciation practice"""
    st.write("**Practice saying this word:**")
    
    # Display word and phonetic
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {question['target_word']}")
        st.caption(f"Phonetic: {question['phonetic']}")
    with col2:
        st.info(f"📷 Image: {question['image_description']}")
    
    # Mock audio playback
    st.write("🔊 Click to hear pronunciation (mock)")
    
    # Mock recording interface
    st.warning("🎤 Practice saying the word out loud")
    
    # For MVP, just let student self-assess
    st.write("**How well did you pronounce it?**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😊 Well", key=f"good_{question['id']}"):
            return True
    with col2:
        if st.button("😐 OK", key=f"ok_{question['id']}"):
            return True
    with col3:
        if st.button("😕 Poorly", key=f"poor_{question['id']}"):
            return False
    
    return None

def render_image_choice(question: Dict) -> Optional[int]:
    """Render image with text choices"""
    st.write("**What does this image show?**")
    
    # Display mock image description
    st.info(f"📷 Image: {question['image_description']}")
    
    # Create columns for options
    cols = st.columns(2)
    selected_option = None
    
    for i, option in enumerate(question['options']):
        with cols[i % 2]:
            if st.button(option, key=f"img_opt_{question['id']}_{i}", use_container_width=True):
                selected_option = i
    
    if selected_option is not None:
        return selected_option
    
    return None

def check_answer(question: Dict, answer: any) -> bool:
    """Check if answer is correct"""
    mechanic = question['mechanic']
    
    if mechanic in ['multiple-choice-text-text', 'image-single-choice-from-texts']:
        return answer == question['correct_answer']
    elif mechanic == 'word-pronunciation-practice':
        # For pronunciation, we're using self-assessment
        return answer  # True if they said they did well or OK
    
    return False
```

## Step 6: Post-Test Analyzer

### lib/analyzer.py
```python
import json
from google import genai
from typing import Dict, List
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_results(test_history: List[Dict], questions: Dict) -> Dict:
    """Analyze test results using LLM to determine placement"""
    
    # Prepare analysis prompt
    prompt = create_analysis_prompt(test_history, questions)
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        result_text = response.text.strip()
        
        # Clean JSON response
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0]
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0]
        
        analysis = json.loads(result_text)
        return analysis
        
    except Exception as e:
        print(f"Error in LLM analysis: {e}")
        # Fallback to simple rule-based analysis
        return simple_analysis(test_history)

def create_analysis_prompt(test_history: List[Dict], questions: Dict) -> str:
    """Create prompt for LLM analysis"""
    
    # Enrich history with question details
    detailed_history = []
    for item in test_history:
        question = item['question']
        detailed_history.append({
            'question_id': question['id'],
            'level': question.get('assigned_level', 1),
            'mechanic': question['mechanic'],
            'skill': question.get('skill', 'Unknown'),
            'correct': item['correct'],
            'response_time': item.get('response_time', 0)
        })
    
    prompt = f"""Analyze this student's ESL placement test results to determine their Novakid level.

TEST RESULTS:
{json.dumps(detailed_history, indent=2)}

NOVAKID LEVEL SYSTEM:
- Level 0 (pre-A1): Complete beginner, basic words only
- Level 1 (A1): Basic vocabulary and simple phrases
- Level 2 (A1+): Expanded vocabulary and basic grammar
- Level 3 (A2): Simple conversations and grammar
- Level 4 (B1): Complex sentences and varied vocabulary
- Level 5 (B2): Fluent communication and complex grammar

ANALYSIS REQUIREMENTS:
1. Determine the student's placement level (0-5)
2. Calculate confidence in the placement
3. Identify strengths and weaknesses
4. Provide specific recommendations

Consider:
- Accuracy patterns across different mechanics
- Performance at different levels
- Consistency of responses
- Skills demonstrated

Return ONLY valid JSON in this exact format:
{{
  "placement": {{
    "novakid_level": 2,
    "confidence": 0.75,
    "cefr_equivalent": "A1+",
    "level_justification": "Consistent performance at Level 2 tasks with some Level 3 success"
  }},
  "skill_analysis": {{
    "vocabulary": {{
      "score": 0.7,
      "evidence": ["Correctly identified 7/10 vocabulary items", "Struggled with abstract concepts"]
    }},
    "pronunciation": {{
      "score": 0.8,
      "evidence": ["Good self-assessment on basic words", "Confident with simple sounds"]
    }},
    "grammar": {{
      "score": 0.6,
      "evidence": ["Understands present simple", "Difficulty with past tense"]
    }}
  }},
  "recommendations": {{
    "immediate_focus": ["Review past tense forms", "Practice vocabulary for daily activities"],
    "strengths_to_build_on": ["Good pronunciation foundation", "Strong basic vocabulary"],
    "suggested_starting_point": "Begin at Novakid Level 2 with grammar support",
    "estimated_progress": "Ready for Level 3 in 4-6 weeks with regular practice"
  }}
}}"""
    
    return prompt

def simple_analysis(test_history: List[Dict]) -> Dict:
    """Fallback rule-based analysis if LLM fails"""
    
    # Calculate basic metrics
    total_questions = len(test_history)
    correct_answers = sum(1 for h in test_history if h['correct'])
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    
    # Group by level
    level_performance = {}
    for item in test_history:
        level = item['question'].get('assigned_level', 1)
        if level not in level_performance:
            level_performance[level] = {'correct': 0, 'total': 0}
        level_performance[level]['total'] += 1
        if item['correct']:
            level_performance[level]['correct'] += 1
    
    # Determine placement level
    placement_level = 1
    for level in sorted(level_performance.keys()):
        level_accuracy = level_performance[level]['correct'] / level_performance[level]['total']
        if level_accuracy >= 0.7:
            placement_level = level
    
    # Map to CEFR
    cefr_mapping = {
        0: 'pre-A1',
        1: 'A1',
        2: 'A1+',
        3: 'A2',
        4: 'B1',
        5: 'B2'
    }
    
    return {
        "placement": {
            "novakid_level": placement_level,
            "confidence": accuracy,
            "cefr_equivalent": cefr_mapping.get(placement_level, 'A1'),
            "level_justification": f"Overall accuracy {accuracy:.1%} with best performance at Level {placement_level}"
        },
        "skill_analysis": {
            "vocabulary": {
                "score": accuracy,
                "evidence": [f"Answered {correct_answers}/{total_questions} questions correctly"]
            },
            "pronunciation": {
                "score": accuracy,
                "evidence": ["Self-assessed pronunciation practice"]
            },
            "grammar": {
                "score": accuracy,
                "evidence": ["Grammar performance matches overall accuracy"]
            }
        },
        "recommendations": {
            "immediate_focus": ["Continue practicing at current level"],
            "strengths_to_build_on": ["Build on demonstrated skills"],
            "suggested_starting_point": f"Begin at Novakid Level {placement_level}",
            "estimated_progress": "Progress varies by individual"
        }
    }