import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import JobCard from '../components/JobCard';
import { jobs as mockJobs } from '../data/jobs';
import { API_BASE_URL } from '../services/api';
import './ExperiencedDashboard.css';

const industries = ['All', 'IT Services', 'Fintech', 'Food Tech', 'E-commerce'];
const experienceOptions = ['Any', '0–2 years', '2–5 years', '5–8 years', '8+ years'];
const salaryRanges = ['Any', '₹10–15 LPA', '₹15–25 LPA', '₹25–40 LPA', '₹40+ LPA'];

export default function ExperiencedDashboard({ activePage, setActivePage }) {
  const [activeTab, setActiveTab] = useState('recommended');
  const [savedJobs, setSavedJobs] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState('All');
  const [selectedExp, setSelectedExp] = useState('Any');
  const [selectedSalary, setSelectedSalary] = useState('Any');

  const [isUploading, setIsUploading] = useState(false);
  const [displayedJobs, setDisplayedJobs] = useState(mockJobs);
  const [dynamicSkillGaps, setDynamicSkillGaps] = useState([]);
  const [dynamicApplied, setDynamicApplied] = useState([]);
  const [extractedSkills, setExtractedSkills] = useState([]);
  const user = JSON.parse(localStorage.getItem("user"));

  // Fetch collaborative recommendations on mount
  useEffect(() => {
    const fetchJobs = async () => {
      if (user && user.user_id) {
        try {
          const response = await fetch(`${API_BASE_URL}/recommend/collaborative/${user.user_id}`);
          if (response.ok) {
            const data = await response.json();
            if (data.recommendations && data.recommendations.length > 0) {
              const formattedJobs = data.recommendations.map((job, idx) => ({
                id: job.job_id || idx + 200,
                title: job.role || 'Senior Developer',
                company: job.company_name || 'Enterprise Client',
                location: job.location || 'Remote',
                match: Math.round(job.match_percentage) || 85,
                salary: job.salary || 'Competitive',
                type: 'job',
                skills: job.required_skills 
                  ? (typeof job.required_skills === 'string' ? job.required_skills.split(/[\s,]+/) : job.required_skills)
                  : ['Java', 'Microservices'],
                logo: '💼',
              }));
              setDisplayedJobs(formattedJobs);
            }
          }
        } catch (error) {
          console.warn('Flask server not running or error fetching collaborative jobs:', error);
        }
      }
    };
    fetchJobs();
  }, []);

  // Toggle saving jobs
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

  // Applying to jobs
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

  // Uploading resume to Flask server on port 5000
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

      if (data.extracted_skills) {
        setExtractedSkills(data.extracted_skills);
        const mockGaps = [
          { skill: 'System Design', priority: 'High', reason: 'Critical for senior positions' },
          { skill: 'AWS Cloud', priority: 'Medium', reason: 'Highly demanded in fintech' },
        ];
        setDynamicSkillGaps(mockGaps);
      }

      if (data.recommendations && data.recommendations.length > 0) {
        const formattedJobs = data.recommendations.map((job, idx) => ({
          id: job.job_id || idx + 200,
          title: job.role || 'Senior Developer',
          company: job.company_name || 'Enterprise Client',
          location: job.location || 'Remote',
          match: Math.round(job.match_percentage) || 85,
          salary: job.salary || 'Competitive',
          type: 'job',
          skills: job.required_skills 
            ? (typeof job.required_skills === 'string' ? job.required_skills.split(/[\s,]+/) : job.required_skills)
            : ['Java', 'Microservices'],
          logo: '💼',
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

  // Filter criteria logic
  const filteredJobs = displayedJobs.filter((job) => {
    if (selectedIndustry !== 'All' && job.industry !== selectedIndustry) return false;
    // Simple mock filters for years of exp and salary
    if (selectedExp !== 'Any' && job.experience && !job.experience.includes(selectedExp.slice(0, 2))) return false;
    return true;
  });

  return (
    <DashboardLayout
      title="Experienced Professionals Dashboard"
      subtitle="Find senior roles matched to your expertise and career trajectory"
      accentClass="exp-theme"
      activePage={activePage}
      setActivePage={setActivePage}
    >
      <div className="exp-layout">
        {/* Filters Sidebar */}
        <aside className="exp-sidebar">
          {/* AI Match Upload */}
          <div className="filter-card card" style={{ marginBottom: '1rem' }}>
            <h4 className="filter-title">🧠 AI Resume Matching</h4>
            <p className="skill-gap-subtitle" style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
              Upload your latest CV to let our ML engine find the best roles.
            </p>
            <label
              className="resume-upload-btn btn btn-primary"
              style={{
                width: '100%',
                textAlign: 'center',
                cursor: isUploading ? 'not-allowed' : 'pointer',
                opacity: isUploading ? 0.7 : 1,
                display: 'block',
                padding: '10px',
              }}
            >
              {isUploading ? 'AI is analyzing...' : '+ Upload Resume'}
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
                disabled={isUploading}
              />
            </label>
          </div>

          {/* Extracted Skills */}
          {extractedSkills.length > 0 && (
            <div className="filter-card card">
              <h4 className="filter-title" style={{ marginBottom: '8px' }}>Parsed Skills</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {extractedSkills.map((skill, index) => (
                  <span key={index} className="tag" style={{ background: '#e0eaf8', color: '#1e3a5f' }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Job Filter Controls */}
          <div className="filter-card card">
            <h4 className="filter-title">🔍 Filter Jobs</h4>

            <div className="filter-group">
              <label className="filter-label">Years of Experience</label>
              <div className="filter-options">
                {experienceOptions.map((opt) => (
                  <button
                    key={opt}
                    className={`filter-chip ${selectedExp === opt ? 'active' : ''}`}
                    onClick={() => setSelectedExp(opt)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label className="filter-label">Industry</label>
              <div className="filter-options">
                {industries.map((ind) => (
                  <button
                    key={ind}
                    className={`filter-chip ${selectedIndustry === ind ? 'active' : ''}`}
                    onClick={() => setSelectedIndustry(ind)}
                  >
                    {ind}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label className="filter-label">Salary Range</label>
              <div className="filter-options">
                {salaryRanges.map((range) => (
                  <button
                    key={range}
                    className={`filter-chip ${selectedSalary === range ? 'active' : ''}`}
                    onClick={() => setSelectedSalary(range)}
                  >
                    {range}
                  </button>
                ))}
              </div>
            </div>

            <button
              className="btn btn-secondary"
              style={{ width: '100%', marginTop: '0.5rem' }}
              onClick={() => {
                setSelectedIndustry('All');
                setSelectedExp('Any');
                setSelectedSalary('Any');
              }}
            >
              Clear Filters
            </button>
          </div>

          {/* Skill Improvement */}
          <div className="skill-improve-card card">
            <h4 className="skill-gap-title">
              <span>📈</span> Skill Improvements
            </h4>
            <p className="skill-gap-subtitle">Boost your match rate</p>
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
                    <p className="skill-reason">{item.reason}</p>
                  </div>
                ))
              ) : (
                <>
                  <div className="skill-gap-item">
                    <div className="skill-gap-row">
                      <span className="skill-gap-name">System Design</span>
                      <span className="skill-priority high">High</span>
                    </div>
                    <p className="skill-reason">Essential for Senior Backend Architect roles</p>
                  </div>
                  <div className="skill-gap-item">
                    <div className="skill-gap-row">
                      <span className="skill-gap-name">AWS Cloud</span>
                      <span className="skill-priority medium">Medium</span>
                    </div>
                    <p className="skill-reason">Demanded by 65% of fintech job posts</p>
                  </div>
                </>
              )}
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="exp-main">
          <div className="tab-list">
            <button
              className={`tab-btn ${activeTab === 'recommended' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommended')}
            >
              Recommended AI Matches ({filteredJobs.length})
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
              {filteredJobs.map((job) => (
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
              {filteredJobs.length === 0 && (
                <div className="empty-state">
                  <p>No jobs match the selected filters. Try adjusting your criteria.</p>
                </div>
              )}
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
                      <span className="status-badge approved">{item.status}</span>
                      <span className="applied-date">{item.date}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                  You haven&apos;t applied to any jobs yet.
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </DashboardLayout>
  );
}