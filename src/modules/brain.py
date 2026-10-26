import openai
import os
import yaml
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', '.env'))

class AIBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
        self.history = [
            {"role": "system", "content": (
                "You are BMO (Beemo) from Adventure Time. "
                "You are a small, teal, living video game console system. "
                "Personality: Playful, loyal, slightly weird, speaks in third person sometimes. "
                "You love Finn and Jake. You can play movies, games, and music. "
                "Keep responses short and conversational. "
                "If asked to play music, say 'Playing music!'. "
                "If asked to play a movie, say 'Playing movie!'."
            )}
        ]

    def get_response(self, user_input):
        """Send input to OpenAI and get response"""
        if not self.api_key:
            return "I need an API key to think! Check my settings."

        self.history.append({"role": "user", "content": user_input})
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o", # Or gpt-3.5-turbo
                messages=self.history,
                max_tokens=100,
                temperature=0.8
            )
            reply = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            
            # Keep history short (sliding window ~10 turns)
            if len(self.history) > 20:
                self.history = [self.history[0]] + self.history[-10:]
                
            return reply
        except Exception as e:
            print(f"Brain Error: {e}")
            return "My brain hurts! I can't think right now."
