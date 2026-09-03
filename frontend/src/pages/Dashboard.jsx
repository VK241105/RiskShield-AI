import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard({
  setResult,
  recentAssessments,
  setRecentAssessments
}) {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    customer_age: "",
    order_amount: "",
    previous_orders: "",
    previous_returns: "",
    previous_refunds: "",
    delivery_days: "",
    discount_percentage: "",
    account_created_date: "",
    orders_last_30_days: "",
    returns_last_90_days: "",
    payment_method: "",
    product_category: ""
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedAssessment, setSelectedAssessment] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/assessments")
      .then((response) => {
        if (!response.ok) {
          throw new Error("History unavailable");
        }
        return response.json();
      })
      .then(({ assessments }) => {
        setRecentAssessments(assessments.map((item) => ({
          id: item.id,
          orderData: item.order_data,
          amount: item.order_data.order_amount,
          category: item.order_data.product_category,
          riskScore: item.result.risk_score,
          riskLevel: item.result.risk_level,
          reviewStatus: item.review_status,
          reviewerNote: item.reviewer_note,
          time: new Date(item.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
          })
        })));
      })
      .catch(() => {});
  }, [setRecentAssessments]);

  const accountAgeInDays = formData.account_created_date
    ? Math.max(
      0,
      Math.floor(
        (Date.now() - new Date(formData.account_created_date).getTime()) /
        (1000 * 60 * 60 * 24)
      )
    )
    : "";

  const loadDemoCase = () => {
    setFormData({
      customer_age: "29",
      order_amount: "1599",
      previous_orders: "12",
      previous_returns: "3",
      previous_refunds: "2",
      delivery_days: "4",
      discount_percentage: "18",
      account_created_date: "2023-06-15",
      orders_last_30_days: "3",
      returns_last_90_days: "2",
      payment_method: "UPI",
      product_category: "Fashion"
    });
    setError("");
  };

  const exportHistory = () => {
    if (recentAssessments.length === 0) {
      return;
    }

    const headers = [
      "time",
      "amount",
      "category",
      "risk_score",
      "risk_level",
      "review_status",
      "reviewer_note",
      "customer_age",
      "account_age_days",
      "previous_orders",
      "previous_returns",
      "previous_refunds",
      "payment_method"
    ];
    const rows = recentAssessments.map((item) => {
      const data = item.orderData || {};
      return [
        item.time,
        item.amount,
        item.category,
        item.riskScore,
        item.riskLevel,
        item.reviewStatus || "PENDING",
        item.reviewerNote || "",
        data.customer_age || "",
        data.customer_account_age_days || "",
        data.previous_orders || "",
        data.previous_returns || "",
        data.previous_refunds || "",
        data.payment_method || ""
      ];
    });
    const csv = [headers, ...rows]
      .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))
      .join("\n");
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    link.download = "riskshield-assessment-history.csv";
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const clearHistory = () => {
    if (window.confirm("Clear all saved assessment history?")) {
      fetch("http://127.0.0.1:8000/assessments", {
        method: "DELETE"
      }).catch(() => {});
      setRecentAssessments([]);
    }
  };

  const deleteAssessment = (assessmentId) => {
    fetch(`http://127.0.0.1:8000/assessments/${assessmentId}`, {
      method: "DELETE"
    }).catch(() => {});
    setRecentAssessments((previous) => previous.filter((item) => item.id !== assessmentId));
    if (selectedAssessment?.id === assessmentId) {
      setSelectedAssessment(null);
    }
  };

  const validateForm = () => {
    if (!formData.account_created_date || accountAgeInDays === "") {
      return "Select the date when the customer account was created.";
    }

    if (accountAgeInDays < 0) {
      return "Account creation date cannot be in the future.";
    }

    if (Number(formData.previous_returns) > Number(formData.previous_orders)) {
      return "Previous returns cannot be greater than previous orders.";
    }

    if (Number(formData.previous_refunds) > Number(formData.previous_orders)) {
      return "Previous refunds cannot be greater than previous orders.";
    }

    if (Number(formData.returns_last_90_days) > Number(formData.previous_orders) + Number(formData.orders_last_30_days)) {
      return "Recent returns cannot exceed the available order history.";
    }

    return "";
  };

  const updateReview = (assessmentId, reviewStatus, reviewerNote) => {
    fetch(`http://127.0.0.1:8000/assessments/${assessmentId}/review`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        review_status: reviewStatus,
        reviewer_note: reviewerNote
      })
    }).catch(() => {});
    setRecentAssessments((previous) => previous.map((item) => (
      item.id === assessmentId
        ? { ...item, reviewStatus, reviewerNote }
        : item
    )));
    setSelectedAssessment((current) => (
      current && current.id === assessmentId
        ? { ...current, reviewStatus, reviewerNote }
        : current
    ));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData({
      ...formData,
      [name]: value
    });

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const orderData = {
        customer_age: Number(formData.customer_age),
        order_amount: Number(formData.order_amount),
        previous_orders: Number(formData.previous_orders),
        previous_returns: Number(formData.previous_returns),
        previous_refunds: Number(formData.previous_refunds),
        delivery_days: Number(formData.delivery_days),
        discount_percentage: Number(
          formData.discount_percentage
        ),
        customer_account_age_days: Number(accountAgeInDays),
        orders_last_30_days: Number(
          formData.orders_last_30_days
        ),
        returns_last_90_days: Number(
          formData.returns_last_90_days
        ),
        payment_method: formData.payment_method,
        product_category: formData.product_category
      };

      const response = await fetch(
        "http://127.0.0.1:8000/predict",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(orderData)
        }
      );

      if (!response.ok) {
        throw new Error("Prediction failed");
      }

      const data = await response.json();

      setResult(data);

      const newAssessment = {
        id: Date.now(),
        orderData,
        amount: orderData.order_amount,
        category: orderData.product_category,
        riskScore: data.risk_score,
        riskLevel: data.risk_level,
        reviewStatus: "PENDING",
        reviewerNote: "",
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit"
        })
      };

      setRecentAssessments((previous) => [
        newAssessment,
        ...previous
      ].slice(0, 5));

      navigate("/risk-analysis");

    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the RiskShield AI backend. Please make sure the FastAPI server is running."
      );

    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      customer_age: "",
      order_amount: "",
      previous_orders: "",
      previous_returns: "",
      previous_refunds: "",
      delivery_days: "",
      discount_percentage: "",
      account_created_date: "",
      orders_last_30_days: "",
      returns_last_90_days: "",
      payment_method: "",
      product_category: ""
    });

    setError("");
  };

  return (
    <div className="dashboard-page">

      {/* INTRODUCTION */}

      <section className="dashboard-intro">

        <div>
          <span className="section-label">
            AI RISK MANAGER
          </span>

          <h1>
            Analyze a return or refund case
          </h1>

          <p>
            Detect return and refund risk before it becomes
            avoidable merchant loss.
          </p>
        </div>

        <div className="dashboard-tools">
          <div className="dashboard-status">
            <span className="status-dot"></span>
            Decision Support
          </div>
          <button type="button" className="utility-button" onClick={loadDemoCase}>
            Load Demo Case
          </button>
        </div>

      </section>


      {/* MAIN CONTENT */}

      <div className="dashboard-grid">

        {/* FORM */}

        <section className="dashboard-card">

          <div className="card-header">

            <div>
              <span className="section-label">
                ORDER INFORMATION
              </span>

              <h2>
                Return Risk Assessment
              </h2>

              <p>
                Enter the available information for
                the customer and order.
              </p>
            </div>

          </div>


          <form onSubmit={handleSubmit}>

            {/* CUSTOMER */}

            <div className="form-block">

              <h3>
                <span>01</span>
                Customer Information
              </h3>

              <div className="form-grid">

                <div className="form-group">
                  <label>
                    Customer Age
                  </label>

                  <input
                    type="number"
                    name="customer_age"
                    min="18"
                    max="100"
                    placeholder="e.g. 25"
                    value={formData.customer_age}
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Account Created Date
                  </label>

                  <input
                    type="date"
                    name="account_created_date"
                    max={new Date().toISOString().split("T")[0]}
                    value={formData.account_created_date}
                    onChange={handleChange}
                    required
                  />

                  <small className="field-hint">
                    {accountAgeInDays === ""
                      ? "Account age is calculated automatically."
                      : `${accountAgeInDays} days of account history`}
                  </small>
                </div>


                <div className="form-group">
                  <label>
                    Previous Orders
                  </label>

                  <input
                    type="number"
                    name="previous_orders"
                    min="0"
                    placeholder="e.g. 20"
                    value={formData.previous_orders}
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Orders — Last 30 Days
                  </label>

                  <input
                    type="number"
                    name="orders_last_30_days"
                    min="0"
                    placeholder="e.g. 5"
                    value={
                      formData.orders_last_30_days
                    }
                    onChange={handleChange}
                    required
                  />
                </div>

              </div>

            </div>


            {/* RETURN HISTORY */}

            <div className="form-block">

              <h3>
                <span>02</span>
                Return & Refund History
              </h3>

              <div className="form-grid">

                <div className="form-group">
                  <label>
                    Previous Returns
                  </label>

                  <input
                    type="number"
                    name="previous_returns"
                    min="0"
                    placeholder="e.g. 2"
                    value={formData.previous_returns}
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Previous Refunds
                  </label>

                  <input
                    type="number"
                    name="previous_refunds"
                    min="0"
                    placeholder="e.g. 1"
                    value={formData.previous_refunds}
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Returns — Last 90 Days
                  </label>

                  <input
                    type="number"
                    name="returns_last_90_days"
                    min="0"
                    placeholder="e.g. 2"
                    value={
                      formData.returns_last_90_days
                    }
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Discount Percentage
                  </label>

                  <input
                    type="number"
                    name="discount_percentage"
                    min="0"
                    max="100"
                    step="0.1"
                    placeholder="e.g. 10"
                    value={
                      formData.discount_percentage
                    }
                    onChange={handleChange}
                    required
                  />
                </div>

              </div>

            </div>


            {/* ORDER DETAILS */}

            <div className="form-block">

              <h3>
                <span>03</span>
                Order Details
              </h3>

              <div className="form-grid">

                <div className="form-group">
                  <label>
                    Order Amount (₹)
                  </label>

                  <input
                    type="number"
                    name="order_amount"
                    min="0"
                    step="0.01"
                    placeholder="e.g. 2499"
                    value={formData.order_amount}
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Delivery Time (days)
                  </label>

                  <input
                    type="number"
                    name="delivery_days"
                    min="0"
                    step="0.1"
                    placeholder="e.g. 3"
                    value={formData.delivery_days}
                    onChange={handleChange}
                    required
                  />
                </div>


                <div className="form-group">
                  <label>
                    Payment Method
                  </label>

                  <select
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleChange}
                    required
                  >
                    <option value="">
                      Select payment method
                    </option>

                    <option value="UPI">
                      UPI
                    </option>

                    <option value="Credit Card">
                      Credit Card
                    </option>

                    <option value="Debit Card">
                      Debit Card
                    </option>

                    <option value="Cash on Delivery">
                      Cash on Delivery
                    </option>

                    <option value="Wallet">
                      Wallet
                    </option>
                  </select>
                </div>


                <div className="form-group">
                  <label>
                    Product Category
                  </label>

                  <select
                    name="product_category"
                    value={formData.product_category}
                    onChange={handleChange}
                    required
                  >
                    <option value="">
                      Select category
                    </option>

                    <option value="Fashion">
                      Fashion
                    </option>

                    <option value="Grocery">
                      Grocery
                    </option>

                    <option value="Accessories">
                      Accessories
                    </option>

                    <option value="Electronics">
                      Electronics
                    </option>

                    <option value="Home">
                      Home
                    </option>
                  </select>
                </div>

              </div>

            </div>


            {/* ERROR MESSAGE */}

            {error && (
              <div className="dashboard-error">
                ⚠️ {error}
              </div>
            )}


            {/* BUTTONS */}

            <div className="dashboard-actions">

              <button
                type="button"
                className="reset-button"
                onClick={resetForm}
                disabled={loading}
              >
                Reset
              </button>

              <button
                type="submit"
                className="analyze-button"
                disabled={loading}
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze Return Risk →"}
              </button>

            </div>

          </form>

        </section>


        {/* RIGHT SIDE */}

        <aside className="dashboard-sidebar">

          {/* RESULT INFORMATION */}

          <div className="dashboard-side-card">

            <span className="section-label">
              ASSESSMENT OUTPUT
            </span>

            <h3>
              What you will receive
            </h3>

            <div className="output-item">
              <span>Risk Score</span>
              <strong>0 — 100</strong>
            </div>

            <div className="output-item">
              <span>Risk Probability</span>
              <strong>AI Estimate</strong>
            </div>

            <div className="output-item">
              <span>Risk Level</span>
              <strong>Low / Medium / High</strong>
            </div>

            <div className="output-item">
              <span>Recommended Action</span>
              <strong>Decision Support</strong>
            </div>

          </div>


          {/* RECENT ASSESSMENTS */}

          <div className="dashboard-side-card">

            <div className="side-card-title">
              <div>
                <span className="section-label">
                  ACTIVITY
                </span>

                <h3>
                  Recent Assessments
                </h3>
              </div>

              <div className="history-tools">
                <span className="activity-count">{recentAssessments.length}</span>
                <button
                  type="button"
                  className="history-action"
                  onClick={exportHistory}
                  disabled={recentAssessments.length === 0}
                >
                  Export
                </button>
                <button
                  type="button"
                  className="history-action danger"
                  onClick={clearHistory}
                  disabled={recentAssessments.length === 0}
                >
                  Clear
                </button>
              </div>
            </div>


            {recentAssessments.length === 0 ? (

              <div className="recent-empty">
                <span>🕘</span>

                <p>
                  No assessments yet.
                  <br />
                  Your recent checks will appear here.
                </p>
              </div>

            ) : (

              <div className="recent-list">

                {recentAssessments.map((item) => (

                  <div
                    className="recent-item"
                    key={item.id}
                    role="button"
                    tabIndex="0"
                    onClick={() => setSelectedAssessment(item)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        setSelectedAssessment(item);
                      }
                    }}
                  >

                    <div>
                      <strong>
                        ₹
                        {Number(
                          item.amount
                        ).toLocaleString("en-IN")}
                      </strong>

                      <span>
                        {item.category}
                      </span>
                    </div>

                    <div className="recent-score">

                      <strong>
                        {item.riskScore}
                      </strong>

                      <span>
                        {item.time}
                      </span>

                    </div>

                    <span className={"review-status " + (item.reviewStatus === "REVIEWED" ? "reviewed" : "pending")}>
                      {item.reviewStatus === "REVIEWED" ? "Reviewed" : "Pending"}
                    </span>

                    <button
                      type="button"
                      className="recent-delete"
                      aria-label="Delete assessment"
                      onClick={(event) => {
                        event.stopPropagation();
                        deleteAssessment(item.id);
                      }}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.stopPropagation();
                          deleteAssessment(item.id);
                        }
                      }}
                    >
                      x
                    </button>

                  </div>

                ))}

              </div>

            )}

          </div>


          {/* DEFENSE ONLY */}

          <div className="dashboard-defense">

            <div>
              🔐
            </div>

            <section>

              <strong>
                Defense-only system
              </strong>

              <p>
                RiskShield AI provides risk signals to
                support authorized merchant review.
                Final decisions remain with a human.
              </p>

            </section>

          </div>

        </aside>

      </div>

      {selectedAssessment && (
        <div className="assessment-modal-backdrop" onClick={() => setSelectedAssessment(null)}>
          <section
            className="assessment-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="assessment-detail-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="assessment-modal-header">
              <div>
                <span className="section-label">SAVED ASSESSMENT</span>
                <h2 id="assessment-detail-title">Assessment details</h2>
                <p>{selectedAssessment.time} · {selectedAssessment.category}</p>
              </div>
              <button
                type="button"
                className="modal-close"
                aria-label="Close assessment details"
                onClick={() => setSelectedAssessment(null)}
              >
                x
              </button>
            </div>

            <div className="assessment-detail-result">
              <div><span>Risk score</span><strong>{selectedAssessment.riskScore} / 100</strong></div>
              <div><span>Risk level</span><strong>{selectedAssessment.riskLevel}</strong></div>
            </div>

            <div className="review-panel">
              <div className="review-panel-heading">
                <div>
                  <span className="section-label">HUMAN REVIEW</span>
                  <strong>{selectedAssessment.reviewStatus || "PENDING"}</strong>
                </div>
                {selectedAssessment.reviewStatus !== "REVIEWED" && (
                  <button
                    type="button"
                    className="review-button"
                    onClick={() => updateReview(selectedAssessment.id, "REVIEWED", selectedAssessment.reviewerNote || "")}
                  >
                    Mark Reviewed
                  </button>
                )}
              </div>
              <label htmlFor="reviewer-note">Reviewer note</label>
              <textarea
                id="reviewer-note"
                rows="3"
                placeholder="Record the reason for the review..."
                value={selectedAssessment.reviewerNote || ""}
                onChange={(event) => updateReview(selectedAssessment.id, selectedAssessment.reviewStatus || "PENDING", event.target.value)}
              />
            </div>

            <div className="assessment-detail-grid">
              {Object.entries(selectedAssessment.orderData || {}).map(([key, value]) => (
                <div key={key}>
                  <span>{key.replaceAll("_", " ")}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}

    </div>
  );
}

export default Dashboard;

