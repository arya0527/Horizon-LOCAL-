import React, { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import MentorCard from '../components/MentorCard';
import { mentors as initialMentors } from '../data/mentors';
import './MentorPage.css';

export default function Mentors({ activePage, setActivePage }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [displayedMentors, setDisplayedMentors] = useState(initialMentors);
  const [isMatching, setIsMatching] = useState(false);

  // Client-side AI match simulator
  const handleAIMatch = () => {
    if (!searchQuery.trim()) return;

    setIsMatching(true);
    setTimeout(() => {
      const searchTerms = searchQuery.toLowerCase().split(/[\s,]+/);
      const matched = initialMentors.map((m) => {
        let matchScore = 50;
        // Basic match calculation based on name, title, bio, or domains
        const searchPool = `${m.name} ${m.title} ${m.bio} ${m.domains.join(' ')}`.toLowerCase();
        let hits = 0;
        searchTerms.forEach((term) => {
          if (searchPool.includes(term)) hits++;
        });

        if (hits > 0) {
          matchScore = Math.min(60 + hits * 10, 99);
        } else {
          matchScore = Math.max(30, Math.round(Math.random() * 20) + 40);
        }

        return { ...m, match: matchScore };
      }).sort((a, b) => b.match - a.match);

      setDisplayedMentors(matched);
      setIsMatching(false);
    }, 800);
  };

  const handleBook = (name) => {
    alert(`Booking a session with ${name}! (UI demo)`);
  };

  const filteredMentors = displayedMentors.filter((mentor) => {
    if (selectedDomain === 'All') return true;
    return mentor.domains.some((d) => d.toLowerCase().includes(selectedDomain.toLowerCase()));
  });

  return (
    <DashboardLayout
      title="Find Your Mentor"
      subtitle="Connect with industry experts matched to your career goals using AI"
      activePage={activePage}
      setActivePage={setActivePage}
    >
      <div className="mentor-page-header">
        <div className="mentor-page-search" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '100%' }}>
            <svg
              style={{ position: 'absolute', left: '12px', top: '12px', color: '#6b7280' }}
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="search"
              placeholder="Enter your skills for AI Matching (e.g. React Python Product Design)..."
              className="mentor-search-input"
              style={{ paddingLeft: '32px' }}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAIMatch()}
            />
          </div>
          <button
            onClick={handleAIMatch}
            disabled={isMatching || !searchQuery.trim()}
            className="btn btn-hero-primary"
            style={{ whiteSpace: 'nowrap', padding: '12px 24px', opacity: isMatching ? 0.7 : 1 }}
          >
            {isMatching ? 'Calculating...' : '🧠 AI Match'}
          </button>
        </div>
        <div className="mentor-page-filters">
          {['All', 'Engineering', 'Product', 'Design', 'Data Science', 'Startup'].map((domain) => (
            <button
              key={domain}
              className={`filter-chip ${selectedDomain === domain ? 'active' : ''}`}
              onClick={() => setSelectedDomain(domain)}
            >
              {domain === 'All' ? 'All Domains' : domain}
            </button>
          ))}
        </div>
      </div>

      <div className="mentor-stats-row">
        <div className="mentor-stat-pill">
          <span className="mentor-stat-pill-value">{initialMentors.length}</span>
          <span className="mentor-stat-pill-label">Expert Mentors</span>
        </div>
        <div className="mentor-stat-pill">
          <span className="mentor-stat-pill-value">544</span>
          <span className="mentor-stat-pill-label">Sessions Completed</span>
        </div>
        <div className="mentor-stat-pill">
          <span className="mentor-stat-pill-value">4.8★</span>
          <span className="mentor-stat-pill-label">Average Rating</span>
        </div>
      </div>

      <div className="mentor-grid">
        {filteredMentors.map((mentor) => (
          <MentorCard
            key={mentor.id}
            name={mentor.name}
            title={mentor.title}
            company={mentor.company}
            domains={mentor.domains}
            match={mentor.match}
            bio={mentor.bio}
            sessions={mentor.sessions}
            rating={mentor.rating}
            avatar={mentor.avatar}
            onBook={() => handleBook(mentor.name)}
          />
        ))}
      </div>
    </DashboardLayout>
  );
}