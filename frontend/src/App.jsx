import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [formData, setFormData] = useState({
    customer_age: 25,
    order_amount: 1500,
    previous_orders: 10,
    previous_returns: 1,
    previous_refunds: 0,
    delivery_days: 3,
    discount_percentage: 10,
    customer_account_age_days: 365,
    orders_last_30_days: 3,
    returns_last_90_days: 1,
    return_rate: 0.1,
    refund_rate: 0.05,
    payment_method: "UPI",
    product_category: "Electronics",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const dataToSend = {
        customer_age: Number(formData.customer_age),
        order_amount: Number(formData.order_amount),
        previous_orders: Number(formData.previous_orders),
        previous_returns: Number(formData.previous_returns),
        previous_refunds: Number(formData.previous_refunds),
        delivery_days: Number(formData.delivery_days),
        discount_percentage: Number(formData.discount_percentage),
        customer_account_age_days: Number(
          formData.customer_account_age_days
        ),
        orders_last_30_days: Number(formData.orders_last_30_days),
        returns_last_90_days: Number(formData.returns_last_90_days),
        return_rate: Number(formData.return_rate),
        refund_rate: Number(formData.refund_rate),
        payment_method: formData.payment_method,
        product_category: formData.product_category,
      };

      const response = await fetch(API_URL + "/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(dataToSend),
      });

      if (!response.ok) {
        throw new Error("Prediction request failed");
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to RiskShield AI backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const getRiskClass = () => {
    if (!result) return "";

    if (result.risk_level === "HIGH") {
      return "high";
    }

    if (result.risk_level === "MEDIUM") {
      return "medium";
    }

    return "low";
  };

  return (
    <div className="app">
      {/* Navbar */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">R</div>

          <div>
            <h1>RiskShield AI</h1>
            <span>Return & Refund Risk Management</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Model Online
        </div>
      </header>

      {/* Main Content */}
      <main className="container">
        <section className="hero">
          <div>
            <p className="eyebrow">AI RISK MANAGER</p>

            <h2>
              Detect risky returns
              <br />
              before they cost you.
            </h2>

            <p className="hero-text">
              Analyze customer and order behavior using machine learning
              to identify potentially risky return and refund activity.
            </p>
          </div>

          <div className="model-card">
            <span>MODEL</span>
            <strong>Random Forest</strong>
            <small>Production threshold: 0.43</small>
          </div>
        </section>

        <div className="dashboard">
          {/* Form */}
          <section className="card">
            <div className="card-header">
              <div>
                <h3>Order Analysis</h3>
                <p>Enter order and customer information.</p>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="field">
                  <label>Customer Age</label>
                  <input
                    type="number"
                    name="customer_age"
                    value={formData.customer_age}
                    onChange={handleChange}
                    min="18"
                  />
                </div>

                <div className="field">
                  <label>Order Amount (₹)</label>
                  <input
                    type="number"
                    name="order_amount"
                    value={formData.order_amount}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Previous Orders</label>
                  <input
                    type="number"
                    name="previous_orders"
                    value={formData.previous_orders}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Previous Returns</label>
                  <input
                    type="number"
                    name="previous_returns"
                    value={formData.previous_returns}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Previous Refunds</label>
                  <input
                    type="number"
                    name="previous_refunds"
                    value={formData.previous_refunds}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Delivery Days</label>
                  <input
                    type="number"
                    name="delivery_days"
                    value={formData.delivery_days}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Discount Percentage</label>
                  <input
                    type="number"
                    name="discount_percentage"
                    value={formData.discount_percentage}
                    onChange={handleChange}
                    min="0"
                    max="100"
                  />
                </div>

                <div className="field">
                  <label>Account Age (Days)</label>
                  <input
                    type="number"
                    name="customer_account_age_days"
                    value={formData.customer_account_age_days}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Orders - Last 30 Days</label>
                  <input
                    type="number"
                    name="orders_last_30_days"
                    value={formData.orders_last_30_days}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Returns - Last 90 Days</label>
                  <input
                    type="number"
                    name="returns_last_90_days"
                    value={formData.returns_last_90_days}
                    onChange={handleChange}
                    min="0"
                  />
                </div>

                <div className="field">
                  <label>Return Rate</label>
                  <input
                    type="number"
                    step="0.01"
                    name="return_rate"
                    value={formData.return_rate}
                    onChange={handleChange}
                    min="0"
                    max="1"
                  />
                </div>

                <div className="field">
                  <label>Refund Rate</label>
                  <input
                    type="number"
                    step="0.01"
                    name="refund_rate"
                    value={formData.refund_rate}
                    onChange={handleChange}
                    min="0"
                    max="1"
                  />
                </div>

                <div className="field">
                  <label>Payment Method</label>

                  <select
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleChange}
                  >
                    <option value="UPI">UPI</option>
                    <option value="Credit Card">Credit Card</option>
                    <option value="Debit Card">Debit Card</option>
                    <option value="Cash on Delivery">
                      Cash on Delivery
                    </option>
                    <option value="Net Banking">Net Banking</option>
                  </select>
                </div>

                <div className="field">
                  <label>Product Category</label>

                  <select
                    name="product_category"
                    value={formData.product_category}
                    onChange={handleChange}
                  >
                    <option value="Electronics">Electronics</option>
                    <option value="Clothing">Clothing</option>
                    <option value="Beauty">Beauty</option>
                    <option value="Home">Home</option>
                    <option value="Sports">Sports</option>
                    <option value="Books">Books</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="predict-button"
                disabled={loading}
              >
                {loading ? "Analyzing Order..." : "Analyze Return Risk"}
              </button>
            </form>

            {error && <div className="error-box">{error}</div>}
          </section>

          {/* Result */}
          <section className="card result-card">
            <div className="card-header">
              <div>
                <h3>AI Risk Assessment</h3>
                <p>Machine learning prediction</p>
              </div>
            </div>

            {!result && !loading && (
              <div className="empty-state">
                <div className="empty-icon">AI</div>

                <h3>Ready to analyze</h3>

                <p>
                  Enter the order information and click
                  <strong> Analyze Return Risk </strong>
                  to generate an AI prediction.
                </p>
              </div>
            )}

            {loading && (
              <div className="empty-state">
                <div className="loader"></div>

                <h3>Analyzing...</h3>

                <p>
                  RiskShield AI is evaluating the order behavior.
                </p>
              </div>
            )}

            {result && (
              <div className="result-content">
                <div className={`risk-circle ${getRiskClass()}`}>
                  <span>{result.risk_score}</span>
                  <small>/ 100</small>
                </div>

                <div className={`risk-badge ${getRiskClass()}`}>
                  {result.risk_level} RISK
                </div>

                <h2>{result.prediction}</h2>

                <p className="probability">
                  Risk probability:{" "}
                  <strong>
                    {(result.risk_probability * 100).toFixed(2)}%
                  </strong>
                </p>

                <div className="recommendation">
                  <span>Recommended Action</span>

                  <strong>{result.recommendation}</strong>
                </div>

                <div className="explanation">
                  <h3>Risk Assessment</h3>

                  <p>
                    The model evaluated customer history, order
                    characteristics, return behavior, refund behavior,
                    payment method, and product category.
                  </p>
                </div>
              </div>
            )}
          </section>
        </div>

        {/* Metrics */}
        <section className="metrics-section">
          <div className="section-title">
            <p className="eyebrow">MODEL PERFORMANCE</p>
            <h2>Measured on held-out test data</h2>
          </div>

          <div className="metrics-grid">
            <div className="metric">
              <span>Precision</span>
              <strong>51.53%</strong>
              <small>Risky predictions that were correct</small>
            </div>

            <div className="metric">
              <span>Recall</span>
              <strong>60.54%</strong>
              <small>Risky orders successfully detected</small>
            </div>

            <div className="metric">
              <span>F1 Score</span>
              <strong>55.68%</strong>
              <small>Balance of precision and recall</small>
            </div>

            <div className="metric">
              <span>ROC-AUC</span>
              <strong>75.83%</strong>
              <small>Overall ranking performance</small>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer>
          <div>
            <strong>RiskShield AI</strong>
            <span>Defense-only AI Risk Management</span>
          </div>

          <p>
            Prototype system • Metrics based on synthetic test data
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;