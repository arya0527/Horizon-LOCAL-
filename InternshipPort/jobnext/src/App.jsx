import React, { useState } from "react";

import Navbar from "./components/Navbar";
import Modal from "./components/Modal";

import Home from "./pages/Home";
import StudentDashboard from "./pages/StudentDashboard";
import ExperiencedDashboard from "./pages/ExperiencedDashboard";
import PlacementDashboard from "./pages/PlacementDashboard";
import Mentors from "./pages/Mentors";
import CompanyDashboard from "./pages/CompanyDashboard";

function App() {

  const [activePage, setActivePage] =
    useState("home");

  const [showLogin, setShowLogin] =
    useState(false);

  const [showSignup, setShowSignup] =
    useState(false);

  return (

    <div className="app-container">

      <Navbar
        activePage={activePage}
        setActivePage={setActivePage}
        setShowLogin={setShowLogin}
        setShowSignup={setShowSignup}
      />

      {showLogin && (
        <Modal
          type="login"
          onClose={() =>
            setShowLogin(false)
          }
        />
      )}

      {showSignup && (
        <Modal
          type="signup"
          onClose={() =>
            setShowSignup(false)
          }
        />
      )}

      {activePage === "home" && (
        <Home
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}

      {activePage === "internships" && (
        <StudentDashboard
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}

      {activePage === "jobs" && (
        <ExperiencedDashboard
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}

      {activePage === "placement" && (
        <PlacementDashboard
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}

      {activePage === "mentors" && (
        <Mentors
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}

      {activePage === "company" && (
        <CompanyDashboard
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}

    </div>
  );
}

export default App;

