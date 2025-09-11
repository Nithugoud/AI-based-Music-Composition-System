import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from config import Config

class MoodAnalyzer:
    def __init__(self):
        self.sentiment_model = pipeline("sentiment-analysis", model=Config.SENTIMENT_MODEL, device=-1)
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.mood_categories = ["happy", "sad", "calm", "energetic", "mysterious", "romantic"]
        self.mood_embeddings = self.embedding_model.encode(self.mood_categories)
        self.high_energy_words = ["excited", "energetic", "workout", "party", "dance", "upbeat"]
        self.low_energy_words = ["calm", "relaxed", "chill", "soft", "slow", "peaceful"]

    def analyze(self, text):
        sentiment = self.sentiment_model(text)[0]
        embedding = self.embedding_model.encode([text])[0]
        similarities = np.dot(self.mood_embeddings, embedding) / (np.linalg.norm(self.mood_embeddings, axis=1) * np.linalg.norm(embedding))
        mood_idx = np.argmax(similarities)
        mood = self.mood_categories[mood_idx]
        energy = self.calculate_energy(text, sentiment)
        return {
            "sentiment": sentiment['label'],
            "sentiment_score": sentiment['score'],
            "mood": mood,
            "energy": energy
        }

    def calculate_energy(self, text, sentiment):
        energy = 5  # base
        high_count = sum(word in text.lower() for word in self.high_energy_words)
        low_count = sum(word in text.lower() for word in self.low_energy_words)
        if sentiment['label'] == "positive":
            energy += 2
        elif sentiment['label'] == "negative":
            energy -= 2
        energy += high_count
        energy -= low_count
        return max(1, min(10, energy))
