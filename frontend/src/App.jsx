import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import RiskAnalysis from "./pages/RiskAnalysis";
import { API_BASE_URL } from "./api";

import "./App.css";

function AppLayout() {
  const [result, setResult] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("riskshield:last-result")) || null;
    } catch {
      return null;
    }
  });
  const [recentAssessments, setRecentAssessments] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("riskshield:assessments")) || [];
    } catch {
      return [];
    }
  });
  const [backendStatus, setBackendStatus] = useState("connecting");

  useEffect(() => {
    if (result) {
      localStorage.setItem("riskshield:last-result", JSON.stringify(result));
    }
  }, [result]);

  useEffect(() => {
    localStorage.setItem(
      "riskshield:assessments",
      JSON.stringify(recentAssessments)
    );
  }, [recentAssessments]);

  useEffect(() => {
    let mounted = true;

    fetch(`${API_BASE_URL}/health`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend unavailable");
        }
        return response.json();
      })
      .then(() => {
        if (mounted) {
          setBackendStatus("online");
        }
      })
      .catch(() => {
        if (mounted) {
          setBackendStatus("offline");
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const location = useLocation();

  const pageTitles = {
    "/": {
      title: "Dashboard",
      subtitle: "Monitor and analyze return & refund risk"
    },
    "/risk-analysis": {
      title: "Risk Analysis",
      subtitle: "AI-powered return risk assessment"
    },
  };

  const currentPage =
    pageTitles[location.pathname] || pageTitles["/"];

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <header className="top-header">
          <div>
            <h2>{currentPage.title}</h2>
            <p>{currentPage.subtitle}</p>
          </div>

          <div className={"system-status " + backendStatus}>
            <span className="status-dot"></span>
            <span>
              {backendStatus === "online"
                ? "System Online"
                : backendStatus === "offline"
                  ? "Backend Offline"
                  : "Connecting..."}
            </span>
          </div>
        </header>

        <Routes>
          <Route
            path="/"
            element={
              <Dashboard
                setResult={setResult}
                recentAssessments={recentAssessments}
                setRecentAssessments={setRecentAssessments}
              />
            }
          />

          <Route
            path="/risk-analysis"
            element={<RiskAnalysis result={result} />}
          />

        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

export default App;

