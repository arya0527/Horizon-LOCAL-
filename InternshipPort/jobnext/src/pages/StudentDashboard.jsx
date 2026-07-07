import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import JobCard from '../components/JobCard';
import { internships as mockInternships } from '../data/jobs';
import { API_BASE_URL } from '../services/api';
import './StudentDashboard.css';

export default function StudentDashboard({ activePage, setActivePage }) {
  const [activeTab, setActiveTab] = useState('recommended');
  const [savedJobs, setSavedJobs] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dynamicSkillGaps, setDynamicSkillGaps] = useState([]);
  const [dynamicApplied, setDynamicApplied] = useState([]);
  const [displayedJobs, setDisplayedJobs] = useState(mockInternships);
  const [extractedSkills, setExtractedSkills] = useState([]);
  const user = JSON.parse(
  localStorage.getItem("user")
);

  // Fetch live internships from local Flask backend on port 5000
  useEffect(() => {
    const fetchInternships = async () => {
      try {
        let url = `${API_BASE_URL}/internships`;
        if (user && user.user_id) {
          url = `${API_BASE_URL}/recommend/collaborative/${user.user_id}`;
        }
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          const list = data.recommendations || data;
          if (list && list.length > 0) {
            const formatted = list.map((item, idx) => ({
              id: item.job_id || idx + 1,
              title: item.title || item.role || 'Internship Role',
              company: item.company || item.company_name || 'Partner Company',
              location: item.location || 'Remote',
              match: item.match_percentage ? Math.round(item.match_percentage) : (item.match_score ? Math.round(item.match_score) : 80 - idx * 5),
              salary: item.salary || 'Competitive',
              type: 'internship',
              skills: item.skills
                ? (typeof item.skills === 'string' ? item.skills.split(/[\s,]+/) : item.skills)
                : (item.required_skills
                  ? (typeof item.required_skills === 'string' ? item.required_skills.split(/[\s,]+/) : item.required_skills)
                  : ['React', 'CSS']),
              logo: '🏢',
            }));
            setDisplayedJobs(formatted);
          }
        }
      } catch (error) {
        console.warn('Flask server not running on port 5000, using mock internships:', error);
      }
    };

    fetchInternships();
  }, []);

  const toggleSave = async (id) => {
    const isSaving = !savedJobs.includes(id);
    setSavedJobs((prev) =>
      prev.includes(id) ? prev.filter((j) => j !== id) : [...prev, id]
    );

    if (user && user.user_id && id && isSaving) {
      try {
        await fetch(`${API_BASE_URL}/recommend/interaction`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.user_id,
            job_id: id,
            interaction_type: 'bookmark',
          }),
        });
      } catch (e) {
        console.error('Failed to log bookmark interaction:', e);
      }
    }
  };

  const handleApply = async (job) => {
    alert(`Successfully applied to ${job.title} at ${job.company}!`);
    setDynamicApplied((prev) => [
      {
        title: job.title,
        company: job.company,
        status: 'Applied',
        date: new Date().toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        }),
      },
      ...prev,
    ]);

    if (user && user.user_id && job.id) {
      try {
        await fetch(`${API_BASE_URL}/recommend/interaction`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.user_id,
            job_id: job.id,
            interaction_type: 'apply',
          }),
        });
      } catch (e) {
        console.error('Failed to log apply interaction:', e);
      }
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('resume', file);

      const response = await fetch(`${API_BASE_URL}/upload_resume`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to score resume.');
      }

      const data = await response.json();

      // Extract skills list
      if (data.extracted_skills) {
        setExtractedSkills(data.extracted_skills);
        // Create mock skill gaps based on missing skills or generic ones
        const mockGaps = [
          { skill: 'TypeScript', priority: 'High', resource: 'Required by top matches' },
          { skill: 'Docker', priority: 'Medium', resource: 'Standard deployment' },
        ];
        setDynamicSkillGaps(mockGaps);
      }

      // Update recommendations
      if (data.recommendations && data.recommendations.length > 0) {
        const formattedJobs = data.recommendations.map((job, idx) => ({
          id: job.job_id || idx + 100,
          title: job.role || 'Software Engineer',
          company: job.company_name || 'Tech Partner',
          location: job.location || 'Remote',
          match: Math.round(job.match_percentage) || 85,
          salary: job.salary || 'Competitive',
          type: 'internship',
          skills: job.missing_skills && job.missing_skills.length > 0 
            ? ['React', ...job.missing_skills.slice(0, 2)] 
            : ['React', 'Node.js'],
          logo: '🏢',
        }));
        setDisplayedJobs(formattedJobs);
      }
    } catch (error) {
      console.error('Error matching resume:', error);
      alert('Error connecting to Flask backend. Make sure the server is running on port 5000.');
    } finally {
      setIsUploading(false);
    }
  };

  const profileCompletion = extractedSkills.length > 0 ? 90 : 72;

  return (
    <DashboardLayout
      title="Student Internship Dashboard"
      subtitle="Discover internships matched to your skills and goals"
      activePage={activePage}
      setActivePage={setActivePage}
    >
      <div className="student-layout">
        {/* Sidebar */}
        <aside className="student-sidebar">
          {/* Profile Card */}
          <div className="profile-card card">
            <div className="profile-avatar">👩‍🎓</div>
            <h3 className="profile-name">
             {user?.name || "Guest User"}
              </h3>

             <p className="profile-college">
                {user?.college || "College Not Set"} · {user?.year || "Year Not Set"}
              </p>
            <div className="profile-completion">
              <div className="profile-completion-header">
                <span>Profile Completion</span>
                <span className="profile-pct">{profileCompletion}%</span>
              </div>
              <div className="progress-bar-track">
                <div className="progress-bar-fill" style={{ width: `${profileCompletion}%` }} />
              </div>
              <p className="profile-completion-hint">
                {extractedSkills.length > 0 
                  ? 'Excellent profile! 90% matches unlocked.' 
                  : 'Add 2 more skills to reach 80%'}
              </p>
            </div>
            <label
              className="resume-upload-btn btn btn-outline"
              style={{
                width: '100%',
                textAlign: 'center',
                cursor: isUploading ? 'not-allowed' : 'pointer',
                opacity: isUploading ? 0.7 : 1,
              }}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              {isUploading ? 'AI is analyzing...' : 'Upload Resume'}
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
                disabled={isUploading}
              />
            </label>
          </div>

          {/* Extracted Skills Card */}
          {extractedSkills.length > 0 && (
            <div className="skill-gap-card card">
              <h4 className="skill-gap-title">
                <span>✅</span> Extracted Skills
              </h4>
              <p className="skill-gap-subtitle">Parsed from your uploaded resume</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {extractedSkills.map((skill, index) => (
                  <span key={index} className="tag" style={{ background: '#e0f2fe', color: '#0369a1' }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Skill Gap Analysis */}
          <div className="skill-gap-card card">
            <h4 className="skill-gap-title">
              <span>🎯</span> Skill Gap Analysis
            </h4>
            <p className="skill-gap-subtitle">Skills to boost your match rate</p>
            <div className="skill-gap-list">
              {dynamicSkillGaps.length > 0 ? (
                dynamicSkillGaps.map((item, index) => (
                  <div key={index} className="skill-gap-item">
                    <div className="skill-gap-row">
                      <span className="skill-gap-name">{item.skill}</span>
                      <span className={`skill-priority ${item.priority.toLowerCase()}`}>
                        {item.priority}
                      </span>
                    </div>
                    <a href="#" className="skill-gap-resource">📚 {item.resource}</a>
                  </div>
                ))
              ) : (
                <>
                  <div className="skill-gap-item">
                    <div className="skill-gap-row">
                      <span className="skill-gap-name">TypeScript</span>
                      <span className="skill-priority high">High</span>
                    </div>
                    <a href="#" className="skill-gap-resource">📚 Learn TypeScript Core</a>
                  </div>
                  <div className="skill-gap-item">
                    <div className="skill-gap-row">
                      <span className="skill-gap-name">Docker</span>
                      <span className="skill-priority medium">Medium</span>
                    </div>
                    <a href="#" className="skill-gap-resource">📚 Get Started with Containers</a>
                  </div>
                </>
              )}
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="student-main">
          <div className="tab-list">
            <button
              className={`tab-btn ${activeTab === 'recommended' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommended')}
            >
              Recommended AI Matches ({displayedJobs.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'applied' ? 'active' : ''}`}
              onClick={() => setActiveTab('applied')}
            >
              Applied ({dynamicApplied.length})
            </button>
          </div>

          {activeTab === 'recommended' && (
            <div className="jobs-grid">
              {displayedJobs.map((job) => (
                <JobCard
                  key={job.id}
                  title={job.title}
                  company={job.company}
                  location={job.location}
                  match={job.match}
                  salary={job.salary}
                  type={job.type}
                  skills={job.skills}
                  logo={job.logo}
                  saved={savedJobs.includes(job.id)}
                  onSave={() => toggleSave(job.id)}
                  onApply={() => handleApply(job)}
                />
              ))}
            </div>
          )}

          {activeTab === 'applied' && (
            <div className="applied-list">
              {dynamicApplied.length > 0 ? (
                dynamicApplied.map((item, i) => (
                  <div key={i} className="applied-item card">
                    <div className="applied-info">
                      <h4 className="applied-title">{item.title}</h4>
                      <p className="applied-company">{item.company}</p>
                    </div>
                    <div className="applied-meta">
                      <span className="status-badge approved">
                        {item.status}
                      </span>
                      <span className="applied-date">{item.date}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                  You haven&apos;t applied to any internships yet.
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </DashboardLayout>
  );
}