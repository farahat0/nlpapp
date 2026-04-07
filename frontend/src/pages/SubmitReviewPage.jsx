import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeReview, getEmployees, createEmployee } from "../services/api";

const RATING_LABELS = {
  1: "Unsatisfactory",
  2: "Below Expectations",
  3: "Meets Expectations",
  4: "Exceeds Expectations",
  5: "Exceptional",
};

function RatingScale({ label, value, onChange }) {
  return (
    <div>
      <label className="block text-sm text-gray-600 mb-2">{label}</label>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            className={`flex-1 flex flex-col items-center gap-1 rounded-lg border-2 px-2 py-3 text-xs transition-all duration-150 cursor-pointer ${
              value === n
                ? "border-blue-600 bg-blue-50 text-blue-700 shadow-sm"
                : "border-gray-200 bg-white text-gray-500 hover:border-gray-300 hover:bg-gray-50"
            }`}
          >
            <span className="text-lg font-semibold">{n}</span>
            <span className="leading-tight text-center">{RATING_LABELS[n]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function CreateEmployeeModal({ isOpen, onClose, onCreated }) {
  const [name, setName] = useState("");
  const [dept, setDept] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await createEmployee(name.trim(), dept.trim());
      setSuccess("Employee created successfully!");
      setName("");
      setDept("");
      onCreated();
      setTimeout(() => {
        setSuccess("");
        onClose();
      }, 1200);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create employee");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 text-xl leading-none"
        >
          ×
        </button>
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Create Employee</h2>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 mb-3">
            {error}
          </p>
        )}
        {success && (
          <p className="text-sm text-green-600 bg-green-50 border border-green-200 rounded px-3 py-2 mb-3">
            {success}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Employee Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g. ahmed farahat"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Department</label>
            <input
              type="text"
              value={dept}
              onChange={(e) => setDept(e.target.value)}
              required
              placeholder="e.g. Engineering"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Employee"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function SubmitReviewPage() {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [department, setDepartment] = useState("");
  const [reviewText, setReviewText] = useState("");
  const [behavioralRating, setBehavioralRating] = useState(null);
  const [performanceRating, setPerformanceRating] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const fetchEmployees = async () => {
    try {
      const res = await getEmployees();
      setEmployees(res.data);
    } catch {
      // silently fail
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleEmployeeChange = (e) => {
    const name = e.target.value;
    setSelectedEmployee(name);
    const emp = employees.find((emp) => emp.name === name);
    setDepartment(emp ? emp.department : "");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!behavioralRating || !performanceRating) {
      setError("Both ratings are required before submitting.");
      return;
    }

    setLoading(true);
    try {
      const res = await analyzeReview(
        selectedEmployee,
        department,
        reviewText,
        behavioralRating,
        performanceRating
      );
      navigate("/results", {
        state: { result: res.data, employeeName: selectedEmployee, department },
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-800">Submit HR Review</h1>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="bg-green-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-green-700"
        >
          + Create Employee
        </button>
      </div>

      <CreateEmployeeModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreated={fetchEmployees}
      />

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 mb-4">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Employee</label>
            <select
              value={selectedEmployee}
              onChange={handleEmployeeChange}
              required
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500 bg-white"
            >
              <option value="">Select an employee...</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.name}>
                  {emp.name} — {emp.department}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Department</label>
            <input
              type="text"
              value={department}
              readOnly
              placeholder="Auto-filled from employee"
              className="w-full border border-gray-200 rounded px-3 py-2 text-sm bg-gray-50 text-gray-600"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Review Text</label>
          <textarea
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            required
            rows={6}
            placeholder="Paste the HR performance review here..."
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500 resize-vertical"
          />
        </div>

        <RatingScale
          label="Behavioral Rating"
          value={behavioralRating}
          onChange={setBehavioralRating}
        />

        <RatingScale
          label="Performance Rating"
          value={performanceRating}
          onChange={setPerformanceRating}
        />

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white text-sm font-medium px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze Review"}
        </button>
      </form>
    </div>
  );
}
