# Adaptive test logic
import json
import random
from typing import Dict, List, Optional

class AdaptiveEngine:
    """Simple adaptive testing engine with deterministic rules"""
    
    def __init__(self, questions_file: str, 
                 early_test_questions: int = 5,
                 max_exploration_distance: int = 2,
                 cooldown_questions: int = 2,
                 momentum_decay: float = 0.7):
        with open(questions_file) as f:
            self.question_bank = json.load(f)
        
        # Configurable parameters
        self.early_test_questions = early_test_questions  # Questions before full exploration
        self.max_exploration_distance = max_exploration_distance  # Max level range expansion
        self.cooldown_questions = cooldown_questions  # Questions to wait after level change
        self.momentum_decay = momentum_decay  # Momentum reduction after level jumps
        
        self.current_level = 1  # Start at Level 1
        self.performance_window = []  # Track last N answers
        self.used_questions = set()  # Track used question IDs
        self.question_history = []  # Full test history
        self.calibration_complete = False
        self.calibration_count = 0
        self.recent_mechanics = []  # Track last few mechanics for diversity
        
        # Momentum system variables
        self.level_momentum = 0.0  # Track direction and speed of level changes (-2.0 to +2.0)
        self.consecutive_successes = 0  # Track consecutive correct answers
        self.level_change_cooldown = 0  # Prevent rapid oscillation between levels
        
        # Mechanic categories for dynamic balancing
        self.AUDIO_MECHANICS = [
            'word-pronunciation-practice', 
            'audio-single-choice-from-images', 
            'sentence-pronunciation-practice', 
            'audio-category-sorting'
        ]
        self.TEXT_MECHANICS = [
            'image-single-choice-from-texts', 
            'multiple-choice-text-text', 
            'sentence-scramble'
        ]
        
        # Mechanic availability by level - matches curriculum constraints
        self.mechanic_availability = {
            0: ['word-pronunciation-practice', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'audio-category-sorting'],
            1: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble', 'audio-category-sorting'],
            2: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble', 'audio-category-sorting'],
            3: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble', 'audio-category-sorting'],
            4: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble', 'audio-category-sorting'],
            5: ['word-pronunciation-practice', 'image-single-choice-from-texts', 'multiple-choice-text-text', 'audio-single-choice-from-images', 'sentence-pronunciation-practice', 'sentence-scramble', 'audio-category-sorting']
        }
    
    def _select_category_balanced(self, available_levels: List[int], preferred_mechanics: List[str]) -> Optional[Dict]:
        """Select question with true 50/50 category balance"""
        # First decide: audio or text category (50/50 coin flip)
        use_audio_category = random.random() < 0.5
        
        # Try the chosen category first, then fallback to the other
        for attempt_audio in [use_audio_category, not use_audio_category]:
            # Get mechanics for this category
            target_mechanics = self.AUDIO_MECHANICS if attempt_audio else self.TEXT_MECHANICS
            
            # Filter to available mechanics at current level
            available_mechanics = self.mechanic_availability[self.current_level]
            category_mechanics = [m for m in available_mechanics if m in target_mechanics]
            
            # Apply diversity filter (prefer recently unused mechanics)
            diverse_mechanics = [m for m in category_mechanics if m not in self.recent_mechanics[-2:]]
            mechanics_to_try = diverse_mechanics if diverse_mechanics else category_mechanics
            
            
            # Also consider preferred mechanics if they overlap
            if preferred_mechanics:
                preferred_in_category = [m for m in preferred_mechanics if m in mechanics_to_try]
                if preferred_in_category:
                    mechanics_to_try = preferred_in_category
            
            # Collect candidates across all available levels
            all_candidates = []
            for level in available_levels:
                level_questions = self.question_bank.get(str(level), [])
                candidates = [
                    q for q in level_questions 
                    if q['mechanic'] in mechanics_to_try 
                    and q['id'] not in self.used_questions
                ]
                
                # Add level assignment to candidates
                for candidate in candidates[:5]:  # Limit per level to avoid dominance
                    candidate_copy = candidate.copy()
                    candidate_copy['assigned_level'] = level
                    all_candidates.append(candidate_copy)
            
            # Select randomly from category candidates
            if all_candidates:
                question = random.choice(all_candidates)
                self.used_questions.add(question['id'])
                self._track_mechanic_usage(question['mechanic'])
                return question
        
        return None
    
    def get_next_question(self) -> Optional[Dict]:
        """Get the next question based on adaptive logic"""
        
        # Calibration phase: start with easy questions from multiple levels
        if not self.calibration_complete:
            question = self._get_calibration_question()
            if question:
                return question
        
        # Adaptive phase: select with true category balance
        available_levels = self._get_available_levels()
        available_mechanics = self.mechanic_availability[self.current_level]
        
        # Get preferred mechanics (not used recently)
        preferred_mechanics = self._get_preferred_mechanics(available_mechanics)
        
        # Use the clean category-first selection
        question = self._select_category_balanced(available_levels, preferred_mechanics)
        if question:
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
                # Use category-balanced selection for calibration too
                question = self._select_category_balanced([level], [])
                if question:
                    question['is_calibration'] = True
                    self.calibration_count += 1
                    
                    if self.calibration_count >= 3:
                        self.calibration_complete = True
                    
                    return question
        
        self.calibration_complete = True
        return None
    
    def _get_available_levels(self) -> List[int]:
        """Conservative level selection with momentum consideration and progressive range expansion"""
        base_levels = [self.current_level]
        
        # Don't explore aggressively until we have stability (early test phase)
        if len(self.question_history) < self.early_test_questions:
            # Early test: stay very close to current level
            if self.current_level > 0:
                base_levels.append(self.current_level - 1)
            if self.current_level < 5:
                base_levels.append(self.current_level + 1)
            return sorted(base_levels)
        
        # Calculate momentum-adjusted exploration distance
        recent_accuracy = sum(self.performance_window[-3:]) / 3 if len(self.performance_window) >= 3 else 0
        
        # Progressive exploration distance based on test progress
        questions_answered = len(self.question_history)
        max_exploration = min(self.max_exploration_distance, 1 + questions_answered // 5)  # Gradually increase range
        
        # Momentum-based exploration adjustments
        if recent_accuracy >= 0.8 and self.level_momentum > 0:
            # Good performance with positive momentum: explore upward, but limited
            upper_bound = min(5, self.current_level + max_exploration)
            for level in range(self.current_level + 1, upper_bound + 1):
                base_levels.append(level)
        elif recent_accuracy <= 0.4 and self.level_momentum < 0:
            # Poor performance with negative momentum: explore downward  
            lower_bound = max(0, self.current_level - max_exploration)
            for level in range(lower_bound, self.current_level):
                base_levels.append(level)
        else:
            # Mixed performance or neutral momentum: limited exploration
            if self.current_level > 0:
                base_levels.append(self.current_level - 1)
            if self.current_level < 5:
                base_levels.append(self.current_level + 1)
        
        # Level 5 exploration phase - ensure high performers get adequate Level 5 testing
        if self.current_level >= 4 and len(self.question_history) >= 8:
            overall_accuracy = sum(1 for h in self.question_history if h['correct']) / len(self.question_history)
            if overall_accuracy >= 0.85:
                # Force Level 5 inclusion for comprehensive assessment
                if 5 not in base_levels:
                    base_levels.append(5)
                
                # If already at Level 5, prioritize staying there for thorough assessment
                if self.current_level == 5 and recent_accuracy >= 0.5:  # Lower threshold for Level 5 retention
                    # Remove lower levels to focus on Level 5 assessment (keep Level 4 as backup)
                    base_levels = [level for level in base_levels if level >= 4]
                    # Ensure Level 5 is prioritized
                    if 5 not in base_levels:
                        base_levels.append(5)
        
        # End-test ceiling push (more conservative than before)
        questions_remaining = 15 - len(self.question_history)
        if questions_remaining <= 3 and len(self.question_history) > 0:
            overall_accuracy = sum(1 for h in self.question_history if h['correct']) / len(self.question_history)
            if overall_accuracy >= 0.85 and self.level_momentum > 1.0:
                # Only push to next level, not jumping multiple levels
                max_level = min(5, self.current_level + 1)
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
        """Smoother level adjustments with momentum and cooldown system"""
        
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
        
        # Update momentum based on performance
        if correct:
            self.consecutive_successes += 1
            self.level_momentum = min(self.level_momentum + 0.3, 2.0)
        else:
            self.consecutive_successes = 0
            self.level_momentum = max(self.level_momentum - 0.5, -2.0)
        
        # Handle cooldown - don't change levels during cooldown period
        if self.level_change_cooldown > 0:
            self.level_change_cooldown -= 1
            return
        
        # Level adjustment with momentum thresholds and sustained performance requirements
        if len(self.performance_window) >= 3:
            recent_accuracy = sum(self.performance_window[-3:]) / 3
            
            # Upward level adjustments - require sustained performance
            if recent_accuracy >= 0.9 and self.level_momentum > 1.5:
                if self.consecutive_successes >= 4 and self.current_level < 5:
                    # Maximum jump of 1 level at a time (no more 2-level jumps)
                    self.current_level += 1
                    self.level_change_cooldown = self.cooldown_questions
                    self.level_momentum *= self.momentum_decay  # Reduce momentum after jump
                    print(f"Level increased to {self.current_level} (excellent performance)")
            elif recent_accuracy >= 0.75 and self.level_momentum > 0.8:
                if self.consecutive_successes >= 3 and self.current_level < 5:
                    self.current_level += 1
                    self.level_change_cooldown = self.cooldown_questions
                    self.level_momentum *= self.momentum_decay
                    print(f"Level increased to {self.current_level} (good performance)")
            
            # Early Level 5 promotion for exceptional performers to allow adequate assessment time
            elif (recent_accuracy >= 0.85 and self.level_momentum > 1.0 and 
                  self.current_level == 4 and len(self.question_history) <= 10):
                # Promote to Level 5 earlier if showing strong Level 4 performance
                if self.consecutive_successes >= 2:
                    self.current_level += 1
                    self.level_change_cooldown = 1  # Shorter cooldown for final level
                    self.level_momentum *= self.momentum_decay
                    print(f"Level increased to {self.current_level} (strong Level 4 performance - early Level 5 assessment)")
            
            # Downward level adjustments - but not from Level 5 easily
            elif recent_accuracy <= 0.3 and self.level_momentum < -0.8:
                if self.current_level > 0:
                    # Make it harder to drop from Level 5 - need sustained poor performance
                    if self.current_level == 5:
                        # Only drop from Level 5 if really struggling (need 2 consecutive wrong answers)
                        if self.consecutive_successes == 0 and len(self.performance_window) >= 4:
                            recent_errors = len([x for x in self.performance_window[-4:] if x == 0])
                            if recent_errors >= 3:  # 3 out of last 4 wrong
                                self.current_level -= 1
                                self.level_change_cooldown = self.cooldown_questions
                                self.level_momentum *= self.momentum_decay
                                print(f"Level decreased to {self.current_level} (sustained difficulties at Level 5)")
                    else:
                        # Normal downward adjustment for other levels
                        self.current_level -= 1
                        self.level_change_cooldown = self.cooldown_questions
                        self.level_momentum *= self.momentum_decay
                        print(f"Level decreased to {self.current_level} (needs support)")
    
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