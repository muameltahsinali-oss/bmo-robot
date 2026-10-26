import time
import os
import threading
import pygame
import yaml
from modules.hardware import HardwareManager
from modules.face import FaceRenderer
from modules.audio import AudioEngine
from modules.brain import AIBrain
from modules.media import MediaPlayer

# Config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.yaml')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
except:
    config = {}

class BMO:
    def __init__(self):
        print("BMO System Initializing...")
        
        # 1. Hardware
        self.hw = HardwareManager()
        
        # 2. Face
        self.face = FaceRenderer(width=self.hw.width, height=self.hw.height)
        
        # 3. Audio
        self.audio = AudioEngine()
        
        # 4. Brain
        self.brain = AIBrain()
        
        # 5. Media
        self.media = MediaPlayer(self.face)
        
        # State
        self.running = True
        self.state = "IDLE"
        self.last_interaction = time.time()
        self.idle_timeout = config.get('system', {}).get('idle_timeout', 30)

        # Start background face loop
        self.lock = threading.Lock()
        
    def run(self):
        """Main Loop"""
        
        # Threads
        face_thread = threading.Thread(target=self._face_loop)
        face_thread.start()
        
        try:
            self.audio.speak("System Online. Who wants to play video games?")
            
            while self.running:
                # 1. State Management
                now = time.time()
                
                # Check Idle
                if (now - self.last_interaction) > self.idle_timeout and self.state == "IDLE":
                    # Start Idle Music Mode
                    if not pygame.mixer.music.get_busy():
                        print("Entering Idle Mode")
                        self.media.play_random_music()
                        self.face.set_state("HAPPY")
                
                # 2. Listen for Wake Word / Command
                # Simple implementation: Listen loop. 
                # Ideally: Wake word (Picovoice) -> then listen.
                # For now: Just listen continuously if not speaking.
                
                if self.state == "IDLE" or self.state == "HAPPY":
                    user_text = self.audio.listen()
                    
                    if user_text:
                        self.last_interaction = time.time()
                        self.media.stop_music()
                        
                        process_input = False
                        
                        # Check Wake Word (simple string match for now)
                        wake_words = ["hey bmo", "bmo", "beemo"]
                        if any(w in user_text for w in wake_words):
                            process_input = True
                            # Strip wake word
                            for w in wake_words:
                                user_text = user_text.replace(w, "").strip()
                        
                        # If just wake word, prompt
                        if process_input and not user_text:
                            self.state = "LISTENING"
                            self.audio.play_sfx("beep") # Assuming asset exists
                            self.audio.speak("Yes?")
                            user_text = self.audio.listen() # Listen again for command
                        
                        if user_text:
                            self.handle_command(user_text)
                            
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.running = False
            self.audio.speak("Shutting down.")
        finally:
            self.running = False
            face_thread.join()

    def handle_command(self, text):
        print(f"Command: {text}")
        self.state = "THINKING"
        self.face.set_state("THINKING")
        
        # Hardcoded Commands
        if "play music" in text:
            self.media.play_random_music()
            self.state = "HAPPY"
            self.face.set_state("HAPPY")
            return

        if "stop" in text:
            self.media.stop_music()
            self.media.stop_video()
            self.state = "IDLE"
            self.face.set_state("IDLE")
            return
            
        if "play movie" in text or "play film" in text:
            # Look for file
            # Ideally parse filename. defaulting to first found.
            files = os.listdir(self.media.film_path)
            if files:
                self.media.play_video(files[0])
            else:
                self.audio.speak("I don't have any movies.")
            self.state = "IDLE"
            return

        # AI Response
        response = self.brain.get_response(text)
        
        self.state = "SPEAKING"
        self.face.set_state("SPEAKING")
        self.face.set_mouth_open(0.5) # Static open, effectively
        
        self.audio.speak(response)
        
        self.face.set_mouth_open(0)
        self.state = "IDLE"
        self.face.set_state("IDLE")

    def _face_loop(self):
        """Dedicated Rendering Loop"""
        clock = pygame.time.Clock()
        while self.running:
            if not self.media.is_playing_video:
                self.face.update()
                
                # Get image from face renderer
                img_pil = self.face.draw()
                
                # Send to Hardware Display
                self.hw.update_display(img_pil)
                
                # Also verify pygame display flip for dev (headless doesn't need this)
                pygame.display.flip()
            
            clock.tick(30)

if __name__ == "__main__":
    bmo = BMO()
    bmo.run()
