import { useNavigate } from "react-router-dom";

function RiskAnalysis({ result }) {
  const navigate = useNavigate();

  if (!result) {
    return (
      <div className="risk-analysis-page">
        <div className="risk-empty-state">
          <div className="risk-empty-icon">🛡️</div>

          <span className="section-label">
            RISK ANALYSIS
          </span>

          <h1>No Risk Analysis Available</h1>

          <p>
            Analyze an order from the dashboard to see
            its AI-powered return and refund risk assessment.
          </p>

          <button
            className="analyze-button"
            onClick={() => navigate("/")}
          >
            Analyze an Order
          </button>
        </div>
      </div>
    );
  }

  const score = Number(result.risk_score || 0);
  const probability = Number(result.risk_probability || 0);
  const riskLevel = result.risk_level || "LOW";

  let riskClass = "low";
  let riskIcon = "✓";

  if (riskLevel === "HIGH") {
    riskClass = "high";
    riskIcon = "⚠️";
  }

  if (riskLevel === "MEDIUM") {
    riskClass = "medium";
    riskIcon = "⚡";
  }

  return (
    <div className="risk-analysis-page">

      <section className="result-header">
        <div>
          <span className="section-label">
            AI RISK ASSESSMENT
          </span>

          <h1>Return Risk Analysis</h1>

          <p>
            RiskShield AI has analyzed the submitted
            customer and order information.
          </p>
        </div>

        <div className={"risk-badge " + riskClass}>
          <span>{riskIcon}</span>
          {riskLevel} RISK
        </div>
      </section>


      <section className={"risk-score-card " + riskClass}>

        <div className="score-circle">
          <div>
            <strong>{score}</strong>
            <span>/ 100</span>
          </div>
        </div>

        <div className="score-info">
          <span className="section-label">
            RISK SCORE
          </span>

          <h2>{result.prediction}</h2>

          <p>
            Estimated probability of risky return or
            refund behavior
          </p>

          <strong className="probability">
            {(probability * 100).toFixed(2)}%
          </strong>
        </div>

      </section>


      <section className={"recommendation-card " + riskClass}>

        <div className="recommendation-icon">
          🛡️
        </div>

        <div>
          <span className="section-label">
            RECOMMENDED ACTION
          </span>

          <h2>{result.recommendation}</h2>

          <p>
            This recommendation supports merchant
            decision-making. The final action should
            remain with an authorized human reviewer.
          </p>
        </div>

      </section>


      <section className="analysis-grid">

        <div className="analysis-card">
          <div className="analysis-card-icon">🤖</div>

          <div>
            <span>AI Prediction</span>
            <strong>{result.prediction}</strong>
          </div>
        </div>


        <div className="analysis-card">
          <div className="analysis-card-icon">📊</div>

          <div>
            <span>Risk Probability</span>
            <strong>
              {(probability * 100).toFixed(2)}%
            </strong>
          </div>
        </div>


        <div className="analysis-card">
          <div className="analysis-card-icon">🎯</div>

          <div>
            <span>Risk Level</span>
            <strong>{riskLevel}</strong>
          </div>
        </div>


        <div className="analysis-card">
          <div className="analysis-card-icon">👤</div>

          <div>
            <span>Decision Mode</span>
            <strong>Human Review</strong>
          </div>
        </div>

      </section>


      <section className="risk-interpretation-card">

        <div className="interpretation-header">
          <div className="interpretation-icon">
            📌
          </div>

          <div>
            <span className="section-label">
              RISK INTERPRETATION
            </span>

            <h2>What does this result mean?</h2>
          </div>
        </div>


        <div className="interpretation-content">

          {riskLevel === "HIGH" && (
            <p>
              This case has a relatively high estimated
              risk. Additional verification or manual review
              may be appropriate before completing the
              return or refund process.
            </p>
          )}

          {riskLevel === "MEDIUM" && (
            <p>
              This case falls into a medium-risk range.
              The merchant may consider additional
              information or verification before making
              the final decision.
            </p>
          )}

          {riskLevel === "LOW" && (
            <p>
              This case falls into a lower-risk range based
              on the information provided. Normal processing
              may be considered, subject to merchant policies
              and human review.
            </p>
          )}

        </div>

      </section>


      <section className="protection-card">

        <div className="protection-icon">
          🔐
        </div>

        <div>
          <span className="section-label">
            RESPONSIBLE DECISION SUPPORT
          </span>

          <h2>
            AI provides a signal — humans make the decision.
          </h2>

          <p>
            RiskShield AI does not automatically reject
            customers or approve refunds. The system provides
            a risk signal so merchants can review potentially
            risky cases while reducing unnecessary friction
            for legitimate customers.
          </p>
        </div>

      </section>


      <div className="result-actions">

        <button
          className="secondary-button"
          onClick={() => navigate("/")}
        >
          Analyze Another Order
        </button>

      </div>

    </div>
  );
}

export default RiskAnalysis;

