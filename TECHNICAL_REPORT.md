a# Technical Report: BMO Robot Architecture

## 1. System Architecture

The BMO system uses a modular Python architecture centered around a main event loop (`main.py`) that orchestrates several independent subsystems.

### Core Modules
*   **Hardware Manager (`hardware.py`)**: 
    *   Abstracts the specific display driver (ST7789/ILI9341).
    *   Uses `spidev` for high-speed SPI communication (essential for smooth UI).
    *   Handles GPIO inputs (buttons) and backlight PWM control.
*   **Face Renderer (`face.py`)**: 
    *   Uses `pygame` for drawing vector graphics (eyes, mouth).
    *   Maintains internal state (`IDLE`, `THINKING`, etc.) independent of the audio thread.
    *   Renders to an off-screen buffer which is then converted to PIL Image for the hardware display.
*   **Audio Engine (`audio.py`)**:
    *   Handles **STT** (input) via `SpeechRecognition` library (wrapping Google/Whisper APIs).
    *   Handles **TTS** (output) via `pyttsx3` (low latency, offline) or `gTTS` (higher quality).
    *   Manages SFX playback via `pygame.mixer`.
*   **AI Brain (`brain.py`)**:
    *   Wraps `OpenAI API` calls.
    *   Maintains conversation context (sliding window of last 10-20 turns).
    *   Injects a "System Prompt" to enforce BMO's personality.
*   **Media Player (`media.py`)**:
    *   Handles long-running media (music/films).
    *   Music: Uses `pygame.mixer.music` for background audio.
    *   Video: Uses `OpenCV` (`cv2`) to decode frames and blit them directly to the display surface.

## 2. Dependencies & Libraries
*   **OS**: Raspberry Pi OS (Bullseye/Bookworm) 64-bit recommended.
*   **Runtime**: Python 3.9+
*   **Key Libraries**:
    *   `pygame`: Framebuffer access, audio mixing, vector drawing.
    *   `openai`: Logic/Brain.
    *   `SpeechRecognition`: Audio capture and STT.
    *   `adafruit-circuitpython-rgb-display`: Efficient SPI display drivers.
    *   `opencv-python`: Lightweight video decoding.

## 3. Performance Optimizations (Raspberry Pi 4)

*   **SPI Baudrate**: Set to 64MHz (`baudrate=64000000`) in `hardware.py`. This is critical for getting >30FPS on SPI screens.
*   **Headless Pygame**: `os.environ["SDL_VIDEODRIVER"] = "dummy"` is used to prevent Pygame from trying to open a window on the desktop (X11), saving resources.
*   **Video Decoding**: OpenCV is used for software decoding. For higher performance (720p+), hardware decoding via `VLC` or `gstreamer` + `MMAL` would be needed, but for small screens (240p/320p), software decoding is sufficient.
*   **Audio Latency**: `pygame.mixer.pre_init(44100, -16, 2, 2048)` reduces audio delay.

## 4. Limitations & Future Work
*   **STT Latency**: Cloud-based STT (Google/OpenAI) introduces 1-2s delay. Local Whisper (tiny model) on Pi 4 is possible but slow (~3-5s). Consider `Vosk` for faster offline command recognition.
*   **Battery**: Current design assumes persistent power. LiPo implementation requires a UPS HAT (e.g., PiSugar) and battery monitoring code.
*   **Vision**: No camera integration yet. Adding `cv2` face tracking would allow BMO to look at the user.

