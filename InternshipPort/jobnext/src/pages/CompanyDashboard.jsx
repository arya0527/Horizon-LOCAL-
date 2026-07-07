import React, { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import './CompanyDashboard.css';

const initialJobs = [
  {
    id: 1,
    title: 'Senior React Developer',
    type: 'Full-time',
    applications: 47,
    boosted: false,
    posted: 'Feb 10, 2026',
    applicants: [
      { name: 'Rahul Sharma', college: 'IIT Delhi', match: 92, status: 'Shortlisted' },
      { name: 'Priya Patel', college: 'NIT Trichy', match: 85, status: 'Applied' },
      { name: 'Arjun Nair', college: 'BITS Pilani', match: 78, status: 'Applied' },
    ],
  },
  {
    id: 2,
    title: 'Product Manager Intern',
    type: 'Internship',
    applications: 31,
    boosted: true,
    posted: 'Feb 15, 2026',
    applicants: [
      { name: 'Sneha Reddy', college: 'IIM Bangalore', match: 94, status: 'Shortlisted' },
      { name: 'Vikram Joshi', college: 'IIT Bombay', match: 71, status: 'Applied' },
    ],
  },
];

function getMatchClass(match) {
  if (match >= 90) return 'green';
  if (match >= 70) return 'blue';
  return 'orange';
}

export default function CompanyDashboard({ activePage, setActivePage }) {
  const [showForm, setShowForm] = useState(false);
  const [expandedJob, setExpandedJob] = useState(null);
  const [postedJobs, setPostedJobs] = useState(initialJobs);
  const [boostedJobs, setBoostedJobs] = useState(
    initialJobs.filter((j) => j.boosted).map((j) => j.id)
  );
  
  const [formData, setFormData] = useState({
    title: '',
    type: 'Full-time',
    description: '',
    skills: '',
    location: '',
    salary: '',
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);

  const toggleBoost = (id) => {
    setBoostedJobs((prev) =>
      prev.includes(id) ? prev.filter((j) => j !== id) : [...prev, id]
    );
  };

  const handlePublishJob = (e) => {
    e.preventDefault();
    if (!formData.title || !formData.skills || !formData.description) {
      alert('Please fill in the title, skills, and description.');
      return;
    }
    
    setIsPublishing(true);
    setTimeout(() => {
      const newJob = {
        id: Math.floor(Math.random() * 1000000),
        title: formData.title,
        type: formData.type,
        applications: 0,
        boosted: false,
        posted: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        applicants: []
      };

      setPostedJobs([newJob, ...postedJobs]);
      setFormData({ title: '', type: 'Full-time', description: '', skills: '', location: '', salary: '' });
      setShowForm(false);
      setIsPublishing(false);
      alert('Job successfully published to live dashboards!');
    }, 600);
  };

  const handleGenerateJD = () => {
    if (!formData.title) {
      alert('Please enter a Job Title first so the AI knows what to write.');
      return;
    }

    setIsGenerating(true);
    setTimeout(() => {
      const skillsStr = formData.skills || 'required technologies';
      const generated = `We are looking for a passionate ${formData.title} to join our dynamic team.

Responsibilities:
- Design, build, and maintain high-performance, reusable, and reliable code.
- Collaborate with cross-functional teams to define, design, and ship new features.

Requirements:
- Proven experience working as a ${formData.title}.
- Strong proficiency in ${skillsStr}.
- Excellent problem-solving skills and attention to detail.`;

      setFormData(prev => ({ ...prev, description: generated }));
      setIsGenerating(false);
    }, 800);
  };

  const updateApplicantStatus = (jobId, applicantName, status) => {
    setPostedJobs(prevJobs => prevJobs.map(job => {
      if (job.id === jobId) {
        return {
          ...job,
          applicants: job.applicants.map(app => 
            app.name === applicantName ? { ...app, status } : app
          )
        };
      }
      return job;
    }));
    alert(`Applicant ${applicantName} has been ${status.toLowerCase()}!`);
  };

  return (
    <DashboardLayout
      title="Company Dashboard"
      subtitle="Post opportunities, manage applicants, and track your hiring analytics"
      accentClass="company-theme"
      activePage={activePage}
      setActivePage={setActivePage}
    >
      {/* Analytics */}
      <div className="company-analytics">
        <div className="analytics-card card">
          <div className="analytics-icon">📋</div>
          <div className="analytics-value">{postedJobs.length}</div>
          <div className="analytics-label">Active Postings</div>
        </div>
        <div className="analytics-card card">
          <div className="analytics-icon">👥</div>
          <div className="analytics-value">
            {postedJobs.reduce((acc, curr) => acc + curr.applications, 0)}
          </div>
          <div className="analytics-label">Total Applications</div>
        </div>
        <div className="analytics-card card">
          <div className="analytics-icon">⭐</div>
          <div className="analytics-value">5</div>
          <div className="analytics-label">Shortlisted</div>
        </div>
        <div className="analytics-card card">
          <div className="analytics-icon">🚀</div>
          <div className="analytics-value">{boostedJobs.length}</div>
          <div className="analytics-label">Boosted Jobs</div>
        </div>
      </div>

      {/* Header Row */}
      <div className="company-header-row">
        <h3 className="section-heading">Posted Jobs &amp; Internships</h3>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✕ Cancel' : '+ Post New Job'}
        </button>
      </div>

      {/* Post Job Form */}
      {showForm && (
        <form className="post-job-form card" onSubmit={handlePublishJob}>
          <h4>Post New Job / Internship</h4>
          <div className="form-row-2">
            <div className="form-group">
              <label className="form-label">Job Title *</label>
              <input
                className="form-input"
                type="text"
                placeholder="e.g. Frontend Developer"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Type *</label>
              <select
                className="form-select"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              >
                <option>Full-time</option>
                <option>Internship</option>
                <option>Part-time</option>
                <option>Contract</option>
              </select>
            </div>
          </div>
          <div className="form-row-2">
            <div className="form-group">
              <label className="form-label">Location</label>
              <input
                className="form-input"
                type="text"
                placeholder="e.g. Bangalore, India"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Salary / Stipend</label>
              <input
                className="form-input"
                type="text"
                placeholder="e.g. ₹20,000/month"
                value={formData.salary}
                onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', flexDirection: 'column' }}>
              <span>Required Skills *</span>
              <span style={{ fontSize: '0.8rem', fontWeight: 'normal', color: '#6b7280', marginTop: '2px' }}>
                Determine student skill gap tracking. Format: Skill [Priority], e.g. React [High], Node [Medium]
              </span>
            </label>
            <input
              className="form-input"
              type="text"
              placeholder="e.g. React [High], TypeScript [Medium]..."
              value={formData.skills}
              onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Job Description *</span>
              <button
                className="btn btn-sm btn-outline"
                onClick={handleGenerateJD}
                disabled={isGenerating}
                type="button"
                style={{ fontSize: '0.8rem', padding: '0.2rem 0.5rem', background: '#eef2ff', borderColor: '#6366f1', color: '#4f46e5' }}
              >
                {isGenerating ? '⏳ Generating...' : '✨ AI Auto-Write'}
              </button>
            </label>
            <textarea
              className="form-textarea"
              placeholder="Describe the role, responsibilities, and requirements..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit" disabled={isPublishing}>
              {isPublishing ? 'Publishing...' : 'Publish Job'}
            </button>
            <button className="btn btn-secondary" type="button" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      {/* Job Listings */}
      <div className="job-listings">
        {postedJobs.map((job) => (
          <div key={job.id} className="job-listing-card card">
            <div className="job-listing-header">
              <div className="job-listing-info">
                <h4 className="job-listing-title">{job.title}</h4>
                <div className="job-listing-meta">
                  <span className={`job-type-badge ${job.type.toLowerCase() === 'internship' ? 'internship' : 'job'}`}>
                    {job.type}
                  </span>
                  <span className="meta-text" style={{ marginLeft: '10px' }}>Posted {job.posted}</span>
                  <span className="meta-text" style={{ marginLeft: '10px' }}>📊 {job.applicants.length} applications</span>
                </div>
              </div>
              <div className="job-listing-actions">
                <button
                  className={`btn btn-sm ${boostedJobs.includes(job.id) ? 'btn-success' : 'btn-secondary'}`}
                  onClick={() => toggleBoost(job.id)}
                >
                  {boostedJobs.includes(job.id) ? '🚀 Boosted' : '🚀 Boost Job'}
                </button>
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => setExpandedJob(expandedJob === job.id ? null : job.id)}
                >
                  {expandedJob === job.id ? 'Hide Applicants' : 'View Applicants'}
                </button>
              </div>
            </div>

            {expandedJob === job.id && (
              <div className="applicants-section">
                <h5 className="applicants-title">Applicants ({job.applicants.length})</h5>
                {job.applicants.length > 0 ? (
                  <div className="applicants-list">
                    {job.applicants.map((applicant, i) => (
                      <div key={i} className="applicant-row">
                        <div className="applicant-avatar">{applicant.name[0]}</div>
                        <div className="applicant-info">
                          <span className="applicant-name">{applicant.name}</span>
                          <span className="applicant-college">{applicant.college}</span>
                        </div>
                        <span className={`match-badge ${getMatchClass(applicant.match)}`}>
                          {applicant.match}% Match
                        </span>
                        <span className={`status-badge ${applicant.status.toLowerCase()}`}>
                          {applicant.status}
                        </span>
                        <div className="applicant-actions">
                          <button
                            className="btn btn-sm btn-success"
                            onClick={() => updateApplicantStatus(job.id, applicant.name, 'Shortlisted')}
                          >
                            Shortlist
                          </button>
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() => updateApplicantStatus(job.id, applicant.name, 'Rejected')}
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>No one has applied to this posting yet.</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </DashboardLayout>
  );
}
