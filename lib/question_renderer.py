# UI components for questions
import streamlit as st
from typing import Dict, Optional, List
from .media_apis import get_unsplash_image, get_audio_url

def render_question(question: Dict, question_number: int = None) -> Optional[any]:
    """Render question based on mechanic type"""
    
    mechanic = question['mechanic']
    
    if mechanic == 'multiple-choice-text-text':
        return render_multiple_choice(question)
    elif mechanic == 'word-pronunciation-practice':
        return render_pronunciation(question)
    elif mechanic == 'image-single-choice-from-texts':
        return render_image_choice(question)
    elif mechanic == 'audio-single-choice-from-images':
        return render_audio_image_choice(question)
    elif mechanic == 'sentence-pronunciation-practice':
        return render_sentence_pronunciation(question)
    elif mechanic == 'sentence-scramble':
        return render_sentence_scramble(question)
    elif mechanic == 'audio-category-sorting':
        return render_audio_category_sorting(question)
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
    recording_key = f'recording_{question["id"]}'
    result_key = f'speech_result_{question["id"]}'
    final_result_key = f'pronunciation_result_{question["id"]}'
    media_rendered_key = f'pron_media_rendered_{question["id"]}'
    
    # Return final result if we have one
    if final_result_key in st.session_state:
        result = st.session_state[final_result_key]
        del st.session_state[final_result_key]
        # Clean up rendered flags
        if media_rendered_key in st.session_state:
            del st.session_state[media_rendered_key]
        return result
    
    # Always show the word header
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; color: #1f77b4;'>{question['target_word']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; font-size: 1.5rem; color: #666;'>/{question['phonetic']}/</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Only render media once per question using session state flag
    if media_rendered_key not in st.session_state:
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
        # Mark media as rendered
        st.session_state[media_rendered_key] = True
    else:
        # Show placeholder to maintain layout
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.empty()  # Maintain space but don't re-render media
    
    st.markdown("---")
    
    # Speech recognition interface
    speech_result = render_speech_recognition(question['target_word'], question['id'])
    if speech_result is not None:
        st.session_state[final_result_key] = speech_result
        st.rerun()
    
    return None

def render_image_choice(question: Dict) -> Optional[int]:
    """Render image with text choices"""
    result_key = f"img_result_{question['id']}"
    image_rendered_key = f"img_rendered_{question['id']}"
    
    # Check if we have a stored result
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        # Clean up the rendered flag
        if image_rendered_key in st.session_state:
            del st.session_state[image_rendered_key]
        return result
    
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>What do you see?</h1>", unsafe_allow_html=True)
    
    # Only render image once per question using session state flag
    if image_rendered_key not in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Real image from Unsplash
            image_url = get_unsplash_image(question['image_description'])
            if image_url:
                st.image(image_url, width=500)
            else:
                st.info(f"📷 {question['image_description']}")

            # Add clear description under the image to help when AI image doesn't match well
            st.markdown(f"<p style='text-align: center; font-size: 1.1rem; color: #666; margin: 10px 0; font-style: italic;'>{question['image_description']}</p>", unsafe_allow_html=True)
        # Mark image as rendered
        st.session_state[image_rendered_key] = True
    else:
        # Show placeholder to maintain layout
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.empty()  # Maintain space but don't re-render image
    
    st.markdown("---")
    
    # Answer buttons
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

def render_audio_image_choice(question: Dict) -> Optional[int]:
    """Render audio with image choices"""
    result_key = f"audio_img_result_{question['id']}"
    media_rendered_key = f"audio_img_media_rendered_{question['id']}"
    
    # Check if we have a stored result
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        # Clean up the rendered flag
        if media_rendered_key in st.session_state:
            del st.session_state[media_rendered_key]
        return result
    
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>🎧 Listen and Choose</h1>", unsafe_allow_html=True)
    
    # Only render audio once per question using session state flag
    if media_rendered_key not in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Real audio from TTS API
            audio_url = get_audio_url(question['target_audio'])
            st.audio(audio_url)
        # Mark media as rendered
        st.session_state[media_rendered_key] = True
    else:
        # Show placeholder to maintain layout
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.empty()  # Maintain space but don't re-render audio
    
    st.markdown("---")
    
    # Image options in a row
    cols = st.columns(len(question['image_options']))
    for i, image_desc in enumerate(question['image_options']):
        with cols[i]:
            # Real image from Unsplash
            image_url = get_unsplash_image(image_desc)
            if image_url:
                st.image(image_url, width=200)
            else:
                st.info(f"📷 {image_desc}")
            
            if st.button(
                f"Choose {chr(65+i)}", 
                key=f"audio_img_opt_{question['id']}_{i}", 
                use_container_width=True,
                type="secondary"
            ):
                st.session_state[result_key] = i
                st.rerun()
    
    return None

