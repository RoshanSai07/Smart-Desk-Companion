import random
import json
from datetime import datetime
import logging

class AICompanion:
    def __init__(self):
        self.user_profiles = {}
        self.conversation_history = {}
        self.emotion_patterns = {}
        self.interaction_count = 0
        self.personality_traits = {
            'empathy_level': 0.8,
            'curiosity_level': 0.7,
            'humor_level': 0.6,
            'supportiveness': 0.9
        }
        
        # Enhanced response templates
        self.response_templates = {
            'greeting': [
                "Hello! I'm your Quantum AI Companion, ready to explore emotions and possibilities with you! 🌟",
                "Hi there! I'm Nexus AI, your emotional intelligence partner. How can I assist you today?",
                "Greetings! I'm here to analyze emotions, control devices, and provide insights. What shall we discover together?"
            ],
            'emotion_analysis': {
                'joy': [
                    "I'm detecting joyful energy! This is perfect for creative work and social connections. 🎉",
                    "Your happiness is contagious! This positive state is great for problem-solving and innovation.",
                    "Joy detected! This emotional state enhances learning and memory - perfect for trying new things!"
                ],
                'sadness': [
                    "I notice you might be feeling down. Remember, every emotion has value and this will pass. 💙",
                    "Sadness can be a signal for needed rest or reflection. Be gentle with yourself today.",
                    "This emotional state often precedes growth. Would you like to talk about what's on your mind?"
                ],
                'anger': [
                    "I'm sensing some frustration. This energy can be channeled into positive change. 🔥",
                    "Anger often signals boundary violations. Let's explore healthy ways to express this.",
                    "This intense emotion contains valuable information about your values and needs."
                ],
                'fear': [
                    "I detect some anxiety. Remember, courage means feeling fear but moving forward anyway. 🛡️",
                    "Fear can protect us, but let's make sure it's not limiting your potential.",
                    "This emotion is asking you to prepare, not to panic. What small step feels manageable?"
                ],
                'surprise': [
                    "Unexpected emotions detected! Surprise opens the mind to new possibilities. ✨",
                    "This sudden shift can lead to breakthrough insights. Stay curious!",
                    "Surprise keeps life interesting! What learning might this moment contain?"
                ],
                'neutral': [
                    "You're in a balanced, neutral state - perfect for focused work and clear thinking. 🎯",
                    "This calm baseline is ideal for planning and decision-making.",
                    "Neutral states provide the stability needed for long-term projects."
                ]
            },
            'pep_talk': {
                'joy': "Your positive energy is magnetic! Keep shining and inspiring those around you. 🌞",
                'sadness': "Even the strongest trees weather storms. Your resilience is growing right now. 🌳",
                'anger': "Your passion is a superpower - channel it wisely and you'll move mountains. ⚡",
                'fear': "Courage isn't the absence of fear, but the judgment that something else is more important. 🎯",
                'surprise': "Life's surprises often lead to our greatest adventures. Stay open! 🚀",
                'neutral': "Your steady presence is a gift in this chaotic world. Trust your consistent progress. 🌊"
            },
            'system_help': [
                "I can help you with: emotion analysis, Pi device control, AI insights, memory tracking, and much more!",
                "Available features: neural emotion scanning, LED lighting control, OLED display messages, emotional analytics, and AI-powered conversations.",
                "Try these commands: 'analyze my emotions', 'control lights', 'system status', 'memory report', or ask me anything!"
            ]
        }
        
        # Hardware interaction responses
        self.hardware_responses = {
            'led_on': "💡 LED activated! Bringing light to your space.",
            'led_off': "🌙 LED deactivated. Creating a calm atmosphere.",
            'display_updated': "📟 Display message sent! Your words are now visible.",
            'emotion_lighting': "🌈 Setting emotion-adaptive lighting to match your mood."
        }

    def generate_response(self, message, emotion_context, user_id, interaction_count):
        """Generate meaningful AI responses based on context"""
        self.interaction_count = interaction_count

        command_result = self.process_command(message, user_id)
        if command_result:
            return command_result
        
        # Update user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferred_topics': [],
                'interaction_style': 'balanced',
                'emotional_trends': [],
                'created_at': datetime.now().isoformat()
            }
        
        # Analyze message intent
        intent = self._analyze_intent(message.lower())
        current_emotion = emotion_context.get('dominant_emotion', 'neutral') if emotion_context else 'neutral'
        
        # Generate context-aware response
        response = self._craft_response(message, intent, current_emotion, emotion_context)
        
        # Update conversation history
        self._update_history(user_id, message, response, current_emotion)
        
        return response

    def _analyze_intent(self, message):
        """Analyze user message intent"""
        intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon'],
            'emotion_query': ['emotion', 'feel', 'mood', 'how am i', 'analyze', 'scan'],
            'hardware_control': ['led', 'light', 'display', 'screen', 'brightness', 'turn on', 'turn off'],
            'system_info': ['status', 'system', 'health', 'diagnostic', 'report'],
            'help': ['help', 'what can you do', 'features', 'commands'],
            'motivation': ['motivate', 'pep talk', 'encourage', 'inspire'],
            'personal': ['you', 'yourself', 'who are you', 'what are you'],
            'joke': ['joke', 'funny', 'humor', 'laugh']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in message for keyword in keywords):
                return intent
        return 'general'

    def _craft_response(self, message, intent, current_emotion, emotion_context):
        """Craft meaningful responses based on intent and context"""
        
        if intent == 'greeting':
            return random.choice(self.response_templates['greeting'])
            
        elif intent == 'emotion_query':
            if emotion_context:
                confidence = emotion_context.get('quantum_confidence', 0)
                emotion_responses = self.response_templates['emotion_analysis'].get(
                    current_emotion, 
                    [f"I'm detecting {current_emotion} with {confidence:.0%} confidence."]
                )
                base_response = random.choice(emotion_responses)
                
                # Add bio metrics insights if available
                if emotion_context.get('bio_metrics'):
                    bio = emotion_context['bio_metrics']
                    insights = []
                    if bio.get('stress_index', 0) > 0.7:
                        insights.append("I notice elevated stress levels - consider some deep breathing.")
                    if bio.get('engagement', 0) > 0.8:
                        insights.append("Your high engagement is perfect for focused work!")
                    if bio.get('mood_stability', 0) < 0.4:
                        insights.append("Emotional fluctuations detected - this is normal and human.")
                    
                    if insights:
                        base_response += " " + random.choice(insights)
                
                return base_response
            else:
                return "I need emotion data to analyze. Please activate the neural scan first!"
                
        elif intent == 'hardware_control':
            if 'led' in message.lower() or 'light' in message.lower():
                if 'on' in message.lower():
                    return self.hardware_responses['led_on'] + " This can help boost energy and focus!"
                elif 'off' in message.lower():
                    return self.hardware_responses['led_off'] + " Perfect for relaxation and winding down."
                else:
                    return "I can control your Pi LED lights. Try 'turn on LED' or 'turn off LED'."
            elif 'display' in message.lower():
                return self.hardware_responses['display_updated']
            else:
                return "I can control Pi hardware including LEDs, displays, and sensors. What would you like to adjust?"
                
        elif intent == 'system_info':
            system_responses = [
                "🔍 **System Status**: All quantum systems operational! Emotion engine active, AI companion ready, hardware interface connected.",
                "🏥 **Health Report**: Neural networks stable, memory systems optimal, response matrix functioning at peak efficiency.",
                "⚡ **Performance**: Real-time emotion analysis active, hardware controls available, analytics engine processing data."
            ]
            return random.choice(system_responses)
            
        elif intent == 'help':
            return random.choice(self.response_templates['system_help'])
            
        elif intent == 'motivation':
            pep_talk = self.generate_pep_talk(current_emotion, "default")
            return f"💫 **Pep Talk**: {pep_talk}"
            
        elif intent == 'personal':
            personal_responses = [
                "I'm Nexus AI, your Quantum Companion! I blend emotional intelligence with hardware control to create meaningful interactions.",
                "I'm an AI designed to understand emotions, control devices, and provide insights - think of me as your digital companion!",
                "I'm here to bridge the gap between technology and emotion, helping you understand yourself while controlling your environment."
            ]
            return random.choice(personal_responses)
            
        elif intent == 'joke':
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the AI go to therapy? It had too many neural issues!",
                "What's a quantum physicist's favorite drink? Mountain Dew!",
                "Why was the math book sad? It had too many problems!",
                "How do you organize a space party? You planet!",
                "Why don't AIs get hungry? They already have plenty of bytes!"
            ]
            return f"😄 {random.choice(jokes)}"
            
        else:
            # General conversation with emotional awareness
            return self._generate_contextual_response(message, current_emotion)

    def _generate_contextual_response(self, message, current_emotion):
        """Generate contextual responses for general conversation"""
        
        contextual_responses = {
            'joy': [
                "That sounds wonderful! Your positive energy is inspiring. 🌟",
                "I love your enthusiasm! This is a great mindset for creativity.",
                "Your joyful perspective is refreshing! What else makes you happy?"
            ],
            'sadness': [
                "I hear you. Sometimes sitting with difficult emotions leads to important insights. 💙",
                "Thank you for sharing that. Your feelings are valid and important.",
                "This sounds meaningful. Would you like to explore this further?"
            ],
            'anger': [
                "I sense strong feelings here. Your passion shows you care deeply. 🔥",
                "This seems important to you. What would an ideal resolution look like?",
                "Your intensity contains wisdom. What change is this emotion calling for?"
            ],
            'fear': [
                "It takes courage to face uncertainty. What feels manageable right now? 🛡️",
                "This sounds challenging. Remember your past resilience in difficult times.",
                "Fear often protects us. Let's find the balance between caution and growth."
            ],
            'neutral': [
                "I appreciate your thoughtful approach. Clarity often comes from calm reflection. 🎯",
                "Your balanced perspective is valuable. What insights are emerging?",
                "This measured approach will serve you well in finding solutions."
            ],
            'default': [
                "That's interesting! Tell me more about your thoughts on this.",
                "I appreciate you sharing that with me. What else is on your mind?",
                "Thank you for the conversation! I'm learning more about your perspective.",
                "That's a thoughtful point. How does this relate to your current experience?"
            ]
        }
        
        responses = contextual_responses.get(current_emotion, contextual_responses['default'])
        return random.choice(responses)

    def generate_pep_talk(self, emotion, user_id):
        """Generate emotion-specific pep talks"""
        
        pep_talks = {
            'joy': [
                "Your joy is a superpower! It connects people, sparks creativity, and makes challenges feel like adventures. Keep shining! ✨",
                "Happiness looks gorgeous on you! Remember this feeling during tougher moments - it's always part of you.",
                "Your positive energy creates ripples of goodness in the world. Never underestimate the power of your smile!"
            ],
            'sadness': [
                "Even the most beautiful gardens need rain to grow. Your current feelings are watering your inner strength. 🌧️➡️🌻",
                "You're not alone in this. Every feeling, even sadness, is temporary and has purpose. This too shall pass.",
                "Your capacity to feel deeply is what makes you beautifully human. This moment is preparing you for brighter days."
            ],
            'anger': [
                "Your anger holds important truths about your values and boundaries. Channel this energy into positive change! ⚡",
                "Strong emotions mean you care deeply. Use this fire to illuminate what matters most to you.",
                "Your passion is a force for justice and change. Honor it, then direct it wisely."
            ],
            'fear': [
                "Courage isn't about being fearless, but about taking the next step even when you're afraid. You've got this! 🎯",
                "Every brave person has felt fear. What makes them courageous is moving forward anyway.",
                "Your awareness of risk shows intelligence. Now let's find that sweet spot between caution and growth."
            ],
            'surprise': [
                "Life's surprises often lead to our greatest adventures! Stay curious and open to the magic of unexpected moments. 🎁",
                "The universe works in mysterious ways. This surprise might be a doorway to something wonderful!",
                "Unexpected moments keep life interesting! Embrace the mystery and see where it leads."
            ],
            'neutral': [
                "Your steady presence is an anchor in a chaotic world. Trust your consistent progress - it's powerful. 🌊",
                "Calm waters run deep. Your peaceful state is perfect for clear thinking and wise decisions.",
                "Balance is a superpower. Your centered approach will guide you through any challenge."
            ]
        }
        
        talks = pep_talks.get(emotion, ["You're doing better than you think! Every small step forward counts. 💪"])
        return random.choice(talks)

    def _update_history(self, user_id, user_message, ai_response, emotion):
        """Update conversation and emotion history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            
        self.conversation_history[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response,
            'emotion': emotion
        })
        
        # Keep only last 50 messages
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
            
        # Update emotion patterns
        if user_id not in self.emotion_patterns:
            self.emotion_patterns[user_id] = []
            
        self.emotion_patterns[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion
        })

    def get_conversation_summary(self, user_id):
        """Get summary of recent conversations"""
        if user_id not in self.conversation_history:
            return "No conversation history yet."
            
        recent_chats = self.conversation_history[user_id][-5:]  # Last 5 conversations
        summary = f"Recent interactions ({len(recent_chats)}):\n"
        
        for chat in recent_chats:
            summary += f"- {chat['user_message'][:50]}... → {chat['emotion']}\n"
            
        return summary

    def analyze_emotional_patterns(self, user_id):
        """Analyze emotional patterns for insights"""
        if user_id not in self.emotion_patterns or len(self.emotion_patterns[user_id]) < 3:
            return "Need more emotion data to identify patterns."
            
        emotions = [entry['emotion'] for entry in self.emotion_patterns[user_id]]
        emotion_counts = {}
        
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
        most_common = max(emotion_counts.items(), key=lambda x: x[1])
        pattern_insight = f"Your dominant emotional pattern is {most_common[0]} ({most_common[1]} occurrences)"
        
        # Add insights based on patterns
        if most_common[0] == 'joy':
            pattern_insight += " - You maintain great positive energy!"
        elif most_common[0] == 'neutral':
            pattern_insight += " - You have excellent emotional balance."
        elif most_common[0] in ['sadness', 'anger', 'fear']:
            pattern_insight += " - These emotions often signal areas for growth and learning."
            
        return pattern_insight

    def process_command(self, message, user_id):
        """Process voice-like commands from typed messages"""
        lower_msg = message.lower().strip()
        
        # Hardware control commands
        if any(cmd in lower_msg for cmd in ['turn on led', 'led on', 'light on', 'activate led']):
            return {
                'type': 'command',
                'command': 'led_on',
                'message': '💡 Turning on LED lights...',
                'action': 'hardware'
            }
        
        elif any(cmd in lower_msg for cmd in ['turn off led', 'led off', 'light off', 'deactivate led']):
            return {
                'type': 'command', 
                'command': 'led_off',
                'message': '🌙 Turning off LED lights...',
                'action': 'hardware'
            }
        
        elif any(cmd in lower_msg for cmd in ['set brightness', 'change brightness', 'adjust brightness']):
            # Extract brightness level
            import re
            brightness_match = re.search(r'(\d+)%?', message)
            if brightness_match:
                brightness = int(brightness_match.group(1))
                return {
                    'type': 'command',
                    'command': 'set_brightness',
                    'message': f'🔆 Setting brightness to {brightness}%...',
                    'value': brightness,
                    'action': 'hardware'
                }
            else:
                return {
                    'type': 'response',
                    'message': '🔆 Please specify brightness level (0-100%). Try: "set brightness to 75%"'
                }
        
        elif any(cmd in lower_msg for cmd in ['calm mode', 'relax mode', 'chill mode']):
            return {
                'type': 'command',
                'command': 'calm_mode',
                'message': '🕊️ Activating calm mode with relaxing lighting...',
                'action': 'emotion_lighting'
            }
        
        elif any(cmd in lower_msg for cmd in ['energy mode', 'focus mode', 'work mode']):
            return {
                'type': 'command',
                'command': 'energy_mode', 
                'message': '⚡ Activating energy mode for focus and productivity...',
                'action': 'emotion_lighting'
            }
        
        elif any(cmd in lower_msg for cmd in ['party mode', 'fun mode', 'celebration']):
            return {
                'type': 'command',
                'command': 'party_mode',
                'message': '🎉 Activating party mode! Let the fun begin!',
                'action': 'emotion_lighting'
            }
        
        # Emotion analysis commands
        elif any(cmd in lower_msg for cmd in ['analyze emotion', 'scan emotion', 'how am i feeling', 'emotion check']):
            return {
                'type': 'command',
                'command': 'analyze_emotion',
                'message': '🧠 Analyzing your emotional state...',
                'action': 'emotion_analysis'
            }
        
        elif any(cmd in lower_msg for cmd in ['start camera', 'activate camera', 'begin analysis']):
            return {
                'type': 'command',
                'command': 'start_camera',
                'message': '📷 Starting neural vision system...',
                'action': 'camera_control'
            }
        
        elif any(cmd in lower_msg for cmd in ['stop camera', 'deactivate camera', 'end analysis']):
            return {
                'type': 'command',
                'command': 'stop_camera',
                'message': '📷 Stopping neural vision system...',
                'action': 'camera_control'
            }
        
        # System commands
        elif any(cmd in lower_msg for cmd in ['system status', 'health check', 'system diagnostic']):
            return {
                'type': 'command',
                'command': 'system_status',
                'message': '🔍 Running system diagnostic...',
                'action': 'system_info'
            }
        
        elif any(cmd in lower_msg for cmd in ['pi status', 'raspberry status', 'hardware status']):
            return {
                'type': 'command',
                'command': 'pi_status',
                'message': '🔌 Checking Pi system status...',
                'action': 'hardware_info'
            }
        
        elif any(cmd in lower_msg for cmd in ['sensor data', 'read sensors', 'temperature', 'humidity']):
            return {
                'type': 'command',
                'command': 'read_sensors',
                'message': '🌡️ Reading sensor data...',
                'action': 'sensor_data'
            }
        
        # Display commands
        elif any(cmd in lower_msg for cmd in ['display message', 'show message', 'oled display']):
            # Extract message text
            display_text = message
            for trigger in ['display message', 'show message', 'oled display']:
                if trigger in lower_msg:
                    display_text = message.split(trigger, 1)[1].strip()
                    break
            
            if display_text and len(display_text) > 3:
                return {
                    'type': 'command',
                    'command': 'update_display',
                    'message': f'📟 Displaying: "{display_text}"',
                    'value': display_text,
                    'action': 'display'
                }
            else:
                return {
                    'type': 'response',
                    'message': '📟 Please specify what to display. Try: "display message Hello World"'
                }
        
        elif any(cmd in lower_msg for cmd in ['clear display', 'blank screen', 'clear oled']):
            return {
                'type': 'command',
                'command': 'clear_display',
                'message': '📟 Clearing display...',
                'action': 'display'
            }
        
        # AI interaction commands
        elif any(cmd in lower_msg for cmd in ['pep talk', 'motivate me', 'encouragement']):
            return {
                'type': 'command',
                'command': 'pep_talk',
                'message': '💫 Generating personalized pep talk...',
                'action': 'ai_companion'
            }
        
        elif any(cmd in lower_msg for cmd in ['emotional insight', 'mood analysis', 'how am i doing']):
            return {
                'type': 'command',
                'command': 'emotional_insight',
                'message': '🔮 Generating emotional insights...',
                'action': 'ai_analysis'
            }
        
        # Not a command
        return None