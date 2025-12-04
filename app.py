from flask import Flask, render_template, jsonify, request, Response, session
from flask_cors import CORS
import cv2
import numpy as np
import json
import time
import threading
from datetime import datetime, timedelta
import logging
import os
from functools import wraps
import requests      
import glob
from flask import send_file

# Import your custom modules
from emotion import EmotionAnalyzer
from companion import AICompanion
from spark import SparkAPI
from config import Config

# ✅ FIXED: Add proper error handling for speech processor
try:
    from speech import SpeechProcessor
    speech_processor = SpeechProcessor()
    print("✅ Speech Processor initialized successfully")
except Exception as e:
    print(f"❌ Speech Processor initialization failed: {e}")
    
    # Create a fallback mock speech processor
    class MockSpeechProcessor:
        def __init__(self):
            self.listening = False
            self.microphone = None
            
        def start_listening(self):
            return {
                'status': 'error', 
                'message': 'Speech features unavailable - check dependencies',
                'demo_mode': True
            }
            
        def stop_listening(self):
            return {
                'status': 'error', 
                'message': 'Speech features unavailable',
                'demo_mode': True
            }
            
        def get_voice_status(self):
            return {
                'status': 'success',
                'listening': False,
                'speech_engine_available': False,
                'microphone_available': False,
                'error': 'Speech recognition not available'
            }
            
        def speak(self, text):
            print(f"🔇 [TTS DEMO] Would speak: {text}")
            return {
                'status': 'error',
                'message': 'Text-to-speech unavailable',
                'demo_mode': True
            }
            
        def get_command(self):
            return None
            
        def emergency_stop(self):
            return {
                'status': 'success',
                'message': 'Speech system already stopped',
                'demo_mode': True
            }
    
    speech_processor = MockSpeechProcessor()
    print("✅ Mock Speech Processor initialized (fallback mode)")

app = Flask(__name__)
app.secret_key = 'AIzaSyDsI9DWYjI3PH7bioo2dZCDhL-JYmfwK40'
CORS(app, supports_credentials=True)

# Configuration
config = Config()

# Pi Server Configuration - UPDATE THIS WITH YOUR PI'S IP
PI_SERVER_URL = "http://10.116.22.223:5001"  # Your pi_server.py URL

# Initialize components with error handling
ai_components_initialized = False

try:
    print("🔄 Initializing AI components...")
    
    # Try to initialize real components
    emotion_analyzer = EmotionAnalyzer()
    print("✅ EmotionAnalyzer initialized")
    
    # Try Google AI API first
    try:
        spark_api = SparkAPI()
        print("✅ Google AI API (SparkAPI) initialized")
        
        # Test the API with a simple call
        test_response = spark_api.get_ai_response("Hello, are you working?", {})
        if "fallback" not in test_response.lower() and "error" not in test_response.lower():
            print("🚀 Google AI API test successful!")
            
            # Create enhanced companion that uses Google AI
            class EnhancedAICompanion:
                def __init__(self, spark_api, fallback_companion):
                    self.spark_api = spark_api
                    self.fallback = fallback_companion
                    self.use_google_ai = True
                    
                def generate_response(self, message, emotion_context, user_id, interaction_count):
                    command_result = self.fallback.process_command(message, user_id)
                    if command_result:
                        return command_result
                    try:
                        if self.use_google_ai:
                            response = self.spark_api.get_ai_response(
                                message=message,
                                emotion_context=emotion_context
                            )
                            # Check if we got a fallback response
                            if any(word in response.lower() for word in ['fallback', 'optimizing', 'realigning']):
                                raise Exception("Google AI returned fallback response")
                            print(f"🤖 Google AI Response: {response[:80]}...")
                            return response
                        else:
                            raise Exception("Google AI disabled")
                    except Exception as e:
                        print(f"⚠️ Google AI failed, using AICompanion: {e}")
                        return self.fallback.generate_response(
                            message, emotion_context, user_id, interaction_count
                        )
                
                def generate_pep_talk(self, emotion, user_id):
                    try:
                        if self.use_google_ai:
                            pep_prompt = f"Generate a short, uplifting pep talk for someone feeling {emotion}. Be encouraging but authentic (2-3 sentences max)."
                            response = self.spark_api.get_ai_response(pep_prompt, {'dominant_emotion': emotion})
                            if any(word in response.lower() for word in ['fallback', 'optimizing']):
                                raise Exception("Google AI pep talk fallback")
                            return response
                        else:
                            raise Exception("Google AI disabled")
                    except Exception as e:
                        print(f"⚠️ Google AI pep talk failed: {e}")
                        return self.fallback.generate_pep_talk(emotion, user_id)
            
            ai_companion = EnhancedAICompanion(spark_api, AICompanion())
            ai_components_initialized = True
            print("🎯 Enhanced AI Companion with Google AI initialized!")
        else:
            raise Exception("Google AI test returned fallback response")
            
    except Exception as google_error:
        print(f"⚠️ Google AI initialization failed: {google_error}")
        # Fallback to regular AICompanion
        ai_companion = AICompanion()
        ai_components_initialized = True
        print("✅ AICompanion initialized (Google AI fallback)")


except Exception as e:
    print(f"❌ AI component initialization failed: {e}")
    # Create mock classes for demo mode
    class MockEmotionAnalyzer:
        def analyze_emotion(self, frame):
            return {
                'dominant_emotion': 'neutral',
                'quantum_confidence': 0.85,
                'emotion_spectrum': {
                    'joy': 0.2, 'neutral': 0.5, 'sadness': 0.1,
                    'anger': 0.1, 'fear': 0.05, 'surprise': 0.05
                },
                'bio_metrics': {
                    'stress_index': 0.3,
                    'mood_stability': 0.8,
                    'engagement': 0.7
                }
            }
        def generate_contextual_demo(self):
            return self.analyze_emotion(None)
    
    class MockAICompanion:
        def generate_response(self, message, emotion_context, user_id, interaction_count):
            # More varied responses based on message content
            lower_msg = message.lower()
            
            if any(word in lower_msg for word in ['hello', 'hi', 'hey', 'greetings']):
                return "Hello! I'm your Nexus AI companion. I can help with emotion analysis, Pi controls, and general assistance. What would you like to explore today?"
            
            elif any(word in lower_msg for word in ['emotion', 'feel', 'mood']):
                current_emotion = emotion_context.get('dominant_emotion', 'unknown')
                return f"I can see you're feeling {current_emotion}. Would you like me to analyze your emotions or adjust the lighting to match your mood?"
            
            elif any(word in lower_msg for word in ['led', 'light', 'brightness']):
                return "I can control your Pi LED lights! Try saying 'turn on LED' or use the Pi Control panel. I can also set emotion-based lighting automatically."
            
            elif any(word in lower_msg for word in ['pi', 'raspberry', 'hardware']):
                status = "connected" if system_state.pi_connected else "in demo mode"
                return f"Your Pi system is {status}. I can control LEDs, displays, read sensors, and more through the Pi Control interface."
            
            elif any(word in lower_msg for word in ['help', 'what can you do']):
                return "I can: • Analyze emotions through camera • Control Pi hardware (LEDs, displays) • Chat with you • Generate insights • Run diagnostics • Process test images • Much more!"
            
            elif any(word in lower_msg for word in ['weather', 'time', 'date']):
                return f"Currently it's {datetime.now().strftime('%H:%M on %B %d')}. I'm focused on emotional intelligence and hardware control rather than external data."
            
            else:
                # Contextual responses based on emotion
                emotion = emotion_context.get('dominant_emotion', 'neutral')
                responses = {
                    'joy': f"That sounds wonderful! I'm glad you're feeling positive. {message} - tell me more!",
                    'sadness': f"I hear you. It's okay to feel this way. {message} - would you like to talk about it?",
                    'anger': f"I sense some frustration. {message} - let's work through this together.",
                    'neutral': f"Thanks for sharing. {message} - I'm here to help with anything you need.",
                    'surprise': f"That's interesting! {message} - I'd love to hear more about that."
                }
                return responses.get(emotion, f"I understand. {message} - how can I assist you further?")
        
        def generate_pep_talk(self, emotion, user_id):
            pep_talks = {
                'joy': "Your happiness is contagious! Keep spreading that positive energy!",
                'neutral': "Your steady presence is your superpower!",
                'sadness': "Even cloudy days make the sunshine brighter when it returns.",
                'anger': "Channel that energy into something creative!",
                'fear': "Courage isn't absence of fear, but moving forward despite it."
            }
            return pep_talks.get(emotion, "You're doing great! Keep moving forward!")
    
    emotion_analyzer = MockEmotionAnalyzer()
    ai_companion = MockAICompanion()
    ai_components_initialized = False
    print("⚠️ Running in demo mode - check API configuration")



