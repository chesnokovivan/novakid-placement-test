# Post-test analysis with LLM
import json
import os
from google import genai
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables directly
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

from config import MODEL_NAME

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
        
        # Add success flag for UI feedback
        analysis['_analysis_method'] = 'ai'
        return analysis
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in LLM analysis: {error_msg}")
        
        # Enhanced fallback with error info
        fallback_result = simple_analysis(test_history)
        fallback_result['_analysis_method'] = 'fallback'
        fallback_result['_analysis_error'] = error_msg
        
        return fallback_result

def create_analysis_prompt(test_history: List[Dict], questions: Dict) -> str:
    """Create prompt for LLM analysis"""
    
    # Enrich history with question details including grammar points
    detailed_history = []
    for item in test_history:
        question = item['question']
        detailed_history.append({
            'question_id': question['id'],
            'level': question.get('assigned_level', 1),
            'mechanic': question['mechanic'],
            'skill': question.get('skill', 'Unknown'),
            'grammar_point': question.get('grammar_point', 'general'),
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
- Accuracy patterns across different mechanics AND skills
- Performance at different levels
- Consistency of responses
- Skills demonstrated (Grammar, Sentence Structure, Vocabulary, Pronunciation, etc.)
- Specific grammar points where student struggled (modal verbs, word order, tenses, etc.)

IMPORTANT ANALYSIS GUIDELINES:
- sentence-scramble mechanic tests ONLY "Sentence Structure" (word order), NOT grammar choices
- multiple-choice-text-text tests "Grammar" including modal verbs, verb forms, articles
- Provide specific recommendations based on actual skills tested, not just mechanic names
- If student failed "sentence-scramble" → recommend "word order practice"
- If student failed "multiple-choice-text-text" with "modal verbs" → recommend "modal verb practice"

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
    # Group by skill for detailed analysis
    skill_performance = {}
    # Track failed grammar points
    failed_grammar_points = []

    for item in test_history:
        level = item['question'].get('assigned_level', 1)
        skill = item['question'].get('skill', 'Unknown')
        grammar_point = item['question'].get('grammar_point', 'general')

        # Level performance
        if level not in level_performance:
            level_performance[level] = {'correct': 0, 'total': 0}
        level_performance[level]['total'] += 1
        if item['correct']:
            level_performance[level]['correct'] += 1

        # Skill performance
        if skill not in skill_performance:
            skill_performance[skill] = {'correct': 0, 'total': 0}
        skill_performance[skill]['total'] += 1
        if item['correct']:
            skill_performance[skill]['correct'] += 1
        else:
            # Track failed grammar points for recommendations
            if grammar_point != 'general':
                failed_grammar_points.append(grammar_point)

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

    # Generate skill-specific scores and recommendations
    skill_scores = {}
    recommendations = []
    strengths = []

    for skill, perf in skill_performance.items():
        skill_accuracy = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
        skill_scores[skill.lower().replace(' ', '_')] = {
            "score": skill_accuracy,
            "evidence": [f"Answered {perf['correct']}/{perf['total']} {skill} questions correctly"]
        }

        # Generate recommendations based on performance
        if skill_accuracy < 0.6:
            if skill == 'Grammar':
                if failed_grammar_points:
                    recommendations.extend([f"Practice {point}" for point in set(failed_grammar_points)])
                else:
                    recommendations.append("Review grammar fundamentals")
            elif skill == 'Sentence Structure':
                recommendations.append("Practice word order and sentence formation")
            elif skill == 'Vocabulary':
                recommendations.append("Expand vocabulary through reading and practice")
            elif skill == 'Pronunciation':
                recommendations.append("Practice pronunciation with audio materials")
        else:
            strengths.append(f"Strong {skill.lower()} skills")

    # Ensure we have the required skill categories
    required_skills = ['vocabulary', 'pronunciation', 'grammar']
    for skill in required_skills:
        if skill not in skill_scores:
            skill_scores[skill] = {
                "score": accuracy,
                "evidence": ["General performance assessment"]
            }

    if not recommendations:
        recommendations = ["Continue practicing at current level"]
    if not strengths:
        strengths = ["Build on demonstrated skills"]

    return {
        "placement": {
            "novakid_level": placement_level,
            "confidence": accuracy,
            "cefr_equivalent": cefr_mapping.get(placement_level, 'A1'),
            "level_justification": f"Overall accuracy {accuracy:.1%} with best performance at Level {placement_level}"
        },
        "skill_analysis": skill_scores,
        "recommendations": {
            "immediate_focus": recommendations[:3],  # Limit to top 3
            "strengths_to_build_on": strengths[:3],  # Limit to top 3
            "suggested_starting_point": f"Begin at Novakid Level {placement_level}",
            "estimated_progress": "Progress varies by individual"
        }
    }