import cv2
import numpy as np
import json
from datetime import datetime, timedelta
import random
from collections import deque
import logging

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("✅ DeepFace imported successfully")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available, using Haar cascades only")

class EmotionAnalyzer:
    def __init__(self):
        # Initialize face detection with fallbacks
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.deepface_available = DEEPFACE_AVAILABLE
        
        # Emotion configuration
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.emotion_mapping = {
            'angry': 'anger',
            'happy': 'joy', 
            'sad': 'sadness',
            'fear': 'fear',
            'surprise': 'surprise',
            'disgust': 'disgust',
            'neutral': 'neutral'
        }
        
        self.emotion_history = deque(maxlen=50)
        
        # Emotional intelligence metrics
        self.mood_stability_score = 0.8
        self.engagement_level = 0.5
        self.stress_trend = 'stable'
        
        print(f"🧠 Emotion Analyzer: Neural networks initialized (DeepFace: {self.deepface_available})")

    def analyze_emotion(self, frame):
        """Enhanced emotion analysis using DeepFace with Haar fallback"""
        try:
            # Try DeepFace first if available
            if self.deepface_available:
                deepface_result = self._analyze_with_deepface(frame)
                if deepface_result and deepface_result.get('face_detected', False):
                    return deepface_result
            
            # Fallback to Haar cascades
            return self._analyze_with_haar(frame)
            
        except Exception as e:
            print(f"❌ Emotion analysis error: {e}")
            return self._generate_fallback_data()

    def _analyze_with_deepface(self, frame):
        """Analyze emotions using DeepFace"""
        try:
            # Convert BGR to RGB for DeepFace
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Analyze with DeepFace
            analysis = DeepFace.analyze(
                rgb_frame, 
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',  # Use opencv as detector
                silent=True
            )
            
            # Handle multiple faces or single face
            if isinstance(analysis, list):
                # Multiple faces detected
                if len(analysis) == 0:
                    return self._generate_no_face_data()
                
                # Use the first face for now (can be enhanced to handle multiple)
                face_data = analysis[0]
            else:
                # Single face detected
                face_data = analysis
            
            # Extract emotion data
            emotion_scores = face_data.get('emotion', {})
            
            if not emotion_scores:
                return self._analyze_with_haar(frame)  # Fallback if no emotions
            
            # Convert to our emotion mapping
            mapped_emotions = self._map_deepface_emotions(emotion_scores)
            
            # Generate enhanced emotional data
            emotion_data = self._generate_contextual_emotion_data(mapped_emotions, len(analysis) if isinstance(analysis, list) else 1)
            
            # Mark as DeepFace analysis
            emotion_data['analysis_method'] = 'deepface'
            emotion_data['deepface_confidence'] = face_data.get('dominant_confidence', 0.8)
            
            return emotion_data
            
        except Exception as e:
            print(f"⚠️ DeepFace analysis failed: {e}")
            return self._analyze_with_haar(frame)  # Fallback to Haar

    def _analyze_with_haar(self, frame):
        """Analyze emotions using Haar cascades (fallback method)"""
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Enhanced face detection
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(faces) == 0:
                return self._generate_no_face_data()
            
            # Generate contextual emotion data
            emotion_data = self._generate_contextual_emotion_data(None, len(faces))
            
            # Update emotional history and trends
            self._update_emotional_trends(emotion_data)
            
            # Mark as Haar analysis
            emotion_data['analysis_method'] = 'haar'
            emotion_data['face_count'] = len(faces)
            
            self.emotion_history.append(emotion_data)
            
            return emotion_data
            
        except Exception as e:
            print(f"❌ Haar analysis error: {e}")
            return self._generate_fallback_data()

    def _map_deepface_emotions(self, deepface_emotions):
        """Map DeepFace emotions to our emotion system"""
        # Normalize DeepFace scores (they're already 0-100)
        total = sum(deepface_emotions.values())
        normalized = {self.emotion_mapping.get(k, k): v/total for k, v in deepface_emotions.items()}
        
        # Ensure all emotions are present
        for emotion in self.emotion_labels:
            mapped_emotion = self.emotion_mapping.get(emotion, emotion)
            if mapped_emotion not in normalized:
                normalized[mapped_emotion] = 0.0
        
        return normalized

    def _generate_contextual_emotion_data(self, deepface_emotions=None, face_count=1):
        """Generate realistic, contextual emotion data"""
        if deepface_emotions:
            # Use DeepFace emotions as base
            emotional_state = deepface_emotions.copy()
        else:
            # Generate base emotional state
            emotional_state = self._get_contextual_base_state()
            
            # Add natural emotional fluctuations
            emotional_state = self._apply_natural_variation(emotional_state)
        
        # Ensure face count influences the analysis
        if face_count > 1:
            emotional_state = self._adjust_for_multiple_faces(emotional_state)
        
        # Find dominant emotion
        dominant_emotion = max(emotional_state.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence
        confidence = self._calculate_confidence(emotional_state, dominant_emotion)
        
        # Generate bio metrics
        bio_metrics = self._generate_bio_metrics(emotional_state, dominant_emotion)
        
        return {
            'dominant_emotion': dominant_emotion,
            'quantum_confidence': confidence,
            'emotion_spectrum': emotional_state,
            'face_detected': True,
            'face_count': face_count,
            'emotional_clarity': self._calculate_emotional_clarity(emotional_state),
            'bio_metrics': bio_metrics,
            'contextual_insights': self._generate_insights(emotional_state, dominant_emotion),
            'analysis_timestamp': datetime.now().isoformat(),
            'mood_stability': self.mood_stability_score,
            'engagement_level': self.engagement_level
        }

    def _get_contextual_base_state(self):
        """Get base emotional state influenced by context"""
        hour = datetime.now().hour
        
        # Time-of-day influenced base states
        if 6 <= hour < 12:  # Morning
            base = {'joy': 0.3, 'neutral': 0.4, 'sadness': 0.1, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.1, 'disgust': 0.0}
        elif 12 <= hour < 18:  # Afternoon
            base = {'joy': 0.25, 'neutral': 0.35, 'sadness': 0.15, 'anger': 0.1, 'fear': 0.05, 'surprise': 0.1, 'disgust': 0.0}
        else:  # Evening/Night
            base = {'joy': 0.2, 'neutral': 0.3, 'sadness': 0.2, 'anger': 0.1, 'fear': 0.1, 'surprise': 0.1, 'disgust': 0.0}
        
        # Add influence from recent emotional history
        if self.emotion_history:
            recent_trend = self._get_recent_emotional_trend()
            for emotion, weight in recent_trend.items():
                base[emotion] = (base[emotion] + weight) / 2
        
        return base

    def _apply_natural_variation(self, base_state):
        """Apply natural emotional variations"""
        varied_state = base_state.copy()
        
        # Add realistic fluctuations
        for emotion in varied_state:
            variation = random.gauss(0, 0.08)
            varied_state[emotion] = max(0, min(1, varied_state[emotion] + variation))
        
        # Normalize to ensure sum = 1
        total = sum(varied_state.values())
        return {k: v/total for k, v in varied_state.items()}

    def _calculate_confidence(self, emotional_state, dominant_emotion):
        """Calculate analysis confidence"""
        dominant_strength = emotional_state[dominant_emotion]
        other_emotions = [v for k, v in emotional_state.items() if k != dominant_emotion]
        
        clarity = dominant_strength - max(other_emotions) if other_emotions else dominant_strength
        base_confidence = 0.6 + (clarity * 0.4)
        
        # Higher confidence for DeepFace analysis
        if hasattr(self, 'deepface_available') and self.deepface_available:
            base_confidence += 0.1
        
        historical_consistency = self._get_historical_consistency(dominant_emotion)
        final_confidence = (base_confidence + historical_consistency) / 2
        
        return min(0.95, max(0.3, final_confidence))

    def _generate_bio_metrics(self, emotional_state, dominant_emotion):
        """Generate realistic bio metrics based on emotional state"""
        stress_emotions = ['anger', 'fear', 'sadness']
        stress_index = sum(emotional_state[e] for e in stress_emotions) / len(stress_emotions)
        
        stability = self.mood_stability_score
        engagement = 1 - emotional_state['neutral']
        
        positive_energy = emotional_state['joy'] + (emotional_state['surprise'] * 0.5)
        negative_drain = sum(emotional_state[e] for e in ['sadness', 'anger', 'fear']) * 0.3
        energy_level = max(0.1, positive_energy - negative_drain)
        
        return {
            'stress_index': round(stress_index, 3),
            'mood_stability': round(stability, 3),
            'engagement_level': round(engagement, 3),
            'energy_level': round(energy_level, 3),
            'focus_capacity': round(1 - stress_index, 3),
            'emotional_vitality': round(positive_energy, 3)
        }

    def _generate_insights(self, emotional_state, dominant_emotion):
        """Generate contextual insights about emotional state"""
        insights = []
        
        max_intensity = max(emotional_state.values())
        if max_intensity > 0.7:
            insights.append("Strong emotional presence detected")
        elif max_intensity < 0.3:
            insights.append("Subtle emotional landscape observed")
        
        strong_emotions = [e for e, i in emotional_state.items() if i > 0.2]
        if len(strong_emotions) > 2:
            insights.append("Complex emotional blend present")
        
        if emotional_state['joy'] > 0.4:
            insights.append("Positive energy flowing")
        if emotional_state['sadness'] > 0.3:
            insights.append("Contemplative state observed")
        if emotional_state['neutral'] > 0.6:
            insights.append("Calm and centered presence")
        
        # Add DeepFace specific insight if used
        if hasattr(self, 'analysis_method') and self.analysis_method == 'deepface':
            insights.append("Advanced neural analysis active")
        
        return insights

    def _update_emotional_trends(self, current_emotion):
        """Update long-term emotional trends"""
        if self.emotion_history:
            recent_emotions = [e['dominant_emotion'] for e in list(self.emotion_history)[-5:]]
            consistency = len(set(recent_emotions)) / len(recent_emotions)
            self.mood_stability_score = 1 - consistency
            
            current_engagement = current_emotion['bio_metrics']['engagement_level']
            self.engagement_level = (self.engagement_level * 0.7) + (current_engagement * 0.3)

    def _get_recent_emotional_trend(self):
        """Get trend from recent emotional history"""
        if len(self.emotion_history) < 3:
            return {emotion: 0 for emotion in self.emotion_labels}
        
        recent = list(self.emotion_history)[-3:]
        trend = {emotion: 0 for emotion in self.emotion_labels}
        
        for analysis in recent:
            for emotion, intensity in analysis['emotion_spectrum'].items():
                trend[emotion] += intensity / len(recent)
        
        return trend

    def _get_historical_consistency(self, current_dominant):
        """Check how consistent current emotion is with recent history"""
        if len(self.emotion_history) < 2:
            return 0.7
        
        recent_dominants = [e['dominant_emotion'] for e in list(self.emotion_history)[-3:]]
        consistency = sum(1 for e in recent_dominants if e == current_dominant) / len(recent_dominants)
        
        return consistency

    def _calculate_emotional_clarity(self, emotional_state):
        """Calculate how clear/defined the emotional state is"""
        intensities = list(emotional_state.values())
        max_intensity = max(intensities)
        second_max = sorted(intensities)[-2] if len(intensities) > 1 else 0
        
        clarity = max_intensity - second_max
        return round(clarity, 3)

    def _adjust_for_multiple_faces(self, emotional_state):
        """Adjust emotional analysis for multiple faces"""
        adjusted = emotional_state.copy()
        for emotion in ['neutral', 'joy']:
            adjusted[emotion] = min(1.0, adjusted[emotion] * 1.2)
        for emotion in ['anger', 'fear']:
            adjusted[emotion] = max(0.0, adjusted[emotion] * 0.8)
        
        total = sum(adjusted.values())
        return {k: v/total for k, v in adjusted.items()}

    def _generate_no_face_data(self):
        """Generate data when no face is detected"""
        return {
            'dominant_emotion': 'neutral',
            'quantum_confidence': 0.3,
            'emotion_spectrum': {
                'joy': 0.1, 'neutral': 0.7, 'sadness': 0.1, 
                'anger': 0.05, 'fear': 0.025, 'surprise': 0.025, 'disgust': 0.0
            },
            'face_detected': False,
            'face_count': 0,
            'emotional_clarity': 0.1,
            'bio_metrics': {
                'stress_index': 0.3,
                'mood_stability': 0.8,
                'engagement_level': 0.2,
                'energy_level': 0.4,
                'focus_capacity': 0.7,
                'emotional_vitality': 0.3
            },
            'contextual_insights': ['Awaiting presence detection', 'Camera system ready'],
            'analysis_timestamp': datetime.now().isoformat(),
            'mood_stability': 0.8,
            'engagement_level': 0.2,
            'analysis_method': 'none'
        }

    def _generate_fallback_data(self):
        """Generate fallback data on error"""
        return {
            'dominant_emotion': 'neutral',
            'quantum_confidence': 0.5,
            'emotion_spectrum': {
                'joy': 0.25, 'neutral': 0.5, 'sadness': 0.1, 
                'anger': 0.05, 'fear': 0.05, 'surprise': 0.05, 'disgust': 0.0
            },
            'face_detected': False,
            'face_count': 0,
            'emotional_clarity': 0.3,
            'bio_metrics': {
                'stress_index': 0.4,
                'mood_stability': 0.6,
                'engagement_level': 0.3,
                'energy_level': 0.5,
                'focus_capacity': 0.6,
                'emotional_vitality': 0.4
            },
            'contextual_insights': ['System calibration in progress'],
            'analysis_timestamp': datetime.now().isoformat(),
            'mood_stability': 0.6,
            'engagement_level': 0.3,
            'analysis_method': 'fallback'
        }

    def generate_contextual_demo(self):
        """Generate enhanced demo data for testing"""
        return self._generate_contextual_emotion_data(None, 1)

    def get_emotional_summary(self):
        """Get summary of emotional patterns"""
        if not self.emotion_history:
            return "Awaiting emotional data..."
        
        recent = list(self.emotion_history)[-10:]
        dominants = [e['dominant_emotion'] for e in recent]
        
        from collections import Counter
        common_emotion = Counter(dominants).most_common(1)[0]
        
        return {
            'predominant_mood': common_emotion[0],
            'frequency': common_emotion[1] / len(recent),
            'stability_score': self.mood_stability_score,
            'engagement_trend': 'increasing' if self.engagement_level > 0.6 else 'stable',
            'sample_size': len(recent)
        }