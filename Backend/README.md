# Emotion Detection — Backend

A Flask REST API that classifies the emotional content of free-text input using a classic NLP + machine learning pipeline (TF-IDF + Logistic Regression). Built to serve the `frontend/` React application in this repository, but usable by any client that can make an HTTP request.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [NLP Pipeline](#nlp-pipeline)
- [Model Details](#model-details)
- [Setup & Installation](#setup--installation)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Overview

Given a sentence such as `"I just found out I got the job offer, I can't stop smiling"`, the API returns a probability breakdown across six core emotions:

```
joy      →  61.4%
surprise →  18.9%
love     →   9.2%
sadness  →   5.1%
anger    →   3.1%
fear     →   2.3%
```

The model is trained once offline (`train_model.py`) and served at request time via a single `/predict` endpoint (`app.py`).

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask + Flask-CORS |
| NLP preprocessing | NLTK (tokenization, stopword removal, lemmatization) |
| Feature extraction | scikit-learn `TfidfVectorizer` |
| Classifier | scikit-learn `LogisticRegression` (multi-class, `predict_proba`) |
| Training data | [`dair-ai/emotion`](https://huggingface.co/datasets/dair-ai/emotion) via Hugging Face `datasets` |
| Model persistence | `pickle` |

## Architecture

```
                 ┌─────────────────────┐
                 │   React Frontend     │
                 └──────────┬───────────┘
                             │  POST /predict { text }
                             ▼
                 ┌─────────────────────┐
                 │   Flask API (app.py) │
                 │  - input validation   │
                 │  - NLP cleaning       │
                 │  - dictionary check   │
                 └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼                              ▼
   ┌─────────────────────┐      ┌─────────────────────┐
   │ vectorizer.pkl        │      │ emotion_model.pkl     │
   │ (TF-IDF, fitted)      │      │ (Logistic Regression) │
   └─────────────────────┘      └─────────────────────┘
```

`train_model.py` is a separate, offline script — it is not called at request time. It downloads the dataset, trains the two artifacts above, and saves them to `model/`. `app.py` only ever *loads and applies* those artifacts; it never retrains.

## NLP Pipeline

The exact same `clean_text()` function runs on every sentence, both during training and at prediction time — this consistency is required for the model to see input in the same shape it learned on.

| Step | What it does | Example |
|---|---|---|
| Normalize | Lowercase, strip URLs/punctuation/numbers | `"I'm SO happy!!"` → `"i m so happy"` |
| Tokenize | Split into individual words | `["i", "m", "so", "happy"]` |
| Stop-word removal | Drop low-information filler words | `["happy"]` |
| Length filter | Drop tokens ≤ 2 characters | (removes noise like `"si"`, `"fu"`) |
| Lemmatization | Reduce words to their base/dictionary form | `"running"` → `"run"` |

After cleaning, a **dictionary check** (`has_recognizable_words`) verifies at least one token is a real English word (via NLTK's `words` corpus, ~236k entries) before the text is passed to the model — this rejects pure gibberish (e.g. `"sdhfsa"`) up front, returning a `400` instead of a fabricated prediction.

## Model Details

- **Feature extraction**: TF-IDF over unigrams + bigrams, capped at 8,000 features.
- **Classifier**: Logistic Regression, `class_weight="balanced"` to offset class imbalance in the training data.
- **Labels**: `sadness`, `joy`, `love`, `anger`, `fear`, `surprise` — the six categories provided by the training dataset. There is currently no support for custom labels (e.g. "stress", "depressed") since no reliable public dataset labels for those exist.
- **Output**: `predict_proba()` returns a probability for *every* class on every request (this is how multi-class softmax classifiers work) — a low percentage does not mean "absent," it means "the model weighs this possibility low relative to the others."

## Setup & Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# One-time: downloads the dataset and trains the model (requires internet)
python train_model.py

# Start the API
python app.py
```

The API is now live at `http://localhost:5000`.

## API Reference

### `GET /`
Health check.

```json
{ "status": "ok", "message": "Emotion Detection API is running" }
```

### `POST /predict`

**Request body**
```json
{ "text": "I can't believe I actually did it, I'm so happy right now!" }
```

**Success response — `200 OK`**
```json
{
  "input_text": "I can't believe I actually did it, I'm so happy right now!",
  "top_emotion": "joy",
  "predictions": [
    { "emotion": "joy",      "percentage": 61.4 },
    { "emotion": "surprise", "percentage": 18.9 },
    { "emotion": "love",     "percentage": 9.2  },
    { "emotion": "sadness",  "percentage": 5.1  },
    { "emotion": "anger",    "percentage": 3.1  },
    { "emotion": "fear",     "percentage": 2.3  }
  ]
}
```

**Error responses — `400 Bad Request`**

| Condition | Response |
|---|---|
| Empty/missing `text` | `{ "error": "Please provide non-empty 'text' in the request body." }` |
| Text has no words after cleaning | `{ "error": "Text had no meaningful words after cleaning. Try a longer sentence." }` |
| No recognizable English word found | `{ "error": "Your input doesn't look like real words. Please describe how you're feeling in a sentence." }` |

## Project Structure

```
backend/
├── app.py              # Flask API — loads model, exposes /predict
├── train_model.py       # Offline training script (run once)
├── requirements.txt
├── model/
│   ├── vectorizer.pkl    # Fitted TF-IDF vectorizer (generated by train_model.py)
│   └── emotion_model.pkl # Trained Logistic Regression model (generated by train_model.py)
└── README.md
```

## Known Limitations

- **Out-of-vocabulary real words produce low-signal, low-confidence predictions.** A word like `"sipper"` is a valid English word and passes the dictionary check, but never appeared in training data — the model still returns a prediction, just an unreliable, near-baseline one. There is currently no confidence-threshold safety net to catch and flag this case (see Roadmap).
- **No support for granular labels** like "stress" or "anxiety" — only the six broad categories the training dataset provides.
- **Single-sentence, English-only.** No batch endpoint, no multilingual support.

## Roadmap

- [ ] Confidence-threshold rejection: return an "unable to confidently detect an emotion" response when the top prediction falls below a set probability, catching real-but-irrelevant input like `"sipper si fu th"`.
- [ ] Model calibration (e.g. temperature scaling) so probability outputs better reflect true confidence.
- [ ] `POST /explain` endpoint — LLM-generated natural-language explanation grounded in the model's existing prediction.
- [ ] Batch prediction endpoint.