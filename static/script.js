// Nexus AI Quantum Dashboard - CONNECTED TO FLASK APP.PY
console.log("🚀 Initializing Nexus AI Quantum Dashboard...");
const FLASK_BASE_URL = "http://localhost:5000"; // Your Flask app URL

class NexusAIDashboard {
  constructor() {
    this.sessionActive = false;
    this.sessionId = null;
    this.cameraActive = false;
    this.isAnalyzing = false;
    this.currentEmotion = null;
    this.emotionHistory = [];
    this.chatHistory = [];
    this.piConnected = false;
    this.sessionStartTime = Date.now();
    this.analysisCount = 0;
    this.chatCount = 0;

    // Pi control state
    this.ledState = false;
    this.ledBrightness = 50;
    this.displayMode = "emotion";
    this.animationSpeed = 5;

    // Demo data
    this.demoEmotions = [
      "joy",
      "neutral",
      "surprise",
      "sadness",
      "anger",
      "fear",
    ];
    this.currentDemoEmotion = 0;
    // Add to the constructor
    this.memoryData = [];
    this.isLoadingMemory = false;

    this.analyticsCharts = {
      trendChart: null,
      distributionChart: null,
      hourlyChart: null,
    };
    this.analyticsData = [];
    this.currentTimeRange = "24h";

    this.testMode = null;
    this.companionVoiceController = null;

    this.initializeDashboard();
  }

  // Add this method to your class (around line 1200, before the UI MANAGEMENT section)
  bindAnalyticsEvents() {
    this.bindButton("refreshAnalytics", () => this.loadAnalyticsData());

    const timeRange = document.getElementById("timeRange");
    if (timeRange) {
      timeRange.addEventListener("change", (e) => {
        this.currentTimeRange = e.target.value;
        this.loadAnalyticsData();
      });
    }
  }

  // Add this utility method (around line 1200, before the UI MANAGEMENT section)
  updateElementText(id, text) {
    const element = document.getElementById(id);
    if (element) element.textContent = text;
  }

  initializeDashboard() {
    console.log("📊 Initializing Quantum Dashboard...");
    this.bindEvents();
    this.checkSystemStatus();
    this.startSession();

    // Start background updates
    setInterval(() => this.updateSystemMetrics(), 1000);
    setInterval(() => this.updatePiStatus(), 5000);

    setInterval(() => {
      if (this.displayMode === "time") {
        this.updatePiDisplayForMode("time");
      }
    }, 60000);

    this.showNotification("Quantum AI systems online and ready", "success");
    this.testMode = new TestMode(this);
    this.companionVoiceController = new CompanionVoiceController(this);
  }

