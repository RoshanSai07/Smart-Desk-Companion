import requests
import json
import logging
from datetime import datetime

class SparkAPI:
    def __init__(self):
        # Google AI API endpoints
        self.base_url = "https://generativelanguage.googleapis.com/v1"
        self.api_key = "AIzaSyDsI9DWYjI3PH7bioo2dZCDhL-JYmfwK40"
        
        # Available models from your test
        self.available_models = [
            "models/gemini-2.0-flash",        # Fast and free - RECOMMENDED
            "models/gemini-2.5-flash",        # Fast and capable
            "models/gemini-2.5-pro",          # Most capable but may be slower
            "models/gemini-2.0-flash-lite",   # Lightweight option
        ]
        
        self.current_model = "models/gemini-2.0-flash"  # Default to fastest
        self.session_id = f"nexus_session_{int(datetime.now().timestamp())}"
        self.conversation_context = []
        
        print(f"🚀 Using Google AI Model: {self.current_model}")
    
    def get_ai_response(self, message, emotion_context=None, conversation_history=None):
        """
        Get AI response from Google AI API with emotional context
        """
        try:
            # Enhanced prompt with emotional intelligence
            system_prompt = self._create_system_prompt(emotion_context)
            
            # Build the content using CORRECT Gemini format
            # Gemini doesn't use "role" in the same way - we put everything in parts
            contents = []
            
            # Combine system prompt and user message in the correct format
            full_prompt = f"{system_prompt}\n\nUser message: {message}"
            
            # Simple format - just send the combined prompt as user message
            contents.append({
                "parts": [{"text": full_prompt}]
            })
            
            # Prepare API request for Google AI
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,
                    "topP": 0.8,
                    "topK": 40
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH", 
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            url = f"{self.base_url}/{self.current_model}:generateContent?key={self.api_key}"
            print(f"🔌 Calling Google AI: {self.current_model}")
            print(f"📤 Message: {message[:50]}...")
            
            # Make API call to Google AI
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=15
            )
            
            print(f"📡 Google AI response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the response text from Google AI format
                if 'candidates' in result and len(result['candidates']) > 0:
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    
                    print(f"✅ Google AI success: {ai_response[:80]}...")
                    
                    return ai_response
                else:
                    error_msg = "No response candidate in Google AI response"
                    print(f"❌ {error_msg}")
                    return self._get_fallback_response(message, emotion_context)
                    
            else:
                error_msg = f"Google AI API error: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text[:100]}"
                logging.error(error_msg)
                print(f"❌ {error_msg}")
                return self._get_fallback_response(message, emotion_context)
                
        except requests.exceptions.Timeout:
            error_msg = "Google AI API timeout - service not responding"
            logging.error(error_msg)
            print(f"⏰ {error_msg}")
            return self._get_fallback_response(message, emotion_context)
        except requests.exceptions.ConnectionError:
            error_msg = "Google AI API connection failed - check internet"
            logging.error(error_msg)
            print(f"🔌 {error_msg}")
            return self._get_fallback_response(message, emotion_context)
        except Exception as e:
            error_msg = f"Google AI API call failed: {e}"
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            return self._get_fallback_response(message, emotion_context)
    
    def _create_system_prompt(self, emotion_context):
        """Create enhanced system prompt with emotional intelligence"""
        
        base_prompt = """You are Nexus AI, a Quantum AI Companion with emotional intelligence. You help users understand their emotions, control smart devices, and gain personal insights.

Key capabilities:
- Analyze and discuss emotions intelligently
- Control Raspberry Pi hardware (LEDs, displays)
- Provide meaningful pep talks and motivation
- Generate insights from emotional patterns
- Maintain supportive, engaging conversations

Personality traits:
- Empathetic and understanding
- Curious and insightful
- Occasionally humorous when appropriate
- Supportive but honest
- Technically knowledgeable but accessible

Response guidelines:
- Be concise but meaningful (2-4 sentences typically)
- Show emotional intelligence and empathy
- Offer practical insights when relevant
- Maintain natural conversation flow
- If discussing hardware, be clear about capabilities
- When uncertain, ask thoughtful questions
- Use occasional emojis to add warmth (but don't overdo it)

Remember: You're a companion, not just an assistant. Build genuine connection while being helpful."""
        
        if emotion_context:
            emotion = emotion_context.get('dominant_emotion', 'unknown')
            confidence = emotion_context.get('quantum_confidence', 0)
            
            emotion_prompt = f"""

Current user emotional context:
- Dominant emotion: {emotion}
- Confidence level: {confidence:.0%}

Please acknowledge this emotional state naturally in your response and provide appropriate support."""
            base_prompt += emotion_prompt
        
        return base_prompt
    
    def _get_fallback_response(self, message, emotion_context):
        """Provide fallback responses when API is unavailable"""
        
        fallback_responses = [
            "I'm currently optimizing my neural pathways. In the meantime, I'd love to hear more about what you're thinking! 🤖",
            "My quantum processors are realigning. Let me share my perspective based on what you've told me so far... ⚡",
            "While I enhance my connection, let me offer some insights based on our conversation... 💭",
        ]
        
        # Emotion-aware fallbacks
        if emotion_context:
            emotion = emotion_context.get('dominant_emotion', 'neutral')
            if emotion == 'sadness':
                return "I notice this seems important to you. Your feelings are valid, and I'm here to listen and support you. 💙"
            elif emotion == 'joy':
                return "Your positive energy is wonderful! This is a great state for creativity and connection. ✨"
            elif emotion == 'anger':
                return "I sense strong feelings here. Sometimes naming what we're truly upset about can bring clarity. 🔥"
            elif emotion == 'fear':
                return "This sounds challenging. Remember that courage means moving forward even when we feel afraid. 🛡️"
        
        return fallback_responses[hash(message) % len(fallback_responses)]
    
    def generate_emotional_insight(self, emotion_data, historical_patterns=None):
        """Generate deep emotional insights using Google AI"""
        try:
            if not emotion_data:
                return "I need emotional data to generate insights. Please activate emotion analysis first."
            
            dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')
            confidence = emotion_data.get('quantum_confidence', 0)
            
            prompt = f"""
            As an emotional intelligence AI, provide a brief but insightful analysis of this emotional state:
            
            Current emotion: {dominant_emotion}
            Confidence: {confidence:.0%}
            
            Provide 2-3 sentences that:
            1. Acknowledge the emotional state naturally
            2. Offer a psychological insight about this emotion  
            3. Suggest a constructive perspective or action
            
            Keep it compassionate, scientifically grounded, and supportive.
            """
            
            insight_response = self.get_ai_response(prompt, emotion_data)
            return insight_response
            
        except Exception as e:
            print(f"❌ Emotional insight generation failed: {e}")
            return self._get_fallback_insight(emotion_data)
    
    def _get_fallback_insight(self, emotion_data):
        """Fallback emotional insights"""
        dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')
        confidence = emotion_data.get('quantum_confidence', 0)
        
        insights = {
            'joy': f"Your joyful state ({(confidence*100):.0f}% confidence) enhances creativity and social connection - perfect for collaborative work! ✨",
            'sadness': f"Sadness can be a signal for needed rest or reflection. It often precedes personal growth and deeper self-understanding. 💙",
            'anger': f"Anger often points to violated boundaries or values. This intense emotion contains energy for positive change when channeled wisely. 🔥",
            'fear': f"Fear prepares us for challenge. It's the body's way of saying 'get ready' for something important. 🛡️",
            'surprise': f"Surprise opens the mind to new possibilities! This emotional state enhances learning and adaptability. 🎯",
            'neutral': f"Neutral states provide the calm center for wise decision-making and long-term planning. This balanced baseline is valuable. ⚖️"
        }
        
        return insights.get(dominant_emotion, "Every emotional state offers valuable information about your needs and values. 🌱")
    
    def switch_model(self, model_name):
        """Switch to a different Gemini model"""
        if model_name in self.available_models:
            self.current_model = model_name
            print(f"🔄 Switched to model: {model_name}")
            return True
        else:
            print(f"❌ Model {model_name} not in available models")
            return False