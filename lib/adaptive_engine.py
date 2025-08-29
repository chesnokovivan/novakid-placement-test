# Adaptive test logic
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