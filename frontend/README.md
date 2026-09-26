# Emotion Detection Model

A full-stack, text-based emotion detection application. Users type a sentence describing how they feel, and the app returns a probability breakdown across six core emotions — powered by a classic NLP + machine learning pipeline, not a black-box API.

> Repository: [`shantanu-nikumbh/Emotion-Detection-Model`](https://github.com/shantanu-nikumbh/Emotion-Detection-Model)

---

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [License](#license)

---

## Demo

**Input**
> "I just found out I got the job offer, I can't stop smiling"

**Output**
| Emotion | Confidence |
|---|---|
| joy | 61.4% |
| surprise | 18.9% |
| love | 9.2% |
| sadness | 5.1% |
| anger | 3.1% |
| fear | 2.3% |

## Features

- Free-text emotion analysis across 6 categories: `joy`, `sadness`, `anger`, `fear`, `love`, `surprise`
- Full transparency into the model's confidence for *every* category, not just the top pick
- Classic, auditable NLP pipeline (tokenization → stop-word removal → lemmatization → TF-IDF), no external LLM dependency for the core prediction
- Input validation that rejects empty or gibberish input before it reaches the model
- Clean separation between a one-time offline training script and a lightweight request-time API

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Flask (Python) |
| NLP | NLTK |
| ML | scikit-learn (TF-IDF + Logistic Regression) |
| Dataset | [`dair-ai/emotion`](https://huggingface.co/datasets/dair-ai/emotion) (Hugging Face) |

## Project Structure

```
Emotion-Detection-Model/
├── frontend/              # React application
│   └── src/components
│               ├── UserInput.js  # Text input + calls POST/predict
│               └── AnalysisResult.jsx # Renders emotion breakdown
├── backend/                # Flask API + ML pipeline
│   ├── app.py
│   ├── train_model.py
│   ├── requirements.txt
│   └── model/               # Trained artifacts (generated, not committed)
└── README.md               # You are here
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Internet access for the one-time dataset download / model training

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python train_model.py           # one-time: downloads data, trains model
python app.py                   # starts API at http://localhost:5000
```

### 2. Frontend

```bash
cd frontend
npm install
npm start                       # starts the React dev server
```

The frontend calls the backend at `http://localhost:5000/predict` — make sure the backend is running first.

## How It Works

```
User types text
      │
      ▼
React frontend (UserInput.jsx)
      │  POST /predict { text }
      ▼
Flask API (app.py)
      │
      ├─ 1. Validate input isn't empty
      ├─ 2. Clean text: tokenize → remove stopwords → lemmatize
      ├─ 3. Reject gibberish (no recognizable English word)
      ├─ 4. Vectorize with TF-IDF
      └─ 5. Classify with Logistic Regression → probabilities per emotion
      │
      ▼
JSON response { top_emotion, predictions: [...] }
      │
      ▼
React frontend renders results (AnalysisResult.jsx)
```

The model itself is trained **once, offline**, by `train_model.py` — the API never retrains on the fly, it only applies the frozen model to new input.

## API Reference

See [`backend/README.md`](./backend/README.md) for the full API reference, including request/response schemas and error cases.

Quick reference:

```
POST /predict
Body: { "text": "your sentence here" }
Response: { "input_text", "top_emotion", "predictions": [{ "emotion", "percentage" }, ...] }
```

## Known Limitations

- Only supports 6 broad emotion categories (no granular labels like "stress" or "anxiety") — no reliable public dataset exists for those.
- A real English word that's simply irrelevant to emotion (e.g. `"sipper"`) can still produce a low-confidence, low-signal prediction, since the current input validation checks word *validity*, not emotional *relevance*. A confidence-threshold safety net is planned (see Roadmap).
- English only, single-sentence input, no batch processing yet.

## Roadmap

- [ ] Confidence-threshold rejection for low-signal predictions
- [ ] Model calibration for more trustworthy probability scores
- [ ] AI-generated natural-language explanation of results (`AiAnalysis` component + `/explain` endpoint)
- [ ] Batch analysis support
- [ ] Deployment guide (Docker / cloud hosting)

## License

Add your preferred license here (e.g. MIT).