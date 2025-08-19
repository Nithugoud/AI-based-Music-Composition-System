# music_parameters.py
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# Load Hugging Face models (sentiment + embeddings)
sentiment_analyzer = pipeline("sentiment-analysis")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def analyze_text(text):
    """Analyze text for sentiment + embeddings"""
    sentiment = sentiment_analyzer(text)[0]
    embedding_vector = embedding_model.encode([text])[0]
    return sentiment, embedding_vector


def map_emotion_to_music(sentiment, embedding_vector):
    """
    Map sentiment + embeddings to music parameters.
    """
    label = sentiment["label"].lower()
    score = sentiment["score"]

    # Default parameters
    params = {
        "tempo": 100,
        "scale": "C major",
        "instrument": "piano",
        "energy": 0.5
    }

    # Adjust based on sentiment
    if label == "positive":
        params["tempo"] = 120 + int(score * 20)  # happier = faster
        params["scale"] = "C major"
        params["instrument"] = "violin"
        params["energy"] = 0.8
    elif label == "negative":
        params["tempo"] = 70 - int(score * 20)   # sadder = slower
        params["scale"] = "A minor"
        params["instrument"] = "cello"
        params["energy"] = 0.3
    else:  # neutral
        params["tempo"] = 90
        params["scale"] = "D major"
        params["instrument"] = "piano"
        params["energy"] = 0.5

    # Use embeddings to vary energy slightly
    params["energy"] += float(embedding_vector[0]) * 0.1
    params["energy"] = max(0.0, min(1.0, params["energy"]))  # clamp 0–1

    return params


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        user_text = " ".join(sys.argv[1:])
    else:
        user_text = "I am feeling happy today because of music."

    print("\nInput Text:", user_text)

    # Step 1.3 + 1.4 combined
    sentiment, embedding = analyze_text(user_text)
    print("Detected Sentiment:", sentiment)

    music_params = map_emotion_to_music(sentiment, embedding)
    print("\nGenerated Music Parameters:", music_params)
