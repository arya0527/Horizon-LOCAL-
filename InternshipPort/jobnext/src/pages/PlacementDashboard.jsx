import React, { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import './PlacementDashboard.css';

const initialStats = [
  { value: '1,240', label: 'Students Registered', icon: '👥' },
  { value: '68%', label: 'Placement Rate', icon: '🎯' },
  { value: '312', label: 'Internships Verified', icon: '✅' },
  { value: '48', label: 'Partner Companies', icon: '🏢' },
];

const initialStudents = [
  { name: 'Rahul Sharma', branch: 'CSE', year: '4th', internship: 'Razorpay — Frontend Intern', status: 'Approved', cgpa: '8.9' },
  { name: 'Priya Patel', branch: 'ECE', year: '3rd', internship: 'Flipkart — Data Analyst', status: 'Pending', cgpa: '8.2' },
  { name: 'Arjun Nair', branch: 'IT', year: '4th', internship: 'Swiggy — Backend Intern', status: 'Approved', cgpa: '7.8' },
  { name: 'Sneha Reddy', branch: 'CSE', year: '3rd', internship: 'Not Applied', status: 'Pending', cgpa: '9.1' },
  { name: 'Vikram Joshi', branch: 'ME', year: '4th', internship: 'Ola — DevOps Intern', status: 'Review', cgpa: '7.5' },
  { name: 'Kavya Singh', branch: 'CSE', year: '3rd', internship: 'Meesho — UI/UX Intern', status: 'Approved', cgpa: '8.6' },
];

export default function PlacementDashboard({ activePage, setActivePage }) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [students, setStudents] = useState(initialStudents);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Form states
  const [studentName, setStudentName] = useState('');
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [duration, setDuration] = useState('');

  const handleAddInternship = (e) => {
    e.preventDefault();
    if (!studentName || !company || !role) {
      alert('Please fill in Name, Company, and Role fields.');
      return;
    }

    const newStudent = {
      name: studentName,
      branch: 'CSE',
      year: '4th',
      internship: `${company} — ${role}`,
      status: 'Approved',
      cgpa: '8.0'
    };

    setStudents([newStudent, ...students]);
    setStudentName('');
    setCompany('');
    setRole('');
    setDuration('');
    setShowAddForm(false);
    alert('Internship verified and added successfully!');
  };

  const filteredStudents = students.filter(s => 
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.company?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.branch.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <DashboardLayout
      title="Placement Authority Dashboard"
      subtitle="Manage student placements, verify internships, and track outcomes"
      accentClass="placement-theme"
      activePage={activePage}
      setActivePage={setActivePage}
    >
      {/* College Profile */}
      <div className="college-profile card">
        <div className="college-logo">🏛️</div>
        <div className="college-info">
          <h3>Indian Institute of Technology, Delhi</h3>
          <p>New Delhi, India · Established 1961 · NAAC Grade A++</p>
          <div className="college-tags">
            <span className="tag">Engineering</span>
            <span className="tag">Technology</span>
            <span className="tag">Research</span>
          </div>
        </div>
        <div className="college-actions">
          <button className="btn btn-outline btn-sm">Edit Profile</button>
        </div>
      </div>

      {/* Stats */}
      <div className="placement-stats-grid">
        {initialStats.map((stat) => (
          <div key={stat.label} className="stat-card">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Graph Section */}
      <div className="graph-section card">
        <div className="graph-header">
          <h4>📊 Placement Trends — 2025–26</h4>
          <div className="graph-legend">
            <span className="legend-dot blue" /> Internships
            <span className="legend-dot green" /> Full-time Offers
          </div>
        </div>
        <div className="graph-placeholder">
          <div className="graph-bars">
            {['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'].map((month, i) => {
              const heights = [30, 45, 60, 75, 55, 80, 90, 68];
              const heights2 = [10, 20, 35, 50, 40, 60, 70, 55];
              return (
                <div key={month} className="graph-bar-group">
                  <div className="graph-bar-pair">
                    <div className="graph-bar blue" style={{ height: `${heights[i]}%` }} />
                    <div className="graph-bar green" style={{ height: `${heights2[i]}%` }} />
                  </div>
                  <span className="graph-month">{month}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="placement-actions">
        <button className="btn btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? '✕ Cancel' : '✅ Add Verified Internship'}
        </button>
        <button className="btn btn-secondary">👤 Approve Student Profiles</button>
        <button className="btn btn-secondary">📥 Export Reports</button>
      </div>

      {/* Add Internship Form */}
      {showAddForm && (
        <form className="add-internship-form card" onSubmit={handleAddInternship}>
          <h4>Add Verified Internship</h4>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Student Name *</label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter student name"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Company *</label>
              <input
                className="form-input"
                type="text"
                placeholder="Company name"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Role *</label>
              <input
                className="form-input"
                type="text"
                placeholder="Internship role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Duration</label>
              <input
                className="form-input"
                type="text"
                placeholder="e.g. 3 months"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary btn-sm" type="submit">Submit</button>
            <button className="btn btn-secondary btn-sm" type="button" onClick={() => setShowAddForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      {/* Student Table */}
      <div className="student-table-section card">
        <div className="table-header">
          <h4>Student Portfolio Tracking</h4>
          <input
            className="form-input"
            type="search"
            placeholder="Search students..."
            style={{ maxWidth: '240px' }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Branch</th>
                <th>Year</th>
                <th>CGPA</th>
                <th>Internship</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student, i) => (
                <tr key={i}>
                  <td><strong>{student.name}</strong></td>
                  <td>{student.branch}</td>
                  <td>{student.year}</td>
                  <td>{student.cgpa}</td>
                  <td className="internship-cell">{student.internship}</td>
                  <td>
                    <span className={`status-badge ${student.status.toLowerCase()}`}>
                      {student.status}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-sm btn-secondary">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
}