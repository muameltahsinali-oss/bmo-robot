import cv2
import pygame
import os
import random
import time
from threading import Thread

class MediaPlayer:
    def __init__(self, surface_manager):
        """
        Args:
            surface_manager: Reference to the FaceRenderer or main display surface 
                             to blit video frames to.
        """
        self.surface_manager = surface_manager
        self.music_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'music')
        self.film_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'films')
        
        self.is_playing_video = False
        self.video_thread = None
        self.stop_video_flag = False

    def play_random_music(self):
        """Play a random MP3 from the music folder"""
        try:
            files = [f for f in os.listdir(self.music_path) if f.endswith('.mp3')]
            if not files:
                print("No music found!")
                return
            
            track = random.choice(files)
            full_path = os.path.join(self.music_path, track)
            print(f"Playing: {track}")
            
            # Using Pygame mixer music channel
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Music Error: {e}")

    def stop_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(1000)

    def play_video(self, filename):
        """
        Play a video file on the Pygame surface.
        Args:
            filename: Name of file in assets/films
        """
        path = os.path.join(self.film_path, filename)
        if not os.path.exists(path):
            print(f"Video not found: {path}")
            return

        if self.is_playing_video:
            self.stop_video()

        self.stop_video_flag = False
        self.is_playing_video = True
        self.video_thread = Thread(target=self._video_loop, args=(path,))
        self.video_thread.start()

    def stop_video(self):
        self.stop_video_flag = True
        if self.video_thread:
            self.video_thread.join()
        self.is_playing_video = False

    def _video_loop(self, path):
        """Read frames and blit to surface"""
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        delay = 1.0 / fps

        target_width = self.surface_manager.width
        target_height = self.surface_manager.height

        while not self.stop_video_flag and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize to fit screen
            frame = cv2.resize(frame, (target_width, target_height))
            
            # Convert BGR (OpenCV) to RGB (Pygame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.swapaxes(0, 1) # Pygame surfaces are (width, height)
            
            # Create surface and blit
            # Note: This is a bit inefficient for high res, but fine for 240x240
            frame_surf = pygame.surfarray.make_surface(frame)
            
            # Lock surface if needed (assuming single thread render control in main)
            # For this simple example, we update the FaceRenderer's screen directly
            # which is hacky. Better: update a shared buffer.
            # Here we assume the main loop handles flipping, so we just draw to screen.
            self.surface_manager.screen.blit(frame_surf, (0, 0))
            # Main loop flips, or we flip here?
            # If main loop is running face animation, we override it.
            # Ideally main state machine pauses face loop.

            # We need to manually flip here if we take over control
            # But the main loop might be flipping.
            # Strategy: main loop checks 'is_playing_video', if so, doesn't draw face.
            
            time.sleep(delay)

        cap.release()
        self.is_playing_video = False
