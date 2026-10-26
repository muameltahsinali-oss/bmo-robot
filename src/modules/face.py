import os
import pygame
import time
import random
from PIL import Image

class FaceRenderer:
    def __init__(self, width=240, height=240):
        self.width = width
        self.height = height
        
        # Load config to check display mode
        try:
            import yaml
            CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.yaml')
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f)
                display_mode = config.get('system', {}).get('display_mode', 'tft')
        except:
             display_mode = 'tft'

        # Initialize Pygame
        # Only use dummy driver if we are targeting the SPI TFT (headless from OS perspective)
        if display_mode == 'tft':
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        
        # Colors
        self.COLOR_BG = (100, 220, 190) # BMO Teal
        self.COLOR_FACE = (0, 0, 0)     # Black
        
        # State
        self.current_state = "IDLE"
        self.last_blink = time.time()
        self.blink_interval = random.uniform(2.0, 6.0)
        self.is_blinking = False
        self.blink_start_time = 0
        self.mouth_open_amount = 0

    def set_state(self, state):
        self.current_state = state

    def set_mouth_open(self, amount):
        """Set mouth openness (0.0 to 1.0) for lip sync"""
        self.mouth_open_amount = amount

    def update(self):
        """Update animation logic"""
        now = time.time()
        
        # Blink Logic
        if not self.is_blinking and (now - self.last_blink > self.blink_interval):
            self.is_blinking = True
            self.blink_start_time = now
            self.blink_interval = random.uniform(2.0, 6.0)
        
        if self.is_blinking and (now - self.blink_start_time > 0.2):
            self.is_blinking = False
            self.last_blink = now

    def draw(self):
        """Render the face to the surface and return PIL image"""
        self.screen.fill(self.COLOR_BG)
        
        # Coordinates
        left_eye_pos = (self.width // 3, self.height // 3)
        right_eye_pos = (self.width * 2 // 3, self.height // 3)
        eye_radius = 10
        
        # Draw Eyes
        if self.is_blinking:
            # Draw closed eyes (lines)
            pygame.draw.line(self.screen, self.COLOR_FACE, (left_eye_pos[0]-10, left_eye_pos[1]), (left_eye_pos[0]+10, left_eye_pos[1]), 3)
            pygame.draw.line(self.screen, self.COLOR_FACE, (right_eye_pos[0]-10, right_eye_pos[1]), (right_eye_pos[0]+10, right_eye_pos[1]), 3)
        else:
            if self.current_state == "LISTENING":
                # Big eyes
                pygame.draw.circle(self.screen, self.COLOR_FACE, left_eye_pos, eye_radius + 5)
                pygame.draw.circle(self.screen, self.COLOR_FACE, right_eye_pos, eye_radius + 5)
            elif self.current_state == "THINKING":
                # One big one small
                pygame.draw.circle(self.screen, self.COLOR_FACE, left_eye_pos, eye_radius + 5)
                pygame.draw.circle(self.screen, self.COLOR_FACE, right_eye_pos, eye_radius - 2)
            else:
                # Normal
                pygame.draw.circle(self.screen, self.COLOR_FACE, left_eye_pos, eye_radius)
                pygame.draw.circle(self.screen, self.COLOR_FACE, right_eye_pos, eye_radius)

        # Draw Mouth
        mouth_center = (self.width // 2, self.height // 2 + 30)
        
        if self.current_state == "SPEAKING":
            # Animated mouth rectangle
            height = 10 + (20 * self.mouth_open_amount)
            rect = pygame.Rect(mouth_center[0]-20, mouth_center[1]-height/2, 40, height)
            pygame.draw.rect(self.screen, self.COLOR_FACE, rect, border_radius=5)
            
        elif self.current_state == "HAPPY":
            # Smile arc
            rect = pygame.Rect(mouth_center[0]-25, mouth_center[1]-20, 50, 40)
            pygame.draw.arc(self.screen, self.COLOR_FACE, rect, 3.14, 0, 3)
            
        elif self.current_state == "THINKING":
            # Flat line
            pygame.draw.line(self.screen, self.COLOR_FACE, (mouth_center[0]-15, mouth_center[1]), (mouth_center[0]+15, mouth_center[1]), 3)
            
        else: # IDLE / LISTENING
            # Small smile
            rect = pygame.Rect(mouth_center[0]-15, mouth_center[1]-10, 30, 20)
            pygame.draw.arc(self.screen, self.COLOR_FACE, rect, 3.14, 0, 3)

        # Convert to PIL Image for the Hardware Manager
        # Pygame surface -> String buffer -> PIL Image
        data = pygame.image.tostring(self.screen, 'RGB')
        img = Image.frombytes('RGB', (self.width, self.height), data)
        return img
