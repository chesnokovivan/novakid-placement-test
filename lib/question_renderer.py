# UI components for questions
import streamlit as st
from typing import Dict, Optional
from .media_apis import get_unsplash_image, get_audio_url
import streamlit.components.v1 as components

def render_question(question: Dict, question_number: int = None) -> Optional[any]:
    """Render question based on mechanic type"""
    
    mechanic = question['mechanic']
    
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
    # Check if we have a stored result first (prevents re-rendering)
    result_key = f"mc_result_{question['id']}"
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        return result
    
    # Centered big question text
    st.markdown(f"<h1 style='text-align: center; font-size: 2.5rem;'>{question['sentence']}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Extra big answer buttons for kids - no help tooltips
    for i, option in enumerate(question['options']):
        if st.button(
            f"{chr(65+i)}) {option}", 
            key=f"mc_opt_{question['id']}_{i}", 
            use_container_width=True,
            type="secondary"
        ):
            st.session_state[result_key] = i
            st.rerun()
    
    return None

def render_pronunciation(question: Dict) -> Optional[bool]:
    """Render word pronunciation practice"""
    # Check states that should skip media rendering
    recording_key = f'recording_{question["id"]}'
    result_key = f'speech_result_{question["id"]}'
    final_result_key = f'pronunciation_result_{question["id"]}'
    
    # Return final result if we have one
    if final_result_key in st.session_state:
        result = st.session_state[final_result_key]
        del st.session_state[final_result_key]
        return result
    
    # If in recording/result state, skip media and go to speech processing
    if recording_key in st.session_state or result_key in st.session_state:
        speech_result = render_speech_recognition(question['target_word'], question['id'])
        if speech_result is not None:
            st.session_state[final_result_key] = speech_result
            st.rerun()
        return None
    
    # Initial state: render media and interface
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; color: #1f77b4;'>{question['target_word']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; font-size: 1.5rem; color: #666;'>/{question['phonetic']}/</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Centered image and audio - only render in initial state
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Real image from Unsplash
        image_url = get_unsplash_image(question['image_description'])
        if image_url:
            st.image(image_url, width=400, caption=question['image_description'])
        else:
            st.info(f"📷 {question['image_description']}")
        
        # Real audio from TTS API
        audio_url = get_audio_url(question['target_word'])
        st.audio(audio_url)
    
    st.markdown("---")
    
    # Speech recognition interface
    speech_result = render_speech_recognition(question['target_word'], question['id'])
    
    return None

def render_image_choice(question: Dict) -> Optional[int]:
    """Render image with text choices"""
    # Check if we have a stored result first (prevents re-rendering)
    result_key = f"img_result_{question['id']}"
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        return result
    
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>What do you see?</h1>", unsafe_allow_html=True)
    
    # Centered image - only rendered in initial state
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Real image from Unsplash
        image_url = get_unsplash_image(question['image_description'])
        if image_url:
            st.image(image_url, width=500, caption=question['image_description'])
        else:
            st.info(f"📷 {question['image_description']}")
    
    st.markdown("---")
    
    # Extra big answer buttons for kids - no help tooltips
    for i, option in enumerate(question['options']):
        if st.button(
            option, 
            key=f"img_opt_{question['id']}_{i}", 
            use_container_width=True,
            type="secondary"
        ):
            st.session_state[result_key] = i
            st.rerun()
    
    return None

def render_speech_recognition(target_word: str, question_id: str) -> Optional[bool]:
    """Render fake speech recognition with recording simulation"""
    
    st.markdown("### 🎤 Say the word out loud!")
    
    # Create columns for centered interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Check if we're in recording state
        recording_key = f'recording_{question_id}'
        result_key = f'speech_result_{question_id}'
        
        if recording_key in st.session_state:
            # Show recording state
            st.markdown("### 🔴 Recording...")
            st.info("Speak clearly now!")
            
            # Auto progress bar to simulate recording
            import time
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                progress_bar.progress(i + 1)
                status_text.text(f'Listening... {i+1}%')
                time.sleep(0.03)  # 3 seconds total
            
            # Random result for demo
            import random
            success = random.choice([True, True, True, False])  # 75% success rate for demo
            
            # Store result and clean up recording state
            st.session_state[result_key] = success
            del st.session_state[recording_key]
            
            # Show result
            if success:
                st.success("✅ Great pronunciation! Well done!")
            else:
                st.error("😊 Good try! Keep practicing!")
            
            time.sleep(1.5)  # Brief pause to show result
            st.rerun()
        
        elif result_key in st.session_state:
            # Return the stored result and clean up
            result = st.session_state[result_key]
            del st.session_state[result_key]
            return result
        
        else:
            # Show initial record button
            if st.button("🎤 Record Your Voice", key=f"speech_btn_{question_id}", use_container_width=True, type="primary"):
                st.session_state[recording_key] = True
                st.rerun()
    
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