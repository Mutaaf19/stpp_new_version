"""
Stock Price Prediction System — Financial Sentiment Utility
Uses yiyanghkust/finbert-tone (TensorFlow Transformer model) for domain-specific financial news sentiment.
Falls back to VADER sentiment when TensorFlow is unavailable (e.g. Vercel serverless).
Loads the model lazily and caches the tokenizer and model in memory to optimize resources.
"""
import os

# TensorFlow is optional — not available on lightweight deployments (e.g. Vercel)
try:
    import tensorflow as tf
    _TF_AVAILABLE = True
except ImportError:
    tf = None
    _TF_AVAILABLE = False

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
    Analyze sentiment of financial text.
    Uses finbert-tone (FinBERT) when TensorFlow is available,
    otherwise falls back to VADER for lightweight deployments.
    
    Returns:
        float: A score between -1.0 (strongly negative) and +1.0 (strongly positive).
               Neutral is mapped close to 0.0.
    """
    if not text or not text.strip():
        return 0.0

    # --- FinBERT path (full environment with TensorFlow) ---
    if _TF_AVAILABLE:
        try:
            tokenizer, model = get_sentiment_model()
            inputs = tokenizer(
                text,
                return_tensors="tf",
                padding=True,
                truncation=True,
                max_length=512
            )
            outputs = model(inputs)
            logits = outputs.logits
            probs = tf.nn.softmax(logits, axis=-1).numpy()[0]
            # yiyanghkust/finbert-tone: 0=Neutral, 1=Positive, 2=Negative
            compound_score = float(probs[1]) - float(probs[2])
            return round(compound_score, 4)
        except Exception as e:
            print(f"FinBERT sentiment failed, falling back to VADER: {e}")

    # --- VADER fallback (lightweight, no TF needed) ---
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores(text)["compound"]
        return round(score, 4)
    except Exception as e:
        print(f"VADER sentiment failed: {e}")
        return 0.0