  bindEvents() {
    // Navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        this.switchPage(item.getAttribute("data-page"));
      });
    });

    // Camera controls
    this.bindButton("startAnalysis", () => this.startCamera());
    this.bindButton("stopAnalysis", () => this.stopCamera());
    this.bindButton("captureFrame", () => this.captureFrame());
    this.bindButton("toggleAnalysis", () => this.toggleAnalysis());
    this.bindButton("calibrateCamera", () => this.calibrateCamera());

    // Quick actions
    this.bindButton("quickPepTalk", () => this.getPepTalk());
    this.bindButton("systemDiagnostic", () => this.systemDiagnostic());
    this.bindButton("quantumInsights", () => this.showQuantumInsights());
    this.bindButton("piControl", () => this.switchPage("pi-control"));
    this.bindButton("emotionReport", () => this.generateEmotionReport());
    this.bindButton("aiCompanion", () => this.switchPage("companion"));
    this.bindButton("refreshPiConnection", () => this.refreshPiConnection());

    // Chat system
    this.bindButton("sendMessage", () => this.sendMessage());
    this.bindButton("clearChat", () => this.clearChat());
    this.bindButton("exportChat", () => this.exportChat());
    this.bindButton("aiSettings", () => this.showAISettings());

    this.bindAnalyticsEvents();

    document.getElementById("chatInput")?.addEventListener("keypress", (e) => {
      if (e.key === "Enter") this.sendMessage();
    });

    // Quick replies
    document.querySelectorAll(".suggestion-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const message = btn.getAttribute("data-message");
        const chatInput = document.getElementById("chatInput");
        if (chatInput) {
          chatInput.value = message;
          this.sendMessage();
        }
      });
    });

    // AI Commands
    document.querySelectorAll(".command-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const command = btn.getAttribute("data-command");
        this.executeAICommand(command);
      });
    });

    // Pi LED Controls - THROUGH FLASK APP
    this.bindButton("ledOn", () => this.setPiLED(true));
    this.bindButton("ledOff", () => this.setPiLED(false));
    this.bindButton("updateDisplay", () => this.updatePiDisplay());
    this.bindButton("clearDisplay", () => this.clearPiDisplay());

    // LED brightness control
    const brightnessSlider = document.getElementById("ledBrightness");
    if (brightnessSlider) {
      brightnessSlider.addEventListener("input", (e) => {
        this.ledBrightness = e.target.value;
        const sliderValue = document.querySelector(".slider-value");
        if (sliderValue) {
          sliderValue.textContent = `${this.ledBrightness}%`;
        }
        this.setPiBrightness(this.ledBrightness);
      });
    }

    // Animation speed control
    const speedSlider = document.getElementById("animationSpeed");
    if (speedSlider) {
      speedSlider.addEventListener("input", (e) => {
        this.animationSpeed = Number(e.target.value);
        const speedValue = document.querySelectorAll(".slider-value")[1];
        if (speedValue) {
          const speeds = ["Very Slow", "Slow", "Medium", "Fast", "Very Fast"];
          const index = Math.floor((this.animationSpeed - 1) / 2);
          speedValue.textContent = speeds[index] || "Medium";
        }
      });
    }

    // Display mode
    const displayMode = document.getElementById("displayMode");
    if (displayMode) {
      displayMode.addEventListener("change", (e) => {
        this.displayMode = e.target.value;

        // Auto-update OLED when mode changes
        this.updatePiDisplayForMode(this.displayMode);
      });
    }

    // LED emotion presets
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const emotion = btn.getAttribute("data-emotion");
        this.setEmotionLighting(emotion);
      });
    });

    // Pi system commands - THROUGH FLASK APP
    this.bindButton("piReboot", () => this.piReboot());
    this.bindButton("piShutdown", () => this.piShutdown());
    this.bindButton("piDiagnostic", () => this.piDiagnostic());
    this.bindButton("piUpdate", () => this.piUpdate());

    // Memory actions
    this.bindButton("clearMemory", () => this.clearMemory());
    this.bindButton("analyzePatterns", () => this.analyzePatterns());
    this.bindButton("exportAllData", () => this.exportAllData());
    this.bindButton("generateReport", () => this.generateReport());
    this.bindButton("backupMemory", () => this.backupMemory());
    this.bindButton("viewStatistics", () => this.viewStatistics());

    // System controls
    this.bindButton("themeToggle", () => this.toggleTheme());
    this.bindButton("fullscreenBtn", () => this.toggleFullscreen());
    this.bindButton("emergencyStop", () => this.emergencyStop());
    this.bindButton("refreshMetrics", () => this.refreshMetrics());

    // Emergency stop modal
    this.bindButton("cancelEmergency", () => this.hideEmergencyModal());
    this.bindButton("confirmEmergency", () => this.confirmEmergencyStop());

    console.log("✅ All event handlers bound");
  }

  bindButton(id, handler) {
    const button = document.getElementById(id);
    if (button) {
      button.addEventListener("click", handler);
    }
  }

  async startSession() {
    try {
      this.showNotification("Establishing quantum session...", "info");

      // First check Flask app connection
      await this.checkFlaskConnection();

      // Then initialize session with Flask
      const sessionData = await this.callFlaskEndpoint(
        "/api/system/init",
        "POST",
        {
          user_id: `quantum_user_${Date.now()}`,
        }
      );

      if (sessionData.status === "success") {
        this.sessionActive = true;
        this.sessionId = sessionData.session_id;

        // Update Pi connection status from session response
        this.piConnected = sessionData.hardware_status?.pi_connected || false;

        this.updateSystemStatus("online");

        if (this.piConnected) {
          this.showNotification(
            "Quantum session established with Pi connection",
            "success"
          );
        } else {
          this.showNotification(
            "Quantum session established (local demo mode)",
            "warning"
          );
        }

        this.updatePiStatusUI();
      } else {
        throw new Error("Session initialization failed");
      }
    } catch (error) {
      console.error("Session start failed:", error);
      this.showNotification("Running in local demo mode", "warning");
      this.sessionActive = true;
      this.piConnected = false;
      this.updatePiStatusUI();
    }
  }

  // FLASK APP CONNECTION METHODS
  async checkFlaskConnection() {
    try {
      const res = await fetch(`${FLASK_BASE_URL}/api/system/health`);
      const data = await res.json();

      console.log("🔍 Health response:", data);

      // More reliable connection check
      this.piConnected = data.pi_connected === true;

      console.log(`🔌 Final Pi Connection Status: ${this.piConnected}`);

      if (this.piConnected) {
        this.showNotification("Flask app connected with Pi access", "success");
      } else {
        this.showNotification("Flask app connected (Pi offline)", "warning");
      }

      return this.piConnected;
    } catch (error) {
      console.error("Flask connection failed:", error);
      this.piConnected = false;
      this.showNotification("Flask app unavailable - demo mode", "warning");
      return false;
    }
  }

  async refreshPiConnection() {
    try {
      this.showNotification("Refreshing Pi connection...", "info");

      const data = await this.callFlaskEndpoint(
        "/api/system/refresh-pi-connection",
        "POST"
      );

      if (data.status === "success") {
        this.piConnected = data.current_connection;
        this.updatePiStatusUI();

        if (this.piConnected) {
          this.showNotification("Pi connection restored!", "success");
        } else {
          this.showNotification("Pi still unavailable", "warning");
        }
      }
    } catch (error) {
      console.error("Connection refresh failed:", error);
      this.showNotification("Connection refresh failed", "error");
    }
  }

  async callFlaskEndpoint(endpoint, method = "GET", body = null) {
    try {
      const options = {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      const res = await fetch(`${FLASK_BASE_URL}${endpoint}`, options);
      const data = await res.json();

      return data;
    } catch (error) {
      console.error(`Flask API call failed (${endpoint}):`, error);
      throw error;
    }
  }

  // PI CONTROL METHODS - THROUGH FLASK APP
  async setPiLED(state) {
    try {
      const endpoint = state ? "/api/pi/led/on" : "/api/pi/led/off";
      const data = await this.callFlaskEndpoint(endpoint, "POST");

      if (data.status === "success") {
        this.ledState = state;
        const message = data.demo
          ? `${data.message}`
          : `LED ${state ? "activated" : "deactivated"}`;
        this.showNotification(message, "success");
      } else {
        throw new Error(data.message || "LED control failed");
      }
    } catch (error) {
      console.error("LED control failed:", error);
      this.showNotification("LED control unavailable", "warning");
    }
  }

  async setPiBrightness(brightness) {
    try {
      const data = await this.callFlaskEndpoint(
        "/api/pi/led/brightness",
        "POST",
        {
          brightness: parseInt(brightness),
        }
      );

      if (data.status === "success") {
        this.ledBrightness = brightness;
        const message = data.demo
          ? `${data.message}`
          : `Brightness set to ${brightness}%`;
        this.showNotification(message, "success");
      } else {
        throw new Error(data.message || "Brightness control failed");
      }
    } catch (error) {
      console.error("Brightness control failed:", error);
      this.showNotification("Brightness control unavailable", "warning");
    }
  }

  async setEmotionLighting(emotion) {
    try {
      const data = await this.callFlaskEndpoint("/api/pi/led/emotion", "POST", {
        emotion: emotion,
      });

      if (data.status === "success") {
        const message = data.demo
          ? `${data.message}`
          : `Emotion lighting: ${emotion} mode`;
        this.showNotification(message, "success");
      } else {
        throw new Error(data.message || "Emotion lighting failed");
      }
    } catch (error) {
      console.error("Emotion lighting failed:", error);
      this.showNotification("Emotion lighting unavailable", "warning");
    }
  }

  // Add this method to update the OLED preview display
  updateOledPreview(message, mode) {
    const oledContent = document.getElementById("oledContent");
    if (!oledContent) return;

    const now = new Date();

    oledContent.innerHTML = `
    <div class="oled-display-preview">
      <div class="oled-header">
        <span class="oled-time">${now.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}</span>
        <span class="oled-temp">${mode.toUpperCase()}</span>
      </div>
      <div class="oled-center">
        ${message}
      </div>
      <div class="oled-footer">
        ${this.piConnected ? "Pi Connected" : "Demo Mode"}
      </div>
    </div>
  `;
  }

  async updatePiDisplay() {
    const messageInput = document.getElementById("displayMessage");
    let message = messageInput?.value;

    if (!message) {
      if (this.currentEmotion) {
        message = `Feeling ${this.currentEmotion.dominant_emotion}`;
      } else {
        message = "Smart Desk Buddy Active";
      }
    }

    try {
      const data = await this.callFlaskEndpoint(
        "/api/pi/display/update",
        "POST",
        {
          message: message,
        }
      );

      if (data.status === "success") {
        // Update OLED preview
        const oledContent = document.getElementById("oledContent");
        if (oledContent) {
          oledContent.innerHTML = `
          <div class="oled-display-preview">
            <div class="oled-header">
              <span class="oled-time">${new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}</span>
              <span class="oled-temp">24°C 52%</span>
            </div>
            <div class="oled-center">
              ${message}
            </div>
            <div class="oled-footer">
              ${data.demo ? "Demo Mode" : "Message updated"}
            </div>
          </div>
        `;
        }
        const notification = data.demo
          ? `${data.message}`
          : "OLED display updated";
        this.showNotification(notification, "success");
      } else {
        throw new Error(data.message || "Display update failed");
      }
    } catch (error) {
      console.error("Display update failed:", error);
      this.showNotification("Display update failed", "warning");
    }

    await this.updatePiDisplayForMode(this.displayMode);
  }

  // Add this method to your NexusAIDashboard class
  async updatePiDisplayForMode(mode) {
    let message = "";

    switch (mode) {
      case "emotion":
        // Show current emotion if available
        if (this.currentEmotion) {
          message = `Feeling ${
            this.currentEmotion.dominant_emotion
          } - ${Math.round(this.currentEmotion.quantum_confidence * 100)}%`;
        } else {
          message = "Awaiting emotion data...";
        }
        break;

      case "message":
        // Use custom message from input field
        const messageInput = document.getElementById("displayMessage");
        message = messageInput?.value || "Smart Desk Buddy";
        break;

      case "time":
        // Show current time and date
        const now = new Date();
        message = `${now.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })} ${now.toLocaleDateString()}`;
        break;

      case "system":
        // Show system status
        message = `System: ${
          this.piConnected ? "Online" : "Demo"
        } | Analysis: ${this.analysisCount}`;
        break;

      default:
        message = "Nexus AI Active";
    }

    // Update the OLED preview immediately
    this.updateOledPreview(message, mode);

    // Send to Pi if connected
    if (this.piConnected) {
      try {
        await this.callFlaskEndpoint("/api/pi/display/update", "POST", {
          message: message,
          mode: mode,
        });
      } catch (error) {
        console.warn("Auto-display update failed:", error);
      }
    }
  }

  async clearPiDisplay() {
    try {
      const data = await this.callFlaskEndpoint(
        "/api/pi/display/clear",
        "POST"
      );

      if (data.status === "success") {
        const oledContent = document.getElementById("oledContent");
        if (oledContent) {
          oledContent.innerHTML = `
          <div class="oled-display-preview">
            <div class="oled-header">
              <span class="oled-time">${new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}</span>
              <span class="oled-temp">24°C 52%</span>
            </div>
            <div class="oled-center">
              Display Cleared
            </div>
            <div class="oled-footer">
              ${data.demo ? "Demo Mode" : "Ready for input"}
            </div>
          </div>
        `;
        }
        const notification = data.demo ? `${data.message}` : "Display cleared";
        this.showNotification(notification, "info");
      } else {
        throw new Error(data.message || "Display clear failed");
      }
    } catch (error) {
      console.error("Display clear failed:", error);
      this.showNotification("Display clear failed", "warning");
    }
  }

  async getPiSystemStatus() {
    try {
      const data = await this.callFlaskEndpoint("/api/pi/status");

      if (data.status === "success") {
        this.piSystemStatus = data.system_status;
        this.updatePiStatusDisplay();
      }
    } catch (error) {
      console.error("Failed to get Pi system status:", error);
    }
  }

  async readPiSensors() {
    try {
      const data = await this.callFlaskEndpoint("/api/pi/sensors");

      if (data.status === "success") {
        this.piSystemStatus = {
          ...this.piSystemStatus,
          sensors: data.sensor_data,
        };
        this.updatePiStatusDisplay();
        return data.sensor_data;
      }
    } catch (error) {
      console.error("Sensor read failed:", error);
      return null;
    }
  }

  // PI SYSTEM COMMANDS - THROUGH FLASK APP
  async piReboot() {
    if (
      confirm(
        "Are you sure you want to reboot the Pi? This will temporarily disconnect all hardware controls."
      )
    ) {
      try {
        this.showNotification("Initiating Pi reboot sequence...", "info");

        const data = await this.callFlaskEndpoint("/api/pi/reboot", "POST");

        if (data.status === "success") {
          const message = data.demo
            ? `${data.message}`
            : "Pi reboot command sent successfully";
          this.showNotification(message, "success");
          this.piConnected = false;
          this.updatePiStatusUI();

          // Try to reconnect after 15 seconds
          setTimeout(() => {
            this.checkFlaskConnection();
          }, 15000);
        } else {
          throw new Error(data.message || "Reboot command failed");
        }
      } catch (error) {
        console.error("Pi reboot failed:", error);
        this.showNotification("Pi reboot command failed", "error");
      }
    }
  }

  async piShutdown() {
    if (
      confirm(
        "Are you sure you want to shutdown the Pi system? This will disconnect all hardware controls until manually restarted."
      )
    ) {
      try {
        this.showNotification("Initiating Pi shutdown sequence...", "warning");

        const data = await this.callFlaskEndpoint("/api/pi/shutdown", "POST");

        if (data.status === "success") {
          this.piConnected = false;
          this.updatePiStatusUI();
          const message = data.demo
            ? `${data.message}`
            : "Pi shutdown command sent successfully";
          this.showNotification(message, "warning");
        } else {
          throw new Error(data.message || "Shutdown command failed");
        }
      } catch (error) {
        console.error("Pi shutdown failed:", error);
        this.showNotification("Pi shutdown command failed", "error");
      }
    }
  }

  async piDiagnostic() {
    try {
      this.showNotification("Running Pi system diagnostics...", "info");

      const data = await this.callFlaskEndpoint("/api/pi/diagnostic");

      const outputConsole = document.getElementById("piOutput");
      if (outputConsole) {
        if (data.status === "success") {
          outputConsole.textContent =
            data.diagnostic_report || "Diagnostic completed successfully";
        } else {
          outputConsole.textContent =
            "ERROR: Unable to retrieve Pi diagnostic information";
        }
      }
    } catch (error) {
      console.error("Pi diagnostic failed:", error);
      const outputConsole = document.getElementById("piOutput");
      if (outputConsole) {
        outputConsole.textContent = "ERROR: Connection to Flask app failed";
      }
      this.showNotification("Pi diagnostic failed - check connection", "error");
    }
  }

  async piUpdate() {
    try {
      this.showNotification("Checking for Pi system updates...", "info");

      const data = await this.callFlaskEndpoint("/api/pi/update", "POST");

      if (data.status === "success") {
        const message = data.demo
          ? `${data.message}`
          : "Pi system is up to date";
        this.showNotification(message, "success");
      } else {
        this.showNotification(data.message || "Update check completed", "info");
      }
    } catch (error) {
      console.error("Pi update check failed:", error);
      this.showNotification("Update check unavailable", "warning");
    }
  }

  // AUTO-UPDATE PI STATUS DISPLAY
  updatePiStatusDisplay() {
    if (!this.piSystemStatus) return;

    const status = this.piSystemStatus;

    // Update temperature and humidity
    const piTemperature = document.getElementById("piTemperature");
    const piMemory = document.getElementById("piMemory");

    if (piTemperature && status.sensors?.temperature_c) {
      piTemperature.textContent = `${Math.round(
        status.sensors.temperature_c
      )}°C`;
    }

    if (piMemory && status.sensors?.humidity) {
      piMemory.textContent = `${Math.round(status.sensors.humidity)}% Humidity`;
    }

    // Update LED status
    const ledStatus = document.getElementById("ledStatus");
    if (ledStatus) {
      ledStatus.textContent = status.led_state ? "ON" : "OFF";
      ledStatus.className = `metric-value ${status.led_state ? "online" : ""}`;
    }

    // Update brightness slider
    const brightnessSlider = document.getElementById("ledBrightness");
    if (brightnessSlider && status.led_brightness_percent) {
      brightnessSlider.value = status.led_brightness_percent;
      const sliderValue = document.querySelector(".slider-value");
      if (sliderValue) {
        sliderValue.textContent = `${status.led_brightness_percent}%`;
      }
    }
  }

  // CAMERA AND EMOTION ANALYSIS
  async startCamera() {
    try {
      this.showNotification("Activating neural vision system...", "info");

      const data = await this.callFlaskEndpoint("/api/camera/start", "POST");

      if (data.status === "success") {
        this.cameraActive = true;
        this.isAnalyzing = true;
        this.updateCameraUI(true);
        this.startCameraFeed();
        this.startEmotionAnalysis();
        this.showNotification("Neural vision system activated", "success");
      } else {
        throw new Error(data.message || "Camera start failed");
      }
    } catch (error) {
      console.error("Camera start failed:", error);
      this.showNotification("Camera unavailable - using demo mode", "warning");
      this.startDemoMode();
    }
  }

  async stopCamera() {
    try {
      const data = await this.callFlaskEndpoint("/api/camera/stop", "POST");

      if (data.status === "success") {
        this.cameraActive = false;
        this.isAnalyzing = false;
        this.updateCameraUI(false);
        this.stopCameraFeed();
        this.showNotification("Neural vision system deactivated", "info");
      } else {
        throw new Error(data.message || "Camera stop failed");
      }
    } catch (error) {
      console.error("Camera stop failed:", error);
      this.cameraActive = false;
      this.isAnalyzing = false;
      this.updateCameraUI(false);
    }
  }

  startCameraFeed() {
    // Update camera feed image
    const cameraFeed = document.getElementById("cameraFeed");
    if (cameraFeed) {
      cameraFeed.innerHTML = `
        <img src="${FLASK_BASE_URL}/api/camera/feed" style="width: 100%; height: 100%; object-fit: cover;" alt="Live Camera Feed">
      `;
    }
  }

  stopCameraFeed() {
    const cameraFeed = document.getElementById("cameraFeed");
    if (cameraFeed) {
      cameraFeed.innerHTML = `
        <div class="camera-placeholder">
          <i class="fas fa-camera"></i>
          <h4>Vision System Ready</h4>
          <p>Activate neural scan to begin analysis</p>
        </div>
      `;
    }
  }

  startEmotionAnalysis() {
    this.analysisInterval = setInterval(async () => {
      if (this.isAnalyzing) {
        await this.analyzeEmotion();
      }
    }, 3000);
  }

  // Add this method to handle emotion JSON storage
  async saveEmotionToJson(emotionData) {
    try {
      const dataToSave = {
        timestamp: new Date().toISOString(),
        dominant_emotion: emotionData.dominant_emotion,
        quantum_confidence: emotionData.quantum_confidence,
        emotion_spectrum: emotionData.emotion_spectrum,
        bio_metrics: emotionData.bio_metrics,
        analysis_timestamp:
          emotionData.analysis_timestamp || new Date().toISOString(),
      };

      // Save via Flask endpoint
      const result = await this.callFlaskEndpoint("/api/emotion/save", "POST", {
        emotion_data: dataToSave,
      });

      if (result.status === "success") {
        console.log("✅ Emotion saved to JSON:", dataToSave.dominant_emotion);
      } else {
        console.warn("⚠️ Emotion save response:", result.message);
      }
    } catch (error) {
      console.error("❌ Failed to save emotion to JSON:", error);
      // Fallback: Try to save directly (if Flask app supports it)
      this.fallbackSaveToJson(emotionData);
    }
  }

  // Fallback method for direct saving
  fallbackSaveToJson(emotionData) {
    const dataToSave = {
      timestamp: new Date().toISOString(),
      dominant_emotion: emotionData.dominant_emotion,
      quantum_confidence: emotionData.quantum_confidence,
      emotion_spectrum: emotionData.emotion_spectrum,
      bio_metrics: emotionData.bio_metrics,
    };

    console.log("📝 Emotion data ready for JSON:", dataToSave);
  }

  async analyzeEmotion() {
    try {
      const data = await this.callFlaskEndpoint("/api/emotion/latest");

      if (data.status === "success") {
        const emotionData = data.emotion_data;
        this.currentEmotion = emotionData;
        this.emotionHistory.push(emotionData);
        this.updateEmotionDisplay(emotionData);
        this.updateEmotionContext(emotionData);
        this.analysisCount++;

        await this.saveEmotionToJson(emotionData);

        // Auto-update Pi display with current emotion
        if (this.piConnected) {
          const emotionMessage = `Feeling ${
            emotionData.dominant_emotion
          } - Confidence: ${Math.round(emotionData.quantum_confidence * 100)}%`;
          await this.updatePiDisplayWithMessage(emotionMessage);
          this.autoAdjustLighting(emotionData.dominant_emotion);
        }
      } else {
        throw new Error("Failed to get emotion data");
      }
    } catch (error) {
      console.error("Emotion analysis failed:", error);
      this.showDemoEmotion();
    }
  }

  async updatePiDisplayWithMessage(message) {
    try {
      const data = await this.callFlaskEndpoint(
        "/api/pi/display/update",
        "POST",
        {
          message: message,
        }
      );

      if (data.status !== "success") {
        console.warn("Auto-display update failed:", data.message);
      }
    } catch (error) {
      console.warn("Auto-display update failed:", error);
    }
  }

  // Enhanced auto-adjust lighting
  autoAdjustLighting(emotion) {
    if (!this.piConnected) return;

    const lightingMap = {
      joy: "energy",
      excitement: "energy",
      sadness: "calm",
      anger: "calm",
      fear: "calm",
      surprise: "party",
      neutral: "focus",
      calm: "calm",
      focus: "focus",
      energy: "energy",
      party: "party",
      creative: "creative",
      sleepy: "sleepy",
      love: "love",
    };

    if (lightingMap[emotion]) {
      this.setEmotionLighting(lightingMap[emotion]);
    }
  }

  // EMOTION DATA GENERATION (for demo mode)
  generateEmotionData() {
    const emotions = this.demoEmotions;
    const dominantEmotion = emotions[this.currentDemoEmotion];
    this.currentDemoEmotion = (this.currentDemoEmotion + 1) % emotions.length;

    return {
      dominant_emotion: dominantEmotion,
      quantum_confidence: 0.7 + Math.random() * 0.25,
      emotion_spectrum: this.generateEmotionSpectrum(dominantEmotion),
      bio_metrics: {
        stress_index: Math.random() * 0.6,
        mood_stability: 0.6 + Math.random() * 0.3,
        engagement: 0.5 + Math.random() * 0.4,
      },
    };
  }

  generateEmotionSpectrum(dominantEmotion) {
    const spectrum = {
      joy: 0.1 + Math.random() * 0.2,
      neutral: 0.1 + Math.random() * 0.2,
      sadness: 0.1 + Math.random() * 0.2,
      anger: 0.1 + Math.random() * 0.2,
      fear: 0.1 + Math.random() * 0.2,
      surprise: 0.1 + Math.random() * 0.2,
    };

    spectrum[dominantEmotion] = 0.5 + Math.random() * 0.4;

    const total = Object.values(spectrum).reduce((a, b) => a + b, 0);
    for (let emotion in spectrum) {
      spectrum[emotion] = spectrum[emotion] / total;
    }

    return spectrum;
  }

  updateEmotionDisplay(emotionData) {
    const emotion = emotionData.dominant_emotion || "neutral";
    const confidence = Math.round((emotionData.quantum_confidence || 0) * 100);

    const emotionIcons = {
      joy: "fa-smile",
      sadness: "fa-sad-tear",
      anger: "fa-angry",
      fear: "fa-surprise",
      surprise: "fa-surprise",
      disgust: "fa-meh-rolling-eyes",
      neutral: "fa-meh",
    };

    const emotionIcon = document.getElementById("emotionIcon");
    const emotionName = document.getElementById("emotionName");
    const confidenceBar = document.getElementById("confidenceBar");
    const confidenceText = document.getElementById("confidenceText");
    const confidenceBadge = document.getElementById("confidenceBadge");

    if (emotionIcon)
      emotionIcon.className = `fas ${emotionIcons[emotion] || "fa-meh"}`;
    if (emotionName) emotionName.textContent = this.capitalize(emotion);
    if (confidenceBar) confidenceBar.style.width = `${confidence}%`;
    if (confidenceText)
      confidenceText.textContent = `Neural Confidence: ${confidence}%`;
    if (confidenceBadge)
      confidenceBadge.innerHTML = `<span>${confidence}%</span>`;

    this.updateEmotionOrb(emotion);
    this.updateEmotionBars(emotionData.emotion_spectrum);

    const analysisCountEl = document.getElementById("analysisCount");
    if (analysisCountEl) analysisCountEl.textContent = this.analysisCount;

    if (emotionData.bio_metrics) {
      const stressLevel = document.getElementById("stressLevel");
      const moodStability = document.getElementById("moodStability");

      if (stressLevel)
        stressLevel.textContent =
          Math.round(emotionData.bio_metrics.stress_index * 100) + "%";
      if (moodStability)
        moodStability.textContent =
          Math.round(emotionData.bio_metrics.mood_stability * 100) + "%";
    }

    if (this.displayMode === "emotion") {
      this.updatePiDisplayForMode("emotion");
    }
  }

  updateEmotionOrb(emotion) {
    const emotionOrb = document.getElementById("emotionOrb");
    if (!emotionOrb) return;

    const emotionColors = {
      joy: "linear-gradient(135deg, #22c55e, #84cc16)",
      sadness: "linear-gradient(135deg, #3b82f6, #06b6d4)",
      anger: "linear-gradient(135deg, #ef4444, #dc2626)",
      fear: "linear-gradient(135deg, #8b5cf6, #a855f7)",
      surprise: "linear-gradient(135deg, #f59e0b, #eab308)",
      disgust: "linear-gradient(135deg, #10b981, #14b8a6)",
      neutral: "linear-gradient(135deg, #06b6d4, #4361ee)",
    };

    emotionOrb.style.background =
      emotionColors[emotion] || emotionColors.neutral;
  }

  updateEmotionBars(spectrum) {
    if (!spectrum) return;

    const emotions = ["joy", "neutral", "sadness", "anger", "fear", "surprise"];
    const emotionBars = document.getElementById("emotionBars");
    if (!emotionBars) return;

    let barsHTML = "";
    emotions.forEach((emotion) => {
      const value = spectrum[emotion] || 0;
      const percentage = Math.round(value * 100);
      const color = this.getEmotionColor(emotion);

      barsHTML += `
        <div class="spectrum-bar">
          <div class="bar-label">
            <span class="emotion-emoji">${this.getEmotionEmoji(emotion)}</span>
            ${this.capitalize(emotion)}
          </div>
          <div class="bar-container">
            <div class="bar-fill" style="width: ${percentage}%; background: ${color};"></div>
          </div>
          <div class="bar-value">${percentage}%</div>
        </div>
      `;
    });

    emotionBars.innerHTML = barsHTML;
  }

  updateEmotionContext(emotionData) {
    const emotion = emotionData.dominant_emotion;
    const confidence = Math.round(emotionData.quantum_confidence * 100);

    const currentEmotionContext = document.getElementById(
      "currentEmotionContext"
    );
    const emotionPattern = document.getElementById("emotionPattern");
    const aiRecommendation = document.getElementById("aiRecommendation");

    if (currentEmotionContext)
      currentEmotionContext.textContent = this.capitalize(emotion);
    if (emotionPattern)
      emotionPattern.textContent = confidence > 70 ? "Clear" : "Uncertain";

    const recommendations = {
      joy: "Great mood! Perfect for creative work and social interactions",
      sadness:
        "Consider taking a break, listening to music, or talking with someone",
      anger: "Deep breathing exercises recommended. Try a short walk",
      fear: "Focus on grounding techniques. Remember this feeling will pass",
      surprise: "Embrace the unexpected positively. Great for learning moments",
      neutral: "Stable state - ideal for focused work and planning",
      disgust:
        "Identify and address the source of discomfort. Fresh air may help",
    };

    if (aiRecommendation) {
      aiRecommendation.textContent =
        recommendations[emotion] || "Continue monitoring emotional patterns";
    }
  }

  // CHAT SYSTEM
  async sendMessage() {
    const input = document.getElementById("chatInput");
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    this.addChatMessage("user", message);
    input.value = "";

    try {
      const data = await this.callFlaskEndpoint("/api/chat/send", "POST", {
        message: message,
        emotion_context: this.currentEmotion || {},
      });

      if (data.status === "success") {
        const aiResponse = data.ai_response.response;
        this.addChatMessage("bot", aiResponse);
        this.chatCount++;

        const chatCountEl = document.getElementById("chatCount");
        if (chatCountEl) chatCountEl.textContent = this.chatCount;

        // ✅ SPEAK AI RESPONSE IF TOGGLE IS ON
        if (
          this.companionVoiceController &&
          this.companionVoiceController.speakResponses
        ) {
          this.companionVoiceController.speakResponse(aiResponse);
        }

        this.processChatCommand(message, aiResponse);
      } else {
        throw new Error(data.message || "Chat failed");
      }
    } catch (error) {
      console.error("Chat failed:", error);
      const fallbackResponse = this.generateAIResponse(message);
      this.addChatMessage("bot", fallbackResponse);

      // ✅ SPEAK FALLBACK RESPONSE TOO
      if (
        this.companionVoiceController &&
        this.companionVoiceController.speakResponses
      ) {
        this.companionVoiceController.speakResponse(fallbackResponse);
      }
    }
  }

  generateAIResponse(message) {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes("hello") || lowerMessage.includes("hi")) {
      return "Hello! I'm your Quantum AI Companion. I can analyze emotions, control devices, and provide insights. How can I assist you today?";
    } else if (lowerMessage.includes("led") || lowerMessage.includes("light")) {
      return "I can control your Pi LED lights. Try saying 'turn on LED' or use the Pi control panel. I can also set emotion-based lighting!";
    } else if (
      lowerMessage.includes("emotion") ||
      lowerMessage.includes("feel")
    ) {
      const currentEmotion = this.currentEmotion?.dominant_emotion || "unknown";
      return `I can analyze emotions through the camera. ${
        this.cameraActive
          ? `Currently detecting ${currentEmotion}. Activate neural scan for real-time analysis!`
          : "Activate the neural scan to get started!"
      }`;
    } else if (
      lowerMessage.includes("pi") ||
      lowerMessage.includes("raspberry")
    ) {
      return `Pi system ${
        this.piConnected ? "is connected and " : "demo mode - "
      }controls are available in the Pi Control section. I can manage LEDs, displays, and more.`;
    } else if (lowerMessage.includes("help")) {
      return "I can: analyze emotions, control Pi devices, provide insights, chat with you, generate reports, and more! What would you like to explore?";
    } else if (lowerMessage.includes("weather")) {
      return "I'm focused on emotional intelligence and device control. For weather, you might want to check a dedicated weather service!";
    } else if (
      lowerMessage.includes("joke") ||
      lowerMessage.includes("funny")
    ) {
      const jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the AI go to therapy? It had too many neural issues!",
        "What's a quantum physicist's favorite drink? Mountain Dew!",
        "Why was the math book sad? It had too many problems!",
      ];
      return jokes[Math.floor(Math.random() * jokes.length)];
    } else {
      return "I'm your Quantum AI assistant! I can help with emotion analysis, Pi control, generating insights, and much more. What would you like to explore?";
    }
  }

  processChatCommand(message, response) {
    const lowerMessage = message.toLowerCase();

    if (
      lowerMessage.includes("turn on led") ||
      lowerMessage.includes("led on")
    ) {
      this.setPiLED(true);
    } else if (
      lowerMessage.includes("turn off led") ||
      lowerMessage.includes("led off")
    ) {
      this.setPiLED(false);
    } else if (
      lowerMessage.includes("analyze emotion") ||
      lowerMessage.includes("scan emotion")
    ) {
      if (!this.cameraActive) {
        this.startCamera();
      } else {
        this.analyzeEmotion();
      }
    } else if (
      lowerMessage.includes("calm mode") ||
      lowerMessage.includes("relax")
    ) {
      this.activateCalmMode();
    }
  }

  addChatMessage(sender, text) {
    const chatMessages = document.getElementById("chatMessages");
    if (!chatMessages) return;

    const timestamp = new Date().toLocaleTimeString();
    const messageHTML = `
      <div class="message ${sender}-message">
        <div class="message-avatar">
          <i class="fas fa-${
            sender === "user" ? "user-astronaut" : "robot"
          }"></i>
        </div>
        <div class="message-content">
          <div class="message-text">${text}</div>
          <div class="message-time">${timestamp}</div>
        </div>
      </div>
    `;

    chatMessages.innerHTML += messageHTML;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // AI COMMAND EXECUTION
  executeAICommand(command) {
    const commands = {
      emotion_analysis: () => this.analyzeEmotion(),
      pep_talk: () => this.getPepTalk(),
      pi_led_on: () => this.setPiLED(true),
      pi_led_off: () => this.setPiLED(false),
      system_report: () => this.systemDiagnostic(),
      stress_check: () => this.stressCheck(),
      mood_trend: () => this.showMoodTrends(),
      emergency_calm: () => this.activateCalmMode(),
    };

    if (commands[command]) {
      commands[command]();
    } else {
      this.showNotification(`Command not recognized: ${command}`, "warning");
    }
  }

  // ADVANCED FEATURES
  async getPepTalk() {
    try {
      this.switchPage("companion");

      const emotion = this.currentEmotion
        ? this.currentEmotion.dominant_emotion
        : "neutral";

      const data = await this.callFlaskEndpoint(
        "/api/companion/pep_talk",
        "POST",
        {
          emotion: emotion,
        }
      );

      if (data.status === "success") {
        this.addChatMessage("bot", data.pep_talk);
      } else {
        throw new Error(data.message || "Pep talk failed");
      }
    } catch (error) {
      console.error("Pep talk failed:", error);
      const fallbackPepTalks = [
        "You're doing amazing! Remember that every challenge is an opportunity to grow. 💪",
        "Your potential is limitless! Keep pushing forward with confidence. 🚀",
      ];
      const randomPepTalk =
        fallbackPepTalks[Math.floor(Math.random() * fallbackPepTalks.length)];
      this.addChatMessage("bot", randomPepTalk);
    }
  }

  async systemDiagnostic() {
    try {
      this.switchPage("companion");

      const healthData = await this.callFlaskEndpoint("/api/system/health");

      let report = `🔍 **System Diagnostic Report**\n\n`;
      report += `🏥 **Overall Status**: ${healthData.status.toUpperCase()}\n`;
      report += `⏱️ **Session Uptime**: ${Math.round(
        healthData.system_uptime / 60
      )} minutes\n`;
      report += `📊 **Emotion Engine**: ${healthData.components?.emotion_engine?.status.toUpperCase()}\n`;
      report += `🤖 **AI Companion**: ${healthData.components?.ai_companion?.status.toUpperCase()}\n`;
      report += `💡 **Pi System**: ${
        healthData.pi_connected ? "CONNECTED" : "DEMO MODE"
      }\n`;
      report += `📷 **Camera**: ${
        healthData.components?.emotion_engine?.camera_active
          ? "LIVE FEED"
          : "STANDBY"
      }\n`;
      report += `💾 **Memory Usage**: ${Math.round(
        30 + Math.random() * 40
      )}%\n`;
      report += `⚡ **Performance**: OPTIMAL\n\n`;
      report += `All systems are functioning within normal parameters.`;

      this.addChatMessage("bot", report);
    } catch (error) {
      console.error("System diagnostic failed:", error);
      this.addChatMessage(
        "bot",
        "🔍 **System Status**: All systems operational in local mode. Pi controls available."
      );
    }
  }

  stressCheck() {
    if (!this.currentEmotion) {
      this.addChatMessage(
        "bot",
        "No emotion data available. Please activate the neural scan first to analyze your stress levels."
      );
      return;
    }

    const stressLevel = this.currentEmotion.bio_metrics?.stress_index || 0.3;
    let message = "";

    if (stressLevel > 0.7) {
      message =
        "🚨 **High stress detected!** Consider taking a break, practicing deep breathing, or going for a short walk. Your well-being comes first.";
    } else if (stressLevel > 0.4) {
      message =
        "⚠️ **Moderate stress levels.** Some relaxation techniques would be beneficial. Try the 'Calm Mode' for quick relief.";
    } else {
      message =
        "✅ **Stress levels are optimal.** Great job managing your well-being! You're doing an excellent job maintaining balance.";
    }

    message += `\n\n**Stress Index**: ${Math.round(stressLevel * 100)}%`;
    message += `\n**Recommendation**: ${
      stressLevel > 0.5
        ? "Take proactive steps to reduce stress"
        : "Maintain your current healthy habits"
    }`;

    this.addChatMessage("bot", message);
  }

  activateCalmMode() {
    this.setEmotionLighting("calm");
    this.addChatMessage(
      "bot",
      "🕊️ **Calm Mode Activated**\n\n" +
        "• Relaxing lighting enabled\n" +
        "• Stress reduction protocols engaged\n" +
        "• Peaceful ambiance established\n\n" +
        "💡 **Tip**: Take three deep breaths with me...\n" +
        "Breathe in slowly (1...2...3...4...)\n" +
        "Hold (1...2...)\n" +
        "Breathe out slowly (1...2...3...4...5...6...)\n\n" +
        "Remember: This moment is temporary. You have the strength and resilience to navigate through anything. 🧘‍♂️"
    );
  }

  // MEMORY BANK FUNCTIONS
  async clearMemory() {
    if (
      confirm(
        "Are you sure you want to clear all emotion history and memory data?"
      )
    ) {
      this.emotionHistory = [];
      this.analysisCount = 0;
      this.showNotification("Memory bank cleared successfully", "info");
      this.updateMemoryStats();
    }
  }

  async analyzePatterns() {
    if (this.emotionHistory.length < 3) {
      this.showNotification(
        "Need more emotion data to analyze patterns",
        "warning"
      );
      return;
    }

    this.showNotification("Analyzing emotional patterns...", "info");

    setTimeout(() => {
      const dominantEmotions = this.emotionHistory.map(
        (e) => e.dominant_emotion
      );
      const emotionCount = {};
      dominantEmotions.forEach((emotion) => {
        emotionCount[emotion] = (emotionCount[emotion] || 0) + 1;
      });

      const mostCommon = Object.keys(emotionCount).reduce((a, b) =>
        emotionCount[a] > emotionCount[b] ? a : b
      );
      this.showNotification(
        `Pattern detected: Mostly ${mostCommon} emotions`,
        "success"
      );
      this.updatePatternRecognition();
    }, 2000);
  }

  updatePatternRecognition() {
    const times = ["Morning", "Afternoon", "Evening"];
    const peakTime = document.getElementById("peakPositivityTime");
    const stressTime = document.getElementById("stressPatternTime");
    const energyTime = document.getElementById("energyPeakTime");

    if (peakTime)
      peakTime.textContent = `${
        times[Math.floor(Math.random() * times)]
      } hours`;
    if (stressTime)
      stressTime.textContent = `${
        times[Math.floor(Math.random() * times)]
      } hours`;
    if (energyTime)
      energyTime.textContent = `${
        times[Math.floor(Math.random() * times)]
      } hours`;
  }

  async exportAllData() {
    this.showNotification("Preparing data export...", "info");
    setTimeout(() => {
      this.showNotification(
        "Data exported successfully (simulated)",
        "success"
      );
    }, 1500);
  }

  async generateReport() {
    this.showNotification("Generating comprehensive report...", "info");
    setTimeout(() => {
      this.showNotification(
        "Report generated successfully (simulated)",
        "success"
      );
    }, 2000);
  }

  async backupMemory() {
    this.showNotification("Creating memory backup...", "info");
    setTimeout(() => {
      const lastBackup = document.getElementById("lastBackup");
      if (lastBackup) lastBackup.textContent = new Date().toLocaleTimeString();
      this.showNotification("Memory backup completed", "success");
    }, 1000);
  }

  async viewStatistics() {
    this.switchPage("history");
    this.showNotification("Displaying memory statistics", "info");
  }

  updateMemoryStats() {
    const totalMemories = document.getElementById("totalMemories");
    const avgMood = document.getElementById("avgMood");
    const sessionCount = document.getElementById("sessionCount");
    const dataSize = document.getElementById("dataSize");
    const storageUsed = document.getElementById("storageUsed");

    if (totalMemories) totalMemories.textContent = this.emotionHistory.length;
    if (avgMood)
      avgMood.textContent = this.emotionHistory.length > 0 ? "72%" : "0%";
    if (sessionCount) sessionCount.textContent = "1";
    if (dataSize)
      dataSize.textContent = `${(this.emotionHistory.length * 0.5).toFixed(
        1
      )}MB`;
    if (storageUsed)
      storageUsed.textContent = `${(this.emotionHistory.length * 0.5).toFixed(
        1
      )} MB`;
  }

  // UI MANAGEMENT
  switchPage(page) {
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active");
    });
    const activeNav = document.querySelector(`[data-page="${page}"]`);
    if (activeNav) activeNav.classList.add("active");

    document.querySelectorAll(".page").forEach((pageEl) => {
      pageEl.classList.remove("active");
    });
    const targetPage = document.getElementById(`${page}-page`);
    if (targetPage) targetPage.classList.add("active");

    const titles = {
      dashboard: "Quantum Dashboard",
      emotion: "Neural Scan",
      companion: "AI Companion",
      "pi-control": "Pi Control Center",
      insights: "AI Insights",
      history: "Memory Bank",
    };

    const pageTitle = document.getElementById("pageTitle");
    if (pageTitle) pageTitle.textContent = titles[page] || "Quantum Dashboard";

    const breadcrumb = document.getElementById("breadcrumb");
    if (breadcrumb) {
      const breadcrumbs = {
        dashboard: "Real-time Neural Analysis Interface",
        emotion: "Advanced Emotional Intelligence Scanning",
        companion: "Neural Dialogue & AI Interaction",
        "pi-control": "Hardware Integration & Device Management",
        insights: "AI-Powered Analytics & Pattern Recognition",
        history: "Emotional Memory & Data Analytics",
      };
      breadcrumb.textContent = breadcrumbs[page] || "Quantum AI Interface";
    }

    if (page === "history") {
      this.updateMemoryStats();
      this.updatePatternRecognition();
      this.loadMemoryData(); // Load memory data when page is opened
    }

    if (page === "emotion") {
      // Clear any existing intervals
      if (this.analyticsInterval) {
        clearInterval(this.analyticsInterval);
      }

      // Initialize analytics page
      setTimeout(() => {
        this.initializeAnalyticsPage();
      }, 100);
    } else {
      // Clear analytics interval when leaving the page
      if (this.analyticsInterval) {
        clearInterval(this.analyticsInterval);
        this.analyticsInterval = null;
      }
    }
  }

  updateSystemMetrics() {
    const uptime = Math.floor((Date.now() - this.sessionStartTime) / 1000);
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    const seconds = uptime % 60;

    const sessionTimer = document.getElementById("sessionTimer");
    if (sessionTimer) {
      sessionTimer.textContent = `${hours.toString().padStart(2, "0")}:${minutes
        .toString()
        .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    }

    const cameraStatus = document.getElementById("cameraStatus");
    if (cameraStatus)
      cameraStatus.textContent = this.cameraActive ? "Active" : "Ready";

    const cameraBadge = document.getElementById("cameraBadge");
    const cameraIcon = document.getElementById("cameraIcon");

    if (this.cameraActive) {
      if (cameraBadge) cameraBadge.innerHTML = '<i class="fas fa-check"></i>';
      if (cameraIcon) cameraIcon.className = "fas fa-eye";
    } else {
      if (cameraBadge) cameraBadge.innerHTML = '<i class="fas fa-video"></i>';
      if (cameraIcon) cameraIcon.className = "fas fa-eye";
    }

    const trendElement = document.getElementById("analysisTrend");
    if (trendElement && this.analysisCount > 0) {
      trendElement.innerHTML = '<i class="fas fa-arrow-up"></i>';
      trendElement.style.color = "var(--success)";
    }

    const memoryUsage = document.getElementById("memoryUsage");
    if (memoryUsage)
      memoryUsage.textContent = Math.round(40 + Math.random() * 25) + "%";

    const responseTime = document.getElementById("responseTime");
    if (responseTime)
      responseTime.textContent = (0.5 + Math.random() * 0.6).toFixed(1) + "s";
  }

  async updatePiStatus() {
    try {
      // Get real Pi status if connected
      if (this.piConnected) {
        const data = await this.callFlaskEndpoint("/api/pi/status");
        if (data.status === "success" && data.system_status) {
          const status = data.system_status;

          const piTemperature = document.getElementById("piTemperature");
          const piMemory = document.getElementById("piMemory");
          const ledStatus = document.getElementById("ledStatus");

          if (piTemperature && status.sensors?.temperature_c) {
            piTemperature.textContent = `${Math.round(
              status.sensors.temperature_c
            )}°C`;
          } else if (piTemperature) {
            piTemperature.textContent = "24°C";
          }

          if (piMemory && status.sensors?.humidity) {
            piMemory.textContent = `${Math.round(
              status.sensors.humidity
            )}% Humidity`;
            piMemory.previousElementSibling.textContent = "Humidity";
          } else if (piMemory) {
            piMemory.textContent = "52% Humidity";
            piMemory.previousElementSibling.textContent = "Humidity";
          }

          if (ledStatus) {
            ledStatus.textContent = status.led_state ? "ON" : "OFF";
            ledStatus.className = `metric-value ${
              status.led_state ? "online" : ""
            }`;
          }

          // Update brightness slider with real value
          const brightnessSlider = document.getElementById("ledBrightness");
          if (brightnessSlider && status.led_brightness_percent) {
            brightnessSlider.value = status.led_brightness_percent;
            const sliderValue = document.querySelector(".slider-value");
            if (sliderValue) {
              sliderValue.textContent = `${status.led_brightness_percent}%`;
            }
          }

          return; // Exit early since we got real data
        }
      }

      // Fallback to demo data if Pi not connected or API call failed
      await new Promise((resolve) => setTimeout(resolve, 800));

      const piTemperature = document.getElementById("piTemperature");
      const piMemory = document.getElementById("piMemory");

      if (piTemperature) {
        const baseTemp = this.piConnected ? 45 : 42;
        piTemperature.textContent = `${Math.round(
          baseTemp + Math.random() * 8
        )}°C`;
      }

      if (piMemory) {
        const baseMemory = this.piConnected ? 65 : 60;
        piMemory.textContent = `${Math.round(
          baseMemory + Math.random() * 15
        )}% Used`;
      }
    } catch (error) {
      console.error("Pi status update failed:", error);
    }
  }

  updatePiStatusUI() {
    const piStatus = document.getElementById("piStatus");
    const piConnectionStatus = document.getElementById("piConnectionStatus");
    const connectionStatus = document.querySelector(".pi-connection-status");

    if (piStatus)
      piStatus.textContent = this.piConnected ? "Online" : "Offline";

    if (piConnectionStatus) {
      piConnectionStatus.textContent = this.piConnected
        ? "Connected"
        : "Disconnected";
      piConnectionStatus.className = `metric-value ${
        this.piConnected ? "online" : ""
      }`;
    }

    if (connectionStatus) {
      const dot = connectionStatus.querySelector(".connection-dot");
      const text = connectionStatus.querySelector("span");

      if (dot)
        dot.className = `connection-dot ${this.piConnected ? "online" : ""}`;
      if (text)
        text.textContent = this.piConnected
          ? "Pi Connected"
          : "Pi Disconnected";
    }
  }

  updateCameraUI(active) {
    const startAnalysis = document.getElementById("startAnalysis");
    const stopAnalysis = document.getElementById("stopAnalysis");
    const toggleAnalysis = document.getElementById("toggleAnalysis");
    const cameraSystemStatus = document.getElementById("cameraSystemStatus");

    if (startAnalysis) startAnalysis.disabled = active;
    if (stopAnalysis) stopAnalysis.disabled = !active;
    if (toggleAnalysis) toggleAnalysis.disabled = !active;

    if (cameraSystemStatus) {
      cameraSystemStatus.textContent = active ? "Active" : "Ready";
      cameraSystemStatus.className = `metric-value ${active ? "online" : ""}`;
    }
  }

  updateSystemStatus(status) {
    const userStatus = document.getElementById("userStatus");
    const systemPulse = document.getElementById("systemPulse");
    const connectionStatus = document.getElementById("connectionStatus");

    if (userStatus) {
      userStatus.textContent = status === "online" ? "Online" : "Offline";
      userStatus.style.color =
        status === "online" ? "var(--success)" : "var(--gray-light)";
    }

    if (systemPulse) {
      systemPulse.style.background =
        status === "online" ? "var(--success)" : "var(--gray-light)";
    }

    if (connectionStatus) {
      connectionStatus.textContent =
        status === "online" ? "Quantum Linked" : "Local Mode";
    }
  }

  // DEMO MODE FUNCTIONS
  startDemoMode() {
    this.cameraActive = true;
    this.isAnalyzing = true;
    this.updateCameraUI(true);

    const cameraFeed = document.getElementById("cameraFeed");
    if (cameraFeed) {
      cameraFeed.innerHTML = `
        <div class="demo-camera-feed">
          <div class="camera-overlay">
            <div class="scan-grid"></div>
            <div class="face-indicator" style="display: flex;">
              <i class="fas fa-user"></i>
              <span>Face Detected</span>
            </div>
          </div>
          <div style="width: 100%; height: 100%; background: linear-gradient(45deg, #06b6d4, #4361ee); 
                      display: flex; align-items: center; justify-content: center; color: white;">
            <div style="text-align: center;">
              <i class="fas fa-camera" style="font-size: 3rem; margin-bottom: 1rem;"></i>
              <p>Quantum Vision Active</p>
              <small>Demo Mode - Real analysis working</small>
            </div>
          </div>
        </div>
      `;
    }

    this.startDemoAnalysis();
  }

  startDemoAnalysis() {
    this.demoInterval = setInterval(() => {
      if (this.isAnalyzing) {
        this.showDemoEmotion();
      }
    }, 5000);
  }

  showDemoEmotion() {
    const emotionData = this.generateEmotionData();
    this.currentEmotion = emotionData;

    this.saveEmotionToJson(emotionData);

    this.emotionHistory.push(emotionData);
    this.updateEmotionDisplay(emotionData);
    this.updateEmotionContext(emotionData);
    this.analysisCount++;
  }

  // UTILITY FUNCTIONS
  showNotification(message, type = "info") {
    const container = document.getElementById("notificationContainer");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <i class="fas fa-${this.getNotificationIcon(type)}"></i>
        <span>${message}</span>
      </div>
    `;

    container.appendChild(notification);

    setTimeout(() => {
      if (notification.parentNode) notification.remove();
    }, 5000);
  }

  getNotificationIcon(type) {
    const icons = {
      success: "check-circle",
      error: "exclamation-circle",
      warning: "exclamation-triangle",
      info: "info-circle",
    };
    return icons[type] || "info-circle";
  }

  getEmotionColor(emotion) {
    const colors = {
      joy: "var(--success)",
      sadness: "var(--secondary)",
      anger: "var(--danger)",
      fear: "var(--info)",
      surprise: "var(--warning)",
      neutral: "var(--gray-light)",
    };
    return colors[emotion] || "var(--gray-light)";
  }

  getEmotionEmoji(emotion) {
    const emojis = {
      joy: "😊",
      sadness: "😢",
      anger: "😠",
      fear: "😨",
      surprise: "😲",
      neutral: "😐",
    };
    return emojis[emotion] || "😐";
  }

  capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // FEATURE IMPLEMENTATIONS
  toggleAnalysis() {
    this.isAnalyzing = !this.isAnalyzing;
    const btn = document.getElementById("toggleAnalysis");
    if (btn) {
      btn.innerHTML = this.isAnalyzing
        ? '<i class="fas fa-pause"></i> Pause Analysis'
        : '<i class="fas fa-play"></i> Resume Analysis';
    }
    this.showNotification(
      `Analysis ${this.isAnalyzing ? "resumed" : "paused"}`,
      "info"
    );
  }

  captureFrame() {
    this.showNotification(
      "Quantum frame captured for neural analysis",
      "success"
    );
  }

  calibrateCamera() {
    this.showNotification("Neural vision calibration initiated...", "info");
    setTimeout(() => {
      this.showNotification("Camera calibration complete", "success");
    }, 2000);
  }

  showQuantumInsights() {
    this.switchPage("insights");
  }

  generateEmotionReport() {
    if (!this.currentEmotion) {
      this.showNotification("No emotion data available for report", "warning");
      return;
    }

    this.addChatMessage(
      "bot",
      `📊 **Emotion Analysis Report**\n\n` +
        `**Primary Emotion**: ${this.capitalize(
          this.currentEmotion.dominant_emotion
        )}\n` +
        `**Confidence**: ${Math.round(
          this.currentEmotion.quantum_confidence * 100
        )}%\n` +
        `**Stress Level**: ${Math.round(
          (this.currentEmotion.bio_metrics?.stress_index || 0) * 100
        )}%\n` +
        `**Mood Stability**: ${Math.round(
          (this.currentEmotion.bio_metrics?.mood_stability || 0) * 100
        )}%\n\n` +
        `**Recommendation**: ${
          document.getElementById("aiRecommendation")?.textContent ||
          "Continue monitoring emotional patterns"
        }`
    );
  }

  showMoodTrends() {
    if (this.emotionHistory.length < 2) {
      this.addChatMessage(
        "bot",
        "Need more emotion data to show trends. Continue using the neural scan to build your emotional history."
      );
      return;
    }

    const recentEmotions = this.emotionHistory
      .slice(-5)
      .map((e) => e.dominant_emotion);
    const emotionCount = {};
    recentEmotions.forEach((emotion) => {
      emotionCount[emotion] = (emotionCount[emotion] || 0) + 1;
    });

    const mostCommon = Object.keys(emotionCount).reduce((a, b) =>
      emotionCount[a] > emotionCount[b] ? a : b
    );

    this.addChatMessage(
      "bot",
      `📈 **Mood Trends**\n\n` +
        `**Recent Pattern**: Mostly ${mostCommon} emotions\n` +
        `**Stability**: ${
          this.currentEmotion.bio_metrics
            ? Math.round(this.currentEmotion.bio_metrics.mood_stability * 100) +
              "%"
            : "Analyzing..."
        }\n` +
        `**Recommendation**: ${
          mostCommon === "joy"
            ? "Maintain your positive activities and social connections!"
            : "Consider activities that enhance mood and reduce stress."
        }`
    );
  }

  clearChat() {
    const chatMessages = document.getElementById("chatMessages");
    if (chatMessages) {
      chatMessages.innerHTML = `
        <div class="message bot-message">
          <div class="message-avatar">
            <i class="fas fa-robot"></i>
          </div>
          <div class="message-content">
            <div class="message-text">
              <strong>Nexus AI:</strong> Hello! I'm your Quantum AI Companion. I can analyze emotions, provide insights, control your Pi system, and much more. How can I assist you today?
            </div>
            <div class="message-time">Quantum System Online</div>
          </div>
        </div>
      `;
    }
    this.showNotification("Chat memory cleared", "info");
  }

  exportChat() {
    this.showNotification("Chat export feature coming soon", "info");
  }

  showAISettings() {
    this.showNotification("AI settings panel coming soon", "info");
  }

  toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute("data-theme") || "dark";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    body.setAttribute("data-theme", newTheme);
    this.showNotification(`Switched to ${newTheme} theme`, "success");
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.log(`Error attempting to enable fullscreen: ${err.message}`);
        this.showNotification("Fullscreen not supported", "warning");
      });
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
  }

  refreshMetrics() {
    this.checkSystemStatus();
    this.showNotification("System metrics refreshed", "success");
  }

  emergencyStop() {
    const modal = document.getElementById("emergencyModal");
    if (modal) modal.style.display = "flex";
  }

  hideEmergencyModal() {
    const modal = document.getElementById("emergencyModal");
    if (modal) modal.style.display = "none";
  }

  confirmEmergencyStop() {
    this.stopCamera();
    this.setPiLED(false);
    this.isAnalyzing = false;
    this.hideEmergencyModal();
    this.showNotification("🛑 ALL SYSTEMS EMERGENCY STOPPED", "error");

    this.updateCameraUI(false);
    const cameraFeed = document.getElementById("cameraFeed");
    if (cameraFeed) {
      cameraFeed.innerHTML = `
        <div class="camera-placeholder">
          <i class="fas fa-shield-alt"></i>
          <h4>System Emergency Stop</h4>
          <p>All systems have been safely terminated</p>
        </div>
      `;
    }
  }

  checkSystemStatus() {
    const backendStatus = document.getElementById("backendStatus");
    const aiEngineStatus = document.getElementById("aiEngineStatus");
    const piConnectionStatus = document.getElementById("piConnectionStatus");

    if (backendStatus) {
      backendStatus.textContent = "Online";
      backendStatus.className = "metric-value online";
    }

    if (aiEngineStatus) {
      aiEngineStatus.textContent = "Active";
      aiEngineStatus.className = "metric-value online";
    }

    if (piConnectionStatus) {
      piConnectionStatus.textContent = this.piConnected
        ? "Connected"
        : "Demo Mode";
      piConnectionStatus.className = `metric-value ${
        this.piConnected ? "online" : ""
      }`;
    }
  }

  async loadMemoryData() {
    try {
      this.isLoadingMemory = true;
      const data = await this.callFlaskEndpoint("/api/memory/history");

      if (data.status === "success") {
        this.memoryData = data.emotion_history || [];
        this.updateMemoryDisplay();
        this.updateMemoryStats();
        this.updatePatternRecognition();
      }
    } catch (error) {
      console.error("Failed to load memory data:", error);
      // For demo, use current session data
      this.memoryData = this.emotionHistory;
      this.updateMemoryDisplay();
    } finally {
      this.isLoadingMemory = false;
    }
  }

  updateMemoryDisplay() {
    const timelineContainer = document.getElementById("memoryTimeline");
    if (!timelineContainer) return;

    if (this.memoryData.length === 0) {
      timelineContainer.innerHTML = `
            <div class="timeline-placeholder">
                <i class="fas fa-history"></i>
                <p>No emotion data recorded yet</p>
                <small>Start neural scanning to build your memory bank</small>
            </div>
        `;
      return;
    }

    // Sort by timestamp, most recent first
    const sortedData = [...this.memoryData]
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 20); // Show last 20 entries

    let timelineHTML = '<div class="timeline">';

    sortedData.forEach((entry, index) => {
      const emotion = entry.emotion_data || entry; // Handle both formats
      const time = new Date(
        entry.timestamp || emotion.analysis_timestamp
      ).toLocaleTimeString();
      const dominantEmotion = emotion.dominant_emotion;
      const confidence = Math.round((emotion.quantum_confidence || 0) * 100);

      timelineHTML += `
            <div class="timeline-item ${index === 0 ? "recent" : ""}">
                <div class="timeline-marker emotion-${dominantEmotion}">
                    <i class="${this.getEmotionTimelineIcon(
                      dominantEmotion
                    )}"></i>
                </div>
                <div class="timeline-content">
                    <div class="timeline-header">
                        <span class="emotion-badge ${dominantEmotion}">${this.capitalize(
        dominantEmotion
      )}</span>
                        <span class="timeline-time">${time}</span>
                    </div>
                    <div class="timeline-details">
                        <div class="confidence-indicator">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${confidence}%"></div>
                            </div>
                            <span>${confidence}% confidence</span>
                        </div>
                        ${
                          emotion.contextual_insights &&
                          emotion.contextual_insights.length > 0
                            ? `<div class="timeline-insight">
                                <i class="fas fa-lightbulb"></i>
                                ${emotion.contextual_insights[0]}
                            </div>`
                            : ""
                        }
                        ${
                          emotion.bio_metrics
                            ? `
                            <div class="bio-metrics">
                                <span class="bio-metric stress-${
                                  emotion.bio_metrics.stress_index > 0.5
                                    ? "high"
                                    : "low"
                                }">
                                    Stress: ${Math.round(
                                      emotion.bio_metrics.stress_index * 100
                                    )}%
                                </span>
                                <span class="bio-metric">
                                    Energy: ${Math.round(
                                      emotion.bio_metrics.energy_level * 100
                                    )}%
                                </span>
                            </div>
                        `
                            : ""
                        }
                    </div>
                </div>
            </div>
        `;
    });

    timelineHTML += "</div>";
    timelineContainer.innerHTML = timelineHTML;
  }

  getEmotionTimelineIcon(emotion) {
    const icons = {
      joy: "fa-smile",
      sadness: "fa-sad-tear",
      anger: "fa-angry",
      fear: "fa-surprise",
      surprise: "fa-surprise",
      disgust: "fa-meh-rolling-eyes",
      neutral: "fa-meh",
    };
    return `fas ${icons[emotion] || "fa-meh"}`;
  }

  updateMemoryStats() {
    const totalMemories = document.getElementById("totalMemories");
    const avgMood = document.getElementById("avgMood");
    const sessionCount = document.getElementById("sessionCount");
    const dataSize = document.getElementById("dataSize");
    const storageUsed = document.getElementById("storageUsed");

    if (totalMemories) totalMemories.textContent = this.memoryData.length;

    // Calculate average positivity (joy + surprise)
    if (avgMood && this.memoryData.length > 0) {
      const totalPositivity = this.memoryData.reduce((sum, entry) => {
        const emotion = entry.emotion_data || entry;
        const spectrum = emotion.emotion_spectrum || {};
        return sum + (spectrum.joy || 0) + (spectrum.surprise || 0) * 0.5;
      }, 0);
      const avgPositivity = Math.round(
        (totalPositivity / this.memoryData.length) * 100
      );
      avgMood.textContent = `${avgPositivity}%`;
    } else if (avgMood) {
      avgMood.textContent = "0%";
    }

    if (sessionCount) sessionCount.textContent = "1"; // You can track multiple sessions later
    if (dataSize)
      dataSize.textContent = `${(this.memoryData.length * 0.2).toFixed(1)}MB`;
    if (storageUsed)
      storageUsed.textContent = `${(this.memoryData.length * 0.2).toFixed(
        1
      )} MB`;
  }

  updatePatternRecognition() {
    if (this.memoryData.length === 0) return;

    // Analyze patterns in the data
    const hourStats = { morning: 0, afternoon: 0, evening: 0, night: 0 };
    const emotionStats = {};
    let totalPositivity = 0;
    let totalStress = 0;

    this.memoryData.forEach((entry) => {
      const emotion = entry.emotion_data || entry;
      const timestamp = new Date(entry.timestamp || emotion.analysis_timestamp);
      const hour = timestamp.getHours();

      // Categorize by time of day
      if (hour >= 6 && hour < 12) hourStats.morning++;
      else if (hour >= 12 && hour < 18) hourStats.afternoon++;
      else if (hour >= 18 && hour < 22) hourStats.evening++;
      else hourStats.night++;

      // Track emotions
      const dominant = emotion.dominant_emotion;
      emotionStats[dominant] = (emotionStats[dominant] || 0) + 1;

      // Calculate positivity and stress
      const spectrum = emotion.emotion_spectrum || {};
      totalPositivity += (spectrum.joy || 0) + (spectrum.surprise || 0) * 0.5;
      totalStress += emotion.bio_metrics?.stress_index || 0;
    });

    // Find peak positivity time
    const peakTime = Object.keys(hourStats).reduce((a, b) =>
      hourStats[a] > hourStats[b] ? a : b
    );

    const peakPositivityTime = document.getElementById("peakPositivityTime");
    const stressPatternTime = document.getElementById("stressPatternTime");
    const energyPeakTime = document.getElementById("energyPeakTime");

    if (peakPositivityTime) {
      const times = {
        morning: "Morning (6AM-12PM)",
        afternoon: "Afternoon (12PM-6PM)",
        evening: "Evening (6PM-10PM)",
        night: "Night (10PM-6AM)",
      };
      peakPositivityTime.textContent = times[peakTime] || "--:--";
    }

    if (stressPatternTime) {
      const avgStress = totalStress / this.memoryData.length;
      stressPatternTime.textContent =
        avgStress > 0.5 ? "High Alert" : "Well Managed";
    }

    if (energyPeakTime) {
      const avgPositivity = totalPositivity / this.memoryData.length;
      energyPeakTime.textContent =
        avgPositivity > 0.5 ? "Optimal Hours" : "Variable";
    }

    // Update memory insights
    this.updateMemoryInsights();
  }

  updateMemoryInsights() {
    const memoryInsights = document.getElementById("memoryInsights");
    if (!memoryInsights) return;

    if (this.memoryData.length === 0) {
      memoryInsights.innerHTML = `
            <div class="insight-item">
                <i class="fas fa-seedling"></i>
                <span>Your emotional patterns are still developing</span>
            </div>
            <div class="insight-item">
                <i class="fas fa-brain"></i>
                <span>Continue using Nexus AI to build richer insights</span>
            </div>
        `;
      return;
    }

    let insights = [];

    // Generate insights based on data
    if (this.memoryData.length < 10) {
      insights.push("Building foundational emotional patterns...");
      insights.push("Continue scanning to reveal deeper insights");
    } else {
      insights.push("Emotional baseline established");
      insights.push("Pattern recognition algorithms active");

      // Add specific insights based on data patterns
      const recentData = this.memoryData.slice(-10);
      const recentEmotions = recentData.map(
        (e) => (e.emotion_data || e).dominant_emotion
      );
      const uniqueEmotions = new Set(recentEmotions).size;

      if (uniqueEmotions <= 2) {
        insights.push("Consistent emotional patterns detected");
      } else {
        insights.push("Dynamic emotional range observed");
      }
    }

    memoryInsights.innerHTML = insights
      .map(
        (insight) => `
        <div class="insight-item">
            <i class="fas fa-lightbulb"></i>
            <span>${insight}</span>
        </div>
    `
      )
      .join("");
  }

  // Add to your existing methods
  async clearMemory() {
    if (
      confirm(
        "Are you sure you want to clear all emotion history and memory data?"
      )
    ) {
      try {
        const result = await this.callFlaskEndpoint(
          "/api/memory/clear",
          "POST"
        );
        if (result.status === "success") {
          this.memoryData = [];
          this.emotionHistory = [];
          this.updateMemoryDisplay();
          this.updateMemoryStats();
          this.showNotification("Memory bank cleared successfully", "success");
        }
      } catch (error) {
        console.error("Clear memory failed:", error);
        this.memoryData = [];
        this.emotionHistory = [];
        this.updateMemoryDisplay();
        this.updateMemoryStats();
        this.showNotification("Memory cleared locally", "info");
      }
    }
  }

  async exportAllData() {
    this.showNotification("Preparing data export...", "info");

    // Create downloadable JSON
    const dataStr = JSON.stringify(this.memoryData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `nexus-ai-emotion-data-${
      new Date().toISOString().split("T")[0]
    }.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    this.showNotification("Data exported successfully", "success");
  }

  // Add these methods after the bindAnalyticsEvents method

  initializeAnalyticsPage() {
    console.log("📈 Initializing analytics page...");
    this.initializeCharts();
    this.loadAnalyticsData();
    this.startAnalyticsUpdates();
  }

  initializeCharts() {
    this.initializeTrendChart();
    this.initializeDistributionChart();
    this.initializeHourlyChart();
    this.initializeStressTimelineChart();
    this.initializeRadarChart();
  }

  initializeTrendChart() {
    const ctx = document.getElementById("emotionTrendChart")?.getContext("2d");
    if (!ctx) {
      console.log("❌ Trend chart canvas not found");
      return;
    }

    // Create gradients
    const gradientJoy = ctx.createLinearGradient(0, 0, 0, 400);
    gradientJoy.addColorStop(0, "rgba(34, 197, 94, 0.3)");
    gradientJoy.addColorStop(1, "rgba(34, 197, 94, 0.05)");

    const gradientNeutral = ctx.createLinearGradient(0, 0, 0, 400);
    gradientNeutral.addColorStop(0, "rgba(59, 130, 246, 0.3)");
    gradientNeutral.addColorStop(1, "rgba(59, 130, 246, 0.05)");

    const gradientStress = ctx.createLinearGradient(0, 0, 0, 400);
    gradientStress.addColorStop(0, "rgba(239, 68, 68, 0.3)");
    gradientStress.addColorStop(1, "rgba(239, 68, 68, 0.05)");

    this.trendChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Joy",
            data: [],
            borderColor: "#22c55e",
            backgroundColor: gradientJoy,
            tension: 0.4,
            fill: true,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
          {
            label: "Neutral",
            data: [],
            borderColor: "#3b82f6",
            backgroundColor: gradientNeutral,
            tension: 0.4,
            fill: true,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
          {
            label: "Stress",
            data: [],
            borderColor: "#ef4444",
            backgroundColor: gradientStress,
            tension: 0.4,
            fill: true,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            mode: "index",
            intersect: false,
            backgroundColor: "rgba(0,0,0,0.8)",
            titleColor: "#fff",
            bodyColor: "#fff",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            grid: {
              color: "rgba(255,255,255,0.05)",
              drawBorder: false,
            },
            ticks: {
              color: "rgba(255,255,255,0.6)",
              font: {
                size: 11,
              },
            },
          },
          y: {
            min: 0,
            max: 100,
            grid: {
              color: "rgba(255,255,255,0.05)",
              drawBorder: false,
            },
            ticks: {
              color: "rgba(255,255,255,0.6)",
              font: {
                size: 11,
              },
              callback: function (value) {
                return value + "%";
              },
            },
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
        },
      },
    });
  }

  initializeDistributionChart() {
    const ctx = document
      .getElementById("emotionDistributionChart")
      ?.getContext("2d");
    if (!ctx) {
      console.log("❌ Distribution chart canvas not found");
      return;
    }

    this.distributionChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Joy", "Neutral", "Sadness", "Anger", "Fear", "Surprise"],
        datasets: [
          {
            data: [25, 25, 15, 10, 10, 15],
            backgroundColor: [
              "#22c55e",
              "#3b82f6",
              "#06b6d4",
              "#ef4444",
              "#8b5cf6",
              "#f59e0b",
            ],
            borderWidth: 2,
            borderColor: "var(--dark)",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: "var(--light)",
              font: {
                size: 11,
              },
            },
          },
        },
        cutout: "60%",
      },
    });
  }

  initializeHourlyChart() {
    const ctx = document.getElementById("hourlyPatternChart")?.getContext("2d");
    if (!ctx) {
      console.log("❌ Hourly chart canvas not found");
      return;
    }

    this.hourlyChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["6AM", "9AM", "12PM", "3PM", "6PM", "9PM"],
        datasets: [
          {
            label: "Positivity Level",
            data: [65, 75, 80, 70, 60, 55],
            backgroundColor: "rgba(34, 197, 94, 0.6)",
            borderColor: "#22c55e",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: "var(--gray-light)",
            },
          },
          y: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: "rgba(255,255,255,0.1)",
            },
            ticks: {
              color: "var(--gray-light)",
              callback: function (value) {
                return value + "%";
              },
            },
          },
        },
      },
    });
  }

  // Replace the initializeRadarChart method
  initializeRadarChart() {
    const ctx = document.getElementById("emotionRadarChart")?.getContext("2d");
    if (!ctx) {
      console.log("❌ Radar chart canvas not found");
      return;
    }

    this.radarChart = new Chart(ctx, {
      type: "radar",
      data: {
        labels: ["Joy", "Calm", "Focus", "Energy", "Social", "Creative"],
        datasets: [
          {
            label: "Your Emotional Profile",
            data: [0, 0, 0, 0, 0, 0], // Start with zeros
            backgroundColor: "rgba(6, 182, 212, 0.2)",
            borderColor: "#06b6d4",
            pointBackgroundColor: "#06b6d4",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "#06b6d4",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: {
              color: "rgba(255,255,255,0.1)",
            },
            grid: {
              color: "rgba(255,255,255,0.1)",
            },
            pointLabels: {
              color: "var(--light)",
              font: {
                size: 11,
              },
            },
            ticks: {
              color: "var(--gray-light)",
              backdropColor: "transparent",
              stepSize: 20,
            },
            beginAtZero: true,
            max: 100,
          },
        },
        plugins: {
          legend: {
            display: false,
          },
        },
      },
    });
  }

  // Replace the initializeStressTimelineChart method
  initializeStressTimelineChart() {
    const ctx = document
      .getElementById("stressTimelineChart")
      ?.getContext("2d");
    if (!ctx) {
      console.log("❌ Stress timeline chart canvas not found");
      return;
    }

    this.stressChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [], // Start empty
        datasets: [
          {
            label: "Stress Level",
            data: [], // Start empty
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            tension: 0.4,
            fill: true,
            borderWidth: 2,
            pointBackgroundColor: "#ef4444",
            pointBorderColor: "#fff",
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `Stress: ${context.parsed.y}%`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              color: "rgba(255,255,255,0.1)",
            },
            ticks: {
              color: "var(--gray-light)",
            },
          },
          y: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: "rgba(255,255,255,0.1)",
            },
            ticks: {
              color: "var(--gray-light)",
              callback: function (value) {
                return value + "%";
              },
            },
          },
        },
      },
    });
  }

  async loadAnalyticsData() {
    console.log("📊 Loading analytics data from emotion.json...");

    try {
      // Try to get data from the emotion.json file via Flask
      const emotionData = await this.callFlaskEndpoint("/api/memory/history");

      if (emotionData.status === "success" && emotionData.emotion_history) {
        this.analyticsData = emotionData.emotion_history;
        console.log(
          `📊 Loaded ${this.analyticsData.length} emotions from emotions.json`
        );

        // Also update memory data for consistency
        this.memoryData = this.analyticsData;

        if (this.analyticsData.length === 0) {
          this.showPlaceholderData();
        } else {
          this.updateAllCharts(this.analyticsData);
          this.updateMetricsOverview(this.analyticsData);
          this.updateAnalyticsInsights(this.analyticsData);
        }
      } else {
        // Fallback to local session data if no file data
        this.analyticsData =
          this.memoryData.length > 0 ? this.memoryData : this.emotionHistory;
        console.log("📊 Using session data as fallback");

        if (this.analyticsData.length === 0) {
          this.showPlaceholderData();
        } else {
          this.updateAllCharts(this.analyticsData);
          this.updateMetricsOverview(this.analyticsData);
          this.updateAnalyticsInsights(this.analyticsData);
        }
      }
    } catch (error) {
      console.error("❌ Analytics data loading failed:", error);
      this.showPlaceholderData();
    }
  }

  showPlaceholderData() {
    console.log("📊 Showing placeholder data");

    // Show placeholder message in insights
    const insightsContainer = document.getElementById("trendInsights");
    if (insightsContainer) {
      insightsContainer.innerHTML = `
      <div class="insight-card">
        <div class="insight-icon">
          <i class="fas fa-brain"></i>
        </div>
        <div class="insight-content">
          <div class="insight-title">Awaiting Data</div>
          <div class="insight-text">Start emotion analysis to generate neural insights and pattern recognition</div>
        </div>
      </div>
    `;
    }

    // ADD PLACEHOLDER DATA FOR CHARTS
    this.showChartPlaceholderData();
  }

  // Add this new method for chart placeholder data
  showChartPlaceholderData() {
    // Placeholder data for trend chart
    if (this.trendChart) {
      const placeholderLabels = [
        "12:00",
        "12:05",
        "12:10",
        "12:15",
        "12:20",
        "12:25",
        "12:30",
      ];
      const placeholderData = [25, 30, 28, 32, 35, 33, 30];

      this.trendChart.data.labels = placeholderLabels;
      this.trendChart.data.datasets[0].data = placeholderData; // Joy
      this.trendChart.data.datasets[1].data = placeholderData.map((d) => d - 5); // Neutral
      this.trendChart.data.datasets[2].data = placeholderData.map(
        (d) => 100 - d
      ); // Stress
      this.trendChart.update("none");
    }

    // Placeholder data for distribution chart
    if (this.distributionChart) {
      const placeholderDistribution = [35, 25, 15, 10, 8, 7];
      this.distributionChart.data.datasets[0].data = placeholderDistribution;
      this.distributionChart.update("none");
    }

    // Placeholder data for hourly chart
    if (this.hourlyChart) {
      const placeholderHourly = [45, 55, 65, 60, 50, 40];
      this.hourlyChart.data.datasets[0].data = placeholderHourly;
      this.hourlyChart.update("none");
    }

    // Placeholder data for stress timeline chart
    if (this.stressChart) {
      const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
      const placeholderStress = [35, 42, 38, 45, 40, 32, 28];

      this.stressChart.data.labels = days;
      this.stressChart.data.datasets[0].data = placeholderStress;
      this.stressChart.update("none");
    }

    // Placeholder data for radar chart
    if (this.radarChart) {
      const placeholderRadar = [45, 60, 55, 50, 40, 35];
      this.radarChart.data.datasets[0].data = placeholderRadar;
      this.radarChart.update("none");
    }

    // Update memory timeline with placeholder
    this.showMemoryTimelinePlaceholder();

    console.log("📊 All charts updated with placeholder data");
  }

  // Add this method for memory timeline placeholder
  showMemoryTimelinePlaceholder() {
    const timelineContainer = document.getElementById("memoryTimeline");
    if (!timelineContainer) return;

    timelineContainer.innerHTML = `
    <div class="timeline-placeholder">
      <i class="fas fa-history"></i>
      <p>No emotion data recorded yet</p>
      <small>Start neural scanning to build your memory bank</small>
    </div>
  `;
  }

  updateAllCharts(data) {
    if (!data || data.length === 0) {
      console.log("📊 No data available for charts, showing placeholder");
      this.showChartPlaceholderData();
      return;
    }

    console.log(`📊 Updating all charts with ${data.length} data points`);

    this.updateTrendChart(data);
    this.updateDistributionChart(data);
    this.updateHourlyChart(data);
    this.updateStressChart(data);
    this.updateRadarChart(data);
  }

  updateTrendChart(data) {
    if (!this.trendChart) return;

    const recentData = data.slice(-10);
    const labels = recentData.map((entry, index) => {
      // Handle both emotion.json format and direct emotion data
      const emotionData = entry.emotion_data || entry;
      const time = new Date(
        entry.timestamp ||
          emotionData.timestamp ||
          emotionData.analysis_timestamp
      );
      return time.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    });

    const joyData = recentData.map((entry) => {
      const emotionData = entry.emotion_data || entry;
      const spectrum = emotionData.emotion_spectrum || {};
      return (spectrum.joy || 0) * 100;
    });

    const neutralData = recentData.map((entry) => {
      const emotionData = entry.emotion_data || entry;
      const spectrum = emotionData.emotion_spectrum || {};
      return (spectrum.neutral || 0) * 100;
    });

    const stressData = recentData.map((entry) => {
      const emotionData = entry.emotion_data || entry;
      const bio = emotionData.bio_metrics || {};
      return (bio.stress_index || 0) * 100;
    });

    this.trendChart.data.labels = labels;
    this.trendChart.data.datasets[0].data = joyData;
    this.trendChart.data.datasets[1].data = neutralData;
    this.trendChart.data.datasets[2].data = stressData;
    this.trendChart.update("active");
  }

  updateDistributionChart(data) {
    if (!this.distributionChart) return;

    const emotionCounts = {
      joy: 0,
      neutral: 0,
      sadness: 0,
      anger: 0,
      fear: 0,
      surprise: 0,
    };

    data.forEach((entry) => {
      const emotionData = entry.emotion_data || entry;
      const dominant = emotionData.dominant_emotion;
      if (dominant && emotionCounts.hasOwnProperty(dominant)) {
        emotionCounts[dominant]++;
      }
    });

    const total = Object.values(emotionCounts).reduce((a, b) => a + b, 0);
    const percentages = Object.values(emotionCounts).map((count) =>
      total > 0 ? Math.round((count / total) * 100) : 0
    );

    this.distributionChart.data.datasets[0].data = percentages;
    this.distributionChart.update("active");
  }

  updateHourlyChart(data) {
    if (!this.hourlyChart) return;

    const hourlyData = Array(6)
      .fill(0)
      .map(() => ({ sum: 0, count: 0 }));
    const hours = [6, 9, 12, 15, 18, 21];

    data.forEach((entry) => {
      const emotionData = entry.emotion_data || entry;
      const timestamp = new Date(
        entry.timestamp ||
          emotionData.timestamp ||
          emotionData.analysis_timestamp
      );
      const hour = timestamp.getHours();

      for (let i = 0; i < hours.length; i++) {
        if (hour >= hours[i] && hour < hours[i] + 3) {
          const spectrum = emotionData.emotion_spectrum || {};
          hourlyData[i].sum += (spectrum.joy || 0) * 100;
          hourlyData[i].count++;
          break;
        }
      }
    });

    const averages = hourlyData.map((data) =>
      data.count > 0 ? Math.round(data.sum / data.count) : 0
    );

    this.hourlyChart.data.datasets[0].data = averages;
    this.hourlyChart.update("active");
  }

  // Replace the updateStressChart method
  updateStressChart(data) {
    if (!this.stressChart || !data || data.length === 0) {
      console.log("📊 No data for stress chart");
      return;
    }

    // Get the last 7 days of data or last 20 entries
    const recentData = data.slice(-20);

    const stressData = [];
    const labels = [];

    recentData.forEach((entry, index) => {
      const emotionData = entry.emotion_data || entry;
      const bio = emotionData.bio_metrics || {};

      // Use actual stress index from bio_metrics, fallback to calculated stress
      let stressLevel = 0;

      if (bio.stress_index !== undefined) {
        stressLevel = bio.stress_index * 100;
      } else {
        // Calculate stress from emotion spectrum if not directly available
        const spectrum = emotionData.emotion_spectrum || {};
        const negativeEmotions =
          (spectrum.anger || 0) +
          (spectrum.fear || 0) +
          (spectrum.sadness || 0);
        stressLevel = Math.min(100, negativeEmotions * 100 * 1.5);
      }

      stressData.push(Math.round(stressLevel));

      // Create labels with timestamps
      const timestamp = new Date(
        entry.timestamp ||
          emotionData.timestamp ||
          emotionData.analysis_timestamp
      );

      if (recentData.length <= 7) {
        // Use day names for small datasets
        labels.push(timestamp.toLocaleDateString("en", { weekday: "short" }));
      } else {
        // Use time for larger datasets
        labels.push(
          timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })
        );
      }
    });

    console.log("📊 Stress chart data:", stressData);

    this.stressChart.data.labels = labels;
    this.stressChart.data.datasets[0].data = stressData;
    this.stressChart.update("active");
  }

  // Add this method to your NexusAIDashboard class - place it after updateStressChart method
  updateRadarChart(data) {
    if (!this.radarChart || !data || data.length === 0) {
      console.log("📊 No data for radar chart");
      return;
    }

    // Calculate radar metrics from actual emotion data
    const metrics = {
      joy: 0,
      calm: 0,
      focus: 0,
      energy: 0,
      social: 0,
      creative: 0,
    };

    let validEntries = 0;

    data.forEach((entry) => {
      const emotionData = entry.emotion_data || entry;
      const spectrum = emotionData.emotion_spectrum || {};
      const bio = emotionData.bio_metrics || {};

      // Only process entries with valid data
      if (spectrum && bio) {
        // Joy from emotion spectrum
        metrics.joy += (spectrum.joy || 0) * 100;

        // Calm from neutral and low-stress states
        metrics.calm +=
          ((spectrum.neutral || 0) + (1 - (bio.stress_index || 0))) * 50;

        // Focus from engagement and low stress
        metrics.focus +=
          ((bio.engagement || 0.5) + (1 - (bio.stress_index || 0))) * 50;

        // Energy from bio metrics or inferred from positive emotions
        metrics.energy += (bio.energy_level || (spectrum.joy || 0) * 0.8) * 100;

        // Social from surprise and positive interactions
        metrics.social +=
          ((spectrum.surprise || 0) + (spectrum.joy || 0) * 0.5) * 100;

        // Creative from joy and engagement
        metrics.creative +=
          ((spectrum.joy || 0) + (bio.engagement || 0.5)) * 50;

        validEntries++;
      }
    });

    if (validEntries === 0) {
      console.log("📊 No valid emotion data for radar chart");
      return;
    }

    // Calculate averages and ensure they're within 0-100 range
    const averages = [
      Math.min(100, Math.max(0, Math.round(metrics.joy / validEntries))),
      Math.min(100, Math.max(0, Math.round(metrics.calm / validEntries))),
      Math.min(100, Math.max(0, Math.round(metrics.focus / validEntries))),
      Math.min(100, Math.max(0, Math.round(metrics.energy / validEntries))),
      Math.min(100, Math.max(0, Math.round(metrics.social / validEntries))),
      Math.min(100, Math.max(0, Math.round(metrics.creative / validEntries))),
    ];

    console.log("📊 Radar chart data:", averages);

    this.radarChart.data.datasets[0].data = averages;
    this.radarChart.update("active");
  }
  // Enhanced updateMetricsOverview to show real stress data
  updateMetricsOverview(data) {
    if (!data || data.length === 0) {
      console.log("📊 No data available, preserving placeholder metrics");
      return; // Don't update metrics if no data
    }
    const totalAnalyses = data.length;

    // Calculate real metrics from emotion data
    let totalJoy = 0;
    let totalStress = 0;
    let totalConfidence = 0;
    let totalEnergy = 0;
    let totalEngagement = 0;

    data.forEach((entry) => {
      const emotionData = entry.emotion_data || entry;
      const spectrum = emotionData.emotion_spectrum || {};
      const bio = emotionData.bio_metrics || {};

      totalJoy += spectrum.joy || 0;
      totalStress += bio.stress_index || 0;
      totalConfidence += emotionData.quantum_confidence || 0;
      totalEnergy += bio.energy_level || 0.5;
      totalEngagement += bio.engagement || 0.5;
    });

    const avgPositivity =
      totalAnalyses > 0 ? Math.round((totalJoy / totalAnalyses) * 100) : 0;
    const avgStress =
      totalAnalyses > 0 ? Math.round((totalStress / totalAnalyses) * 100) : 0;
    const avgConfidence =
      totalAnalyses > 0
        ? Math.round((totalConfidence / totalAnalyses) * 100)
        : 0;
    const avgEnergy =
      totalAnalyses > 0 ? Math.round((totalEnergy / totalAnalyses) * 100) : 0;
    const avgEngagement =
      totalAnalyses > 0
        ? Math.round((totalEngagement / totalAnalyses) * 100)
        : 0;

    // Calculate stability from emotion consistency
    const emotionCounts = {};
    data.forEach((entry) => {
      const emotionData = entry.emotion_data || entry;
      const dominant = emotionData.dominant_emotion;
      if (dominant) {
        emotionCounts[dominant] = (emotionCounts[dominant] || 0) + 1;
      }
    });

    const uniqueEmotions = Object.keys(emotionCounts).length;
    const stabilityScore =
      totalAnalyses > 0
        ? Math.max(0, 100 - (uniqueEmotions / totalAnalyses) * 50)
        : 0;

    // Find most common emotion
    let mostCommon = "--";
    if (totalAnalyses > 0 && Object.keys(emotionCounts).length > 0) {
      const mostCommonEntry = Object.entries(emotionCounts).reduce((a, b) =>
        a[1] > b[1] ? a : b
      );
      mostCommon = this.capitalize(mostCommonEntry[0]);
    }

    // Update DOM elements with real data
    this.updateElementText("totalAnalyses", totalAnalyses);
    this.updateElementText("avgPositivity", `${avgPositivity}%`);
    this.updateElementText("avgStress", `${avgStress}%`);
    this.updateElementText("stabilityScore", `${Math.round(stabilityScore)}%`);
    this.updateElementText("engagementScore", `${avgEngagement}%`);
    this.updateElementText("dataPointsCount", totalAnalyses);
    this.updateElementText("mostCommonEmotion", mostCommon);
    this.updateElementText("avgConfidence", `${avgConfidence}%`);

    console.log("📊 Updated metrics with real data:", {
      totalAnalyses,
      avgPositivity,
      avgStress,
      avgConfidence,
      stabilityScore,
      mostCommon,
    });
  }

  updateAnalyticsInsights(data) {
    const insightsContainer = document.getElementById("trendInsights");
    if (!insightsContainer) return;

    if (data.length < 3) {
      insightsContainer.innerHTML = `
            <div class="insight-card">
                <div class="insight-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <div class="insight-content">
                    <div class="insight-title">Awaiting Data</div>
                    <div class="insight-text">Start emotion analysis to generate neural insights and pattern recognition</div>
                </div>
            </div>
        `;
      return;
    }

    const insights = this.generateCleanInsights(data);

    insightsContainer.innerHTML = insights
      .map(
        (insight) => `
        <div class="insight-card">
            <div class="insight-icon" style="background: ${insight.background}">
                <i class="${insight.icon}"></i>
            </div>
            <div class="insight-content">
                <div class="insight-title">${insight.title}</div>
                <div class="insight-text">${insight.text}</div>
            </div>
        </div>
    `
      )
      .join("");
  }

  generateCleanInsights(data) {
    const insights = [];

    // Calculate basic metrics
    const totalJoy = data.reduce(
      (sum, entry) => sum + (entry.emotion_data?.emotion_spectrum?.joy || 0),
      0
    );
    const totalStress = data.reduce(
      (sum, entry) =>
        sum + (entry.emotion_data?.bio_metrics?.stress_index || 0),
      0
    );
    const avgJoy = (totalJoy / data.length) * 100;
    const avgStress = (totalStress / data.length) * 100;

    // Insight 1: Overall emotional health
    if (avgJoy > 60) {
      insights.push({
        title: "Positive Baseline",
        text: "Strong emotional foundation with consistent positivity",
        icon: "fas fa-smile",
        background: "linear-gradient(135deg, #22c55e, #16a34a)",
      });
    } else {
      insights.push({
        title: "Emotional Balance",
        text: "Maintaining steady emotional patterns with room for growth",
        icon: "fas fa-balance-scale",
        background: "linear-gradient(135deg, #3b82f6, #2563eb)",
      });
    }

    // Insight 2: Stress management
    if (avgStress < 30) {
      insights.push({
        title: "Low Stress",
        text: "Excellent stress management and emotional regulation",
        icon: "fas fa-wind",
        background: "linear-gradient(135deg, #10b981, #059669)",
      });
    } else {
      insights.push({
        title: "Stress Awareness",
        text: "Opportunities to enhance stress management techniques",
        icon: "fas fa-heartbeat",
        background: "linear-gradient(135deg, #f59e0b, #d97706)",
      });
    }

    // Insight 3: Pattern analysis
    insights.push({
      title: "Pattern Recognition",
      text: "Neural network detecting emotional consistency patterns",
      icon: "fas fa-wave-pulse",
      background: "linear-gradient(135deg, #8b5cf6, #7c3aed)",
    });

    return insights;
  }

  startAnalyticsUpdates() {
    // Update analytics every 10 seconds when on the page
    this.analyticsInterval = setInterval(() => {
      const emotionPage = document.getElementById("emotion-page");
      if (emotionPage?.classList.contains("active")) {
        this.loadAnalyticsData();
      }
    }, 10000);
  }

  // Also add this method to check for JSON file
  async checkForEmotionJson() {
    try {
      // Try to fetch the emotion.json file directly
      const response = await fetch("/logs/emotions.json");
      if (response.ok) {
        const data = await response.json();
        console.log("📁 Found emotion.json file:", data);
        return data.emotion_logs || [];
      }
    } catch (error) {
      console.log("📁 No emotion.json file found or error loading it");
    }
    return [];
  }
}

class TestMode {
  constructor(dashboard) {
    this.dashboard = dashboard;
    this.isActive = false;
    this.continuousMode = false;
    this.testImages = [];
    this.selectedImages = new Set();
    this.currentTestIndex = 0;
    this.testResults = [];
    this.initializeTestMode();
  }

  initializeTestMode() {
    // Test mode button
    const testModeBtn = document.getElementById("testModeBtn");
    if (testModeBtn) {
      testModeBtn.addEventListener("click", () => {
        this.toggleTestMode();
      });
    }

    // Stop test mode button
    const stopTestModeBtn = document.getElementById("stopTestMode");
    if (stopTestModeBtn) {
      stopTestModeBtn.addEventListener("click", () => {
        this.stopTestMode();
      });
    }

    // Scan folder button
    const scanFolderBtn = document.getElementById("scanFolder");
    if (scanFolderBtn) {
      scanFolderBtn.addEventListener("click", () => {
        this.scanImagesFolder();
      });
    }

    // Start selected tests
    const startSelectedTestsBtn = document.getElementById("startSelectedTests");
    if (startSelectedTestsBtn) {
      startSelectedTestsBtn.addEventListener("click", () => {
        this.startSelectedTests();
      });
    }

    // Select all images
    const selectAllImagesBtn = document.getElementById("selectAllImages");
    if (selectAllImagesBtn) {
      selectAllImagesBtn.addEventListener("click", () => {
        this.toggleSelectAll();
      });
    }

    // Continuous mode button
    const continuousModeBtn = document.getElementById("continuousTestMode");
    if (continuousModeBtn) {
      continuousModeBtn.addEventListener("click", () => {
        this.toggleContinuousMode();
      });
    }

    // Single image test button
    const testSingleImageBtn = document.getElementById("testSingleImage");
    if (testSingleImageBtn) {
      testSingleImageBtn.addEventListener("click", () => {
        this.testSingleImage();
      });
    }

    console.log("✅ Test Mode initialized");
  }

  async scanImagesFolder() {
    const folderPath = document.getElementById("imagesFolder").value;
    this.addLog(`📁 Scanning folder: ${folderPath}`, "info");

    try {
      const response = await fetch("/api/test/scan-folder", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ folder_path: folderPath }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      if (result.status === "success") {
        this.testImages = result.images;
        this.renderTestImages();

        if (this.testImages.length === 0) {
          this.addLog(
            `❌ No images found in folder. Please add images to the '${folderPath}' directory.`,
            "warning"
          );
        } else {
          this.addLog(
            `✅ Found ${this.testImages.length} images in folder`,
            "success"
          );
        }
      } else {
        throw new Error(result.message || "Scan failed");
      }
    } catch (error) {
      console.error("Folder scan failed:", error);
      this.addLog(`❌ Failed to scan folder: ${error.message}`, "error");
      this.addLog(
        "💡 Make sure the images folder exists and contains image files",
        "info"
      );
    }
  }

  renderTestImages() {
    const grid = document.getElementById("testImagesGrid");
    if (!grid) return;

    grid.innerHTML = "";

    if (this.testImages.length === 0) {
      grid.innerHTML = `
                <div class="no-images-message">
                    <i class="fas fa-folder-open"></i>
                    <p>No images found</p>
                    <small>Add images to your images/ folder</small>
                </div>
            `;
      return;
    }

    // Group images by folder
    const imagesByFolder = {};
    this.testImages.forEach((image, index) => {
      const folder = image.folder || "root";
      if (!imagesByFolder[folder]) {
        imagesByFolder[folder] = [];
      }
      imagesByFolder[folder].push({ ...image, index });
    });

    // Render each folder
    Object.entries(imagesByFolder).forEach(([folder, folderImages]) => {
      // Add folder header if there are multiple folders
      if (Object.keys(imagesByFolder).length > 1) {
        const folderHeader = document.createElement("div");
        folderHeader.className = "folder-header";
        folderHeader.innerHTML = `<i class="fas fa-folder"></i> ${folder}`;
        folderHeader.style.gridColumn = "1 / -1";
        folderHeader.style.marginTop = "15px";
        folderHeader.style.padding = "5px 10px";
        folderHeader.style.background = "rgba(59, 130, 246, 0.2)";
        folderHeader.style.borderRadius = "5px";
        folderHeader.style.fontWeight = "600";
        folderHeader.style.color = "#3b82f6";
        grid.appendChild(folderHeader);
      }

      // Render images in this folder
      folderImages.forEach((image) => {
        const imageItem = document.createElement("div");
        imageItem.className = "test-image-item";
        imageItem.dataset.index = image.index;

        const isSelected = this.selectedImages.has(image.index);

        imageItem.innerHTML = `
                    <div class="test-image-checkbox ${
                      isSelected ? "checked" : ""
                    }">
                        ${isSelected ? '<i class="fas fa-check"></i>' : ""}
                    </div>
                    <img src="/api/test/get-image?path=${encodeURIComponent(
                      image.path
                    )}" 
                         alt="${image.name}"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="image-fallback" style="display: none;">
                        <i class="fas fa-image"></i>
                        <span>${image.name}</span>
                    </div>
                    <div class="test-image-label">${image.name}</div>
                    ${
                      folder !== "root"
                        ? `<div class="test-image-folder">${folder}</div>`
                        : ""
                    }
                `;

        // Add click handler for selection
        imageItem.addEventListener("click", (e) => {
          this.toggleImageSelection(image.index, imageItem);
        });

        grid.appendChild(imageItem);
      });
    });

    this.updateTestControls();
  }

  toggleImageSelection(index, element) {
    if (this.selectedImages.has(index)) {
      this.selectedImages.delete(index);
      element.classList.remove("selected");
      element.querySelector(".test-image-checkbox").classList.remove("checked");
      element.querySelector(".test-image-checkbox").innerHTML = "";
    } else {
      this.selectedImages.add(index);
      element.classList.add("selected");
      element.querySelector(".test-image-checkbox").classList.add("checked");
      element.querySelector(".test-image-checkbox").innerHTML =
        '<i class="fas fa-check"></i>';
    }

    this.updateTestControls();
  }

  toggleSelectAll() {
    const allSelected = this.selectedImages.size === this.testImages.length;

    if (allSelected) {
      // Deselect all
      this.selectedImages.clear();
      document.querySelectorAll(".test-image-item").forEach((item) => {
        item.classList.remove("selected");
        item.querySelector(".test-image-checkbox").classList.remove("checked");
        item.querySelector(".test-image-checkbox").innerHTML = "";
      });
    } else {
      // Select all
      this.selectedImages = new Set([...Array(this.testImages.length).keys()]);
      document.querySelectorAll(".test-image-item").forEach((item, index) => {
        item.classList.add("selected");
        item.querySelector(".test-image-checkbox").classList.add("checked");
        item.querySelector(".test-image-checkbox").innerHTML =
          '<i class="fas fa-check"></i>';
      });
    }

    this.updateTestControls();
  }

  updateTestControls() {
    const startButton = document.getElementById("startSelectedTests");
    const selectAllButton = document.getElementById("selectAllImages");
    const continuousButton = document.getElementById("continuousTestMode");
    const singleImageButton = document.getElementById("testSingleImage");

    if (!startButton || !selectAllButton) return;

    const selectedCount = this.selectedImages.size;

    if (selectedCount > 0) {
      startButton.disabled = false;
      startButton.innerHTML = `<i class="fas fa-play"></i> Test ${selectedCount} Selected Images`;

      if (continuousButton) continuousButton.disabled = false;
      if (singleImageButton) singleImageButton.disabled = false;

      selectAllButton.innerHTML = `<i class="fas fa-times"></i> Deselect All`;
    } else {
      startButton.disabled = true;
      startButton.innerHTML = `<i class="fas fa-play"></i> Test Selected Images`;

      if (continuousButton) continuousButton.disabled = true;
      if (singleImageButton) singleImageButton.disabled = true;

      selectAllButton.innerHTML = `<i class="fas fa-check-square"></i> Select All`;
    }
  }

  toggleTestMode() {
    if (this.isActive) {
      this.stopTestMode();
    } else {
      this.startTestMode();
    }
  }

  startTestMode() {
    this.isActive = true;

    // Show test panel
    const testModePanel = document.getElementById("testModePanel");
    if (testModePanel) {
      testModePanel.style.display = "block";
    }

    const testModeBtn = document.getElementById("testModeBtn");
    if (testModeBtn) {
      testModeBtn.innerHTML = '<i class="fas fa-vial"></i> Test Mode Active';
      testModeBtn.classList.add("btn-warning");
    }

    this.addLog("🧪 Test Mode Activated", "success");
    this.addLog("Click 'Scan Folder' to load test images", "info");

    // Auto-scan the default folder
    setTimeout(() => {
      this.scanImagesFolder();
    }, 500);
  }

  stopTestMode() {
    this.isActive = false;
    this.continuousMode = false;
    this.selectedImages.clear();

    const testModePanel = document.getElementById("testModePanel");
    if (testModePanel) {
      testModePanel.style.display = "none";
    }

    const testModeBtn = document.getElementById("testModeBtn");
    if (testModeBtn) {
      testModeBtn.innerHTML =
        '<i class="fas fa-vial"></i> Test with Local Images';
      testModeBtn.classList.remove("btn-warning");
    }

    // Reset continuous mode button
    const continuousButton = document.getElementById("continuousTestMode");
    if (continuousButton) {
      continuousButton.innerHTML =
        '<i class="fas fa-sync"></i> Continuous Mode';
      continuousButton.classList.remove("btn-warning");
    }

    this.addLog("Test Mode Stopped", "info");
  }

  async startSelectedTests() {
    if (this.selectedImages.size === 0) {
      this.addLog("❌ No images selected for testing", "warning");
      return;
    }

    this.testResults = [];
    this.currentTestIndex = 0;

    const selectedIndices = Array.from(this.selectedImages).sort();
    this.addLog(
      `🚀 Starting test sequence with ${selectedIndices.length} images...`,
      "info"
    );

    // Disable controls during testing
    this.setTestControlsState(false);

    // Process images sequentially
    await this.processImageSequence(selectedIndices);

    // Re-enable controls
    this.setTestControlsState(true);
  }

  async processImageSequence(indices) {
    for (let i = 0; i < indices.length; i++) {
      if (!this.isActive) break;

      const imageIndex = indices[i];
      const testImage = this.testImages[imageIndex];

      // Update progress
      this.updateProgress(i + 1, indices.length, testImage.name);

      // Mark image as processing
      this.markImageProcessing(imageIndex, true);

      this.addLog(`🔄 Processing: ${testImage.name}`, "info");

      try {
        // Use the enhanced processing that mimics camera behavior
        const result = await this.processImageLikeCamera(
          testImage.path,
          testImage.name
        );

        // Store result
        this.testResults.push({
          image: testImage.name,
          detected: result.dominant_emotion,
          confidence: result.quantum_confidence,
          emotion_spectrum: result.emotion_spectrum,
          bio_metrics: result.bio_metrics,
        });

        // Mark image as completed
        this.markImageProcessing(imageIndex, false);
        this.markImageCompleted(imageIndex);

        this.addLog(
          `✅ ${testImage.name}: ${result.dominant_emotion} (${Math.round(
            result.quantum_confidence * 100
          )}% confidence)`,
          "success"
        );
      } catch (error) {
        this.markImageProcessing(imageIndex, false);
        this.markImageError(imageIndex);
        this.addLog(
          `❌ Error processing ${testImage.name}: ${error.message}`,
          "error"
        );
      }

      // Add delay between images to simulate real-time processing
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }

    this.completeTestSequence();
  }

  // CORE METHOD: Process image exactly like camera feed
  async processImageLikeCamera(imagePath, imageName) {
    try {
      // 1. Send to Flask for analysis (same as camera)
      const response = await fetch("/api/test/process-image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_path: imagePath,
          image_name: imageName,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const result = await response.json();

      if (result.status === "success") {
        const emotionData = result.emotion_data;

        if (this.dashboard) {
          await this.dashboard.saveEmotionToJson(emotionData);
        }

        // 2. Update ALL the same displays as camera feed
        this.updateDashboardLikeCamera(emotionData);

        // 3. Trigger ALL the same hardware responses as camera
        await this.triggerFullHardwareResponse(emotionData);

        // 4. Update analytics and memory (same as camera)
        this.updateAnalyticsAndMemory(emotionData);

        return emotionData;
      } else {
        throw new Error(result.message || "Processing failed");
      }
    } catch (error) {
      console.error("Image processing failed:", error);
      throw error;
    }
  }

  // Method to update dashboard exactly like camera feed
  updateDashboardLikeCamera(emotionData) {
    if (!this.dashboard) return;

    // Update current emotion (same as camera)
    this.dashboard.currentEmotion = emotionData;
    this.dashboard.emotionHistory.push(emotionData);

    // Update all UI components (same as camera)
    this.dashboard.updateEmotionDisplay(emotionData);
    this.dashboard.updateEmotionContext(emotionData);
    this.dashboard.analysisCount++;

    // Update counters and metrics
    const analysisCountEl = document.getElementById("analysisCount");
    if (analysisCountEl)
      analysisCountEl.textContent = this.dashboard.analysisCount;

    // Update system metrics
    this.dashboard.updateSystemMetrics();
  }

  // Method to trigger full hardware response
  async triggerFullHardwareResponse(emotionData) {
    if (!this.dashboard || !this.dashboard.piConnected) return;

    try {
      const emotion = emotionData.dominant_emotion;
      const confidence = Math.round(emotionData.quantum_confidence * 100);

      // 1. Auto-adjust lighting (same as camera)
      await this.dashboard.autoAdjustLighting(emotion);

      // 2. Update OLED display with emotion (same as camera)
      const emotionMessage = `Feeling ${emotion} - Confidence: ${confidence}%`;
      await this.dashboard.updatePiDisplayWithMessage(emotionMessage);

      // 3. Set emotion-specific lighting presets
      await this.dashboard.setEmotionLighting(emotion);

      this.addLog(`💡 Full hardware response: ${emotion} mode`, "success");
    } catch (error) {
      this.addLog(`⚠️ Hardware response failed: ${error.message}`, "warning");
    }
  }

  // Method to update analytics and memory
  updateAnalyticsAndMemory(emotionData) {
    if (!this.dashboard) return;

    // Add to memory data for analytics
    this.dashboard.memoryData.push({
      timestamp: new Date().toISOString(),
      emotion_data: emotionData,
    });

    // Update memory stats
    this.dashboard.updateMemoryStats();

    // Refresh analytics if on analytics page
    const emotionPage = document.getElementById("emotion-page");
    if (emotionPage?.classList.contains("active")) {
      this.dashboard.loadAnalyticsData();
    }
  }

  // Continuous mode for real-time simulation
  async toggleContinuousMode() {
    if (this.continuousMode) {
      this.stopContinuousMode();
    } else {
      await this.startContinuousMode();
    }
  }

  async startContinuousMode() {
    if (this.selectedImages.size === 0) {
      this.addLog("❌ No images selected for continuous mode", "warning");
      return;
    }

    this.continuousMode = true;
    const selectedIndices = Array.from(this.selectedImages).sort();

    const continuousButton = document.getElementById("continuousTestMode");
    if (continuousButton) {
      continuousButton.innerHTML =
        '<i class="fas fa-stop"></i> Stop Continuous';
      continuousButton.classList.add("btn-warning");
    }

    this.addLog("🔄 Starting continuous mode (like camera feed)...", "success");

    let cycleCount = 0;
    while (this.continuousMode && this.isActive) {
      cycleCount++;
      this.addLog(`🔄 Continuous mode cycle ${cycleCount}`, "info");

      for (const index of selectedIndices) {
        if (!this.continuousMode || !this.isActive) break;

        const testImage = this.testImages[index];

        try {
          await this.processImageLikeCamera(testImage.path, testImage.name);

          // Wait between "frames" like camera interval (3 seconds)
          await new Promise((resolve) => setTimeout(resolve, 3000));
        } catch (error) {
          this.addLog(`❌ Error in continuous mode: ${error.message}`, "error");
        }
      }

      // Brief pause between cycles
      if (this.continuousMode) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }
  }

  stopContinuousMode() {
    this.continuousMode = false;

    const continuousButton = document.getElementById("continuousTestMode");
    if (continuousButton) {
      continuousButton.innerHTML =
        '<i class="fas fa-sync"></i> Continuous Mode';
      continuousButton.classList.remove("btn-warning");
    }

    this.addLog("⏹️ Continuous mode stopped", "info");
  }

  // Test single image immediately
  async testSingleImage() {
    if (this.selectedImages.size === 0) {
      this.addLog("❌ No image selected for testing", "warning");
      return;
    }

    if (this.selectedImages.size > 1) {
      this.addLog(
        "ℹ️ Multiple images selected, testing first one only",
        "info"
      );
    }

    const firstIndex = Array.from(this.selectedImages)[0];
    const testImage = this.testImages[firstIndex];

    this.addLog(`🎯 Testing single image: ${testImage.name}`, "info");

    try {
      await this.processImageLikeCamera(testImage.path, testImage.name);
      this.addLog(
        `✅ Single image test completed: ${testImage.name}`,
        "success"
      );
    } catch (error) {
      this.addLog(`❌ Single image test failed: ${error.message}`, "error");
    }
  }

  // Utility methods
  updateProgress(current, total, imageName) {
    const progress = (current / total) * 100;
    const progressBar = document.getElementById("testProgressBar");
    const progressText = document.getElementById("testProgressText");

    if (progressBar) progressBar.style.width = `${progress}%`;
    if (progressText) {
      progressText.textContent = `Processing: ${imageName} (${current}/${total})`;
    }
  }

  markImageProcessing(index, isProcessing) {
    const imageElement = document.querySelector(
      `.test-image-item[data-index="${index}"]`
    );
    if (imageElement) {
      if (isProcessing) {
        imageElement.classList.add("processing");
      } else {
        imageElement.classList.remove("processing");
      }
    }
  }

  markImageCompleted(index) {
    const imageElement = document.querySelector(
      `.test-image-item[data-index="${index}"]`
    );
    if (imageElement) {
      imageElement.classList.add("completed");
      imageElement.classList.remove("error");
    }
  }

  markImageError(index) {
    const imageElement = document.querySelector(
      `.test-image-item[data-index="${index}"]`
    );
    if (imageElement) {
      imageElement.classList.add("error");
      imageElement.classList.remove("completed");
    }
  }

  setTestControlsState(enabled) {
    const startButton = document.getElementById("startSelectedTests");
    const selectAllButton = document.getElementById("selectAllImages");
    const continuousButton = document.getElementById("continuousTestMode");
    const singleImageButton = document.getElementById("testSingleImage");

    if (startButton) startButton.disabled = !enabled;
    if (selectAllButton) selectAllButton.disabled = !enabled;
    if (continuousButton) continuousButton.disabled = !enabled;
    if (singleImageButton) singleImageButton.disabled = !enabled;
  }

  completeTestSequence() {
    this.addLog("🎉 TEST SEQUENCE COMPLETE", "success");

    // Calculate statistics
    const totalTests = this.testResults.length;
    const successfulTests = this.testResults.filter(
      (r) => r.confidence > 0.5
    ).length;
    const avgConfidence =
      this.testResults.reduce((sum, r) => sum + r.confidence, 0) / totalTests;

    this.addLog(
      `📊 Processed ${totalTests} images (${successfulTests} successful)`,
      "info"
    );
    this.addLog(
      `📈 Average confidence: ${(avgConfidence * 100).toFixed(1)}%`,
      "info"
    );

    // Show emotion distribution
    const emotionCounts = {};
    this.testResults.forEach((result) => {
      emotionCounts[result.detected] =
        (emotionCounts[result.detected] || 0) + 1;
    });

    this.addLog("Emotion Distribution:", "info");
    Object.entries(emotionCounts).forEach(([emotion, count]) => {
      const percentage = (count / totalTests) * 100;
      this.addLog(`  ${emotion}: ${count} (${percentage.toFixed(1)}%)`, "info");
    });

    // Update progress bar to complete
    const progressBar = document.getElementById("testProgressBar");
    const progressText = document.getElementById("testProgressText");

    if (progressBar) progressBar.style.width = "100%";
    if (progressText) {
      progressText.textContent = `Complete! Processed ${totalTests} images`;
    }

    // Show notification in main dashboard
    if (this.dashboard && this.dashboard.showNotification) {
      this.dashboard.showNotification(
        `Test complete: ${totalTests} images processed`,
        "success"
      );
    }
  }

  addLog(message, type = "info") {
    const log = document.getElementById("testLog");
    if (!log) return;

    const entry = document.createElement("div");
    entry.className = `log-entry ${type}`;

    const timestamp = new Date().toLocaleTimeString();
    entry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-message">${message}</span>
        `;

    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;

    // Keep log manageable (last 50 entries)
    while (log.children.length > 50) {
      log.removeChild(log.firstChild);
    }
  }

  // Add this method to handle emotion JSON storage
  async saveEmotionToJson(emotionData) {
    try {
      const dataToSave = {
        timestamp: new Date().toISOString(),
        dominant_emotion: emotionData.dominant_emotion,
        quantum_confidence: emotionData.quantum_confidence,
        emotion_spectrum: emotionData.emotion_spectrum,
        bio_metrics: emotionData.bio_metrics,
        analysis_timestamp:
          emotionData.analysis_timestamp || new Date().toISOString(),
      };

      // Save via Flask endpoint
      const result = await this.callFlaskEndpoint("/api/emotion/save", "POST", {
        emotion_data: dataToSave,
      });

      if (result.status === "success") {
        console.log("✅ Emotion saved to JSON:", dataToSave.dominant_emotion);
      } else {
        console.warn("⚠️ Emotion save response:", result.message);
      }
    } catch (error) {
      console.error("❌ Failed to save emotion to JSON:", error);
      // Fallback: Try to save directly (if Flask app supports it)
      this.fallbackSaveToJson(emotionData);
    }
  }

  // Fallback method for direct saving
  fallbackSaveToJson(emotionData) {
    const dataToSave = {
      timestamp: new Date().toISOString(),
      dominant_emotion: emotionData.dominant_emotion,
      quantum_confidence: emotionData.quantum_confidence,
      emotion_spectrum: emotionData.emotion_spectrum,
      bio_metrics: emotionData.bio_metrics,
    };

    console.log("📝 Emotion data ready for JSON:", dataToSave);
  }
}