def render_sentence_pronunciation(question: Dict) -> Optional[bool]:
    """Render sentence pronunciation practice"""
    recording_key = f'sentence_recording_{question["id"]}'
    result_key = f'sentence_speech_result_{question["id"]}'
    final_result_key = f'sentence_pronunciation_result_{question["id"]}'
    media_rendered_key = f'sentence_pron_media_rendered_{question["id"]}'
    
    # Return final result if we have one
    if final_result_key in st.session_state:
        result = st.session_state[final_result_key]
        del st.session_state[final_result_key]
        # Clean up rendered flags
        if media_rendered_key in st.session_state:
            del st.session_state[media_rendered_key]
        return result
    
    # Always show the sentence header
    st.markdown(f"<h1 style='text-align: center; font-size: 2.5rem; color: #1f77b4;'>{question['target_sentence']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; font-size: 1.5rem; color: #666;'>/{question['phonetic']}/</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Only render media once per question using session state flag
    if media_rendered_key not in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Real image from Unsplash
            image_url = get_unsplash_image(question['image_description'])
            if image_url:
                st.image(image_url, width=400, caption=question['image_description'])
            else:
                st.info(f"📷 {question['image_description']}")
            
            # Real audio from TTS API
            audio_url = get_audio_url(question['target_sentence'])
            st.audio(audio_url)
        # Mark media as rendered
        st.session_state[media_rendered_key] = True
    else:
        # Show placeholder to maintain layout
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.empty()  # Maintain space but don't re-render media
    
    st.markdown("---")
    
    # Speech recognition interface
    speech_result = render_speech_recognition(question['target_sentence'], question['id'], is_sentence=True)
    if speech_result is not None:
        st.session_state[final_result_key] = speech_result
        st.rerun()
    
    return None

def render_sentence_scramble(question: Dict) -> Optional[List[int]]:
    """Render sentence scramble with drag-drop word ordering"""
    result_key = f"scramble_result_{question['id']}"
    selected_words_key = f"scramble_selected_{question['id']}"
    
    # Check if we have a stored result
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        # Clean up selected words
        if selected_words_key in st.session_state:
            del st.session_state[selected_words_key]
        return result
    
    # Initialize selected words if not present
    if selected_words_key not in st.session_state:
        st.session_state[selected_words_key] = []
    
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>🧩 Put the words in order</h1>", unsafe_allow_html=True)
    
    # Show sentence template with blanks
    sentence_parts = question['sentence_template'].split('___')
    display_sentence = ""
    selected_words = st.session_state[selected_words_key]
    blank_index = 0
    
    for i, part in enumerate(sentence_parts):
        display_sentence += part
        if i < len(sentence_parts) - 1:  # Not the last part
            if blank_index < len(selected_words):
                display_sentence += f"<span style='background: #e3f2fd; padding: 5px 10px; border-radius: 5px; margin: 0 5px; font-weight: bold;'>{question['word_options'][selected_words[blank_index]]}</span>"
            else:
                display_sentence += "<span style='background: #f5f5f5; padding: 5px 10px; border-radius: 5px; margin: 0 5px; border: 2px dashed #ccc;'>___</span>"
            blank_index += 1
    
    st.markdown(f"<h2 style='text-align: center; font-size: 1.8rem; margin: 30px 0;'>{display_sentence}</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Word options buttons
    st.markdown("### Choose words in order:")
    
    # Calculate how many blanks we need to fill
    num_blanks = question['sentence_template'].count('___')
    
    # Show available words
    cols = st.columns(min(len(question['word_options']), 4))  # Max 4 columns
    for i, word in enumerate(question['word_options']):
        col_idx = i % len(cols)
        with cols[col_idx]:
            # Disable button if already selected or if we've filled all blanks
            disabled = i in selected_words or len(selected_words) >= num_blanks
            button_type = "secondary" if not disabled else "primary"
            
            if st.button(
                word, 
                key=f"word_btn_{question['id']}_{i}",
                use_container_width=True,
                type=button_type,
                disabled=disabled
            ):
                if len(selected_words) < num_blanks:
                    st.session_state[selected_words_key].append(i)
                    st.rerun()
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Clear All", key=f"clear_{question['id']}", use_container_width=True):
            st.session_state[selected_words_key] = []
            st.rerun()
    
    with col2:
        if st.button("⬅️ Remove Last", key=f"remove_last_{question['id']}", use_container_width=True):
            if selected_words:
                st.session_state[selected_words_key].pop()
                st.rerun()
    
    with col3:
        # Submit button - only enabled when all blanks are filled
        submit_disabled = len(selected_words) < num_blanks
        if st.button(
            "✅ Submit", 
            key=f"submit_{question['id']}", 
            use_container_width=True, 
            type="primary",
            disabled=submit_disabled
        ):
            st.session_state[result_key] = selected_words.copy()
            st.rerun()
    
    return None

def render_speech_recognition(target_word: str, question_id: str, is_sentence: bool = False) -> Optional[bool]:
    """Render fake speech recognition with recording simulation"""
    
    prompt_text = "### 🎤 Say the sentence out loud!" if is_sentence else "### 🎤 Say the word out loud!"
    st.markdown(prompt_text)
    
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

def render_audio_category_sorting(question: Dict) -> Optional[Dict]:
    """Render audio category sorting mechanic"""
    result_key = f"category_sort_result_{question['id']}"
    media_rendered_key = f"category_sort_media_rendered_{question['id']}"
    answers_key = f"category_sort_answers_{question['id']}"
    
    # Check if we have a stored result
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        # Clean up flags and answers
        if media_rendered_key in st.session_state:
            del st.session_state[media_rendered_key]
        if answers_key in st.session_state:
            del st.session_state[answers_key]
        return result
    
    # Initialize answers dict if not present
    if answers_key not in st.session_state:
        st.session_state[answers_key] = {}
    
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>🎧 Sort the Words!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Listen to each word and click the correct category</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show categories as cards/buttons
    st.markdown("### Categories:")
    category_cols = st.columns(len(question['categories']))
    
    for i, category in enumerate(question['categories']):
        with category_cols[i]:
            # Category card with image
            st.markdown(f"<div style='text-align: center; background: #f0f8ff; padding: 20px; border-radius: 15px; margin: 10px; border: 3px solid #1f77b4;'>"
                       f"<h3 style='color: #1f77b4; margin: 0;'>{category['name']}</h3>"
                       f"</div>", unsafe_allow_html=True)
            
            # Real image from Unsplash for category
            image_url = get_unsplash_image(category['image_description'])
            if image_url:
                st.image(image_url, width=200, caption=category['name'])
            else:
                st.info(f"📷 {category['image_description']}")
    
    st.markdown("---")
    
    # Show audio items to sort
    st.markdown("### Listen and Sort:")
    
    answers = st.session_state[answers_key]
    all_answered = True
    
    for i, audio_item in enumerate(question['audio_items']):
        word = audio_item['word']
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            # Audio player with word
            audio_url = get_audio_url(word)
            st.audio(audio_url)
            st.markdown(f"<p style='text-align: center; font-size: 1.5rem;'>Word #{i+1}</p>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("→")
        
        with col3:
            # Category selection buttons
            if word not in answers:
                all_answered = False
                
            for cat_idx, category in enumerate(question['categories']):
                selected = answers.get(word) == cat_idx
                button_type = "primary" if selected else "secondary"
                
                if st.button(
                    f"🏷️ {category['name']}", 
                    key=f"sort_btn_{question['id']}_{i}_{cat_idx}",
                    type=button_type,
                    use_container_width=True
                ):
                    st.session_state[answers_key][word] = cat_idx
                    st.rerun()
        
        st.markdown("---")
    
    # Submit button
    if all_answered:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("✅ Submit All", key=f"submit_sort_{question['id']}", type="primary", use_container_width=True):
                st.session_state[result_key] = answers.copy()
                st.rerun()
    else:
        st.info("🎯 Please sort all words before submitting!")
    
    return None

def check_answer(question: Dict, answer: any) -> bool:
    """Check if answer is correct"""
    mechanic = question['mechanic']
    
    if mechanic in ['multiple-choice-text-text', 'image-single-choice-from-texts', 'audio-single-choice-from-images']:
        return answer == question['correct_answer']
    elif mechanic in ['word-pronunciation-practice', 'sentence-pronunciation-practice']:
        # For pronunciation, we're using self-assessment
        return answer  # True if they said they did well or OK
    elif mechanic == 'sentence-scramble':
        # Check if the selected word order matches the correct order
        return answer == question['correct_order']
    elif mechanic == 'audio-category-sorting':
        # Check if all audio items are sorted correctly
        if not isinstance(answer, dict):
            return False
        
        correct_count = 0
        total_items = len(question['audio_items'])
        
        for audio_item in question['audio_items']:
            word = audio_item['word']
            correct_category = audio_item['category_index']
            user_category = answer.get(word, -1)
            
            if user_category == correct_category:
                correct_count += 1
        
        # Consider it correct if they get majority right (to be kid-friendly)
        return correct_count >= (total_items * 0.6)
    
    return False