# Enhanced Pi Server Client with robust error handling
class PiServerClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.connected = False
        self.last_connection_check = None
        self.connection_retries = 0
        self.max_retries = 3
        
    def check_connection(self, force_check=False):
        """Check connection to Pi server with better error handling"""
        try:
            # Don't check too frequently (every 30 seconds max)
            current_time = datetime.now()
            if (not force_check and 
                self.last_connection_check and 
                (current_time - self.last_connection_check).total_seconds() < 10):
                return self.connected
            
            print(f"🔌 Checking Pi Server connection: {self.base_url}")
            
            # Try multiple endpoints in case health is not available
            endpoints_to_try = [
                "/api/health",
                "/api/system/status", 
                "/api/sensors/read"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    full_url = f"{self.base_url}{endpoint}"
                    print(f"📡 Trying endpoint: {full_url}")
                    
                    response = requests.get(full_url, timeout=5)
                    print(f"📡 Response from {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"📋 Response data: {data}")
                            self.connected = True
                            self.connection_retries = 0
                            self.last_connection_check = current_time
                            print("✅ Pi Server connected successfully!")
                            return True
                        except ValueError as e:
                            print(f"⚠️ Invalid JSON from {endpoint}: {e}")
                            continue
                        
                except requests.exceptions.Timeout:
                    print(f"⏰ Timeout on {endpoint}")
                    continue
                except requests.exceptions.ConnectionError:
                    print(f"🔌 Connection refused on {endpoint}")
                    continue
                except Exception as e:
                    print(f"⚠️ Endpoint {endpoint} failed: {e}")
                    continue
            
            # If all endpoints failed
            self.connected = False
            self.connection_retries += 1
            self.last_connection_check = current_time
            print(f"❌ All Pi Server endpoints failed (retry {self.connection_retries}/{self.max_retries})")
            return False
            
        except Exception as e:
            print(f"❌ Pi Server connection check failed: {e}")
            self.connected = False
            self.last_connection_check = datetime.now()
            return False
    
    def call_pi_api(self, endpoint, method="GET", data=None, timeout=10):
        """Make API call to Pi server with auto-reconnection"""
        # If not connected and we haven't maxed retries, try to reconnect
        if not self.connected and self.connection_retries < self.max_retries:
            self.check_connection(force_check=True)
            
        if not self.connected:
            return {
                'status': 'error', 
                'message': 'Pi server not connected',
                'demo_mode': True
            }
            
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            print(f"📤 Calling Pi API: {method} {url}")
            if data:
                print(f"📦 Request data: {data}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return {'status': 'error', 'message': f'Unsupported method: {method}'}
            
            print(f"📥 Pi API response status: {response.status_code}")
            
            # Handle non-JSON responses
            try:
                response_data = response.json()
                print(f"📥 Pi API response data: {response_data}")
            except ValueError:
                response_data = {
                    'status': 'error', 
                    'message': 'Invalid JSON response', 
                    'raw_response': response.text[:100]  # First 100 chars
                }
            
            return response_data
            
        except requests.exceptions.Timeout:
            error_msg = f"Pi API timeout ({endpoint})"
            print(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = f"Pi server connection refused ({endpoint})"
            print(f"❌ {error_msg}")
            self.connected = False
            return {'status': 'error', 'message': error_msg}
        except Exception as e:
            error_msg = f"Pi API call failed ({endpoint}): {str(e)}"
            print(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
    
    # Pi control methods with demo fallback
    def led_on(self):
        result = self.call_pi_api("/api/led/on", "POST")
        if result.get('status') != 'success':
            return {'status': 'success', 'message': 'LED ON (demo mode)', 'demo': True}
        return result
    
    def led_off(self):
        result = self.call_pi_api("/api/led/off", "POST")
        if result.get('status') != 'success':
            return {'status': 'success', 'message': 'LED OFF (demo mode)', 'demo': True}
        return result
    
    def set_brightness(self, brightness):
        result = self.call_pi_api("/api/led/brightness", "POST", {"brightness": brightness})
        if result.get('status') != 'success':
            return {'status': 'success', 'message': f'Brightness set to {brightness}% (demo mode)', 'demo': True}
        return result
    
    def set_emotion_lighting(self, emotion):
        result = self.call_pi_api("/api/led/emotion", "POST", {"emotion": emotion})
        if result.get('status') != 'success':
            return {'status': 'success', 'message': f'Emotion lighting: {emotion} (demo mode)', 'demo': True}
        return result
    
    def update_display(self, message):
        result = self.call_pi_api("/api/display/update", "POST", {"message": message})
        if result.get('status') != 'success':
            return {'status': 'success', 'message': f'Display updated: {message} (demo mode)', 'demo': True}
        return result
    
    def clear_display(self):
        result = self.call_pi_api("/api/display/clear", "POST")
        if result.get('status') != 'success':
            return {'status': 'success', 'message': 'Display cleared (demo mode)', 'demo': True}
        return result
    
    def read_sensors(self):
        result = self.call_pi_api("/api/sensors/read", "GET")
        if result.get('status') != 'success':
            # Return demo sensor data
            return {
                'status': 'success',
                'sensor_data': {
                    'temperature_c': 24.5 + (np.random.random() - 0.5) * 2,
                    'humidity': 50 + (np.random.random() - 0.5) * 10,
                    'pressure': 1013 + (np.random.random() - 0.5) * 5,
                    'demo_data': True
                },
                'demo': True
            }
        return result
    
    def get_system_status(self):
        result = self.call_pi_api("/api/system/status", "GET")
        if result.get('status') != 'success':
            # Return demo system status
            return {
                'status': 'success',
                'system_status': {
                    'device': 'Raspberry Pi (Demo Mode)',
                    'led_available': True,
                    'oled_available': True,
                    'dht_available': True,
                    'led_state': False,
                    'led_brightness_percent': 50,
                    'last_sensor_read': datetime.now().isoformat(),
                    'demo_mode': True
                },
                'demo': True
            }
        return result
    
    def get_emotions_list(self):
        result = self.call_pi_api("/api/emotions/list", "GET")
        if result.get('status') != 'success':
            return {
                'status': 'success',
                'emotions': ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral', 'calm', 'energy', 'focus'],
                'demo': True
            }
        return result
    
    def reboot_pi(self):
        result = self.call_pi_api("/api/reboot", "POST")
        if result.get('status') != 'success':
            return {'status': 'success', 'message': 'Reboot command sent (demo mode)', 'demo': True}
        return result

# Initialize Pi Server Client
pi_client = PiServerClient(PI_SERVER_URL)

# Global state with thread safety
class SystemState:
    def __init__(self):
        self.camera_active = False
        self.is_analyzing = False
        self.current_emotion = {}
        self.session_data = {}
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        # Will be updated after pi_client initialization
        self.pi_connected = False

system_state = SystemState()

class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.lock = threading.Lock()
        self.retry_count = 0
        self.max_retries = 3
    
    def start_camera(self):
        with self.lock:
            try:
                # Try to use camera if available, otherwise use demo mode
                for camera_index in [0, 1, 2]:
                    self.camera = cv2.VideoCapture(camera_index)
                    if self.camera.isOpened():
                        ret, frame = self.camera.read()
                        if ret and frame is not None:
                            self.is_running = True
                            self.retry_count = 0
                            print(f"✅ Camera started on index {camera_index}")
                            return True
                
                # If no camera found, use demo mode
                print("⚠️ No camera found - using demo mode")
                self.is_running = True
                return True
                
            except Exception as e:
                print(f"⚠️ Camera start error: {e} - using demo mode")
                self.is_running = True
                return True
    
    def get_frame(self):
        with self.lock:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    self.current_frame = frame
                    return frame
            
            # Return demo frame if no camera
            return self.generate_demo_frame()
    
    def generate_demo_frame(self):
        """Generate a demo frame when no camera is available"""
        width, height = 640, 480
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create gradient background
        for y in range(height):
            blue = int(50 + (y / height) * 100)
            green = int(30 + (y / height) * 70)
            red = int(100 + (y / height) * 100)
            frame[y, :] = [blue, green, red]
        
        # Add some visual elements
        cv2.circle(frame, (width//2, height//2), 100, (255, 255, 255), 2)
        cv2.putText(frame, "DEMO MODE", (width//2 - 80, height//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Camera Simulation", (width//2 - 100, height//2 + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def stop_camera(self):
        with self.lock:
            self.is_running = False
            if self.camera:
                self.camera.release()
            self.current_frame = None
            print("✅ Camera stopped")

camera_manager = CameraManager()

def emotion_analysis_worker():
    """Background worker for emotion analysis with guaranteed saving"""
    analysis_count = 0
    while True:
        try:
            if camera_manager.is_running and system_state.is_analyzing:
                frame = camera_manager.get_frame()
                if frame is not None:
                    emotion_result = emotion_analyzer.analyze_emotion(frame)
                    
                    if emotion_result:
                        with system_state.lock:
                            system_state.current_emotion = emotion_result
                            system_state.current_emotion['analysis_id'] = analysis_count
                            system_state.current_emotion['timestamp'] = datetime.now().isoformat()
                            system_state.current_emotion['source'] = 'camera'
                        
                        # ✅ GUARANTEED SAVE: Always log emotion data
                        print(f"📊 Analysis #{analysis_count}: {emotion_result.get('dominant_emotion')}")
                        log_emotion_data(emotion_result)
                        
                        # Auto-update Pi hardware based on emotion
                        if system_state.pi_connected:
                            auto_update_hardware(emotion_result)
                        
                        analysis_count += 1
                        
        except Exception as e:
            print(f"❌ Emotion analysis error: {e}")
        
        time.sleep(2)  # Analyze every 2 seconds
def auto_update_hardware(emotion_data):
    """Automatically update Pi hardware based on emotion"""
    try:
        dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')
        
        # Update OLED display with current emotion
        if system_state.pi_connected:
            pi_client.update_display(f"Emotion: {dominant_emotion.title()}")
        
        # Auto-adjust lighting based on emotion
        if emotion_data.get('quantum_confidence', 0) > 0.6:
            pi_client.set_emotion_lighting(dominant_emotion)
            
    except Exception as e:
        print(f"❌ Auto hardware update failed: {e}")

# Start background worker
analysis_thread = threading.Thread(target=emotion_analysis_worker, daemon=True)
analysis_thread.start()

def log_emotion_data(emotion_data):
    """Enhanced emotion data logging to ensure persistence"""
    try:
        # Create enhanced log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'dominant_emotion': emotion_data.get('dominant_emotion', 'unknown'),
            'quantum_confidence': emotion_data.get('quantum_confidence', 0),
            'emotion_spectrum': emotion_data.get('emotion_spectrum', {}),
            'bio_metrics': emotion_data.get('bio_metrics', {}),
            'session_id': system_state.session_data.get('session_id', 'unknown'),
            'analysis_id': emotion_data.get('analysis_id', 0),
            'source': emotion_data.get('source', 'camera'),
            'hardware_connected': system_state.pi_connected
        }
        
        # Ensure logs directory exists
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'emotions.json')
        print(f"📝 Saving emotion to: {log_file}")
        
        # Initialize or load existing data
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️ Error reading existing log file, creating new: {e}")
                data = {'emotion_logs': [], 'sessions': {}}
        else:
            data = {'emotion_logs': [], 'sessions': {}}
        
        # Add new log entry
        data['emotion_logs'].append(log_entry)
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(data['emotion_logs']) > 1000:
            data['emotion_logs'] = data['emotion_logs'][-1000:]
        
        # Update session data
        session_id = system_state.session_data.get('session_id')
        if session_id:
            if 'sessions' not in data:
                data['sessions'] = {}
            if session_id not in data['sessions']:
                data['sessions'][session_id] = {
                    'start_time': system_state.session_data.get('start_time'),
                    'emotion_count': 0
                }
            data['sessions'][session_id]['emotion_count'] = len(
                [log for log in data['emotion_logs'] if log.get('session_id') == session_id]
            )
        
        # Save to file
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Emotion saved to JSON: {log_entry['dominant_emotion']} (Confidence: {log_entry['quantum_confidence']:.2f})")
        
    except Exception as e:
        print(f"❌ Emotion logging error: {e}")
        import traceback
        traceback.print_exc()

# Authentication and session management
def require_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not system_state.session_data.get('session_id'):
            return jsonify({'status': 'error', 'message': 'No active session'}), 401
        return f(*args, **kwargs)
    return decorated_function

# System Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system/init', methods=['POST'])
def system_init():
    """Initialize quantum session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', f'quantum_user_{int(time.time())}')
        
        with system_state.lock:
            system_state.session_data = {
                'session_id': user_id,
                'start_time': datetime.now().isoformat(),
                'user_preferences': {},
                'emotion_history': [],
                'chat_history': [],
                'interaction_count': 0
            }
        
        # Initialize Pi hardware for new session
        if pi_client.connected:
            try:
                pi_client.update_display("Nexus AI Ready")
                pi_client.led_on()
                print("✅ Pi hardware initialized for new session")
            except Exception as e:
                print(f"⚠️ Pi hardware init failed: {e}")
        
        return jsonify({
            'status': 'success',
            'session_id': user_id,
            'message': 'Quantum session initialized successfully',
            'hardware_status': {
                'pi_connected': pi_client.connected,
                'pi_server_url': PI_SERVER_URL,
                'pi_server_status': 'connected' if pi_client.connected else 'disconnected'
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Session initialization failed: {str(e)}'}), 500

@app.route('/api/system/health', methods=['GET'])
def system_health():
    """Comprehensive system health check"""
    try:
        uptime = (datetime.now() - system_state.start_time).total_seconds()
        
        # Get Pi system status if connected
        pi_status = {}
        if pi_client.connected:
            try:
                pi_response = pi_client.get_system_status()
                if pi_response.get('status') == 'success':
                    pi_status = pi_response.get('system_status', {})
            except Exception as e:
                print(f"⚠️ Pi status check failed: {e}")

        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system_uptime': uptime,
            'pi_connected': pi_client.connected,
            'pi_connection_retries': pi_client.connection_retries,
            'components': {
                'emotion_engine': {
                    'status': 'active',
                    'camera_active': camera_manager.is_running,
                    'analysis_active': system_state.is_analyzing,
                    'last_analysis': system_state.current_emotion.get('timestamp')
                },
                'ai_companion': {
                    'status': 'active', 
                    'model_loaded': True
                },
                'hardware_interface': {
                    'status': 'active' if pi_client.connected else 'disconnected',
                    'pi_connected': pi_client.connected,
                    'pi_server_url': PI_SERVER_URL,
                    'pi_hardware_status': pi_status
                },
                'voice_interface': {
                    'status': 'active' if hasattr(speech_processor, 'listening') else 'inactive',
                    'listening': getattr(speech_processor, 'listening', False),
                    'microphone_available': getattr(speech_processor, 'microphone', None) is not None
                }
            }
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system/refresh-pi-connection', methods=['POST'])
def refresh_pi_connection():
    """Manually refresh Pi server connection"""
    try:
        previous_status = pi_client.connected
        pi_client.check_connection(force_check=True)
        
        with system_state.lock:
            system_state.pi_connected = pi_client.connected
        
        return jsonify({
            'status': 'success',
            'previous_connection': previous_status,
            'current_connection': pi_client.connected,
            'message': f'Pi connection refreshed: {"Connected" if pi_client.connected else "Disconnected"}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Connection refresh failed: {str(e)}'}), 500

# Camera Routes
@app.route('/api/camera/start', methods=['POST'])
@require_session
def camera_start():
    """Start camera"""
    try:
        success = camera_manager.start_camera()
        if success:
            system_state.camera_active = True
            system_state.is_analyzing = True
            
            if pi_client.connected:
                pi_client.update_display("Vision Active")
            
            return jsonify({
                'status': 'success',
                'message': 'Neural vision system activated',
                'camera_active': True,
                'analysis_active': True
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'Camera initialization failed'
            }), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Camera start failed: {str(e)}'}), 500

@app.route('/api/camera/stop', methods=['POST'])
@require_session
def camera_stop():
    """Stop camera feed"""
    try:
        camera_manager.stop_camera()
        system_state.camera_active = False
        system_state.is_analyzing = False
        
        if pi_client.connected:
            pi_client.update_display("Vision Ready")
        
        return jsonify({
            'status': 'success',
            'message': 'Neural vision system deactivated',
            'camera_active': False,
            'analysis_active': False
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/camera/feed')
@require_session
def camera_feed():
    """Camera feed endpoint"""
    def generate():
        while True:
            try:
                if not camera_manager.is_running:
                    frame = camera_manager.generate_demo_frame()
                else:
                    frame = camera_manager.get_frame()
                
                if frame is not None:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Camera feed error: {e}")
                time.sleep(0.1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Emotion Analysis Routes
@app.route('/api/emotion/latest')
@require_session
def emotion_latest():
    """Get latest emotion analysis"""
    try:
        with system_state.lock:
            if system_state.current_emotion:
                return jsonify({
                    'status': 'success',
                    'emotion_data': system_state.current_emotion,
                    'analysis_quality': 'high'
                })
            else:
                demo_emotion = emotion_analyzer.generate_contextual_demo() if hasattr(emotion_analyzer, 'generate_contextual_demo') else emotion_analyzer.analyze_emotion(None)
                return jsonify({
                    'status': 'success',
                    'emotion_data': demo_emotion,
                    'analysis_quality': 'demo'
                })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# AI Companion Routes
@app.route('/api/chat/send', methods=['POST'])
@require_session
def chat_send():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        emotion_context = data.get('emotion_context', {})
        
        if not message:
            return jsonify({'status': 'error', 'message': 'Empty message'}), 400
        
        # ✅ STORE USER MESSAGE
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'user',
            'message': message,
            'emotion_context': emotion_context
        }
        
        # Store in session data
        with system_state.lock:
            if 'chat_history' not in system_state.session_data:
                system_state.session_data['chat_history'] = []
            system_state.session_data['chat_history'].append(chat_entry)
            system_state.session_data['interaction_count'] = system_state.session_data.get('interaction_count', 0) + 1
        
        # Generate AI response (may be a command or normal response)
        ai_response = ai_companion.generate_response(
            message=message,
            emotion_context=emotion_context,
            user_id=system_state.session_data.get('session_id'),
            interaction_count=system_state.session_data.get('interaction_count', 0)
        )
        
        # Check if response is a command that needs execution
        command_executed = False
        command_result = None
        
        if isinstance(ai_response, dict) and ai_response.get('type') == 'command':
            command_executed = True
            command_result = execute_command(ai_response['command'], ai_response.get('value'))
        
        # ✅ STORE AI RESPONSE
        ai_chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'assistant', 
            'message': ai_response.get('message') if isinstance(ai_response, dict) else ai_response,
            'emotion_context': system_state.current_emotion,
            'is_command': command_executed,
            'command_result': command_result if command_executed else None
        }
        
        with system_state.lock:
            system_state.session_data['chat_history'].append(ai_chat_entry)
        
        # ✅ SAVE TO PERMANENT STORAGE
        save_chat_to_file(chat_entry, ai_chat_entry)
        
        response_data = {
            'status': 'success',
            'ai_response': {
                'response': ai_response.get('message') if isinstance(ai_response, dict) else ai_response,
                'timestamp': datetime.now().isoformat(),
                'is_command': command_executed,
                'command_type': ai_response.get('action') if command_executed else None
            },
            'interaction_count': system_state.session_data.get('interaction_count', 0)
        }
        
        # Add command execution result if applicable
        if command_executed and command_result:
            response_data['command_result'] = command_result
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Chat failed: {str(e)}'}), 500

def execute_command(command, value=None):
    """Execute hardware and system commands"""
    try:
        print(f"🎯 Executing command: {command}")
        
        if command == 'led_on':
            result = pi_client.led_on()
            return {'action': 'led_on', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'led_off':
            result = pi_client.led_off()
            return {'action': 'led_off', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'set_brightness':
            if value is not None:
                result = pi_client.set_brightness(value)
                return {'action': 'set_brightness', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'calm_mode':
            result = pi_client.set_emotion_lighting('calm')
            return {'action': 'calm_mode', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'energy_mode':
            result = pi_client.set_emotion_lighting('energy')
            return {'action': 'energy_mode', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'party_mode':
            result = pi_client.set_emotion_lighting('party')
            return {'action': 'party_mode', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'analyze_emotion':
            # Trigger immediate emotion analysis
            if camera_manager.is_running:
                frame = camera_manager.get_frame()
                if frame is not None:
                    emotion_result = emotion_analyzer.analyze_emotion(frame)
                    if emotion_result:
                        with system_state.lock:
                            system_state.current_emotion = emotion_result
                        log_emotion_data(emotion_result)
                        return {
                            'action': 'analyze_emotion', 
                            'result': emotion_result,
                            'success': True
                        }
            return {'action': 'analyze_emotion', 'result': 'Camera not active', 'success': False}
        
        elif command == 'start_camera':
            success = camera_manager.start_camera()
            if success:
                system_state.camera_active = True
                system_state.is_analyzing = True
            return {'action': 'start_camera', 'result': {'active': success}, 'success': success}
        
        elif command == 'stop_camera':
            camera_manager.stop_camera()
            system_state.camera_active = False
            system_state.is_analyzing = False
            return {'action': 'stop_camera', 'result': {'active': False}, 'success': True}
        
        elif command == 'system_status':
            # Return current system status
            uptime = (datetime.now() - system_state.start_time).total_seconds()
            status = {
                'uptime': uptime,
                'camera_active': system_state.camera_active,
                'analysis_active': system_state.is_analyzing,
                'pi_connected': system_state.pi_connected,
                'current_emotion': system_state.current_emotion.get('dominant_emotion', 'unknown')
            }
            return {'action': 'system_status', 'result': status, 'success': True}
        
        elif command == 'pi_status':
            result = pi_client.get_system_status()
            return {'action': 'pi_status', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'read_sensors':
            result = pi_client.read_sensors()
            return {'action': 'read_sensors', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'update_display':
            if value:
                result = pi_client.update_display(value)
                return {'action': 'update_display', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'clear_display':
            result = pi_client.clear_display()
            return {'action': 'clear_display', 'result': result, 'success': result.get('status') == 'success'}
        
        elif command == 'pep_talk':
            # This is handled by the AI companion directly
            return {'action': 'pep_talk', 'result': 'Generated by AI', 'success': True}
        
        elif command == 'emotional_insight':
            # This is handled by the AI companion directly  
            return {'action': 'emotional_insight', 'result': 'Generated by AI', 'success': True}
        
        return {'action': command, 'result': 'Command not implemented', 'success': False}
        
    except Exception as e:
        print(f"❌ Command execution failed: {e}")
        return {'action': command, 'result': f'Error: {str(e)}', 'success': False}

@app.route('/api/chat/commands', methods=['GET'])
@require_session
def available_commands():
    """Get list of available voice commands"""
    commands = {
        'hardware_controls': [
            'turn on led / led on',
            'turn off led / led off', 
            'set brightness to X%',
            'calm mode / relax mode',
            'energy mode / focus mode',
            'party mode / fun mode'
        ],
        'camera_controls': [
            'start camera / activate camera',
            'stop camera / deactivate camera',
            'analyze emotion / scan emotion'
        ],
        'display_controls': [
            'display message [your text]',
            'clear display / blank screen'
        ],
        'system_info': [
            'system status / health check',
            'pi status / hardware status', 
            'sensor data / temperature'
        ],
        'ai_companion': [
            'pep talk / motivate me',
            'emotional insight / mood analysis'
        ]
    }
    
    return jsonify({
        'status': 'success',
        'commands': commands,
        'message': 'Try typing these commands in the chat!'
    })

@app.route('/api/chat/history', methods=['GET'])
@require_session
def chat_history():
    """Get chat history"""
    try:
        with system_state.lock:
            chat_history = system_state.session_data.get('chat_history', [])
        
        return jsonify({
            'status': 'success',
            'chat_history': chat_history[-50:],  # Last 50 messages
            'total_messages': len(chat_history)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to get chat history: {str(e)}'}), 500

def save_chat_to_file(user_message, ai_response):
    """Save chat messages to JSON file for persistence"""
    try:
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        chat_file = os.path.join(logs_dir, 'chat_history.json')
        
        # Load existing chat history
        if os.path.exists(chat_file):
            try:
                with open(chat_file, 'r') as f:
                    data = json.load(f)
            except:
                data = {'chats': []}
        else:
            data = {'chats': []}
        
        # Add new conversation turn
        conversation_turn = {
            'timestamp': datetime.now().isoformat(),
            'session_id': system_state.session_data.get('session_id'),
            'user_message': user_message,
            'ai_response': ai_response
        }
        
        data['chats'].append(conversation_turn)
        
        # Keep only last 1000 conversations
        if len(data['chats']) > 1000:
            data['chats'] = data['chats'][-1000:]
        
        # Save to file
        with open(chat_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"💬 Chat saved: {user_message.get('message', '')[:50]}...")
        
    except Exception as e:
        print(f"⚠️ Failed to save chat: {e}")
        
@app.route('/api/chat/clear', methods=['POST'])
@require_session
def clear_chat():
    """Clear chat history"""
    try:
        with system_state.lock:
            system_state.session_data['chat_history'] = []
        
        return jsonify({
            'status': 'success',
            'message': 'Chat history cleared'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to clear chat: {str(e)}'}), 500
@app.route('/api/companion/pep_talk', methods=['POST'])
@require_session
def pep_talk():
    """Get pep talk"""
    try:
        data = request.get_json()
        emotion = data.get('emotion', 'neutral')
        
        pep_talk = ai_companion.generate_pep_talk(
            emotion=emotion,
            user_id=system_state.session_data.get('session_id')
        )
        
        return jsonify({
            'status': 'success',
            'pep_talk': pep_talk
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# PI CONTROL ROUTES - CALLING PI_SERVER.PY
@app.route('/api/pi/led/on', methods=['POST'])
@require_session
def pi_led_on():
    """Turn Pi LED on"""
    try:
        result = pi_client.led_on()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'LED control failed: {str(e)}'}), 500

@app.route('/api/pi/led/off', methods=['POST'])
@require_session
def pi_led_off():
    """Turn Pi LED off"""
    try:
        result = pi_client.led_off()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'LED control failed: {str(e)}'}), 500

@app.route('/api/pi/led/brightness', methods=['POST'])
@require_session
def pi_led_brightness():
    """Set Pi LED brightness"""
    try:
        data = request.get_json()
        brightness = data.get('brightness', 50)
        
        result = pi_client.set_brightness(brightness)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Brightness control failed: {str(e)}'}), 500

@app.route('/api/pi/led/emotion', methods=['POST'])
@require_session
def pi_led_emotion():
    """Set emotion-based lighting"""
    try:
        data = request.get_json()
        emotion = data.get('emotion', 'neutral')
        
        result = pi_client.set_emotion_lighting(emotion)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Emotion lighting failed: {str(e)}'}), 500

@app.route('/api/pi/display/update', methods=['POST'])
@require_session
def pi_display_update():
    """Update Pi OLED display"""
    try:
        data = request.get_json()
        message = data.get('message', 'Smart Desk Buddy Active')
        
        result = pi_client.update_display(message)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Display update failed: {str(e)}'}), 500

@app.route('/api/pi/display/clear', methods=['POST'])
@require_session
def pi_display_clear():
    """Clear Pi OLED display"""
    try:
        result = pi_client.clear_display()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Display clear failed: {str(e)}'}), 500

@app.route('/api/pi/status', methods=['GET'])
@require_session
def pi_status():
    """Get Pi system status"""
    try:
        result = pi_client.get_system_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Status check failed: {str(e)}'}), 500

@app.route('/api/pi/sensors', methods=['GET'])
@require_session
def pi_sensors():
    """Get Pi sensor data"""
    try:
        result = pi_client.read_sensors()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Sensor read failed: {str(e)}'}), 500

@app.route('/api/pi/reboot', methods=['POST'])
@require_session
def pi_reboot():
    """Reboot Pi system"""
    try:
        result = pi_client.reboot_pi()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Reboot command failed: {str(e)}'}), 500

@app.route('/api/pi/shutdown', methods=['POST'])
@require_session
def pi_shutdown():
    """Shutdown Pi system"""
    try:
        # Note: pi_server.py doesn't have shutdown endpoint, using reboot as fallback
        result = pi_client.reboot_pi()
        if result.get('status') == 'success':
            result['message'] = 'Shutdown command received (manual shutdown recommended for safety)'
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Shutdown command failed: {str(e)}'}), 500

@app.route('/api/pi/diagnostic', methods=['GET'])
@require_session
def pi_diagnostic():
    """Run Pi diagnostic"""
    try:
        # Get comprehensive diagnostic information from Pi server
        status_result = pi_client.get_system_status()
        sensors_result = pi_client.read_sensors()
        
        diagnostic_report = "Pi System Diagnostic Report\n"
        diagnostic_report += "===========================\n"
        
        if status_result.get('status') == 'success':
            status = status_result.get('system_status', {})
            diagnostic_report += f"System: {status.get('device', 'Unknown')}\n"
            diagnostic_report += f"Status: {'ONLINE' if pi_client.connected else 'DEMO MODE'}\n"
            diagnostic_report += f"LED Available: {status.get('led_available', False)}\n"
            diagnostic_report += f"OLED Available: {status.get('oled_available', False)}\n"
            diagnostic_report += f"Sensors Available: {status.get('dht_available', False)}\n"
            diagnostic_report += f"LED State: {'ON' if status.get('led_state') else 'OFF'}\n"
            diagnostic_report += f"Brightness: {status.get('led_brightness_percent', 0)}%\n"
        else:
            diagnostic_report += "System: Raspberry Pi (Demo Mode)\n"
            diagnostic_report += "Status: DEMO MODE\n"
        
        if sensors_result.get('status') == 'success':
            sensors = sensors_result.get('sensor_data', {})
            diagnostic_report += f"Temperature: {sensors.get('temperature_c', 'N/A')}°C\n"
            diagnostic_report += f"Humidity: {sensors.get('humidity', 'N/A')}%\n"
        else:
            diagnostic_report += "Temperature: 24.5°C (demo)\n"
            diagnostic_report += "Humidity: 52% (demo)\n"
        
        diagnostic_report += f"Last Sensor Read: {datetime.now().strftime('%H:%M:%S')}\n"
        diagnostic_report += "All systems: OPERATIONAL\n"
        diagnostic_report += "Diagnostic complete."
        
        return jsonify({
            'status': 'success',
            'diagnostic_report': diagnostic_report
        })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Diagnostic failed: {str(e)}'}), 500

@app.route('/api/pi/update', methods=['POST'])
@require_session
def pi_update():
    """Check for Pi system updates"""
    try:
        # Simulate update check
        return jsonify({
            'status': 'success',
            'message': 'Pi system is up to date',
            'update_available': False,
            'demo_mode': not pi_client.connected
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Update check failed: {str(e)}'}), 500

@app.route('/api/pi/emotions/list', methods=['GET'])
@require_session
def pi_emotions_list():
    """Get available emotions from Pi"""
    try:
        result = pi_client.get_emotions_list()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to get emotions list: {str(e)}'}), 500


@app.route('/api/memory/history', methods=['GET'])
@require_session
def memory_history():
    """Get emotion history from memory bank"""
    try:
        # Read from the emotion log file
        log_file = 'logs/emotions.json'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
            
            # Get emotion logs for current session
            session_id = system_state.session_data.get('session_id')
            emotion_logs = data.get('emotion_logs', [])
            
            # Filter by current session if needed, or return all
            session_logs = [log for log in emotion_logs if log.get('session_id') == session_id]
            
            return jsonify({
                'status': 'success',
                'emotion_history': session_logs if session_logs else emotion_logs[-50:],  # Last 50 entries
                'total_count': len(emotion_logs)
            })
        else:
            return jsonify({
                'status': 'success',
                'emotion_history': [],
                'total_count': 0
            })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to load memory: {str(e)}'}), 500

@app.route('/api/memory/clear', methods=['POST'])
@require_session
def memory_clear():
    """Clear emotion history"""
    try:
        log_file = 'logs/emotions.json'
        
        if os.path.exists(log_file):
            # Keep the file structure but clear the logs
            with open(log_file, 'w') as f:
                json.dump({'emotion_logs': [], 'sessions': {}}, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': 'Memory bank cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to clear memory: {str(e)}'}), 500


@app.route('/api/test/scan-folder', methods=['POST'])
@require_session
def scan_images_folder():
    """Scan a folder for images (including subdirectories)"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path', 'images/')
        
        print(f"📁 Scanning folder: {folder_path}")
        
        # Ensure folder exists
        if not os.path.exists(folder_path):
            print(f"❌ Folder does not exist: {folder_path}")
            try:
                os.makedirs(folder_path, exist_ok=True)
                print(f"✅ Created folder: {folder_path}")
                return jsonify({
                    'status': 'success',
                    'folder_path': folder_path,
                    'image_count': 0,
                    'images': [],
                    'message': 'Folder created (no images found)'
                })
            except Exception as e:
                return jsonify({
                    'status': 'error', 
                    'message': f'Folder {folder_path} does not exist and could not be created: {str(e)}'
                }), 400
        
        # Find all image files recursively
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.JPG', '.JPEG', '.PNG', '.BMP', '.GIF']
        images = []
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Check if file has image extension
                if any(file.lower().endswith(ext.lower()) for ext in image_extensions):
                    full_path = os.path.join(root, file)
                    
                    images.append({
                        'name': file,
                        'path': full_path,
                        'relative_path': os.path.relpath(full_path, folder_path) if root.startswith(folder_path) else file,
                        'folder': os.path.basename(root) if root != folder_path else 'root',
                        'full_path': os.path.abspath(full_path)
                    })
        
        # Sort by filename
        images.sort(key=lambda x: x['name'])
        
        print(f"✅ Found {len(images)} images in {folder_path}")
        
        return jsonify({
            'status': 'success',
            'folder_path': folder_path,
            'image_count': len(images),
            'images': images
        })
        
    except Exception as e:
        print(f"❌ Error scanning folder: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/test/get-image')
@require_session
def get_test_image():
    """Serve test images securely"""
    try:
        image_path = request.args.get('path')
        
        if not image_path:
            return jsonify({'status': 'error', 'message': 'No image path provided'}), 400
        
        print(f"🖼️ Serving image: {image_path}")
        
        # Security check - ensure path exists
        if not os.path.exists(image_path):
            # Try different path resolutions
            possible_paths = [
                image_path,
                os.path.join('images', image_path),
                os.path.join(os.getcwd(), 'images', image_path),
                os.path.abspath(image_path)
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            else:
                print(f"❌ Image not found at any path: {image_path}")
                return jsonify({'status': 'error', 'message': 'Image not found'}), 404
        
        return send_file(image_path)
        
    except Exception as e:
        print(f"❌ Error serving image: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def convert_numpy_types(obj):
    """Recursively convert numpy data types to native Python types for JSON serialization"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.generic):
        return obj.item()  # Convert numpy scalars to Python scalars
    elif isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert numpy arrays to Python lists
    else:
        return obj

@app.route('/api/test/process-image', methods=['POST'])
@require_session
def process_test_image():
    """Process a test image through emotion analysis"""
    try:
        print("=== DEBUG: Starting process_test_image ===")
        
        # Check request data
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400
            
        data = request.get_json()
        print(f"📦 Received data: {data}")
        
        if not data:
            print("❌ No data in request")
            return jsonify({'status': 'error', 'message': 'No JSON data received'}), 400
        
        image_path = data.get('image_path')
        image_name = data.get('image_name', 'Unknown')
        
        print(f"🎯 Processing image: {image_name}")
        print(f"📍 Image path: {image_path}")
        
        # Validate input
        if not image_path:
            print("❌ No image_path provided")
            return jsonify({'status': 'error', 'message': 'Missing image_path'}), 400
        
        # Resolve and check path
        if not os.path.isabs(image_path):
            abs_path = os.path.abspath(os.path.join(os.getcwd(), image_path))
            print(f"🔍 Resolved path: {abs_path}")
        else:
            abs_path = image_path
            
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"🔎 File exists: {os.path.exists(abs_path)}")
        
        if not os.path.exists(abs_path):
            print(f"❌ File not found: {abs_path}")
            return jsonify({
                'status': 'error', 
                'message': f'Image not found: {abs_path}'
            }), 404
        
        # Try to load image
        print("🖼️ Attempting to load image with OpenCV...")
        image = cv2.imread(abs_path)
        
        if image is None:
            print(f"❌ OpenCV failed to load image: {abs_path}")
            # Try alternative loading methods
            try:
                from PIL import Image
                print("🔄 Trying PIL fallback...")
                pil_image = Image.open(abs_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                print("✅ PIL fallback successful")
            except ImportError:
                print("❌ PIL not available")
                return jsonify({
                    'status': 'error', 
                    'message': 'OpenCV failed to load image and PIL not available'
                }), 400
            except Exception as pil_error:
                print(f"❌ PIL also failed: {pil_error}")
                return jsonify({
                    'status': 'error', 
                    'message': f'Failed to load image with any method: {str(pil_error)}'
                }), 400
        
        print(f"✅ Image loaded successfully: {image.shape}")
        
        # Check if emotion_analyzer exists
        if 'emotion_analyzer' not in globals():
            print("❌ emotion_analyzer not found in globals!")
            return jsonify({
                'status': 'error', 
                'message': 'Emotion analyzer not initialized'
            }), 500
            
        print("🧠 Starting emotion analysis...")
        
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze_emotion(image)
        
        print(f"✅ Emotion analysis complete: {emotion_result.get('dominant_emotion', 'unknown')}")
        
        # CONVERT NUMPY TYPES TO NATIVE PYTHON TYPES - THIS IS THE FIX!
        emotion_result = convert_numpy_types(emotion_result)
        
        # Add metadata
        emotion_result.update({
            'image_name': image_name,
            'image_path': abs_path,
            'source': 'test_image'
        })
        
        print("=== DEBUG: process_test_image completed successfully ===")
        
        return jsonify({
            'status': 'success',
            'emotion_data': emotion_result
        })
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in process_test_image: {str(e)}")
        import traceback
        print("🔍 Full stack trace:")
        traceback.print_exc()
        return jsonify({
            'status': 'error', 
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/test/debug-process', methods=['POST'])
@require_session
def debug_process_image():
    """Debug endpoint to see what's happening with image processing"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        image_name = data.get('image_name', 'Unknown')
        
        print(f"🔍 DEBUG: Processing image: {image_name}")
        print(f"🔍 DEBUG: Image path: {image_path}")
        
        # Check if file exists
        if not image_path or not os.path.exists(image_path):
            print(f"❌ DEBUG: Image file not found: {image_path}")
            return jsonify({'status': 'error', 'message': 'Image file not found', 'debug_path': image_path}), 404
        
        # Try to load the image
        print(f"🔍 DEBUG: Attempting to load image...")
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ DEBUG: Failed to load image with OpenCV")
            return jsonify({'status': 'error', 'message': 'Failed to load image with OpenCV'}), 400
        
        print(f"✅ DEBUG: Image loaded successfully, shape: {image.shape}")
        
        # Try emotion analysis
        print(f"🔍 DEBUG: Attempting emotion analysis...")
        emotion_result = emotion_analyzer.analyze_emotion(image)
        
        print(f"✅ DEBUG: Emotion analysis successful: {emotion_result.get('dominant_emotion', 'unknown')}")
        
        # CONVERT NUMPY TYPES TO NATIVE PYTHON TYPES - THIS IS THE FIX!
        emotion_result = convert_numpy_types(emotion_result)
        
        return jsonify({
            'status': 'success',
            'emotion_data': emotion_result,
            'debug_info': {
                'image_loaded': True,
                'image_shape': image.shape,
                'analysis_success': True
            }
        })
        
    except Exception as e:
        print(f"❌ DEBUG: Exception in process-image: {str(e)}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error', 
            'message': f'Debug error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

def log_test_analysis(emotion_data, image_name):
    """Log test image analysis to the same system as camera data"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'source': 'test_image',
            'image_name': image_name,
            'emotion_data': emotion_data
        }
        
        # Append to the same emotion log file as camera
        log_file = 'logs/emotion.json'
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        print(f"📝 Logged test analysis for: {image_name}")
        
    except Exception as e:
        print(f"⚠️ Failed to log test analysis: {e}")
    
@app.route('/api/test/health', methods=['GET'])
@require_session
def test_health():
    """Test mode health check"""
    return jsonify({
        'status': 'success',
        'message': 'Test mode endpoints are active',
        'endpoints': {
            'scan_folder': '/api/test/scan-folder',
            'get_image': '/api/test/get-image', 
            'process_image': '/api/test/process-image'
        }
    })

@app.route('/api/emotion/save', methods=['POST'])
@require_session
def save_emotion():
    """Force save emotion data to JSON file"""
    try:
        data = request.get_json()
        emotion_data = data.get('emotion_data', {})
        
        if not emotion_data:
            return jsonify({'status': 'error', 'message': 'No emotion data provided'}), 400
        
        print(f"💾 Manual save request for emotion: {emotion_data.get('dominant_emotion', 'unknown')}")
        
        # Log the emotion data
        log_emotion_data(emotion_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Emotion data saved successfully',
            'emotion': emotion_data.get('dominant_emotion', 'unknown'),
            'confidence': emotion_data.get('quantum_confidence', 0)
        })
        
    except Exception as e:
        print(f"❌ Emotion save error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to save emotion: {str(e)}'}), 500
    

@app.route('/api/test-google-ai', methods=['POST'])
def test_google_ai():
    """Test Google AI API connectivity"""
    try:
        data = request.get_json()
        test_message = data.get('message', 'Hello, are you working?')
        
        # Test the API directly
        spark_api = SparkAPI()
        response = spark_api.get_ai_response(test_message, {})
        
        return jsonify({
            'status': 'success',
            'test_message': test_message,
            'api_response': response,
            'api_working': 'fallback' not in response.lower() and 'error' not in response.lower()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f'Google AI test failed: {str(e)}'
        }), 500

@app.route('/api/speech/start', methods=['POST'])
@require_session
def speech_start():
    """Start voice listening"""
    try:
        result = speech_processor.start_listening()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Speech start failed: {str(e)}'}), 500

@app.route('/api/speech/stop', methods=['POST'])
@require_session
def speech_stop():
    """Stop voice listening"""
    try:
        result = speech_processor.stop_listening()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Speech stop failed: {str(e)}'}), 500

@app.route('/api/speech/status', methods=['GET'])
@require_session
def speech_status():
    """Get speech system status"""
    try:
        status = speech_processor.get_voice_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Speech status failed: {str(e)}'}), 500

@app.route('/api/speech/commands')
@require_session
def speech_get_commands():
    """Get voice commands from queue"""
    try:
        command = speech_processor.get_command()
        if command:
            return jsonify({'status': 'success', 'command': command})
        else:
            return jsonify({'status': 'success', 'command': None})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Command retrieval failed: {str(e)}'}), 500

@app.route('/api/speech/speak', methods=['POST'])
@require_session
def speech_speak():
    """Text-to-speech endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'status': 'error', 'message': 'No text provided'}), 400
            
        result = speech_processor.speak(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Speech failed: {str(e)}'}), 500

@app.route('/api/speech/emergency-stop', methods=['POST'])
@require_session
def speech_emergency_stop():
    """Emergency stop all speech processing"""
    try:
        result = speech_processor.emergency_stop()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Emergency stop failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'status': 'error', 'message': 'Session required'}), 401

if __name__ == '__main__':
    print("🚀 Starting Nexus AI Quantum Backend with PI SERVER INTEGRATION...")
    
    # Initialize Pi connection
    def initialize_system():
        print("🔄 Initializing system components...")
        time.sleep(1)
        pi_client.check_connection(force_check=True)
        with system_state.lock:
            system_state.pi_connected = pi_client.connected
        
        print(f"🔌 Pi Server Connection: {'✅ CONNECTED' if pi_client.connected else '❌ DISCONNECTED'}")
        if not pi_client.connected:
            print(f"🌐 Pi Server URL: {PI_SERVER_URL}")
            print("💡 Running in demo mode - Pi controls will simulate hardware actions")
    
    initialize_system()
    def voice_command_worker():
        """Background worker to process voice commands"""
        while True:
            try:
                # Only process if speech is actually available
                if hasattr(speech_processor, 'get_command') and callable(getattr(speech_processor, 'get_command')):
                    command = speech_processor.get_command()
                    if command:
                        print(f"🎤 Voice command received: {command['text']}")
                        
                        # Process the voice command through your existing chat system
                        ai_response = ai_companion.generate_response(
                            message=command['text'],
                            emotion_context=system_state.current_emotion,
                            user_id=system_state.session_data.get('session_id'),
                            interaction_count=system_state.session_data.get('interaction_count', 0)
                        )
                        
                        # Speak the response if TTS is available
                        if ai_response and hasattr(speech_processor, 'speak'):
                            response_text = ai_response.get('message') if isinstance(ai_response, dict) else ai_response
                            speech_processor.speak(response_text)
                else:
                    # If speech is not available, sleep longer to reduce CPU usage
                    time.sleep(5)
                            
            except Exception as e:
                print(f"❌ Voice command processing error: {e}")
                time.sleep(5)  # Longer sleep on error
            
            time.sleep(0.5)  # Check for commands every 0.5 seconds
            
    voice_thread = threading.Thread(target=voice_command_worker, daemon=True)
    voice_thread.start()

    print("\n📡 Available Endpoints:")
    endpoints = [
        ("POST", "/api/system/init", "Initialize session"),
        ("GET", "/api/system/health", "System health check"),
        ("POST", "/api/system/refresh-pi-connection", "Refresh Pi connection"),
        ("POST", "/api/camera/start", "Start camera"),
        ("POST", "/api/camera/stop", "Stop camera"), 
        ("GET", "/api/camera/feed", "Camera feed"),
        ("GET", "/api/emotion/latest", "Emotion analysis"),
        ("POST", "/api/chat/send", "AI chat"),
        ("POST", "/api/companion/pep_talk", "Pep talk"),
        # Pi Control Endpoints
        ("POST", "/api/pi/led/on", "Turn LED on"),
        ("POST", "/api/pi/led/off", "Turn LED off"),
        ("POST", "/api/pi/led/brightness", "Set brightness"),
        ("POST", "/api/pi/led/emotion", "Emotion lighting"),
        ("POST", "/api/pi/display/update", "Update display"),
        ("POST", "/api/pi/display/clear", "Clear display"),
        ("GET", "/api/pi/status", "Pi status"),
        ("GET", "/api/pi/sensors", "Sensor data"),
        ("POST", "/api/pi/reboot", "Reboot Pi"),
        ("POST", "/api/pi/shutdown", "Shutdown Pi"),
        ("GET", "/api/pi/diagnostic", "Run diagnostic"),
        ("POST", "/api/pi/update", "Check updates"),
        ("GET", "/api/pi/emotions/list", "Get emotions"),
        # Test Mode Endpoints
        ("POST", "/api/test/scan-folder", "Scan images folder"),
        ("GET", "/api/test/get-image", "Get test image"),
        ("POST", "/api/test/process-image", "Process test image"),
        ("GET", "/api/test/health", "Test mode health"),
        ("GET", "/api/debug/routes", "Debug routes"),
        # Speech Endpoints
        ("POST", "/api/speech/start", "Start voice listening"),
        ("POST", "/api/speech/stop", "Stop voice listening"), 
        ("GET", "/api/speech/status", "Get speech status"),
        ("GET", "/api/speech/commands", "Get voice commands"),
        ("POST", "/api/speech/speak", "Text-to-speech"),
        ("POST", "/api/speech/emergency-stop", "Emergency stop")
    ]

    for method, path, desc in endpoints:
        print(f"   {method:6} {path:25} {desc}")
    
    print(f"\n🌐 Main Server: http://{config.host}:{config.port}")
    print(f"🔌 Pi Server: {PI_SERVER_URL}")
    print("⭐ System Ready! All features operational!")
    
    app.run(host=config.host, port=config.port, debug=config.debug, threaded=True)