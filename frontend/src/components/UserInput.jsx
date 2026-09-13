import React, { useState } from "react";

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
      // Replace this URL with your backend API
      const res = await fetch("http://localhost:5000/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: emotionText,
        }),
      });

      const data = await res.json();

      setResponse(data);
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
    <div className="user-input">

      {/* Heading */}
      <h1>How are you feeling?</h1>

      <p>
        Tell us what is on your mind. You can describe your feelings,
        thoughts, or what happened today.
      </p>

      {/* User Input */}
      <textarea
        value={emotionText}
        onChange={(e) => setEmotionText(e.target.value)}
        placeholder="I have been feeling anxious lately because..."
        rows="6"
      />

      {/* Analyze Button */}
      <button
        onClick={handleAnalyze}
        disabled={loading || !emotionText.trim()}
      >
        {loading ? "Analyzing..." : "Analyze Emotion"}
      </button>

      {/* Backend Response */}
      <div className="analysis-response">

        <h2> Analysis</h2>

        {!response && !loading && (
          <p>
            Your emotion analysis will appear here.
          </p>
        )}

        {loading && (
          <p>
            Understanding what you're feeling...
          </p>
        )}

        {response && (
          <div className="response-content">
            {response.error ? (
              <p>{response.error}</p>
            ) : (
              <>
                <p>
                  <strong>Emotion:</strong>{" "}
                  {response.emotion}
                </p>

                <p>
                  <strong>Confidence:</strong>{" "}
                  {response.confidence}%
                </p>

                <p>
                  <strong>Analysis:</strong>{" "}
                  {response.analysis}
                </p>
              </>
            )}
          </div>
        )}

      </div>
    </div>
  );
};

export default UserInput;

