import os
import re
import pickle

import nltk
import pandas as pd
from datasets import load_dataset
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# One-time NLTK resource downloads
for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

# dair-ai/emotion label order (fixed by the dataset itself)
LABEL_NAMES = ["sadness", "joy", "love", "anger", "fear", "surprise"]


# Load dataset 
def load_data() -> pd.DataFrame:
    print("Downloading dataset: dair-ai/emotion ...")
    dataset = load_dataset("dair-ai/emotion")
    train_df = pd.DataFrame(dataset["train"])
    val_df = pd.DataFrame(dataset["validation"])
    test_df = pd.DataFrame(dataset["test"])
    df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    df["label_name"] = df["label"].apply(lambda i: LABEL_NAMES[i])
    print(f"Loaded {len(df)} labeled sentences across {df['label_name'].nunique()} emotions.")
    print(df["label_name"].value_counts())
    return df


# Preprocessing pipeline 
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)            # remove links
    text = re.sub(r"[^a-z\s]", " ", text)                    # keep letters only
    tokens = word_tokenize(text)                              # tokenization
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]  # stop-word removal
    tokens = [LEMMATIZER.lemmatize(t) for t in tokens]        # lemmatization
    return " ".join(tokens)


def main():
    df = load_data()

    print("Cleaning text (tokenize -> remove stopwords -> lemmatize) ...")
    df["clean_text"] = df["text"].apply(clean_text)
    df = df[df["clean_text"].str.strip() != ""]  # drop rows that became empty

    # TF-IDF vectorization 
    print("Vectorizing with TF-IDF ...")
    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df["clean_text"])
    y = df["label_name"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    # Train model 
    print("Training Logistic Regression classifier ...")
    model = LogisticRegression(max_iter=1000, C=5, class_weight="balanced")
    model.fit(X_train, y_train)

    print("\nEvaluation on held-out test set:")
    print(classification_report(y_test, model.predict(X_test)))

    # Save artifacts
    os.makedirs("model", exist_ok=True)
    with open("model/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("model/emotion_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("\nSaved model/vectorizer.pkl and model/emotion_model.pkl")
    print("You can now run: python app.py")


if __name__ == "__main__":
    main()