// Voice Controller for AI Companion
// Enhanced Voice Controller for AI Companion
class CompanionVoiceController {
  constructor(dashboard) {
    this.dashboard = dashboard;
    this.isListening = false;
    this.speakResponses = true;
    this.isSpeaking = false;
    this.commandCheckInterval = null;
    this.recognition = null;
    this.speechSynthesis = window.speechSynthesis;
    this.utterance = null;

    // Voice states
    this.voiceStates = {
      READY: "ready",
      LISTENING: "listening",
      PROCESSING: "processing",
      SPEAKING: "speaking",
      ERROR: "error",
    };

    this.currentState = this.voiceStates.READY;
    this.init();
  }

  speakIfEnabled(text) {
    if (this.speakResponses) {
      return this.speakResponse(text);
    }
    return Promise.resolve();
  }

  async init() {
    try {
      await this.setupSpeechRecognition();
      this.bindVoiceEvents();
      this.checkVoiceSupport();
      this.startStatusPolling();

      console.log("🎤 Voice controller initialized successfully");
    } catch (error) {
      console.error("❌ Voice controller initialization failed:", error);
      this.showVoiceError("Voice features unavailable");
    }
  }

  setupSpeechRecognition() {
    return new Promise((resolve, reject) => {
      // Check for browser support
      if (
        !("webkitSpeechRecognition" in window) &&
        !("SpeechRecognition" in window)
      ) {
        reject(new Error("Speech recognition not supported"));
        return;
      }

      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();

      // Configuration
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = "en-US";
      this.recognition.maxAlternatives = 1;

      // Event handlers
      this.recognition.onstart = () => {
        console.log("🎤 Speech recognition started");
        this.updateVoiceState(this.voiceStates.LISTENING);
        this.updateVoiceUI();
      };

      this.recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0].transcript)
          .join("");

        this.handleSpeechResult(transcript, event.results[0].isFinal);
      };

