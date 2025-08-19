class Config:
    # Hugging Face sentiment model for mood detection
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # Hugging Face embedding model for semantic similarity
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Maximum sequence length for inputs
    MAX_LENGTH = 128
    
    # Device to run models on (CPU or GPU if available)
    DEVICE = "cpu"
