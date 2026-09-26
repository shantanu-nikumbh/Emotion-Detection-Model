import React, { useState } from "react";
import AnalysisResult from "./Analysisresult";
import "../styles/UserInput.css";
import '../index.css'

const UserInput = () => {
  const [emotionText, setEmotionText] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!emotionText.trim()) {
      return;
    }

    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: emotionText,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setResponse({ error: data.error || "Something went wrong." });
      } else {
        setResponse(data);
      }
    } catch (error) {
      console.error("Error analyzing emotion:", error);

      setResponse({
        error: "Unable to analyze your emotion. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="user-input-page">
      <section className="user-input-card">

        <div className="user-input-header">
          <span className="user-input-label">EMOTION ANALYSIS</span>

          <h1 className="user-input-title">
            How are you feeling?
          </h1>

          <p className="user-input-description">
            Tell us what is on your mind. You can describe your feelings,
            thoughts, or what happened today.
          </p>
        </div>

        <div className="user-input-form">
          <label htmlFor="emotion-text" className="user-input-field-label">
            Share your thoughts
          </label>

          <textarea
            id="emotion-text"
            className="user-input-textarea"
            value={emotionText}
            onChange={(e) => setEmotionText(e.target.value)}
            placeholder="I have been feeling anxious lately because..."
            rows="6"
          />

          <div className="user-input-action">
            <span className="user-input-helper">
              Your thoughts will be analyzed to identify emotional patterns.
            </span>

            <button
              className="user-input-button"
              onClick={handleAnalyze}
              disabled={loading || !emotionText.trim()}
            >
              {loading ? "Analyzing..." : "Analyze Emotion"}
            </button>
          </div>
        </div>

        <div className="analysis-response">
          <div className="analysis-response-header">
            <h2 className="analysis-response-title">Analysis</h2>
            <span className="analysis-response-indicator"></span>
          </div>

          <div className="analysis-response-content">
            <AnalysisResult data={response} loading={loading} />
          </div>
        </div>

      </section>
    </main>
  );
};

export default UserInput;

