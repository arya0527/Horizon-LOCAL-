import React, { useState } from 'react';
import './Navbar.css';

export default function Navbar({ activePage, setActivePage, setShowLogin, setShowSignup }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const navLinks = [
    { label: 'Internships', path: 'internships' },
    { label: 'Jobs', path: 'jobs' },
    { label: 'Mentors', path: 'mentors' },
    { label: 'Placement Authority', path: 'placement' },
    { label: 'Company', path: 'company' },
  ];

  const handleNavClick = (path) => {
    setActivePage(path);
    setMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <a href="#" className="navbar-brand" onClick={() => handleNavClick('home')}>
          <img src="/assets/generated/logo.dim_200x48.png" alt="Horizon Next" className="navbar-logo" />
          <span className="navbar-brand-text">Horizon Next</span>
        </a>

        <button
          className={`navbar-hamburger ${menuOpen ? 'open' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
          {navLinks.map((link) => (
            <a
              key={link.path}
              href="#"
              className={`navbar-link ${activePage === link.path ? 'active' : ''}`}
              onClick={() => handleNavClick(link.path)}
            >
              {link.label}
            </a>
          ))}
          <div className="navbar-auth">
            {localStorage.getItem("user") ? (
              <>
                <span className="navbar-user-greeting" style={{ fontSize: "0.875rem", fontWeight: "600", color: "var(--gray-700)", marginRight: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                  👤 {JSON.parse(localStorage.getItem("user")).name}
                </span>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => {
                    localStorage.removeItem("user");
                    window.location.reload();
                  }}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => setShowLogin(true)}
                >
                  Login
                </button>

                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => setShowSignup(true)}
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
