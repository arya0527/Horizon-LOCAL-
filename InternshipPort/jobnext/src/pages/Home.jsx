import React from 'react';
import Footer from '../components/Footer';
import './Home.css';

const features = [
  {
    icon: '🎯',
    title: 'Resume-to-Job Matching',
    description:
      'Our AI analyzes your resume and matches you with the most relevant jobs and internships based on your skills, experience, and career goals.',
    color: '#dbeafe',
    iconBg: '#2563eb',
  },
  {
    icon: '🚀',
    title: 'Internship Recommendation',
    description:
      'Get personalized internship recommendations tailored to your academic background, skill set, and preferred industry — updated in real time.',
    color: '#ede9fe',
    iconBg: '#7c3aed',
  },
  {
    icon: '🤝',
    title: 'Mentor Discovery',
    description:
      "Connect with industry professionals who match your career aspirations. Book 1:1 sessions and get guidance from those who've been there.",
    color: '#d1fae5',
    iconBg: '#059669',
  },
];

export default function Home({ activePage, setActivePage }) {
  const handleNavClick = (e, path) => {
    e.preventDefault();
    setActivePage(path);
    window.scrollTo(0, 0);
  };

  return (
    <div className="home-wrapper">

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-bg-image" style={{ backgroundImage: 'url(/assets/generated/hero-bg.dim_1440x700.png)' }} />
        <div className="hero-overlay" />
        <div className="container hero-content">
          <div className="hero-badge">🇮🇳 Built for India&apos;s Talent</div>
          <h1 className="hero-headline">
            AI-Powered Career Matching<br />
            <span className="hero-headline-accent">for India</span>
          </h1>
          <p className="hero-subheading">
            Horizon Next connects students, experienced professionals, and companies through intelligent AI matching — helping you find the right opportunity at the right time.
          </p>
          <div className="hero-actions">
            <a href="#" className="btn btn-hero-primary" onClick={(e) => handleNavClick(e, 'internships')}>
              Get Started
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
            <a href="#" className="btn btn-hero-outline" onClick={(e) => handleNavClick(e, 'internships')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              Upload Resume
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section features-section">
        <div className="container">
          <h2 className="section-title">Everything You Need to Succeed</h2>
          <p className="section-subtitle">
            From AI-powered matching to expert mentorship — Horizon Next is your complete career companion.
          </p>
          <div className="features-grid">
            {features.map((feature) => (
              <div key={feature.title} className="feature-card card">
                <div
                  className="feature-icon"
                  style={{ background: feature.color }}
                >
                  <span>{feature.icon}</span>
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-desc">{feature.description}</p>
                <a href="#" className="feature-link" onClick={(e) => handleNavClick(e, 'internships')}>
                  Learn more
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section how-section">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">Get matched with your dream opportunity in three simple steps.</p>
          <div className="how-grid">
            <div className="how-step">
              <div className="how-step-number">01</div>
              <h4>Create Your Profile</h4>
              <p>Upload your resume and fill in your skills, experience, and career preferences.</p>
            </div>
            <div className="how-connector" />
            <div className="how-step">
              <div className="how-step-number">02</div>
              <h4>AI Analyzes &amp; Matches</h4>
              <p>Our AI engine scans thousands of opportunities and ranks them by compatibility.</p>
            </div>
            <div className="how-connector" />
            <div className="how-step">
              <div className="how-step-number">03</div>
              <h4>Apply &amp; Get Hired</h4>
              <p>Apply to matched roles with one click and track your applications in real time.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-card">
            <h2>Ready to Find Your Next Opportunity?</h2>
            <p>Discover internships, jobs, and mentors tailored to your career goals with Horizon Next.</p>
            <div className="cta-actions">
              <a href="#" className="btn btn-hero-primary" onClick={(e) => handleNavClick(e, 'internships')}>
                Explore Internships
              </a>
              <a href="#" className="btn btn-hero-outline" onClick={(e) => handleNavClick(e, 'jobs')}>
                Browse Jobs
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer setActivePage={setActivePage} />
    </div>
  );
}