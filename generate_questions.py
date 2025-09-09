# Question bank generator script
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

For 'audio-single-choice-from-images':
{{
  "id": "L{level}_AI_001",
  "mechanic": "audio-single-choice-from-images",
  "target_audio": "elephant",
  "image_options": ["Large gray animal with trunk", "Small brown dog", "Yellow bird with wings"],
  "correct_answer": 0,
  "skill": "Listening Comprehension",
  "difficulty": 0.3,
  "topic": "animals"
}}

For 'sentence-pronunciation-practice':
{{
  "id": "L{level}_SP_001",
  "mechanic": "sentence-pronunciation-practice",
  "target_sentence": "How are you today?",
  "phonetic": "/haʊ ɑr ju təˈdeɪ/",
  "image_description": "Two people greeting each other with smiles",
  "skill": "Sentence Pronunciation",
  "difficulty": 0.4,
  "sentence_type": "greeting"
}}

For 'sentence-scramble':
{{
  "id": "L{level}_SS_001",
  "mechanic": "sentence-scramble",
  "sentence_template": "I ___ to ___ every day",
  "word_options": ["go", "school", "am", "went"],
  "correct_order": [0, 1],
  "skill": "Grammar",
  "difficulty": 0.4,
  "grammar_point": "sentence structure"
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
            level_mechanics.append('audio-single-choice-from-images')
            level_mechanics.append('sentence-pronunciation-practice')
        if level >= 1:
            level_mechanics.append('image-single-choice-from-texts')
            level_mechanics.append('sentence-scramble')
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
    elif mechanic == 'audio-single-choice-from-images':
        fallback = [
            {
                "id": f"L{level}_AI_FALLBACK_001",
                "mechanic": "audio-single-choice-from-images",
                "target_audio": "cat",
                "image_options": ["Small furry pet animal", "Large brown dog", "Colorful bird flying"],
                "correct_answer": 0,
                "skill": "Listening Comprehension",
                "difficulty": 0.2,
                "topic": "animals"
            }
        ]
    elif mechanic == 'sentence-pronunciation-practice':
        fallback = [
            {
                "id": f"L{level}_SP_FALLBACK_001",
                "mechanic": "sentence-pronunciation-practice",
                "target_sentence": "Hello, how are you?",
                "phonetic": "/həˈloʊ haʊ ɑr ju/",
                "image_description": "Two friends waving and smiling",
                "skill": "Sentence Pronunciation",
                "difficulty": 0.3,
                "sentence_type": "greeting"
            }
        ]
    elif mechanic == 'sentence-scramble':
        fallback = [
            {
                "id": f"L{level}_SS_FALLBACK_001",
                "mechanic": "sentence-scramble",
                "sentence_template": "I ___ a ___",
                "word_options": ["am", "student", "is", "teacher"],
                "correct_order": [0, 1],
                "skill": "Grammar",
                "difficulty": 0.3,
                "grammar_point": "be verb sentence"
            }
        ]
    
    return fallback

if __name__ == "__main__":
    print("Starting question generation...")
    generate_questions()