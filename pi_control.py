#!/usr/bin/env python3
"""
To be on raspberry pi
pi_server.py - Enhanced Nexus AI Pi Server (WS281x + OLED + DHT)

OLED Layout (EXACTLY like test version):
- Header: Time (left) | Temp|Humidity (right) - font_header (10px)
- Center: Main messages with circular scrolling - font_mid (15px bold)
- Footer: Status notifications - font_footer (9px)
"""

import os
import time
import threading
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS  # Add CORS support

# ---------------------------
# Hardware config (user)
# ---------------------------
LED_COUNT = 16        # Number of LED pixels.
LED_PIN = 18          # GPIO pin for data (PWM capable)
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 200  # 0-255 default
LED_INVERT = False
LED_CHANNEL = 0

# ---------------------------
# Try imports (with fallback)
# ---------------------------
LED_AVAILABLE = False
OLED_AVAILABLE = False
DHT_AVAILABLE = False

try:
    from rpi_ws281x import PixelStrip, Color
    LED_AVAILABLE = True
except Exception as e:
    print(f"⚠️ rpi_ws281x not available: {e} — running in DEMO LED mode")

try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import sh1106, ssd1306
    from luma.core.render import canvas
    from PIL import ImageFont, ImageDraw
    OLED_AVAILABLE = True
except Exception as e:
    print(f"⚠️ OLED (luma) not available: {e} — running in DEMO OLED mode")

try:
    import board
    import adafruit_dht
    DHT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ DHT libs not available: {e} — running in DEMO sensor mode")

# ---------------------------
# Helpers
# ---------------------------
def map_percent_to_255(percent):
    try:
        p = float(percent)
    except Exception:
        p = 100.0
    p = max(0.0, min(100.0, p))
    return int(round(p * 255.0 / 100.0))

def clamp_rgb(t):
    return (max(0, min(255, int(t[0]))),
            max(0, min(255, int(t[1]))),
            max(0, min(255, int(t[2]))))

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    pos = pos % 256
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    pos -= 170
    return (0, pos * 3, 255 - pos * 3)

def interpolate_color(color1, color2, factor):
    """Interpolate between two RGB colors."""
    return (
        int(color1[0] + (color2[0] - color1[0]) * factor),
        int(color1[1] + (color2[1] - color1[1]) * factor),
        int(color1[2] + (color2[2] - color1[2]) * factor)
    )

