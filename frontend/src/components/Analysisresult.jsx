import React from "react";
import "../styles/AnalysisResult.css";
import '../index.css'

const AnalysisResult = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="analysis-state">
        <div className="analysis-loader"></div>
        <p className="analysis-state-text">
          Understanding what you're feeling...
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="analysis-state analysis-empty">
        <p className="analysis-state-text">
          Your emotion analysis will appear here.
        </p>
      </div>
    );
  }

  if (data.error) {
    return (
      <div className="analysis-error">
        <span className="analysis-error-icon">!</span>
        <p>{data.error}</p>
      </div>
    );
  }

  const { top_emotion: topEmotion, predictions = [] } = data;

  return (
    <div className="response-content">

      <div className="top-emotion-card">
        <div className="top-emotion-info">
          <span className="top-emotion-label">PRIMARY EMOTION</span>
          <h3 className="top-emotion-name">{topEmotion}</h3>
        </div>

        
      </div>

      <div className="emotion-breakdown">
        <div className="emotion-breakdown-header">
          <div>
            <h3>Emotion breakdown</h3>
            <p>Here's how your emotions were detected.</p>
          </div>
        </div>

        <ul className="emotion-bars">
          {predictions.map(({ emotion, percentage }) => (
            <li key={emotion} className="emotion-bar-row">

              <div className="emotion-bar-details">
                <span className="emotion-label">
                  {emotion}
                </span>

                <span className="emotion-percentage">
                  {percentage}%
                </span>
              </div>

              <div className="emotion-bar-track">
                <div
                  className="emotion-bar-fill"
                  style={{ width: `${percentage}%` }}
                />
              </div>

            </li>
          ))}
        </ul>
      </div>

    </div>
  );
};

export default AnalysisResult;

