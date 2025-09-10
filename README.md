# AI-Powered English Placement Test

An intelligent placement test system for Novakid that determines student English proficiency levels (0-5) through adaptive testing. The system uses AI to adjust question difficulty in real-time based on student performance.

## How the Adaptive Engine Works

### 🎯 Smart Calibration Phase
The test begins with 3 carefully selected calibration questions:
- **Question 1**: Level 0 pronunciation (baseline assessment)
- **Question 2**: Level 1 vocabulary recognition (basic skills check)
- **Question 3**: Level 2 grammar (structural understanding)

This gives the system an initial understanding of the student's abilities across different skill areas.

### 🧠 Intelligent Question Selection
After calibration, the adaptive engine:

- **Responds to Performance**: High accuracy (90%+) triggers exploration of higher levels, while low accuracy focuses on foundational skills
- **Maintains Variety**: Tracks recently used question types to prevent boring repetition
- **Follows Curriculum**: Respects CEFR progression - no grammar questions until Level 2, vocabulary recognition starts at Level 1
- **Explores Dynamically**: Strong performers get expanded level ranges to properly assess their ceiling

### ⚡ Real-Time Adaptation
The system adjusts difficulty after every answer:
- **Level Jumping**: Perfect performance over 4+ questions can trigger 2-level jumps
- **Standard Progression**: 80% accuracy moves up one level, 30% accuracy moves down
- **End-Test Push**: Final questions challenge high performers with advanced content to ensure accurate placement

### 🎨 Three Question Types
1. **Pronunciation Practice**: Listen and repeat target words (all levels)
2. **Image-Text Matching**: Choose text that matches images (Level 1+)  
3. **Grammar Fill-in-the-Blank**: Complete sentences with correct grammar (Level 2+)

### 🏆 Sophisticated Placement
The final recommendation considers:
- **Overall accuracy** across all questions
- **Performance patterns** at different difficulty levels
- **Skill-specific strengths** (pronunciation, vocabulary, grammar)
- **Confidence metrics** based on consistency

### 📊 Key Features
- **15 questions total** for efficient yet thorough assessment
- **6 proficiency levels** mapped to CEFR standards (pre-A1 to B2)
- **Kid-friendly interface** designed for ages 4-12
- **Real-time analysis** using Google Gemini AI for detailed placement recommendations

The result is an accurate, engaging placement test that adapts to each student's unique learning profile while maintaining pedagogical soundness.