# ---------------------------
# Enhanced Pi Hardware Controller
# ---------------------------
class EnhancedPiHardwareController:
    def __init__(self):
        # hardware objects
        self.strip = None
        self.device = None  # Fixed: changed from self.oled to self.device
        self.dht = None

        # state
        self.led_on_state = False
        self.led_brightness_percent = int(round(LED_BRIGHTNESS * 100.0 / 255.0))
        self.current_color = (255, 255, 255)
        self.current_message = "Hello! Smart Desk Buddy is Active"
        self.last_sensor_read = None
        self.sensor_data = {'temperature_c': 24, 'humidity': 52}  # Default demo values

        # animation control
        self.anim_thread = None
        self.anim_stop = threading.Event()

        # OLED state (EXACTLY like test version)
        self.scroll_x = 0
        self.msg_change_time = time.time()
        self.scroll_reset_timer = 0
        self.bottom_status = "System ready"
        self.bottom_status_expire = 0

        # emotion color palette (no emojis)
        self.emotion_colors = {
            'joy': (255, 255, 0),       # Bright yellow
            'excitement': (255, 165, 0), # Orange
            'sadness': (0, 100, 255),    # Deep blue
            'anger': (255, 0, 0),        # Pure red
            'fear': (128, 0, 128),       # Purple
            'surprise': (255, 255, 255), # White
            'neutral': (180, 180, 180),  # Soft grey
            'calm': (0, 255, 180),       # Aqua
            'focus': (0, 120, 255),      # Blue
            'energy': (255, 50, 0),      # Bright orange-red
            'party': (255, 0, 255),      # Magenta for party base
            'creative': (0, 255, 255),   # Cyan
            'sleepy': (50, 50, 150),     # Deep blue
            'love': (255, 105, 180),     # Hot pink
        }

        # Reduced randomness footer messages - more stable and relevant
        self.quotes = [
            "Smart Desk Buddy Active",
            "System operational",
            "Hardware ready",
            "Nexus AI Connected",
            "Monitoring sensors",
            "Awaiting commands"
        ]
        self.current_quote_index = 0  # Sequential instead of random

        # init hardware
        self._init_led()
        self._init_oled()
        self._init_dht()

        # startup sequence
        self._enhanced_startup_sequence()

        # start background tasks
        self._start_oled_updater()
        self._start_sensor_monitoring()

        print("✅ Enhanced PiHardwareController initialized")

    # ---------- Enhanced LED Control ----------
    def _init_led(self):
        if not LED_AVAILABLE:
            print("LED: DEMO mode (no rpi_ws281x).")
            return
        try:
            self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                                    LED_BRIGHTNESS, LED_CHANNEL)
            self.strip.begin()
            print("✅ LED strip initialized.")
        except Exception as e:
            print(f"⚠️ LED init failed: {e}")
            self.strip = None

    def _apply_brightness_hardware(self):
        if not self.strip:
            return
        try:
            val = map_percent_to_255(self.led_brightness_percent)
            self.strip.setBrightness(val)
            self.strip.show()
        except Exception as e:
            print("⚠️ setBrightness error:", e)

    def _set_brightness(self, percent):
        self.led_brightness_percent = int(max(0, min(100, int(percent))))
        if self.strip:
            self._apply_brightness_hardware()
        else:
            print(f"[DEMO] brightness set -> {self.led_brightness_percent}%")

    def _set_strip_color_all(self, rgb):
        rgb = clamp_rgb(rgb)
        if not self.strip:
            print(f"[DEMO] set color all -> {rgb}")
            self.led_on_state = True
            return True
        try:
            for i in range(LED_COUNT):
                self.strip.setPixelColor(i, Color(rgb[0], rgb[1], rgb[2]))
            self.strip.show()
            self.led_on_state = True
            return True
        except Exception as e:
            print("⚠️ set color all error:", e)
            return False

    def led_on(self):
        return self._set_strip_color_all(self.current_color)

    def led_off(self):
        if not self.strip:
            print("[DEMO] LEDs off")
            self.led_on_state = False
            return True
        try:
            for i in range(LED_COUNT):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
            self.led_on_state = False
            self._stop_animation()
            return True
        except Exception as e:
            print("⚠️ led_off error:", e)
            return False

    # ---------- Enhanced Animations ----------
    def _stop_animation(self):
        if self.anim_thread and self.anim_thread.is_alive():
            self.anim_stop.set()
            self.anim_thread.join(timeout=1.0)
        self.anim_stop.clear()
        self.anim_thread = None

    def _start_animation(self, target_fn, *args, **kwargs):
        self._stop_animation()
        self.anim_stop.clear()
        self.anim_thread = threading.Thread(target=target_fn, args=args, kwargs=kwargs, daemon=True)
        self.anim_thread.start()

    def set_emotion_lighting(self, emotion):
        e = str(emotion).lower() if emotion else "neutral"

        # Special animations
        if e == 'focus':
            self.current_color = self.emotion_colors['focus']
            self._start_animation(self._anim_focus_alternate)
            return True
        elif e == 'party':
            self._start_animation(self._anim_rainbow_party)
            return True
        elif e == 'surprise':
            self._start_animation(self._anim_surprise_flash)
            return True
        elif e == 'energy':
            self._start_animation(self._anim_energy_pulse)
            return True
        elif e == 'calm':
            self._start_animation(self._anim_calm_breathing)
            return True

        # Static colors with smooth transition
        color = self.emotion_colors.get(e, (255, 255, 255))
        self._stop_animation()
        self.current_color = color
        self._start_animation(self._anim_smooth_transition, color)
        return True

    def _anim_smooth_transition(self, target_color, duration=1.0):
        """Smoothly transition from current color to target color."""
        start_color = self.current_color
        steps = 30
        try:
            for i in range(steps):
                if self.anim_stop.is_set():
                    break
                factor = i / steps
                current = interpolate_color(start_color, target_color, factor)
                self._set_strip_color_all(current)
                time.sleep(duration / steps)
            if not self.anim_stop.is_set():
                self._set_strip_color_all(target_color)
        except Exception as e:
            print("Smooth transition error:", e)

    def _anim_focus_alternate(self):
        """Alternate between focus blue and white for concentration."""
        colors = [self.emotion_colors['focus'], (200, 200, 255)]
        try:
            while not self.anim_stop.is_set():
                for color in colors:
                    if self.anim_stop.is_set():
                        break
                    self._set_strip_color_all(color)
                    time.sleep(0.8)
        finally:
            if not self.anim_stop.is_set():
                self._set_strip_color_all(self.current_color)

    def _anim_rainbow_party(self):
        """Enhanced rainbow party animation."""
        try:
            pos = 0
            while not self.anim_stop.is_set():
                for i in range(LED_COUNT):
                    if self.anim_stop.is_set():
                        break
                    color = wheel((i * 256 // LED_COUNT + pos) % 256)
                    self.strip.setPixelColor(i, Color(color[0], color[1], color[2]))
                self.strip.show()
                pos = (pos + 2) % 256
                time.sleep(0.05)
        except Exception as e:
            print("Rainbow party error:", e)
        finally:
            if not self.anim_stop.is_set():
                self._set_strip_color_all(self.current_color)

    def _anim_surprise_flash(self):
        """Quick white flashes followed by color burst."""
        try:
            # Quick white flashes
            for _ in range(4):
                if self.anim_stop.is_set():
                    return
                self._set_strip_color_all((255, 255, 255))
                time.sleep(0.1)
                self.led_off()
                time.sleep(0.1)
            
            # Color burst
            if not self.anim_stop.is_set():
                colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
                for color in colors:
                    if self.anim_stop.is_set():
                        break
                    self._set_strip_color_all(color)
                    time.sleep(0.2)
                
                # Settle on surprise color
                if not self.anim_stop.is_set():
                    self._set_strip_color_all(self.emotion_colors['surprise'])
        except Exception as e:
            print("Surprise flash error:", e)

    def _anim_energy_pulse(self):
        """Pulsing energy animation."""
        try:
            base_color = self.emotion_colors['energy']
            while not self.anim_stop.is_set():
                for intensity in range(0, 101, 5):
                    if self.anim_stop.is_set():
                        break
                    factor = intensity / 100.0
                    color = (
                        int(base_color[0] * factor),
                        int(base_color[1] * factor),
                        int(base_color[2] * factor)
                    )
                    self._set_strip_color_all(color)
                    time.sleep(0.03)
                for intensity in range(100, -1, -5):
                    if self.anim_stop.is_set():
                        break
                    factor = intensity / 100.0
                    color = (
                        int(base_color[0] * factor),
                        int(base_color[1] * factor),
                        int(base_color[2] * factor)
                    )
                    self._set_strip_color_all(color)
                    time.sleep(0.03)
        except Exception as e:
            print("Energy pulse error:", e)

    def _anim_calm_breathing(self):
        """Slow breathing animation for calm state."""
        try:
            base_color = self.emotion_colors['calm']
            while not self.anim_stop.is_set():
                # Slow pulse
                for i in range(0, 101, 2):
                    if self.anim_stop.is_set():
                        break
                    factor = 0.3 + 0.7 * (i / 100.0)
                    color = (
                        int(base_color[0] * factor),
                        int(base_color[1] * factor),
                        int(base_color[2] * factor)
                    )
                    self._set_strip_color_all(color)
                    time.sleep(0.05)
                for i in range(100, -1, -2):
                    if self.anim_stop.is_set():
                        break
                    factor = 0.3 + 0.7 * (i / 100.0)
                    color = (
                        int(base_color[0] * factor),
                        int(base_color[1] * factor),
                        int(base_color[2] * factor)
                    )
                    self._set_strip_color_all(color)
                    time.sleep(0.05)
        except Exception as e:
            print("Calm breathing error:", e)

    # ---------- EXACT OLED UI from test version ----------
    def _init_oled(self):
        if not OLED_AVAILABLE:
            print("OLED: DEMO mode (no luma).")
            return
        try:
            serial = i2c(port=1, address=0x3C)
            self.device = sh1106(serial, width=128, height=64)
            
            # EXACT fonts from test version
            try:
                self.font_header = ImageFont.truetype("DejaVuSans.ttf", 10)
                self.font_mid = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
                self.font_footer = ImageFont.truetype("DejaVuSans.ttf", 9)
            except:
                # Fallback to default fonts
                self.font_header = ImageFont.load_default()
                self.font_mid = ImageFont.load_default()
                self.font_footer = ImageFont.load_default()
            
            print("✅ OLED initialized with EXACT test version fonts.")
        except Exception as e:
            print("⚠️ OLED init error:", e)
            self.device = None

    def _get_text_width(self, draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def display_message(self, message):
        """Set center message - main content area."""
        self.current_message = str(message)
        self.scroll_x = 0
        self.scroll_reset_timer = 0
        print(f"[OLED] Center message -> {self.current_message}")

    def set_bottom_status(self, text, duration=4.0):
        """Set bottom status - for notifications, success messages."""
        self.bottom_status = str(text)
        self.bottom_status_expire = time.time() + float(duration)
        print(f"[OLED] Bottom status -> {text} (for {duration}s)")

    def clear_display(self):
        self.current_message = ""
        self.bottom_status = "Display cleared"
        self.bottom_status_expire = time.time() + 3
        self.scroll_x = 0
        self.scroll_reset_timer = 0
        
        if not self.device:
            print("[DEMO] OLED cleared")
            return True
        
        try:
            with canvas(self.device) as draw:
                draw.rectangle(self.device.bounding_box, outline=0, fill=0)
            return True
        except Exception as e:
            print("⚠️ OLED clear error:", e)
            return False

    def _get_next_quote(self):
        """Get next quote sequentially with timing control"""
        # Only change quote every 10 seconds
        current_time = time.time()
        if not hasattr(self, 'last_quote_time'):
            self.last_quote_time = 0
        
        # If less than 10 seconds have passed, return current quote
        if current_time - self.last_quote_time < 60.0 and hasattr(self, 'current_quote'):
            return self.current_quote
        
        # Otherwise, get new quote and update timer
        quote = self.quotes[self.current_quote_index]
        self.current_quote_index = (self.current_quote_index + 1) % len(self.quotes)
        self.last_quote_time = current_time
        self.current_quote = quote
        return quote

    def _draw_oled_ui(self):
        """EXACT OLED UI from test version with header, center, footer layout."""
        if not self.device:
            # Demo output
            temp = self.sensor_data.get('temperature_c', 24)
            hum = self.sensor_data.get('humidity', 52)
            print(f"[OLED] {datetime.now().strftime('%H:%M')} | {temp}C {hum}% | {self.current_message[:20]}... | {self.bottom_status}")
            return

        try:
            with canvas(self.device) as draw:
                # ✅ HEADER (EXACT from test)
                now = datetime.now().strftime("%H:%M")
                draw.text((0, 0), now, font=self.font_header, fill=255)

                temp_hum = f"{int(self.sensor_data['temperature_c'])}°C {int(self.sensor_data['humidity'])}%"
                tw = self._get_text_width(draw, temp_hum, self.font_header)
                draw.text((128 - tw, 0), temp_hum, font=self.font_header, fill=255)

                # ✅ CURRENT MID MESSAGE (EXACT scrolling logic from test)
                text = self.current_message
                mid_y = 25
                text_w = self._get_text_width(draw, text, self.font_mid)

                # No scroll needed → center + time-based change
                if text_w <= 128:
                    draw.text(((128 - text_w) // 2, mid_y), text, font=self.font_mid, fill=255)
                else:
                    # Circular scrolling effect (EXACT from test)
                    # Draw the text twice for seamless looping
                    draw.text((self.scroll_x, mid_y), text, font=self.font_mid, fill=255)
                    draw.text((self.scroll_x + text_w + 30, mid_y), text, font=self.font_mid, fill=255)
                    
                    # Scroll to the left
                    self.scroll_x -= 1
                    
                    # Reset position when first copy is completely off screen
                    if self.scroll_x <= -text_w - 30:
                        self.scroll_x = 0
                        self.scroll_reset_timer += 1

                # ✅ FOOTER (EXACT from test but with SEQUENTIAL quotes)
                footer_text = self.bottom_status
                if time.time() > self.bottom_status_expire:
                    # Show sequential quote if no active status (reduced randomness)
                    footer_text = self._get_next_quote()
                
                fw = self._get_text_width(draw, footer_text, self.font_footer)
                draw.text(((128 - fw) // 2, 52), footer_text, font=self.font_footer, fill=255)

        except Exception as e:
            print("⚠️ OLED draw error:", e)

    def _start_oled_updater(self):
        """Background thread for OLED updates - EXACT timing from test."""
        def oled_loop():
            while True:
                try:
                    self._draw_oled_ui()
                    
                    # Clear expired status messages
                    if (self.bottom_status and 
                        self.bottom_status_expire > 0 and 
                        time.time() > self.bottom_status_expire):
                        
                        self.bottom_status = ""
                        self.bottom_status_expire = 0
                            
                except Exception as e:
                    print("OLED updater error:", e)
                
                time.sleep(0.04)  # EXACT timing from test version

        t = threading.Thread(target=oled_loop, daemon=True)
        t.start()

    # ---------- Sensor Management ----------
    def _init_dht(self):
        if not DHT_AVAILABLE:
            print("DHT: DEMO mode.")
            return
        try:
            self.dht = adafruit_dht.DHT22(board.D4)
            print("✅ DHT22 initialized.")
        except Exception as e:
            print("⚠️ DHT init failed:", e)
            self.dht = None

    def read_sensors(self):
        data = {
            'timestamp': datetime.now().isoformat(), 
            'temperature_c': None, 
            'humidity': None, 
            'success': False
        }
        
        if not self.dht:
            # Demo values with slight variation
            data.update({
                'temperature_c': round(24.0 + random.uniform(-1, 1), 1),
                'humidity': round(52.0 + random.uniform(-5, 5), 1),
                'success': True
            })
        else:
            try:
                t = self.dht.temperature
                h = self.dht.humidity
                if t is not None and h is not None:
                    data.update({
                        'temperature_c': round(float(t), 1),
                        'humidity': round(float(h), 1),
                        'success': True
                    })
            except Exception as e:
                print("⚠️ DHT read error:", e)
                data['error'] = str(e)
        
        self.sensor_data = data
        self.last_sensor_read = datetime.now()
        return data

    def _start_sensor_monitoring(self):
        def monitor():
            while True:
                try:
                    self.read_sensors()
                except Exception as e:
                    print("Sensor monitor error:", e)
                time.sleep(30)  # Read every 30 seconds
        t = threading.Thread(target=monitor, daemon=True)
        t.start()

    # ---------- System Status ----------
    def get_system_status(self):
        return {
            'led_available': LED_AVAILABLE and self.strip is not None,
            'oled_available': OLED_AVAILABLE and self.device is not None,
            'dht_available': DHT_AVAILABLE and self.dht is not None,
            'led_state': self.led_on_state,
            'led_brightness_percent': self.led_brightness_percent,
            'current_color': self.current_color,
            'current_message': self.current_message,
            'bottom_status': self.bottom_status,
            'last_sensor_read': self.last_sensor_read.isoformat() if self.last_sensor_read else None,
            'sensors': self.sensor_data,
            'emotions_available': list(self.emotion_colors.keys())
        }

    # ---------- Enhanced Startup Sequence ----------
    def _enhanced_startup_sequence(self):
        print("🚀 Running enhanced startup sequence...")
        
        # Set initial messages (EXACTLY like you wanted)
        self.display_message("Hello! Smart Desk Buddy is Active")
        self.set_bottom_status("System ready", duration=5)
        
        # LED test
        test_colors = [
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green  
            (0, 0, 255),      # Blue
            (255, 255, 255),  # White
        ]
        
        if self.strip:
            try:
                for color in test_colors:
                    self._set_strip_color_all(color)
                    time.sleep(0.3)
                self.led_off()
            except Exception as e:
                print("LED startup error:", e)
        else:
            print("[DEMO] LED color test")

        print("✅ Enhanced startup complete. System ready!")

# ---------------------------
# Flask App & Enhanced Routes
# ---------------------------
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

hw = EnhancedPiHardwareController()

@app.route('/')
def root():
    return jsonify({
        'status': 'success', 
        'message': 'Enhanced Nexus AI Pi Server Running',
        'layout': 'EXACT test version OLED UI',
        'hardware': {
            'led': LED_AVAILABLE,
            'oled': OLED_AVAILABLE, 
            'sensors': DHT_AVAILABLE
        }
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'success', 
        'timestamp': datetime.now().isoformat(), 
        'device': 'Raspberry Pi',
        'hardware': {
            'led': LED_AVAILABLE and hw.strip is not None,
            'oled': OLED_AVAILABLE and hw.device is not None,
            'sensors': DHT_AVAILABLE and hw.dht is not None
        }
    })

@app.route('/api/led/on', methods=['POST'])
def api_led_on():
    try:
        ok = hw.led_on()
        hw.set_bottom_status("LED turned on", duration=3)
        return jsonify({
            'status': 'success' if ok else 'error',
            'message': 'LED turned on successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/led/off', methods=['POST'])
def api_led_off():
    try:
        ok = hw.led_off()
        hw.set_bottom_status("LED turned off", duration=3)
        return jsonify({
            'status': 'success' if ok else 'error',
            'message': 'LED turned off successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/led/brightness', methods=['POST'])
def api_led_brightness():
    try:
        data = request.get_json(force=True, silent=True) or {}
        brightness = data.get('brightness')
        if brightness is None:
            return jsonify({'status': 'error', 'message': 'brightness parameter missing'}), 400
        
        hw._set_brightness(brightness)
        hw.set_bottom_status(f"Brightness {int(brightness)}%", duration=2)
        return jsonify({
            'status': 'success', 
            'brightness': hw.led_brightness_percent,
            'message': f'Brightness set to {brightness}%'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/led/emotion', methods=['POST'])
def api_led_emotion():
    try:
        data = request.get_json(force=True, silent=True) or {}
        emotion = data.get('emotion', 'neutral')
        ok = hw.set_emotion_lighting(emotion)
        hw.set_bottom_status(f"Emotion: {emotion}", duration=3)
        return jsonify({
            'status': 'success' if ok else 'error', 
            'emotion': emotion,
            'color': hw.emotion_colors.get(emotion.lower(), (255,255,255)),
            'message': f'Emotion lighting set to {emotion}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/display/update', methods=['POST'])
def api_display_update():
    try:
        data = request.get_json(force=True, silent=True) or {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({'status': 'error', 'message': 'message parameter missing'}), 400
        
        hw.display_message(message)
        hw.set_bottom_status("Message updated", duration=2)
        return jsonify({
            'status': 'success', 
            'message': message,
            'display_message': 'Message displayed successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/display/clear', methods=['POST'])
def api_display_clear():
    try:
        ok = hw.clear_display()
        return jsonify({
            'status': 'success' if ok else 'error',
            'message': 'Display cleared successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sensors/read', methods=['GET'])
def api_sensors_read():
    try:
        data = hw.read_sensors()
        return jsonify({
            'status': 'success', 
            'sensor_data': data,
            'message': 'Sensor data read successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def api_system_status():
    try:
        status = hw.get_system_status()
        return jsonify({
            'status': 'success', 
            'system_status': status,
            'message': 'System status retrieved successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/emotions/list', methods=['GET'])
def api_emotions_list():
    """Get list of available emotions and their colors."""
    try:
        return jsonify({
            'status': 'success',
            'emotions': hw.emotion_colors,
            'message': 'Emotions list retrieved successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reboot', methods=['POST'])
def api_reboot():
    try:
        hw.set_bottom_status("Rebooting system", duration=5)
        # Don't actually reboot in demo - just show message
        if LED_AVAILABLE or OLED_AVAILABLE or DHT_AVAILABLE:
            threading.Thread(target=lambda: (time.sleep(2), os.system("sudo reboot")), daemon=True).start()
            return jsonify({
                'status': 'success', 
                'message': 'Rebooting Pi...'
            })
        else:
            return jsonify({
                'status': 'success',
                'message': 'Reboot command received (demo mode)'
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ---------------------------
# Run Enhanced Server
# ---------------------------
if __name__ == '__main__':
    print("🚀 Starting Enhanced Nexus AI Pi Server")
    print(f"Hardware Status - LED: {LED_AVAILABLE}, OLED: {OLED_AVAILABLE}, DHT: {DHT_AVAILABLE}")
    print("Available emotions:", list(hw.emotion_colors.keys()))
    print("OLED UI: EXACT test version layout with sequential footer messages")
    print("CORS: Enabled for cross-origin requests")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        hw.led_off()
        print("✅ Cleanup complete")
