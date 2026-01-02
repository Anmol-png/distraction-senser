import json
import os
from datetime import datetime
import config

class DataManager:
    def __init__(self, data_file=config.DATA_FILE):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure data file exists with proper structure"""
        if not os.path.exists(os.path.dirname(self.data_file)):
            os.makedirs(os.path.dirname(self.data_file))
        
        if not os.path.exists(self.data_file):
            initial_data = {
                "sessions": [],
                "total_study_time": 0,
                "total_distractions": 0,
                "created_at": datetime.now().isoformat()
            }
            self.save_data(initial_data)
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return {
                "sessions": [],
                "total_study_time": 0,
                "total_distractions": 0
            }
    
    def save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def add_session(self, session_data):
        """Add a new study session"""
        data = self.load_data()
        
        session = {
            "id": len(data["sessions"]) + 1,
            "start_time": session_data.get("start_time"),
            "end_time": session_data.get("end_time"),
            "duration": session_data.get("duration", 0),
            "distractions": session_data.get("distractions", 0),
            "focus_score": session_data.get("focus_score", 100),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S")
        }
        
        data["sessions"].append(session)
        data["total_study_time"] += session["duration"]
        data["total_distractions"] += session["distractions"]
        
        self.save_data(data)
        return session
    
    def get_all_sessions(self):
        """Get all study sessions"""
        data = self.load_data()
        return data.get("sessions", [])
    
    def get_today_sessions(self):
        """Get today's study sessions"""
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = self.get_all_sessions()
        return [s for s in sessions if s.get("date") == today]
    
    def get_statistics(self):
        """Get overall statistics"""
        data = self.load_data()
        sessions = data.get("sessions", [])
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_study_time": 0,
                "total_distractions": 0,
                "avg_session_duration": 0,
                "avg_focus_score": 0
            }
        
        total_sessions = len(sessions)
        total_time = sum(s["duration"] for s in sessions)
        total_distractions = sum(s["distractions"] for s in sessions)
        avg_duration = total_time / total_sessions if total_sessions > 0 else 0
        avg_score = sum(s.get("focus_score", 0) for s in sessions) / total_sessions if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "total_study_time": total_time,
            "total_distractions": total_distractions,
            "avg_session_duration": avg_duration,
            "avg_focus_score": avg_score
        }
    
    def clear_all_data(self):
        """Clear all session data (reset)"""
        initial_data = {
            "sessions": [],
            "total_study_time": 0,
            "total_distractions": 0,
            "reset_at": datetime.now().isoformat()
        }
        return self.save_data(initial_data)
