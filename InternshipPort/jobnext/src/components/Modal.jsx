import React, { useState } from "react";
import "./Modal.css";
import { API_BASE_URL } from "../services/api";

function Modal({ type, onClose }) {
  const [modalType, setModalType] = useState(type); // 'login' or 'signup'
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    college: "",
    year: ""
  });
  const [errorMsg, setErrorMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setIsLoading(true);

    const endpoint =
      modalType === "login"
        ? `${API_BASE_URL}/login`
        : `${API_BASE_URL}/register`;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      if (modalType === "login") {
        if (data.user) {
          localStorage.setItem("user", JSON.stringify(data.user));
          window.location.reload();
        } else {
          setErrorMsg(data.message || "Failed to log in.");
        }
      } else {
        alert(data.message || "Successfully registered!");
        setModalType("login");
      }
    } catch (error) {
      console.error("Auth error:", error);
      setErrorMsg("Failed to connect to the authentication server. Ensure port 5000 is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-container">
        {/* Close Button */}
        <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">
            {modalType === "login" ? "Welcome Back" : "Create Account"}
          </h2>
          <p className="modal-subtitle">
            {modalType === "login"
              ? "Sign in to access your AI career dashboard"
              : "Register to get personalized matches & mentorship"}
          </p>
        </div>

        {/* Form Body */}
        <div className="modal-body">
          {errorMsg && (
            <div style={{ color: "#e11d48", background: "#fff1f2", padding: "10px 14px", borderRadius: "8px", fontSize: "0.85rem", marginBottom: "1rem", border: "1px solid #fecdd3" }}>
              ⚠️ {errorMsg}
            </div>
          )}

          <form className="modal-form" onSubmit={handleSubmit}>
            {modalType === "signup" && (
              <>
                {/* Full Name */}
                <div className="modal-input-wrapper">
                  <span className="modal-input-icon">👤</span>
                  <input
                    className="modal-input"
                    name="name"
                    type="text"
                    placeholder="Full Name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                  />
                </div>

                {/* College */}
                <div className="modal-input-wrapper">
                  <span className="modal-input-icon">🏫</span>
                  <input
                    className="modal-input"
                    name="college"
                    type="text"
                    placeholder="College / University"
                    required
                    value={formData.college}
                    onChange={handleChange}
                  />
                </div>

                {/* Year */}
                <div className="modal-input-wrapper">
                  <span className="modal-input-icon">📅</span>
                  <input
                    className="modal-input"
                    name="year"
                    type="text"
                    placeholder="Graduation Year (e.g. 2027)"
                    required
                    value={formData.year}
                    onChange={handleChange}
                  />
                </div>
              </>
            )}

            {/* Email */}
            <div className="modal-input-wrapper">
              <span className="modal-input-icon">✉️</span>
              <input
                className="modal-input"
                name="email"
                type="email"
                placeholder="Email Address"
                required
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            {/* Password */}
            <div className="modal-input-wrapper">
              <span className="modal-input-icon">🔒</span>
              <input
                className="modal-input"
                name="password"
                type="password"
                placeholder="Password"
                required
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            {/* Submit */}
            <button className="modal-submit-btn" type="submit" disabled={isLoading}>
              {isLoading ? "Processing..." : modalType === "login" ? "Sign In" : "Sign Up"}
            </button>
          </form>

          {/* Switch Link */}
          <div className="modal-footer-toggle">
            {modalType === "login" ? (
              <>
                Don't have an account?
                <button className="modal-toggle-link" onClick={() => setModalType("signup")}>
                  Sign Up
                </button>
              </>
            ) : (
              <>
                Already have an account?
                <button className="modal-toggle-link" onClick={() => setModalType("login")}>
                  Sign In
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Modal;