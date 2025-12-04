# speech.py - USING GOOGLE TTS (BEST QUALITY)
import speech_recognition as sr
import threading
import queue
import time
import os
from datetime import datetime
from gtts import gTTS
import pygame
import tempfile

class SpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command_queue = queue.Queue()
        self.listening = False
        self.processing = False
        self.is_speaking = False
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Calibrate microphone
        self._calibrate_microphone()
        
        print("🎤 Speech Processor: High-quality voice interface initialized")

    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            print("🔊 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibrated")
        except Exception as e:
            print(f"❌ Microphone calibration failed: {e}")

    def start_listening(self):
        """Start continuous voice listening"""
        if self.listening:
            return {"status": "already_listening"}
        
        self.listening = True
        listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listen_thread.start()
        
        return {"status": "listening_started", "message": "I'm listening now. How can I help you?"}

    def stop_listening(self):
        """Stop voice listening"""
        self.listening = False
        return {"status": "listening_stopped", "message": "I'll stop listening now. Just call me when you need me."}

    def _listen_loop(self):
        """Main listening loop"""
        while self.listening:
            try:
                print("👂 Listening for voice commands...")
                
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Process audio in separate thread
                process_thread = threading.Thread(
                    target=self._process_audio, 
                    args=(audio,),
                    daemon=True
                )
                process_thread.start()
                
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                continue
            except Exception as e:
                print(f"❌ Listening error: {e}")
                time.sleep(1)  # Prevent tight loop on error

    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            print("🔄 Processing speech...")
            
            # Recognize speech using Google Web Speech API
            text = self.recognizer.recognize_google(audio)
            
            if text:
                command = {
                    'timestamp': datetime.now().isoformat(),
                    'text': text,
                    'confidence': 'high'
                }
                
                self.command_queue.put(command)
                print(f"🎯 Voice command recognized: '{text}'")
                
        except sr.UnknownValueError:
            print("❌ I didn't quite catch that. Could you please repeat?")
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
        except Exception as e:
            print(f"❌ Audio processing error: {e}")

    def get_command(self):
        """Get next voice command from queue"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def speak(self, text):
        """Convert text to speech using Google TTS (High Quality)"""
        if self.is_speaking:
            return {"status": "already_speaking"}
            
        try:
            print(f"🗣️ Speaking: {text}")
            
            # Clean text for speech
            friendly_text = self._make_text_friendly(text)
            
            def _speak():
                self.is_speaking = True
                try:
                    # Create temporary file for audio
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                        temp_filename = tmp_file.name
                    
                    # Generate speech using Google TTS
                    tts = gTTS(text=friendly_text, lang='en', slow=False)
                    tts.save(temp_filename)
                    
                    # Play the audio
                    pygame.mixer.music.load(temp_filename)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to complete
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                    
                    # Clean up
                    pygame.mixer.music.unload()
                    os.unlink(temp_filename)
                    
                except Exception as e:
                    print(f"❌ TTS playback error: {e}")
                finally:
                    self.is_speaking = False
            
            # Speak in separate thread
            speak_thread = threading.Thread(target=_speak, daemon=True)
            speak_thread.start()
            
            return {"status": "speaking", "text": friendly_text}
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return {"status": "error", "message": str(e)}

    def _make_text_friendly(self, text):
        """Make text more friendly and soothing for speech"""
        # Remove technical formatting
        text = text.replace('**', '').replace('*', '')
        
        # Replace technical terms with friendlier alternatives
        friendly_replacements = {
            'ERROR': 'I encountered a small issue',
            'WARNING': 'Just letting you know',
            'FAILED': "couldn't complete",
            'ACTIVATED': 'is now active',
            'DEACTIVATED': 'is now resting',
            'ANALYSIS': 'check-in',
            'SCANNING': 'taking a look',
            'SYSTEM': 'I',
            'COMMAND': 'request',
            'PROCESSING': 'working on',
            'INITIALIZING': 'getting ready',
            'CALIBRATING': 'adjusting',
            'QUANTUM': '',
            'NEURAL': ''
        }
        
        for technical, friendly in friendly_replacements.items():
            text = text.replace(technical, friendly)
        
        return text

    def speak_greeting(self):
        """Speak a friendly greeting"""
        greetings = [
            "Hello there! I'm your Nexus AI companion, ready to help.",
            "Hi! I'm here and listening. What would you like to do today?",
            "Greetings! I'm awake and ready to assist you.",
            "Hello! It's nice to connect with you. How can I help?",
            "Hi there! I'm your AI assistant, here to make your day better."
        ]
        import random
        greeting = random.choice(greetings)
        return self.speak(greeting)

    def process_text_command(self, text):
        """Process text command as if it was spoken"""
        command = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'confidence': 'manual'
        }
        
        self.command_queue.put(command)
        return {"status": "command_queued", "text": text}

    def get_voice_status(self):
        """Get voice system status"""
        return {
            'listening': self.listening,
            'processing': self.processing,
            'speaking': self.is_speaking,
            'queue_size': self.command_queue.qsize(),
            'microphone_available': self.microphone is not None,
            'tts_engine': 'google_tts_high_quality',
            'last_activity': datetime.now().isoformat()
        }

    def emergency_stop(self):
        """Emergency stop all voice processing"""
        self.listening = False
        self.processing = False
        
        # Stop any current speech
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Clear command queue
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
        
        return {"status": "emergency_stop", "message": "Voice system stopped"}

# Install required packages: pip install gTTS pygame
speech_processor = SpeechProcessor()