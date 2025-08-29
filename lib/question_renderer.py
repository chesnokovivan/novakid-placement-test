# UI components for questions
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