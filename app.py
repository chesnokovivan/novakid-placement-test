import streamlit as st
import json
import os
import datetime
from typing import Dict, Optional

from lib.adaptive_engine import AdaptiveEngine
from lib.question_renderer import render_question, check_answer
from lib.analyzer import analyze_results
from config import QUESTIONS_FILE, RESULTS_DIR, QUESTIONS_PER_TEST

st.set_page_config(
    page_title="Novakid Placement Test",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for bigger buttons for kids
st.markdown("""
<style>
    .stButton > button {
        height: 80px !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: 3px solid #e0e0e0 !important;
        margin: 10px 0 !important;
    }
    
    .stButton > button:hover {
        border-color: #1f77b4 !important;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3) !important;
        transform: translateY(-2px) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
        height: 90px !important;
    }
    
    .stButton > button[kind="secondary"] {
        height: 85px !important;
        background-color: #f8f9fa !important;
    }
    
    /* Make images more centered and responsive */
    .stImage {
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Center audio player */
    .stAudio {
        display: flex !important;
        justify-content: center !important;
    }
</style>

<script>
// Listen for speech recognition results from iframe
window.addEventListener('message', function(event) {
    if (event.data.type === 'speech_result') {
        // Store result in sessionStorage for Streamlit to check
        sessionStorage.setItem('speech_result_' + event.data.questionId, JSON.stringify(event.data));
        // Force page refresh to trigger Streamlit check
        setTimeout(() => window.location.reload(), 1000);
    }
});
</script>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'test_completed' not in st.session_state:
        st.session_state.test_completed = False
    if 'adaptive_engine' not in st.session_state:
        st.session_state.adaptive_engine = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 0
    if 'test_history' not in st.session_state:
        st.session_state.test_history = []
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'test_results' not in st.session_state:
        st.session_state.test_results = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False

def check_prerequisites():
    """Check if required files exist"""
    if not os.path.exists(QUESTIONS_FILE):
        st.error("❌ Question bank not found!")
        st.info("Please run: `python generate_questions.py` to generate the question bank first.")
        st.stop()
    
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)

def show_welcome_screen():
    """Display welcome screen and collect student info"""
    st.title("🎓 Novakid English Placement Test")
    
    st.markdown("""
    Welcome! This adaptive test will help us determine your English level.
    
    **What to expect:**
    - 15 carefully selected questions
    - Questions adapt to your performance
    - 3 types: Grammar, Pronunciation, and Vocabulary
    - Takes about 10-15 minutes
    
    **Instructions:**
    - Answer each question to the best of your ability
    - Take your time - there's no time pressure
    - The test will get easier or harder based on your answers
    """)
    
    st.markdown("---")
    
    with st.form("student_info"):
        st.subheader("Student Information")
        name = st.text_input("Your name (optional):", placeholder="Enter your name")
        age = st.selectbox("Your age:", options=["Prefer not to say"] + list(range(4, 18)))
        
        start_button = st.form_submit_button("🚀 Start Test", type="primary", use_container_width=True)
        
        if start_button:
            st.session_state.student_name = name or f"Student_{datetime.datetime.now().strftime('%H%M')}"
            st.session_state.student_age = age
            start_test()
            st.rerun()

def start_test():
    """Initialize the adaptive test"""
    try:
        st.session_state.adaptive_engine = AdaptiveEngine(QUESTIONS_FILE)
        st.session_state.test_started = True
        st.session_state.question_number = 0
        st.session_state.test_history = []
        st.session_state.current_question = st.session_state.adaptive_engine.get_next_question()
        st.session_state.answer_submitted = False
        
        if st.session_state.current_question:
            st.session_state.question_number = 1
        
    except Exception as e:
        st.error(f"Failed to start test: {e}")
        st.info("Please make sure the question bank is generated and your API key is configured.")

def process_answer(answer):
    """Process student answer and move to next question"""
    if st.session_state.current_question is None:
        return
    
    # Check if answer is correct
    is_correct = check_answer(st.session_state.current_question, answer)
    
    # Add to test history
    st.session_state.test_history.append({
        'question': st.session_state.current_question,
        'answer': answer,
        'correct': is_correct,
        'response_time': 0  # Not tracking time in MVP
    })
    
    # Update adaptive engine
    st.session_state.adaptive_engine.update_performance(
        st.session_state.current_question['id'], 
        is_correct
    )
    
    # Brief feedback
    if is_correct:
        st.success("✅ Correct!")
    else:
        st.error("❌ Incorrect")
    
    # Check if test should continue
    if len(st.session_state.test_history) >= QUESTIONS_PER_TEST:
        complete_test()
        return
    
    # Get next question
    next_question = st.session_state.adaptive_engine.get_next_question()
    if next_question:
        st.session_state.current_question = next_question
        st.session_state.question_number += 1
        st.session_state.answer_submitted = False
    else:
        complete_test()
    
    # Brief pause then auto-advance
    import time
    time.sleep(1)
    st.rerun()

def complete_test():
    """Complete the test and show results"""
    st.session_state.test_completed = True
    
    # Analyze results
    try:
        questions_dict = {}
        with open(QUESTIONS_FILE) as f:
            questions_dict = json.load(f)
        
        st.session_state.test_results = analyze_results(
            st.session_state.test_history,
            questions_dict
        )
    except Exception as e:
        st.error(f"Error analyzing results: {e}")
        print(f"Analysis error details: {e}")
        # Fallback to basic results
        correct_count = sum(1 for h in st.session_state.test_history if h['correct'])
        accuracy = correct_count / len(st.session_state.test_history)
        estimated_level = min(5, max(0, int(accuracy * 5)))
        
        st.session_state.test_results = {
            "placement": {
                "novakid_level": estimated_level,
                "confidence": accuracy,
                "cefr_equivalent": ["pre-A1", "A1", "A1+", "A2", "B1", "B2"][estimated_level],
                "level_justification": f"Based on {accuracy:.1%} accuracy"
            }
        }
    
    # Save results
    save_test_results()

def save_test_results():
    """Save test results to file"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_result_{st.session_state.student_name}_{timestamp}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    result_data = {
        "student_name": st.session_state.student_name,
        "student_age": getattr(st.session_state, 'student_age', 'Not provided'),
        "timestamp": timestamp,
        "test_history": st.session_state.test_history,
        "analysis": st.session_state.test_results,
        "final_level": st.session_state.adaptive_engine.current_level if st.session_state.adaptive_engine else 1
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
        st.success(f"Results saved: {filename}")
    except Exception as e:
        st.warning(f"Could not save results: {e}")

def show_test_interface():
    """Show the main test interface"""
    # All progress and scoring info goes to sidebar
    with st.sidebar:
        st.title("🎓 Test Progress")
        
        # Progress
        progress = st.session_state.question_number / QUESTIONS_PER_TEST
        st.metric("Questions", f"{st.session_state.question_number}/{QUESTIONS_PER_TEST}")
        st.progress(progress)
        
        # Current level
        current_level = st.session_state.adaptive_engine.current_level
        st.metric("Current Level", f"Level {current_level}")
        
        # Question type
        if st.session_state.current_question:
            mechanic = st.session_state.current_question['mechanic']
            mechanic_labels = {
                'multiple-choice-text-text': '📝 Grammar',
                'word-pronunciation-practice': '🗣️ Pronunciation', 
                'image-single-choice-from-texts': '🖼️ Vocabulary',
                'audio-single-choice-from-images': '🎧 Listen & Choose',
                'sentence-pronunciation-practice': '🗣️ Sentence Practice',
                'sentence-scramble': '🧩 Word Order'
            }
            st.info(mechanic_labels.get(mechanic, mechanic))
        
        # Running score
        if st.session_state.test_history:
            correct_count = sum(1 for h in st.session_state.test_history if h['correct'])
            accuracy = correct_count / len(st.session_state.test_history)
            st.metric("Accuracy", f"{accuracy:.0%}")
    
    # Clean main area - only question and answers
    if st.session_state.current_question and not st.session_state.answer_submitted:
        # Render the question
        answer = render_question(st.session_state.current_question, st.session_state.question_number)
        
        # Process answer if provided
        if answer is not None:
            st.session_state.answer_submitted = True
            process_answer(answer)
    
    elif st.session_state.answer_submitted:
        # Just show feedback briefly, auto-advance handled in process_answer
        pass
    
    else:
        st.warning("No more questions available. Completing test...")
        complete_test()
        st.rerun()

def show_results_screen():
    """Display final test results with kid-friendly design"""
    # Big celebration header
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 4rem; margin: 0;'>🎉</h1>
        <h1 style='color: #1f77b4; font-size: 3rem; margin: 0;'>Awesome Job!</h1>
        <h2 style='color: #666; font-size: 1.5rem; margin: 10px 0;'>You completed the test! 🌟</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.test_results:
        placement = st.session_state.test_results['placement']
        
        # Giant level badge
        level_colors = {0: "#FF6B6B", 1: "#4ECDC4", 2: "#45B7D1", 3: "#96CEB4", 4: "#FECA57", 5: "#9B59B6"}
        level_color = level_colors.get(placement['novakid_level'], "#1f77b4")
        
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, {level_color}22 0%, {level_color}44 100%); 
                    border-radius: 20px; margin: 20px 0; border: 3px solid {level_color};'>
            <h1 style='font-size: 4rem; color: {level_color}; margin: 0;'>Level {placement['novakid_level']}</h1>
            <h3 style='color: #333; margin: 10px 0;'>Your English Level</h3>
            <p style='font-size: 1.2rem; color: #666; margin: 5px 0;'>CEFR: {placement['cefr_equivalent']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fun skill badges
        if 'skill_analysis' in st.session_state.test_results:
            st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🏆 Your Super Skills!</h2>", unsafe_allow_html=True)
            
            skill_analysis = st.session_state.test_results['skill_analysis']
            skill_icons = {"vocabulary": "📚", "pronunciation": "🗣️", "grammar": "✏️"}
            
            cols = st.columns(len(skill_analysis))
            for i, (skill, data) in enumerate(skill_analysis.items()):
                with cols[i]:
                    score = data['score']
                    icon = skill_icons.get(skill, "⭐")
                    
                    # Star rating based on score
                    stars = "⭐" * max(1, min(5, int(score * 5)))
                    
                    # Color coding
                    if score >= 0.9:
                        badge_color = "#4CAF50"  # Green
                        badge_text = "Amazing!"
                    elif score >= 0.7:
                        badge_color = "#FF9800"  # Orange
                        badge_text = "Great!"
                    else:
                        badge_color = "#2196F3"  # Blue
                        badge_text = "Good!"
                    
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background: {badge_color}22; 
                                border-radius: 15px; margin: 10px; border: 2px solid {badge_color};'>
                        <div style='font-size: 3rem; margin: 0;'>{icon}</div>
                        <h3 style='color: {badge_color}; margin: 10px 0;'>{skill.title()}</h3>
                        <div style='font-size: 1.5rem; margin: 5px 0;'>{stars}</div>
                        <p style='color: {badge_color}; font-weight: bold; margin: 5px 0;'>{badge_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # What this means section
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🎯 What This Means</h2>", unsafe_allow_html=True)
        
        # Kid-friendly explanation
        level_descriptions = {
            0: "You're just starting your English adventure! 🌱",
            1: "You know some English words and can say simple things! 🌿", 
            2: "You can have basic conversations and understand simple stories! 🌳",
            3: "You can talk about many topics and understand most conversations! 🌲",
            4: "You're really good at English and can discuss complex topics! 🏔️",
            5: "You're almost like a native speaker - amazing job! 🏆"
        }
        
        description = level_descriptions.get(placement['novakid_level'], "You're doing great!")
        st.markdown(f"""
        <div style='text-align: center; padding: 25px; background: #f0f8ff; 
                    border-radius: 15px; border-left: 5px solid #1f77b4;'>
            <p style='font-size: 1.3rem; color: #333; margin: 0;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Next steps - kid friendly
        if 'recommendations' in st.session_state.test_results:
            st.markdown("---")
            st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🚀 What's Next?</h2>", unsafe_allow_html=True)
            
            recs = st.session_state.test_results['recommendations']
            
            # Starting point as a big friendly card
            starting_point = recs.get('suggested_starting_point', 'Keep practicing!')
            st.markdown(f"""
            <div style='text-align: center; padding: 25px; background: #e8f5e8; 
                        border-radius: 15px; border: 2px solid #4CAF50; margin: 20px 0;'>
                <h3 style='color: #4CAF50; margin: 0 0 10px 0;'>🎯 Your Starting Point</h3>
                <p style='font-size: 1.2rem; color: #333; margin: 0;'>{starting_point}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Strengths and focus areas in kid-friendly format
            col1, col2 = st.columns(2)
            
            with col1:
                if recs.get('strengths_to_build_on'):
                    st.markdown("""
                    <div style='padding: 20px; background: #fff3cd; border-radius: 15px; border: 2px solid #ffc107;'>
                        <h3 style='color: #e67e22; text-align: center;'>💪 Your Superpowers</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for strength in recs['strengths_to_build_on'][:2]:  # Limit to 2 for kids
                        st.markdown(f"<p style='margin: 10px 0; color: #666;'>⭐ {strength}</p>", unsafe_allow_html=True)
            
            with col2:
                if recs.get('immediate_focus'):
                    st.markdown("""
                    <div style='padding: 20px; background: #e1f5fe; border-radius: 15px; border: 2px solid #03a9f4;'>
                        <h3 style='color: #0277bd; text-align: center;'>🎯 Practice These</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for focus in recs['immediate_focus'][:2]:  # Limit to 2 for kids
                        st.markdown(f"<p style='margin: 10px 0; color: #666;'>📚 {focus}</p>", unsafe_allow_html=True)
    
    # Fun test stats for kids
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #1f77b4;'>📊 Your Test Numbers</h2>", unsafe_allow_html=True)
    
    correct_count = sum(1 for h in st.session_state.test_history if h['correct'])
    total_questions = len(st.session_state.test_history)
    accuracy = correct_count / total_questions if total_questions else 0
    
    # Visual progress bar for correct answers
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 15px; margin: 10px 0;'>
            <h3 style='color: #333; margin: 0 0 15px 0;'>You got {correct_count} out of {total_questions} questions right!</h3>
            <div style='background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0;'>
                <div style='background: #4CAF50; height: 100%; width: {accuracy*100}%; transition: width 0.5s;'></div>
            </div>
            <p style='font-size: 1.2rem; color: #4CAF50; margin: 10px 0; font-weight: bold;'>{accuracy:.0%} Correct! 🎯</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Big friendly action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Try Again!", use_container_width=True, type="primary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                if key.startswith(('test_', 'current_', 'question_', 'student_', 'adaptive_', 'answer_')):
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("🔍 See All Questions", use_container_width=True):
            show_detailed_results()

def show_detailed_results():
    """Show detailed question-by-question results"""
    st.subheader("📋 Detailed Results")
    
    for i, item in enumerate(st.session_state.test_history, 1):
        question = item['question']
        
        with st.expander(f"Question {i}: {question['mechanic'].replace('-', ' ').title()}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if question['mechanic'] == 'multiple-choice-text-text':
                    st.write(f"**Question:** {question['sentence']}")
                    st.write(f"**Your answer:** {question['options'][item['answer']]}")
                    if not item['correct']:
                        st.write(f"**Correct answer:** {question['options'][question['correct_answer']]}")
                
                elif question['mechanic'] == 'word-pronunciation-practice':
                    st.write(f"**Word:** {question['target_word']}")
                    st.write(f"**Your assessment:** {'Good' if item['answer'] else 'Needs practice'}")
                
                elif question['mechanic'] == 'image-single-choice-from-texts':
                    st.write(f"**Image:** {question['image_description']}")
                    st.write(f"**Your answer:** {question['options'][item['answer']]}")
                    if not item['correct']:
                        st.write(f"**Correct answer:** {question['options'][question['correct_answer']]}")
            
            with col2:
                status = "✅" if item['correct'] else "❌"
                st.markdown(f"**Result:** {status}")
                st.caption(f"Level {question.get('assigned_level', 'Unknown')}")

def main():
    """Main application logic"""
    # Initialize session state
    initialize_session_state()
    
    # Check prerequisites
    check_prerequisites()
    
    # Route to appropriate screen
    if not st.session_state.test_started:
        show_welcome_screen()
    
    elif st.session_state.test_completed:
        show_results_screen()
    
    else:
        show_test_interface()
    
    # Sidebar with debug info (for development)
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.json({
            "Current Level": st.session_state.adaptive_engine.current_level if st.session_state.adaptive_engine else "N/A",
            "Questions Answered": len(st.session_state.test_history),
            "Performance Window": st.session_state.adaptive_engine.performance_window if st.session_state.adaptive_engine else [],
            "Test Started": st.session_state.test_started,
            "Test Completed": st.session_state.test_completed
        })

if __name__ == "__main__":
    main()