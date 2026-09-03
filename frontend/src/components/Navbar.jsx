import { NavLink } from "react-router-dom";

function Navbar() {
  return (
    <aside className="sidebar">

      <div className="brand">
        <div className="brand-icon">
          🛡️
        </div>

        <div>
          <h1>RiskShield AI</h1>
          <span>Risk Management</span>
        </div>
      </div>

      <nav className="sidebar-nav">

        <NavLink
          to="/"
          className={({ isActive }) =>
            `nav-item ${isActive ? "active" : ""}`
          }
        >
          <span>▦</span>
          Dashboard
        </NavLink>

        <NavLink
          to="/risk-analysis"
          className={({ isActive }) =>
            `nav-item ${isActive ? "active" : ""}`
          }
        >
          <span>◉</span>
          Risk Analysis
        </NavLink>

      </nav>

      <div className="sidebar-footer">

        <div className="secure-badge">
          <span className="secure-dot"></span>
          Defense-only system
        </div>

        <p>
          AI-powered return and refund
          risk management.
        </p>

      </div>

    </aside>
  );
}

export default Navbar;