import React from 'react';
import './JobCard.css';

function getMatchClass(match) {
  if (match >= 90) return 'green';
  if (match >= 70) return 'blue';
  return 'orange';
}

export default function JobCard({
  title,
  company,
  location,
  match = 50,
  salary = 'Competitive',
  type = 'internship',
  skills = [],
  logo = '💼',
  onSave,
  onApply,
  saved = false,
}) {
  // Safe skill array handling
  const skillArray = Array.isArray(skills)
    ? skills
    : typeof skills === 'string'
    ? skills.split(',').map((s) => s.trim())
    : [];

  return (
    <div className="job-card card">
      <div className="job-card-header">
        <div className="job-card-logo">{logo}</div>
        <div className="job-card-info">
          <h4 className="job-card-title">{title}</h4>
          <p className="job-card-company">{company}</p>
        </div>
        <span className={`match-badge ${getMatchClass(match)}`}>
          {match}% Match
        </span>
      </div>

      <div className="job-card-meta">
        <span className="job-meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          {location || 'India'}
        </span>
        <span className="job-meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="1" x2="12" y2="23"/>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
          {salary}
        </span>
        <span className={`job-type-badge ${type.toLowerCase()}`}>
          {type.toLowerCase() === 'internship' ? 'Internship' : 'Full-time'}
        </span>
      </div>

      <div className="job-card-skills">
        {skillArray.map((skill, index) => (
          <span key={index} className="tag">{skill}</span>
        ))}
      </div>

      <div className="job-card-actions">
        <button className="btn btn-primary btn-sm" onClick={onApply}>
          Apply Now
        </button>
        <button
          className={`btn btn-sm ${saved ? 'btn-success' : 'btn-secondary'}`}
          onClick={onSave}
        >
          {saved ? '✓ Saved' : 'Save'}
        </button>
      </div>
    </div>
  );
}