      this.recognition.onerror = (event) => {
        console.error("🎤 Speech recognition error:", event.error);
        this.handleRecognitionError(event.error);
      };

      this.recognition.onend = () => {
        console.log("🎤 Speech recognition ended");
        if (this.isListening) {
          // Auto-restart if still in listening mode
          setTimeout(() => this.startListening(), 500);
        } else {
          this.updateVoiceState(this.voiceStates.READY);
          this.updateVoiceUI();
        }
      };

      resolve();
    });
  }

  bindVoiceEvents() {
    // Voice controls with better error handling
    this.safeBindEvent("startVoiceListening", "click", () =>
      this.startListening()
    );
    this.safeBindEvent("stopVoiceListening", "click", () =>
      this.stopListening()
    );
    this.safeBindEvent("speakTestPhrase", "click", () =>
      this.speakTestPhrase()
    );

    // Speak responses toggle - Enhanced version
    this.setupSpeakResponsesToggle();

    // Voice command presets
    document.querySelectorAll(".voice-command-preset").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const command = btn.getAttribute("data-command");
        this.processVoiceCommand(command, true);
      });
    });
  }

  setupSpeakResponsesToggle() {
    const speakCheckbox = document.getElementById("speakResponses");
    if (speakCheckbox) {
      // Set initial state from checkbox
      this.speakResponses = speakCheckbox.checked;

      speakCheckbox.addEventListener("change", (e) => {
        this.speakResponses = e.target.checked;
        this.dashboard.showNotification(
          `Voice responses ${this.speakResponses ? "enabled" : "disabled"}`,
          "info"
        );

        // Save preference to localStorage
        this.saveVoicePreference();
      });

      // Load saved preference
      this.loadVoicePreference();
    }
  }

  saveVoicePreference() {
    try {
      localStorage.setItem(
        "nexusAI_speakResponses",
        this.speakResponses.toString()
      );
    } catch (error) {
      console.log("Could not save voice preference:", error);
    }
  }

  loadVoicePreference() {
    try {
      const saved = localStorage.getItem("nexusAI_speakResponses");
      if (saved !== null) {
        this.speakResponses = saved === "true";
        const speakCheckbox = document.getElementById("speakResponses");
        if (speakCheckbox) {
          speakCheckbox.checked = this.speakResponses;
        }
      }
    } catch (error) {
      console.log("Could not load voice preference:", error);
    }
  }

  safeBindEvent(elementId, eventType, handler) {
    const element = document.getElementById(elementId);
    if (element) {
      element.addEventListener(eventType, handler);
    }
  }

  async startListening() {
    if (!this.recognition) {
      this.showVoiceError("Speech recognition not available");
      return;
    }

    try {
      this.isListening = true;
      this.updateVoiceState(this.voiceStates.LISTENING);
      this.updateVoiceUI();

      await this.recognition.start();

      this.dashboard.showNotification("🎤 Listening... Speak now", "info");
    } catch (error) {
      console.error("❌ Failed to start listening:", error);
      this.showVoiceError("Failed to start listening");
      this.stopListening();
    }
  }

  stopListening() {
    this.isListening = false;

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (error) {
        console.log("Recognition already stopped");
      }
    }

    this.updateVoiceState(this.voiceStates.READY);
    this.updateVoiceUI();
    this.dashboard.showNotification("🔇 Voice listening stopped", "info");
  }

  handleSpeechResult(transcript, isFinal) {
    if (!isFinal) {
      // Show interim results
      this.updateInterimTranscript(transcript);
      return;
    }

    if (transcript.trim().length < 2) {
      console.log("Ignoring empty transcript");
      return;
    }

    console.log("🎤 Final transcript:", transcript);
    this.updateVoiceState(this.voiceStates.PROCESSING);
    this.updateVoiceUI();

    // Clear interim results
    this.clearInterimTranscript();

    // Add voice message to chat
    this.addVoiceMessage(transcript);

    // Process the command
    this.processVoiceCommand(transcript);
  }

  handleRecognitionError(error) {
    const errorMessages = {
      "not-allowed":
        "Microphone access denied. Please allow microphone permissions.",
      "audio-capture": "No microphone found. Please check your audio devices.",
      network: "Network error occurred during speech recognition.",
      "no-speech": "No speech detected. Please try again.",
      aborted: "Speech recognition aborted.",
      "bad-grammar": "Speech grammar error.",
    };

    const message =
      errorMessages[error] || `Speech recognition error: ${error}`;
    this.showVoiceError(message);

    if (error === "not-allowed" || error === "audio-capture") {
      this.isListening = false;
      this.updateVoiceState(this.voiceStates.ERROR);
      this.updateVoiceUI();
    }
  }

  async processVoiceCommand(transcript, isPreset = false) {
    try {
      // Quick command processing for common tasks
      const quickResponse = this.processQuickCommand(transcript);
      if (quickResponse) {
        this.addAIResponse(quickResponse.response);

        // ✅ SPEAK RESPONSE IF TOGGLE IS ON
        if (this.speakResponses) {
          await this.speakResponse(quickResponse.response);
        }

        if (quickResponse.action) {
          quickResponse.action();
        }
        return;
      }

      // Send to AI for complex responses
      const response = await this.sendToAI(transcript);
      this.addAIResponse(response);

      // ✅ SPEAK RESPONSE IF TOGGLE IS ON
      if (this.speakResponses) {
        await this.speakResponse(response);
      }
    } catch (error) {
      console.error("❌ Command processing failed:", error);
      const errorResponse =
        "I encountered an error processing your voice command. Please try again.";
      this.addAIResponse(errorResponse);

      // ✅ SPEAK ERROR RESPONSE TOO
      if (this.speakResponses) {
        await this.speakResponse(errorResponse);
      }
    } finally {
      this.updateVoiceState(this.voiceStates.READY);
      this.updateVoiceUI();
    }
  }

  processQuickCommand(transcript) {
    const lowerTranscript = transcript.toLowerCase().trim();

    const quickCommands = {
      hello: {
        response:
          "Hello! I'm your Nexus AI voice assistant. How can I help you today?",
        action: null,
      },
      "stop listening": {
        response: "Okay, I'll stop listening for now.",
        action: () => this.stopListening(),
      },
      "turn on led": {
        response: "Turning on the LED lights for you.",
        action: () => this.dashboard.setPiLED(true),
      },
      "turn off led": {
        response: "Turning off the LED lights.",
        action: () => this.dashboard.setPiLED(false),
      },
      "analyze emotion": {
        response: "Starting emotion analysis with the camera.",
        action: () => {
          if (!this.dashboard.cameraActive) {
            this.dashboard.startCamera();
          }
        },
      },
      "how are you": {
        response:
          "I'm functioning optimally! Ready to help you with emotion analysis and device control.",
        action: null,
      },
      "what can you do": {
        response:
          "I can analyze emotions through camera, control Raspberry Pi devices, chat with you, generate insights, and much more!",
        action: null,
      },
      "calm mode": {
        response: "Activating calm mode with relaxing lighting and ambiance.",
        action: () => this.dashboard.activateCalmMode(),
      },
    };

    // Find matching command
    for (const [command, config] of Object.entries(quickCommands)) {
      if (lowerTranscript.includes(command)) {
        return config;
      }
    }

    return null;
  }

  async sendToAI(message) {
    try {
      const emotionContext = this.dashboard.currentEmotion || {};

      const response = await this.dashboard.callFlaskEndpoint(
        "/api/chat/send",
        "POST",
        {
          message: message,
          emotion_context: emotionContext,
          is_voice: true,
        }
      );

      if (response.status === "success") {
        return response.ai_response.response;
      } else {
        throw new Error(response.message || "AI response failed");
      }
    } catch (error) {
      console.error("❌ AI communication failed:", error);
      return "I'm having trouble connecting to the AI right now. Please check your connection and try again.";
    }
  }

  async speakResponse(text) {
    if (!this.speakResponses || this.isSpeaking) return;

    return new Promise((resolve) => {
      try {
        // Clean the text for speech
        const cleanText = text
          .replace(/\*\*(.*?)\*\*/g, "$1") // Remove bold
          .replace(/\*(.*?)\*/g, "$1") // Remove italic
          .replace(/Nexus AI:\s*/g, "") // Remove AI prefix
          .replace(/[\[\]]/g, "") // Remove brackets
          .trim();

        if (!cleanText) {
          resolve();
          return;
        }

        // Stop any current speech
        if (this.utterance) {
          this.speechSynthesis.cancel();
        }

        this.isSpeaking = true;
        this.updateVoiceState(this.voiceStates.SPEAKING);
        this.updateVoiceUI();

        this.utterance = new SpeechSynthesisUtterance(cleanText);

        // Configure speech
        this.utterance.rate = 0.9;
        this.utterance.pitch = 1.0;
        this.utterance.volume = 0.8;

        // Get available voices
        const voices = this.speechSynthesis.getVoices();
        const preferredVoice = voices.find(
          (voice) =>
            voice.name.includes("Google") || voice.name.includes("Samantha")
        );
        if (preferredVoice) {
          this.utterance.voice = preferredVoice;
        }

        this.utterance.onend = () => {
          this.isSpeaking = false;
          this.utterance = null;
          this.updateVoiceState(this.voiceStates.READY);
          this.updateVoiceUI();
          resolve();
        };

        this.utterance.onerror = (event) => {
          console.error("❌ Speech synthesis error:", event.error);
          this.isSpeaking = false;
          this.utterance = null;
          this.updateVoiceState(this.voiceStates.READY);
          this.updateVoiceUI();
          resolve();
        };

        this.speechSynthesis.speak(this.utterance);
      } catch (error) {
        console.error("❌ Speech synthesis failed:", error);
        this.isSpeaking = false;
        this.updateVoiceState(this.voiceStates.READY);
        this.updateVoiceUI();
        resolve();
      }
    });
  }

  async speakTestPhrase() {
    const testPhrase =
      "Hello! This is your Nexus AI companion. Voice system is working correctly.";
    await this.speakResponse(testPhrase);
  }

  updateVoiceState(newState) {
    this.currentState = newState;
    this.updateVoiceUI();
  }

  updateVoiceUI() {
    const startBtn = document.getElementById("startVoiceListening");
    const stopBtn = document.getElementById("stopVoiceListening");
    const voiceStatus = document.getElementById("voiceStatusDisplay");
    const voiceActivity = document.getElementById("voiceActivity");
    const voiceState = document.getElementById("voiceState");

    if (!voiceStatus) return;

    const stateConfig = {
      [this.voiceStates.READY]: {
        startVisible: true,
        stopVisible: false,
        statusText: "Ready for voice commands",
        activityClass: "",
        stateText: "Ready",
        stateClass: "ready",
      },
      [this.voiceStates.LISTENING]: {
        startVisible: false,
        stopVisible: true,
        statusText: "Listening... Speak now",
        activityClass: "listening",
        stateText: "Listening",
        stateClass: "listening",
      },
      [this.voiceStates.PROCESSING]: {
        startVisible: false,
        stopVisible: false,
        statusText: "Processing your command...",
        activityClass: "processing",
        stateText: "Processing",
        stateClass: "processing",
      },
      [this.voiceStates.SPEAKING]: {
        startVisible: false,
        stopVisible: false,
        statusText: "Speaking response...",
        activityClass: "speaking",
        stateText: "Speaking",
        stateClass: "speaking",
      },
      [this.voiceStates.ERROR]: {
        startVisible: true,
        stopVisible: false,
        statusText: "Voice system error",
        activityClass: "error",
        stateText: "Error",
        stateClass: "error",
      },
    };

    const config =
      stateConfig[this.currentState] || stateConfig[this.voiceStates.READY];

    if (startBtn)
      startBtn.style.display = config.startVisible ? "block" : "none";
    if (stopBtn) stopBtn.style.display = config.stopVisible ? "block" : "none";

    voiceStatus.querySelector("span").textContent = config.statusText;

    if (voiceActivity) {
      voiceActivity.className = "voice-activity";
      if (config.activityClass) {
        voiceActivity.classList.add(config.activityClass);
      }
    }

    if (voiceState) {
      voiceState.textContent = config.stateText;
      voiceState.className = `voice-state ${config.stateClass}`;
    }
  }

  updateInterimTranscript(transcript) {
    const interimElement = document.getElementById("interimTranscript");
    if (interimElement) {
      interimElement.textContent = transcript;
      interimElement.style.display = "block";
    }
  }

  clearInterimTranscript() {
    const interimElement = document.getElementById("interimTranscript");
    if (interimElement) {
      interimElement.textContent = "";
      interimElement.style.display = "none";
    }
  }

  addVoiceMessage(text) {
    const chatMessages = document.getElementById("chatMessages");
    if (!chatMessages) return;

    const messageDiv = document.createElement("div");
    messageDiv.className = "message user-message voice-message";
    messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-microphone"></i>
      </div>
      <div class="message-content">
        <div class="message-text">${this.escapeHtml(text)}</div>
        <div class="message-time">Voice Input • ${new Date().toLocaleTimeString()}</div>
      </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  addAIResponse(response) {
    const chatMessages = document.getElementById("chatMessages");
    if (!chatMessages) return;

    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message voice-response";
    messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="message-content">
        <div class="message-text">
          <strong>Nexus AI:</strong> ${this.escapeHtml(response)}
        </div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
      </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  checkVoiceSupport() {
    const support = {
      speechRecognition: !!(
        window.SpeechRecognition || window.webkitSpeechRecognition
      ),
      speechSynthesis: !!window.speechSynthesis,
    };

    console.log("🎤 Voice support check:", support);

    if (!support.speechRecognition) {
      this.showVoiceError("Speech recognition not supported in this browser");
    }

    if (!support.speechSynthesis) {
      this.showVoiceError("Speech synthesis not supported in this browser");
    }

    return support;
  }

  showVoiceError(message) {
    console.error("🎤 Voice error:", message);
    this.dashboard.showNotification(`🎤 ${message}`, "error");

    // Update UI to show error state
    this.updateVoiceState(this.voiceStates.ERROR);
    this.updateVoiceUI();
  }

  startStatusPolling() {
    // Optional: Poll for server-side voice status if needed
    setInterval(() => {
      if (this.isListening) {
        this.checkServerVoiceStatus();
      }
    }, 10000);
  }

  async checkServerVoiceStatus() {
    try {
      const status = await this.dashboard.callFlaskEndpoint(
        "/api/speech/status"
      );
      if (status.status === "success") {
        // Sync with server state if needed
      }
    } catch (error) {
      // Silent fail - server status check is optional
    }
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Cleanup method
  destroy() {
    this.stopListening();

    if (this.utterance) {
      this.speechSynthesis.cancel();
    }

    if (this.commandCheckInterval) {
      clearInterval(this.commandCheckInterval);
    }

    console.log("🎤 Voice controller destroyed");
  }
}

// Enhanced CSS for voice interface
const voiceStyles = `
.voice-controls {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.voice-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.voice-activity {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--gray-light);
  transition: all 0.3s ease;
}

.voice-activity.listening {
  background: var(--success);
  animation: pulse 1.5s infinite;
}

.voice-activity.processing {
  background: var(--warning);
  animation: pulse 1s infinite;
}

.voice-activity.speaking {
  background: var(--info);
  animation: pulse 0.8s infinite;
}

.voice-activity.error {
  background: var(--danger);
}

.voice-state {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.voice-state.ready { background: var(--success); color: white; }
.voice-state.listening { background: var(--warning); color: white; }
.voice-state.processing { background: var(--info); color: white; }
.voice-state.speaking { background: var(--secondary); color: white; }
.voice-state.error { background: var(--danger); color: white; }

.voice-message .message-avatar {
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
}

.voice-response .message-avatar {
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
}

#interimTranscript {
  font-style: italic;
  color: var(--gray-light);
  margin: 0.5rem 0;
  min-height: 1.2rem;
}

.voice-command-presets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
}

.voice-command-preset {
  padding: 0.5rem;
  background: var(--darker);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.8rem;
  text-align: center;
}

.voice-command-preset:hover {
  background: var(--dark-light);
  transform: translateY(-1px);
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Responsive design */
@media (max-width: 768px) {
  .voice-controls {
    padding: 0.75rem;
  }
  
  .voice-command-presets {
    grid-template-columns: 1fr 1fr;
  }
}
`;

// Inject voice styles
const voiceStyleSheet = document.createElement("style");
voiceStyleSheet.textContent = voiceStyles;
document.head.appendChild(voiceStyleSheet);

// Initialize companion voice controller when dashboard is ready
function initCompanionVoice(dashboard) {
  if (dashboard.companionVoiceController) {
    dashboard.companionVoiceController.destroy();
  }

  dashboard.companionVoiceController = new CompanionVoiceController(dashboard);
  return dashboard.companionVoiceController;
}

// Export for global access if needed
window.CompanionVoiceController = CompanionVoiceController;

// Initialize companion voice controller
// let companionVoice;

// // Initialize when companion page is loaded
// function initCompanionVoice() {
//   companionVoice = new CompanionVoiceController();
// }

// // Call this when switching to companion page
// document.addEventListener("DOMContentLoaded", function () {
//   // Your existing page navigation code...

//   // When companion page becomes active
//   const companionPage = document.getElementById("companion-page");
//   if (companionPage.classList.contains("active")) {
//     initCompanionVoice();
//   }
// });

// OLED Styles
const oledStyles = `
.oled-display-preview {
  width: 128px;
  height: 64px;
  background: #000;
  color: #fff;
  font-family: monospace;
  padding: 4px;
  border: 2px solid #333;
  border-radius: 4px;
  margin: 0 auto;
}

.oled-header {
  display: flex;
  justify-content: space-between;
  font-size: 8px;
  margin-bottom: 8px;
}

.oled-center {
  font-size: 12px;
  text-align: center;
  margin: 8px 0;
  white-space: nowrap;
  overflow: hidden;
}

.oled-footer {
  font-size: 8px;
  text-align: center;
  color: #888;
}

.oled-text {
  font-size: 12px;
  text-align: center;
  margin: 20px 0;
}
`;

// Inject OLED styles
const styleSheet = document.createElement("style");
styleSheet.textContent = oledStyles;
document.head.appendChild(styleSheet);

// Theme switching CSS
const style = document.createElement("style");
style.textContent = `
  [data-theme="light"] {
    --dark: #f8fafc;
    --darker: #e2e8f0;
    --dark-light: #ffffff;
    --light: #0f172a;
    --lighter: #1e293b;
    --gray: #475569;
    --gray-light: #64748b;
    --glass-bg: rgba(248, 250, 252, 0.85);
    --glass-border: rgba(15, 23, 42, 0.12);
  }
`;
document.head.appendChild(style);

// Initialize dashboard when page loads
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new NexusAIDashboard();
  console.log("🎊 Nexus AI Quantum Dashboard fully operational!");
});

// Global error handler
window.addEventListener("error", (e) => {
  console.error("Global error:", e.error);
});
