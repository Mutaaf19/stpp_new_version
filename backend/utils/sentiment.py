"""
Stock Price Prediction System — Financial Sentiment Utility
Uses yiyanghkust/finbert-tone (TensorFlow Transformer model) for domain-specific financial news sentiment.
Loads the model lazily and caches the tokenizer and model in memory to optimize resources.
"""
import os
import tensorflow as tf

_tokenizer = None
_model = None

def get_sentiment_model():
    """Lazily initialize the AutoTokenizer and TF Model."""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
        # Load yiyanghkust/finbert-tone (has complete native TensorFlow weights)
        model_name = "yiyanghkust/finbert-tone"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = TFAutoModelForSequenceClassification.from_pretrained(model_name)
    return _tokenizer, _model


def get_financial_sentiment(text: str) -> float:
    """
    Analyze sentiment of financial text using finbert-tone.
    
    Returns:
        float: A score between -1.0 (strongly negative) and +1.0 (strongly positive).
               Neutral is mapped close to 0.0.
    """
    if not text or not text.strip():
        return 0.0
        
    try:
        tokenizer, model = get_sentiment_model()
        
        # Tokenize text with standard truncation and padding
        inputs = tokenizer(
            text,
            return_tensors="tf",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Run inference in TF
        outputs = model(inputs)
        logits = outputs.logits
        
        # Apply Softmax to get probabilities
        probs = tf.nn.softmax(logits, axis=-1).numpy()[0]
        
        # yiyanghkust/finbert-tone label order:
        # 0: Neutral, 1: Positive, 2: Negative
        pos_prob = float(probs[1])
        neg_prob = float(probs[2])
        
        # Compound score: positive probability minus negative probability
        compound_score = pos_prob - neg_prob
        return round(compound_score, 4)
            
    except Exception as e:
        print(f"Error analyzing sentiment with finbert-tone: {e}")
        return 0.0
