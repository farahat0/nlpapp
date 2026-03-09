import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const registerUser = (username, password) =>
  API.post("/api/v1/auth/register", { username, password });

export const loginUser = (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  return API.post("/api/v1/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const getMe = () => API.get("/api/v1/auth/me");

// NLP
export const analyzeReview = (employee_name, department, review_text) =>
  API.post("/api/v1/nlp/analyze", { employee_name, department, review_text });

// Reviews
export const getReviews = () => API.get("/api/v1/reviews/");

export const getEmployeeReviews = (name) =>
  API.get(`/api/v1/reviews/${name}`);

export const deleteReview = (id) => API.delete(`/api/v1/reviews/${id}`);

// Analytics
export const getOverviewStats = () => API.get("/api/v1/analytics/overview");

export const getDepartmentStats = (department) =>
  API.get(`/api/v1/analytics/department/${department}`);

export const getEmployeeStats = (name) =>
  API.get(`/api/v1/analytics/employee/${name}`);

export default API;
