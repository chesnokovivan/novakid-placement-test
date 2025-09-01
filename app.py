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
                'image-single-choice-from-texts': '🖼️ Vocabulary'
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
    """Display final test results"""
    st.title("🎉 Test Complete!")
    
    if st.session_state.test_results:
        placement = st.session_state.test_results['placement']
        
        # Main result card
        with st.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Novakid Level",
                    f"Level {placement['novakid_level']}",
                    help="Your recommended starting level"
                )
            
            with col2:
                st.metric(
                    "CEFR Level", 
                    placement['cefr_equivalent'],
                    help="Common European Framework reference"
                )
            
            with col3:
                confidence_pct = f"{placement['confidence']:.0%}"
                st.metric(
                    "Confidence",
                    confidence_pct,
                    help="How confident we are in this placement"
                )
        
        st.markdown("---")
        
        # Level justification with analysis method feedback
        st.subheader("📊 Placement Analysis")
        
        # Show analysis method info
        analysis_method = st.session_state.test_results.get('_analysis_method', 'unknown')
        if analysis_method == 'fallback':
            st.warning("⚠️ AI analysis unavailable - showing basic placement based on accuracy")
            error_info = st.session_state.test_results.get('_analysis_error', 'Unknown error')
            st.caption(f"Analysis error: {error_info}")
        elif analysis_method == 'ai':
            st.success("✨ Analysis powered by AI")
        
        st.info(placement['level_justification'])
        
        # Skill breakdown if available
        if 'skill_analysis' in st.session_state.test_results:
            st.subheader("🔍 Skill Analysis")
            
            skill_analysis = st.session_state.test_results['skill_analysis']
            
            cols = st.columns(len(skill_analysis))
            for i, (skill, data) in enumerate(skill_analysis.items()):
                with cols[i]:
                    score_pct = f"{data['score']:.0%}"
                    st.metric(skill.title(), score_pct)
                    with st.expander(f"View {skill} details"):
                        for evidence in data['evidence']:
                            st.write(f"• {evidence}")
        
        # Recommendations
        if 'recommendations' in st.session_state.test_results:
            st.subheader("💡 Recommendations")
            
            recs = st.session_state.test_results['recommendations']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Next Steps:**")
                for focus in recs.get('immediate_focus', []):
                    st.write(f"• {focus}")
                
                st.markdown("**Starting Point:**")
                st.success(recs.get('suggested_starting_point', 'Begin regular practice'))
            
            with col2:
                st.markdown("**Strengths:**")
                for strength in recs.get('strengths_to_build_on', []):
                    st.write(f"• {strength}")
                
                st.markdown("**Timeline:**")
                st.info(recs.get('estimated_progress', 'Continue practicing regularly'))
    
    # Test statistics
    st.markdown("---")
    st.subheader("📈 Test Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        correct_count = sum(1 for h in st.session_state.test_history if h['correct'])
        st.metric("Questions Correct", f"{correct_count}/{len(st.session_state.test_history)}")
    
    with col2:
        accuracy = correct_count / len(st.session_state.test_history) if st.session_state.test_history else 0
        st.metric("Accuracy", f"{accuracy:.0%}")
    
    with col3:
        final_level = st.session_state.adaptive_engine.current_level if st.session_state.adaptive_engine else 1
        st.metric("Final Test Level", f"Level {final_level}")
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Take Test Again", use_container_width=True):
            # Reset session state
            for key in list(st.session_state.keys()):
                if key.startswith(('test_', 'current_', 'question_', 'student_', 'adaptive_', 'answer_')):
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📄 View Detailed Results", use_container_width=True):
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