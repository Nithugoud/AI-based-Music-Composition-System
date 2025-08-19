from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from config import Config

class MoodAnalyzer:
    def __init__(self):
        # Load sentiment analysis pipeline
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(Config.SENTIMENT_MODEL)
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(Config.SENTIMENT_MODEL)
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.sentiment_model,
            tokenizer=self.sentiment_tokenizer,
            device=0 if Config.DEVICE == "cuda" and torch.cuda.is_available() else -1
        )

        # Load embedding model
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)

    def analyze_sentiment(self, text: str):
        """
        Returns sentiment label and score for the given text.
        """
        result = self.sentiment_pipeline(text)[0]
        return {
            "label": result["label"],
            "score": round(result["score"], 3)
        }

    def get_embedding(self, text: str):
        """
        Returns a vector embedding for semantic similarity tasks.
        """
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()


# 🔹 Testing the analyzer directly
if __name__ == "__main__":
    analyzer = MoodAnalyzer()
    test_text = "I am feeling very happy today because of good music!"
    
    sentiment = analyzer.analyze_sentiment(test_text)
    embedding = analyzer.get_embedding(test_text)

    print("Input Text:", test_text)
    print("Detected Sentiment:", sentiment)
    print("Embedding Vector (first 10 values):", embedding[:10])
