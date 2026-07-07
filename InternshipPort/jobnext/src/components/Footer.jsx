import React from 'react';
import './Footer.css';

export default function Footer({ setActivePage }) {
  const year = new Date().getFullYear();

  const handleNavClick = (e, path) => {
    e.preventDefault();
    if (setActivePage) {
      setActivePage(path);
      window.scrollTo(0, 0);
    }
  };

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="footer-logo-row">
              <img src="/assets/generated/logo.dim_200x48.png" alt="Horizon Next" className="footer-logo" />
              <span className="footer-brand-name">Horizon Next</span>
            </div>
            <p className="footer-tagline">
              AI-powered career matching platform connecting students, professionals, and companies across India.
            </p>
          </div>

          <div className="footer-col">
            <h4 className="footer-col-title">Platform</h4>
            <ul className="footer-links">
              <li><a href="#" onClick={(e) => handleNavClick(e, 'internships')}>Internships</a></li>
              <li><a href="#" onClick={(e) => handleNavClick(e, 'jobs')}>Jobs</a></li>
              <li><a href="#" onClick={(e) => handleNavClick(e, 'mentors')}>Mentors</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4 className="footer-col-title">For Organizations</h4>
            <ul className="footer-links">
              <li><a href="#" onClick={(e) => handleNavClick(e, 'placement')}>Placement Authority</a></li>
              <li><a href="#" onClick={(e) => handleNavClick(e, 'company')}>Company Dashboard</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4 className="footer-col-title">Company</h4>
            <ul className="footer-links">
              <li><a href="#">About Us</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copy">
            &copy; {year} Horizon Next. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
