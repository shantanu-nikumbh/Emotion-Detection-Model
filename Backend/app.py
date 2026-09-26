
import os
import re
import pickle

import nltk
from flask import Flask, request, jsonify
from flask_cors import CORS
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4", "words"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

# A dictionary of real English words, used to reject gibberish input like
# "sdhfsa" before it ever reaches the model. Built once at startup.
from nltk.corpus import words as nltk_words
ENGLISH_VOCAB = set(w.lower() for w in nltk_words.words())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "emotion_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "vectorizer.pkl")

if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError(
        "Model files not found. Run 'python train_model.py' first to "
        "download the dataset and train the model."
    )

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

app = Flask(__name__)
CORS(app)  # allows the React dev server (different port) to call this API


def clean_text(text: str) -> str:
    """Same preprocessing pipeline used in train_model.py."""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    tokens = [LEMMATIZER.lemmatize(t) for t in tokens]
    return " ".join(tokens)


def has_recognizable_words(cleaned_text: str) -> bool:
    """
    Returns True if at least one token in the cleaned text is a real
    English word (per NLTK's words corpus). Used to catch gibberish
    input (e.g. "sdhfsa") that survives clean_text() as a non-empty
    string but carries no actual meaning for the model to analyze.
    """
    tokens = cleaned_text.split()
    if not tokens:
        return False
    return any(token in ENGLISH_VOCAB for token in tokens)


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Emotion Detection API is running"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please provide non-empty 'text' in the request body."}), 400

    cleaned = clean_text(text)
    if not cleaned:
        return jsonify({"error": "Text had no meaningful words after cleaning. Try a longer sentence."}), 400

    if not has_recognizable_words(cleaned):
        return jsonify({
            "error": "Your input doesn't look like real words. Please describe how you're feeling in a sentence."
        }), 400

    vector = vectorizer.transform([cleaned])
    probabilities = model.predict_proba(vector)[0]
    classes = model.classes_

    results = sorted(
        [
            {"emotion": cls, "percentage": round(float(p) * 100, 2)}
            for cls, p in zip(classes, probabilities)
        ],
        key=lambda x: x["percentage"],
        reverse=True,
    )

    return jsonify({
        "input_text": text,
        "top_emotion": results[0]["emotion"],
        "predictions": results,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)