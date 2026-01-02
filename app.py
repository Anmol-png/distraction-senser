import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add utils to path
sys.path.append(os.path.dirname(__file__))
from utils.data_manager import DataManager
import config

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Initialize Data Manager
data_manager = DataManager()

# Initialize session state
if 'study_start_time' not in st.session_state:
    st.session_state.study_start_time = None
if 'session_duration' not in st.session_state:
    st.session_state.session_duration = 0
if 'distraction_count' not in st.session_state:
    st.session_state.distraction_count = 0
if 'is_studying' not in st.session_state:
    st.session_state.is_studying = False
if 'last_face_time' not in st.session_state:
    st.session_state.last_face_time = time.time()
if 'focus_time' not in st.session_state:
    st.session_state.focus_time = 0
if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = 0

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .alert-danger {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        font-size: 1.3rem;
        text-align: center;
        animation: pulse 1.5s infinite;
        box-shadow: 0 4px 15px rgba(255,107,107,0.4);
    }
    .alert-success {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        font-size: 1.3rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(81,207,102,0.4);
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    .status-focused {
        background-color: #51cf66;
        color: white;
    }
    .status-distracted {
        background-color: #ff6b6b;
        color: white;
    }
    .camera-frame {
        border: 3px solid #667eea;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f'<h1 class="main-header">{config.APP_ICON} Distraction Sense AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-Powered Study Focus Companion</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    distraction_threshold = st.slider(
        "Distraction Alert Threshold",
        min_value=config.MIN_DISTRACTION_THRESHOLD,
        max_value=config.MAX_DISTRACTION_THRESHOLD,
        value=config.DEFAULT_DISTRACTION_THRESHOLD,
        help="Time in seconds before distraction alert triggers"
    )
    
    alert_sound = st.checkbox("🔔 Enable Sound Alerts", value=True)
    show_camera = st.checkbox("📹 Show Camera Feed", value=True)
    
    st.divider()
    
    st.header("📊 Session Overview")
    
    if st.session_state.is_studying:
        elapsed = int(time.time() - st.session_state.study_start_time)
        st.metric("⏱️ Session Time", f"{elapsed // 60}m {elapsed % 60}s")
        st.metric("🎯 Distractions", st.session_state.distraction_count)
        
        focus_score = max(0, 100 - (st.session_state.distraction_count * config.DISTRACTION_PENALTY))
        st.metric("⭐ Focus Score", f"{focus_score}%")
    else:
        stats = data_manager.get_statistics()
        st.metric("📚 Total Sessions", stats['total_sessions'])
        st.metric("⏰ Total Study Time", f"{stats['total_study_time'] // 60} min")
        st.metric("📊 Avg Focus Score", f"{stats['avg_focus_score']:.1f}%")
    
    st.divider()
    
    st.header("💡 Quick Tips")
    st.info("""
    - Keep your face visible
    - Good lighting helps
    - Take breaks every 25-30 min
    - Stay hydrated 💧
    """)
    
    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.button("⚠️ Confirm Clear", type="primary"):
            data_manager.clear_all_data()
            st.success("Data cleared!")
            st.rerun()

# Main content area
tab1, tab2, tab3 = st.tabs(["🎯 Study Session", "📊 Analytics", "ℹ️ About"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Live Monitoring")
        
        camera_placeholder = st.empty()
        
        # Control buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if not st.session_state.is_studying:
                if st.button("▶️ Start Session", use_container_width=True, type="primary"):
                    st.session_state.is_studying = True
                    st.session_state.study_start_time = time.time()
                    st.session_state.distraction_count = 0
                    st.session_state.focus_time = 0
                    st.rerun()
        
        with btn_col2:
            if st.session_state.is_studying:
                if st.button("⏸️ Pause", use_container_width=True):
                    st.session_state.is_studying = False
                    st.info("Session paused. Click Start to resume.")
        
        with btn_col3:
            if st.session_state.is_studying:
                if st.button("⏹️ End Session", use_container_width=True, type="secondary"):
                    # Save session
                    session_duration = int(time.time() - st.session_state.study_start_time)
                    focus_score = max(0, 100 - (st.session_state.distraction_count * config.DISTRACTION_PENALTY))
                    
                    session_data = {
                        "start_time": datetime.fromtimestamp(st.session_state.study_start_time).isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "duration": session_duration,
                        "distractions": st.session_state.distraction_count,
                        "focus_score": focus_score
                    }
                    
                    data_manager.add_session(session_data)
                    
                    st.session_state.is_studying = False
                    st.success(f"✅ Session saved! Duration: {session_duration // 60}m, Score: {focus_score}%")
                    time.sleep(2)
                    st.rerun()
    
    with col2:
        st.subheader("🎯 Current Status")
        status_placeholder = st.empty()
        alert_placeholder = st.empty()
        tips_placeholder = st.empty()

    # Main monitoring loop
    if st.session_state.is_studying:
        cap = cv2.VideoCapture(0)
        
        with mp_face_detection.FaceDetection(
            min_detection_confidence=config.FACE_DETECTION_CONFIDENCE
        ) as face_detection:
            
            ret, frame = cap.read()
            
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_frame)
                
                face_detected = False
                
                if results.detections:
                    face_detected = True
                    st.session_state.last_face_time = time.time()
                    st.session_state.focus_time += 1
                    
                    if show_camera:
                        for detection in results.detections:
                            mp_drawing.draw_detection(rgb_frame, detection)
                
                # Check for distraction
                time_since_face = time.time() - st.session_state.last_face_time
                current_time = time.time()
                
                if time_since_face > distraction_threshold:
                    # Distraction detected
                    if current_time - st.session_state.last_alert_time > config.ALERT_COOLDOWN:
                        alert_placeholder.markdown(
                            '<div class="alert-danger">⚠️ DISTRACTION DETECTED!<br>Please refocus on your studies!</div>',
                            unsafe_allow_html=True
                        )
                        st.session_state.distraction_count += 1
                        st.session_state.last_alert_time = current_time
                    
                    status_placeholder.markdown("""
                    <div style='text-align: center;'>
                        <span class='status-badge status-distracted'>🔴 DISTRACTED</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif face_detected:
                    alert_placeholder.markdown(
                        '<div class="alert-success">✅ Great Focus!<br>Keep up the good work!</div>',
                        unsafe_allow_html=True
                    )
                    
                    status_placeholder.markdown("""
                    <div style='text-align: center;'>
                        <span class='status-badge status-focused'>🟢 FOCUSED</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display camera feed
                if show_camera:
                    camera_placeholder.markdown('<div class="camera-frame">', unsafe_allow_html=True)
                    camera_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)
                else:
                    camera_placeholder.info("📹 Camera monitoring in background...")
                
                # Session stats
                elapsed = int(time.time() - st.session_state.study_start_time)
                focus_score = max(0, 100 - (st.session_state.distraction_count * config.DISTRACTION_PENALTY))
                
                tips_placeholder.markdown(f"""
                ### 📈 Session Stats
                - **Time Elapsed:** {elapsed // 60}m {elapsed % 60}s
                - **Face Detected:** {'✅' if face_detected else '❌'}
                - **Distractions:** {st.session_state.distraction_count}
                - **Focus Score:** {focus_score}%
                """)
        
        cap.release()
        time.sleep(0.1)
        st.rerun()
    
    else:
        camera_placeholder.info("👆 Click **'▶️ Start Session'** to begin monitoring your study session")
        status_placeholder.info("💤 Session not active")

with tab2:
    st.subheader("📊 Study Analytics")
    
    sessions = data_manager.get_all_sessions()
    
    if sessions:
        df = pd.DataFrame(sessions)
        
        # Statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Sessions</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_time = df['duration'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Study Time</div>
                <div class="metric-value">{total_time // 60}m</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_score = df['focus_score'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Focus Score</div>
                <div class="metric-value">{avg_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_distractions = df['distractions'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Distractions</div>
                <div class="metric-value">{total_distractions}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Focus score trend
            fig1 = px.line(df, x='date', y='focus_score', 
                          title='Focus Score Trend',
                          labels={'focus_score': 'Focus Score (%)', 'date': 'Date'})
            fig1.update_traces(line_color='#667eea', line_width=3)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Distraction analysis
            fig2 = px.bar(df, x='date', y='distractions',
                         title='Distraction Count by Session',
                         labels={'distractions': 'Distractions', 'date': 'Date'})
            fig2.update_traces(marker_color='#ff6b6b')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Session table
        st.subheader("📋 Session History")
        display_df = df[['date', 'time', 'duration', 'distractions', 'focus_score']].copy()
        display_df['duration'] = display_df['duration'].apply(lambda x: f"{x // 60}m {x % 60}s")
        display_df['focus_score'] = display_df['focus_score'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.info("📭 No study sessions recorded yet. Start your first session to see analytics!")

with tab3:
    st.subheader("ℹ️ About Distraction Sense AI")
    
    st.markdown("""
    ### 🎯 What is Distraction Sense?
    
    Distraction Sense is an AI-powered study assistant that helps students maintain focus 
    by monitoring their attention in real-time using computer vision technology.
    
    ### 🔍 How It Works
    
    1. **Face Detection**: Uses your webcam to detect if you're looking at your study material
    2. **Distraction Alert**: Notifies you when you look away for too long
    3. **Analytics**: Tracks your focus patterns and provides insights
    4. **Gentle Reminders**: Helps you build better study habits naturally
    
    ### 🛠️ Technology Stack
    
    - **MediaPipe**: Google's ML framework for face detection
    - **OpenCV**: Computer vision processing
    - **Streamlit**: Web application framework
    - **Python**: Core programming language
    
    ### 📊 Focus Score Calculation
    
    ```
    Focus Score = 100 - (Number of Distractions × 5)
    ```
    
    - **90-100**: Excellent Focus 🏆
    - **75-89**: Good Focus 👍
    - **60-74**: Average Focus 😐
    - **Below 60**: Needs Improvement 📉
    
    ### 🚀 Features
    
    - ✅ Real-time face detection
    - ✅ Customizable alert thresholds
    - ✅ Session tracking and analytics
    - ✅ Productivity scoring
    - ✅ Privacy-focused (no data leaves your device)
    
    ### 🔒 Privacy
    
    All processing happens locally on your device. No video or images are stored or transmitted.
    
    ### 📝 Tips for Best Results
    
    - Ensure good lighting in your study area
    - Position yourself clearly in front of the camera
    - Minimize background movement
    - Take regular breaks (25-30 minutes)
    
    ---
    
    **Made with ❤️ for students, by students**
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <b>Pro Tip:</b> Regular breaks improve focus and retention!</p>
    <p style='font-size: 0.9rem;'>Distraction Sense AI © 2026 | Built with Streamlit & MediaPipe</p>
</div>
""", unsafe_allow_html=True)
