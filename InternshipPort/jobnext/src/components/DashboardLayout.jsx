import React from 'react';
import Footer from './Footer';
import './DashboardLayout.css';

export default function DashboardLayout({
  children,
  title,
  subtitle,
  accentClass = '',
  activePage,
  setActivePage,
}) {
  return (
    <div className={`dashboard-wrapper ${accentClass}`}>
      <div className="dashboard-hero">
        <div className="container">
          <h1 className="dashboard-title">{title}</h1>
          {subtitle && <p className="dashboard-subtitle">{subtitle}</p>}
        </div>
      </div>
      <main className="dashboard-main">
        <div className="container">
          {children}
        </div>
      </main>
      <Footer setActivePage={setActivePage} />
    </div>
  );
}
