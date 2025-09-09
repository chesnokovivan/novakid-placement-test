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
        self.recent_mechanics = []  # Track last few mechanics for diversity
        
        # Mechanic availability by level - matches curriculum constraints
        self.mechanic_availability = {
            0: ['word-pronunciation-practice', 'audio-single-choice-from-images', 'sentence-pronunciation-practice'],
            1: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble'],
            2: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble'],
            3: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble'],
            4: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble'],
            5: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble']
        }
    
    def get_next_question(self) -> Optional[Dict]:
        """Get the next question based on adaptive logic"""
        
        # Calibration phase: start with easy questions from multiple levels
        if not self.calibration_complete:
            question = self._get_calibration_question()
            if question:
                return question
        
        # Adaptive phase: select from appropriate level with mechanic diversity
        available_levels = self._get_available_levels()
        available_mechanics = self.mechanic_availability[self.current_level]
        
        # Get preferred mechanics (not used recently)
        preferred_mechanics = self._get_preferred_mechanics(available_mechanics)
        
        # Try to find unused question with preferred mechanic first
        for level in available_levels:
            level_questions = self.question_bank.get(str(level), [])
            
            # First try preferred mechanics
            for mechanic_priority in [preferred_mechanics, available_mechanics]:
                candidates = [
                    q for q in level_questions 
                    if q['mechanic'] in mechanic_priority 
                    and q['id'] not in self.used_questions
                ]
                
                if candidates:
                    question = random.choice(candidates[:5])
                    self.used_questions.add(question['id'])
                    question['assigned_level'] = level
                    self._track_mechanic_usage(question['mechanic'])
                    return question
        
        return None
    
    def _get_calibration_question(self) -> Optional[Dict]:
        """Get calibration questions from different levels"""
        calibration_levels = [0, 1, 2]  # Test multiple levels initially
        
        if self.calibration_count < 3:
            level = calibration_levels[self.calibration_count]
            level_questions = self.question_bank.get(str(level), [])
            
            # Use diverse mechanics for calibration - respect level constraints
            level_mechanics = self.mechanic_availability[level]
            # Instead of cycling predictably, use all available mechanics for better diversity
            calibration_mechanics = level_mechanics
            candidates = [
                q for q in level_questions 
                if q['mechanic'] in calibration_mechanics 
                and q['id'] not in self.used_questions
            ]
            
            if candidates:
                question = random.choice(candidates)
                self.used_questions.add(question['id'])
                question['assigned_level'] = level
                question['is_calibration'] = True
                self.calibration_count += 1
                self._track_mechanic_usage(question['mechanic'])
                
                if self.calibration_count >= 3:
                    self.calibration_complete = True
                
                return question
        
        self.calibration_complete = True
        return None
    
    def _get_available_levels(self) -> List[int]:
        """Get pool of levels to select from based on performance - with dynamic exploration"""
        base_levels = [self.current_level]
        
        # Calculate recent accuracy for performance-responsive exploration
        recent_accuracy = 0
        if len(self.performance_window) >= 2:
            recent_accuracy = sum(self.performance_window[-2:]) / 2
        
        # Dynamic range expansion based on performance patterns
        if len(self.performance_window) >= 3:
            last3_accuracy = sum(self.performance_window[-3:]) / 3
            
            # High performers get expanded exploration range
            if last3_accuracy >= 0.9:  # 90%+ recent performance
                # Perfect or near-perfect: explore aggressively upward
                for level in range(self.current_level, min(6, self.current_level + 4)):
                    if level not in base_levels:
                        base_levels.append(level)
            elif last3_accuracy >= 0.75:  # 75%+ recent performance
                # Strong performers: moderate upward exploration
                for level in range(self.current_level, min(6, self.current_level + 2)):
                    if level not in base_levels:
                        base_levels.append(level)
        
        # Standard exploration for moderate/poor performers
        if recent_accuracy >= 0.75 and self.current_level < 5:
            if (self.current_level + 1) not in base_levels:
                base_levels.append(self.current_level + 1)
        elif recent_accuracy <= 0.25 and self.current_level > 0:
            if (self.current_level - 1) not in base_levels:
                base_levels.append(self.current_level - 1)
        
        # Always include variety for average performers
        if len(self.performance_window) < 3 or sum(self.performance_window[-3:]) / 3 < 0.75:
            if self.current_level > 0 and (self.current_level - 1) not in base_levels:
                base_levels.append(self.current_level - 1)
            if self.current_level < 5 and (self.current_level + 1) not in base_levels:
                base_levels.append(self.current_level + 1)
        
        # End-test ceiling push for high performers
        questions_remaining = 15 - len(self.question_history)
        if questions_remaining <= 5 and len(self.question_history) > 0:
            overall_accuracy = sum(1 for h in self.question_history if h['correct']) / len(self.question_history)
            if overall_accuracy >= 0.85:
                # Push toward highest levels in final questions
                max_level = min(5, self.current_level + 2)
                if max_level not in base_levels:
                    base_levels.append(max_level)
        
        return sorted([level for level in base_levels if 0 <= level <= 5])
    
    def _get_preferred_mechanics(self, available_mechanics: List[str]) -> List[str]:
        """Get mechanics that haven't been used recently for diversity"""
        if len(self.recent_mechanics) < 2:
            return available_mechanics
        
        # Get mechanics not used in last 2 questions (reduced from 3 for better diversity)
        recent_set = set(self.recent_mechanics[-2:])
        preferred = [m for m in available_mechanics if m not in recent_set]
        
        return preferred if preferred else available_mechanics
    
    def _track_mechanic_usage(self, mechanic: str):
        """Track mechanic usage for diversity"""
        self.recent_mechanics.append(mechanic)
        if len(self.recent_mechanics) > 5:
            self.recent_mechanics.pop(0)
    
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
        
        # Adjust level based on performance with aggressive jumping for perfect performers
        if len(self.performance_window) >= 3:
            recent_accuracy = sum(self.performance_window[-3:]) / 3
            
            # Aggressive level jumping for perfect performance
            if recent_accuracy == 1.0 and len(self.performance_window) >= 4:
                # Perfect accuracy over 4+ questions: jump 2 levels
                if self.current_level < 4:
                    self.current_level += 2
                    print(f"Level jumped to {self.current_level} (perfect performance)")
                elif self.current_level < 5:
                    self.current_level += 1
                    print(f"Level increased to {self.current_level}")
            elif recent_accuracy >= 0.8 and self.current_level < 5:
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