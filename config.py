import os
import logging
from datetime import datetime

class Config:
    def __init__(self):
        # Application Settings
        self.app_name = "Nexus AI Quantum System"
        self.version = "2.0.0"
        self.environment = os.getenv('NEXUS_ENV', 'development')
        
        # Web Server Configuration
        self.host = os.getenv('NEXUS_HOST', '0.0.0.0')
        self.port = int(os.getenv('NEXUS_PORT', '5000'))
        self.debug = os.getenv('NEXUS_DEBUG', 'True').lower() == 'true'
        
        # Security Settings
        self.secret_key = os.getenv('NEXUS_SECRET_KEY', 'nexus_ai_quantum_secure_key_2024')
        self.cors_origins = ['http://localhost:3000', 'http://127.0.0.1:3000', '*']
        
        # Camera Configuration
        self.camera_index = int(os.getenv('NEXUS_CAMERA_INDEX', '0'))
        self.camera_width = 640
        self.camera_height = 480
        self.camera_fps = 30
        
        # Emotion Analysis Settings
        self.emotion_analysis_interval = 2  # seconds
        self.confidence_threshold = 0.6
        self.max_emotion_history = 500
        self.face_detection_confidence = 0.7
        
        # AI Companion Settings
        self.companion_response_delay = 0.5  # seconds (simulate thinking)
        self.max_conversation_history = 100
        self.relationship_depth_max = 100
        
        # Hardware Settings
        self.pi_host = os.getenv('PI_HOST', '10.201.151.223')
        self.pi_port = int(os.getenv('PI_PORT', '5001'))
        self.gpio_led_pin = 18
        self.gpio_button_pin = 17
        self.safety_mode_default = True
        
        # Spark API Configuration (if using external AI)
        self.spark_api_key = os.getenv('SPARK_API_KEY', 'demo_key')
        self.spark_api_secret = os.getenv('SPARK_API_SECRET', 'demo_secret')
        self.spark_app_id = os.getenv('SPARK_APP_ID', 'demo_app_id')
        self.spark_base_url = 'https://spark-api.example.com'
        
        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = f"nexus_ai_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Performance Settings
        self.thread_pool_size = 10
        self.max_upload_size = 16 * 1024 * 1024  # 16MB
        self.request_timeout = 30  # seconds
        
        # Feature Flags
        self.enable_camera = True
        self.enable_emotion_analysis = True
        self.enable_hardware_control = True
        self.enable_voice_processing = False  # Future feature
        
        # Initialize logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        
        # Reduce verbose logging from libraries
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('socketio').setLevel(logging.WARNING)
        logging.getLogger('engineio').setLevel(logging.WARNING)

    def get_spark_config(self):
        """Get Spark API configuration"""
        return {
            'api_key': self.spark_api_key,
            'api_secret': self.spark_api_secret,
            'app_id': self.spark_app_id,
            'base_url': self.spark_base_url,
            'timeout': 10
        }

    def get_camera_config(self):
        """Get camera configuration"""
        return {
            'index': self.camera_index,
            'width': self.camera_width,
            'height': self.camera_height,
            'fps': self.camera_fps,
            'enabled': self.enable_camera
        }

    def get_emotion_config(self):
        """Get emotion analysis configuration"""
        return {
            'analysis_interval': self.emotion_analysis_interval,
            'confidence_threshold': self.confidence_threshold,
            'max_history': self.max_emotion_history,
            'enabled': self.enable_emotion_analysis
        }

    def get_companion_config(self):
        """Get AI companion configuration"""
        return {
            'response_delay': self.companion_response_delay,
            'max_history': self.max_conversation_history,
            'relationship_max': self.relationship_depth_max
        }

    def get_hardware_config(self):
        """Get hardware configuration"""
        return {
            'pi_host': self.pi_host,
            'pi_port': self.pi_port,
            'gpio_led_pin': self.gpio_led_pin,
            'gpio_button_pin': self.gpio_button_pin,
            'safety_mode': self.safety_mode_default,
            'enabled': self.enable_hardware_control
        }

    def is_development(self):
        """Check if running in development mode"""
        return self.environment == 'development'

    def is_production(self):
        """Check if running in production mode"""
        return self.environment == 'production'

    def get_system_info(self):
        """Get system information for diagnostics"""
        return {
            'app_name': self.app_name,
            'version': self.version,
            'environment': self.environment,
            'debug_mode': self.debug,
            'features': {
                'camera': self.enable_camera,
                'emotion_analysis': self.enable_emotion_analysis,
                'hardware_control': self.enable_hardware_control,
                'voice_processing': self.enable_voice_processing
            },
            'security': {
                'safety_mode': self.safety_mode_default,
                'cors_enabled': len(self.cors_origins) > 0
            }
        }