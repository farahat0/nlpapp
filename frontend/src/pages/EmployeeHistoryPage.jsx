import { useState, useEffect } from "react";
import { getReviews, deleteReview, getEmployees } from "../services/api";

const RATING_LABELS = {
  1: "Unsatisfactory",
  2: "Below Expectations",
  3: "Meets Expectations",
  4: "Exceeds Expectations",
  5: "Exceptional",
};

export default function EmployeeHistoryPage() {
  const [reviews, setReviews] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchReviews = async (employeeName) => {
    setLoading(true);
    setError("");
    try {
      const res = await getReviews(employeeName || undefined);
      setReviews(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load reviews");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getEmployees()
      .then((res) => setEmployees(res.data))
      .catch(() => {});
    fetchReviews();
  }, []);

  const handleEmployeeChange = (e) => {
    const name = e.target.value;
    setSelectedEmployee(name);
    fetchReviews(name);
  };

  const handleDelete = async (id) => {
    try {
      await deleteReview(id);
      setReviews(reviews.filter((r) => r.id !== id));
    } catch {
      setError("Failed to delete review");
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">
        Review History
      </h1>

      {/* Employee filter dropdown */}
      <div className="mb-6">
        <label className="block text-sm text-gray-600 mb-1">Filter by Employee</label>
        <select
          value={selectedEmployee}
          onChange={handleEmployeeChange}
          className="w-full max-w-sm border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500 bg-white"
        >
          <option value="">All Employees</option>
          {employees.map((emp) => (
            <option key={emp.id} value={emp.name}>
              {emp.name} — {emp.department}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 mb-4">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : reviews.length === 0 ? (
        <p className="text-gray-500 text-sm">No reviews found.</p>
      ) : (
        <div className="space-y-3">
          {reviews.map((review) => (
            <div
              key={review.id}
              className="bg-white border border-gray-200 rounded-lg p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-medium text-gray-800">
                    {review.employee_name}
                  </p>
                  <p className="text-sm text-gray-400">
                    {review.department} —{" "}
                    {new Date(review.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(review.id)}
                  className="text-sm text-gray-400 hover:text-red-500"
                >
                  Delete
                </button>
              </div>
              <div className="flex gap-4 text-sm">
                <span className="text-gray-600">
                  Sentiment:{" "}
                  <span className="font-medium">{review.sentiment}</span>
                </span>
                <span className="text-gray-600">
                  Behavioral:{" "}
                  <span className="font-medium">
                    {review.behavioral_rating}/5
                    {review.behavioral_rating && (
                      <span className="text-gray-400 ml-1 text-xs">
                        ({RATING_LABELS[review.behavioral_rating]})
                      </span>
                    )}
                  </span>
                </span>
                <span className="text-gray-600">
                  Performance:{" "}
                  <span className="font-medium">
                    {review.performance_rating}/5
                    {review.performance_rating && (
                      <span className="text-gray-400 ml-1 text-xs">
                        ({RATING_LABELS[review.performance_rating]})
                      </span>
                    )}
                  </span>
                </span>
              </div>
              {review.skills_found && review.skills_found.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {review.skills_found.map((skill, i) => (
                    <span
                      key={i}
                      className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
