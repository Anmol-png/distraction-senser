# Configuration settings for Distraction Sense AI

# Face Detection Settings
FACE_DETECTION_CONFIDENCE = 0.5
MIN_DETECTION_CONFIDENCE = 0.5

# Distraction Settings
DEFAULT_DISTRACTION_THRESHOLD = 10  # seconds
MAX_DISTRACTION_THRESHOLD = 30
MIN_DISTRACTION_THRESHOLD = 5

# Camera Settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Alert Settings
ALERT_SOUND_ENABLED = True
ALERT_COOLDOWN = 5  # seconds between alerts

# Session Settings
AUTO_SAVE_INTERVAL = 60  # Save session data every 60 seconds
MAX_SESSION_DURATION = 7200  # 2 hours max

# Data Storage
DATA_FILE = "data/sessions.json"
BACKUP_ENABLED = True

# UI Settings
APP_TITLE = "Distraction Sense - AI Study Assistant"
APP_ICON = "🎓"
THEME_COLOR = "#1f77b4"

# Productivity Scoring
DISTRACTION_PENALTY = 5  # Each distraction reduces score by 5%
PERFECT_SCORE = 100
MIN_SCORE = 0

# Study Recommendations
BREAK_REMINDER_INTERVAL = 1800  # 30 minutes
HYDRATION_REMINDER_INTERVAL = 3600  # 1 hour
