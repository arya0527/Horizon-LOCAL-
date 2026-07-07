import React from 'react';
import './MentorCard.css';

function getMatchClass(match) {
  if (match >= 90) return 'green';
  if (match >= 70) return 'blue';
  return 'orange';
}

export default function MentorCard({
  name,
  title,
  company,
  domains = [],
  match = 50,
  bio,
  sessions = 0,
  rating = 4.5,
  avatar = '👨‍💼',
  onBook,
}) {
  const domainArray = Array.isArray(domains) ? domains : [];

  return (
    <div className="mentor-card card">
      <div className="mentor-card-header">
        <div className="mentor-avatar">{avatar}</div>
        <div className="mentor-info">
          <h4 className="mentor-name">{name}</h4>
          <p className="mentor-title">{title}</p>
          <p className="mentor-company">{company}</p>
        </div>
        <span className={`match-badge ${getMatchClass(match)}`}>
          {match}% Match
        </span>
      </div>

      <p className="mentor-bio">{bio}</p>

      <div className="mentor-domains">
        {domainArray.map((domain, index) => (
          <span key={index} className="tag">{domain}</span>
        ))}
      </div>

      <div className="mentor-stats">
        <div className="mentor-stat">
          <span className="mentor-stat-value">⭐ {rating}</span>
          <span className="mentor-stat-label">Rating</span>
        </div>
        <div className="mentor-stat">
          <span className="mentor-stat-value">{sessions}</span>
          <span className="mentor-stat-label">Sessions</span>
        </div>
      </div>

      <button className="btn btn-primary" style={{ width: '100%' }} onClick={onBook}>
        Book a Session
      </button>
    </div>
  );
}
