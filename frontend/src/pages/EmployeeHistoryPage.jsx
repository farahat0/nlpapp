import { useState, useEffect } from "react";
import { getReviews, getEmployees } from "../services/api";
import { exportReviewToXlsx } from "../utils/exportReview";

const RATING_LABELS = {
  1: "Unsatisfactory",
  2: "Below Expectations",
  3: "Meets Expectations",
  4: "Exceeds Expectations",
  5: "Exceptional",
};

const formatRecommendations = (text) => {
  if (!text) return null;
  if (text.includes('* ')) {
    const items = text.split('* ').filter(item => item.trim() !== '');
    return (
      <div className="space-y-3 mt-1">
        {items.map((item, index) => (
          <p key={index} className="text-sm text-gray-700 leading-relaxed">
            • {item.trim()}
          </p>
        ))}
      </div>
    );
  }
  return <p className="text-sm text-gray-700 leading-relaxed">{text}</p>;
};

function RatingCard({ title, value }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <p className="text-xl font-semibold text-gray-800">{value}/5</p>
      <p className="text-xs text-gray-400">{RATING_LABELS[value] || "N/A"}</p>
    </div>
  );
}

function ExpandedReview({ review }) {
  return (
    <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
      {/* Review Text */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-500 mb-1">Review Text</h3>
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
          {review.review_text}
        </p>
      </div>

      {/* Sentiment */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-500 mb-1">Sentiment</h3>
        <p className="text-lg font-semibold text-gray-800">{review.sentiment}</p>
        {review.sentiment_confidence != null && (
          <p className="text-sm text-gray-400">
            Confidence: {(review.sentiment_confidence * 100).toFixed(0)}%
          </p>
        )}
      </div>

      {/* Behavioral & Performance Ratings */}
      <div className="grid grid-cols-2 gap-4">
        <RatingCard title="Behavioral Rating" value={review.behavioral_rating} />
        <RatingCard title="Performance Rating" value={review.performance_rating} />
      </div>

      {/* Skills Found */}
      {review.skills_found && review.skills_found.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Skills Identified</h3>
          <div className="flex flex-wrap gap-2">
            {review.skills_found.map((skill, i) => (
              <span
                key={i}
                className="bg-green-50 text-green-700 text-sm px-3 py-1 rounded-full border border-green-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Skill Gaps */}
      {review.skill_gaps && review.skill_gaps.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Skill Gaps</h3>
          <div className="flex flex-wrap gap-2">
            {review.skill_gaps.map((gap, i) => (
              <span
                key={i}
                className="bg-orange-50 text-orange-700 text-sm px-3 py-1 rounded-full border border-orange-200"
              >
                {gap}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {review.recommendations && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-1">Recommendations</h3>
          {formatRecommendations(review.recommendations)}
        </div>
      )}

      {/* Meta info + Export */}
      <div className="flex items-center justify-between pt-3">
        <div className="flex items-center gap-4 text-xs text-gray-400">
          {review.created_by && (
            <span>Created by: <span className="font-medium text-gray-500">{review.created_by}</span></span>
          )}
          <span>
            {new Date(review.created_at).toLocaleString()}
          </span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            exportReviewToXlsx(review);
          }}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 hover:border-emerald-300 transition-colors duration-150 cursor-pointer"
          title="Export this analysis to Excel"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export .xlsx
        </button>
      </div>
    </div>
  );
}

export default function EmployeeHistoryPage() {
  const [reviews, setReviews] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchReviews = async (employeeName) => {
    setLoading(true);
    setError("");
    setExpandedId(null);
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

  const toggleCard = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
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
          {reviews.map((review) => {
            const isExpanded = expandedId === review.id;
            return (
              <div
                key={review.id}
                className={`bg-white border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                  isExpanded
                    ? "border-blue-300 shadow-sm"
                    : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                }`}
                onClick={() => toggleCard(review.id)}
              >
                {/* Collapsed header — always visible */}
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-800">
                      {review.employee_name}
                    </p>
                    <p className="text-sm text-gray-400">
                      {review.department} —{" "}
                      {new Date(review.created_at).toLocaleDateString()}
                    </p>
                    {review.created_by && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        Created by: <span className="text-gray-500 font-medium">{review.created_by}</span>
                      </p>
                    )}
                  </div>
                  <span className="text-gray-300 text-lg">
                    {isExpanded ? "▲" : "▼"}
                  </span>
                </div>

                {/* Expanded detail */}
                {isExpanded && <ExpandedReview review={review} />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
