import speech_recognition as sr
import pyttsx3
import os
import pygame
import random
import yaml
import time
import threading

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.yaml')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
except:
    config = {}

class AudioEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # TTS Engine Init
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', config.get('audio', {}).get('rate', 150))
        self.tts_engine.setProperty('volume', config.get('system', {}).get('volume', 0.8))
        
        # Audio Player (for SFX)
        pygame.mixer.init()
        
        # Paths
        self.sfx_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sounds')

    def play_sfx(self, sound_name):
        """Play a sound effect from assets/sounds"""
        try:
            path = os.path.join(self.sfx_path, f"{sound_name}.wav")
            if os.path.exists(path):
                pygame.mixer.Sound(path).play()
        except Exception as e:
            print(f"Error playing SFX: {e}")

    def speak(self, text):
        """Convert text to speech"""
        print(f"BMO: {text}")
        # We run this in a thread or blocking depending on need.
        # For simple BMO, blocking is often safer to prevent overlap.
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except RuntimeError:
            # Handle loop already running
            pass

    def listen(self):
        """Listen for audio and return text"""
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return None

        try:
            print("Recognizing...")
            # Use Google Speech Recognition as default fallback for RPi (requires internet)
            # Ideally use generic 'whisper' if setup, but that's heavy on RPi 4.
            # Using google for "online" and sphinx/vosk for "offline" is standard.
            text = self.recognizer.recognize_google(audio)
            print(f"User: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
