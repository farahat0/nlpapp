import { useState, useEffect } from "react";
import { getReviews, getEmployeeReviews, deleteReview } from "../services/api";

export default function EmployeeHistoryPage() {
  const [reviews, setReviews] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchReviews = async (name) => {
    setLoading(true);
    setError("");
    try {
      const res = name
        ? await getEmployeeReviews(name)
        : await getReviews();
      setReviews(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load reviews");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchReviews(search.trim() || null);
  };

  const handleDelete = async (id) => {
    try {
      await deleteReview(id);
      setReviews(reviews.filter((r) => r.id !== id));
    } catch (err) {
      setError("Failed to delete review");
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">
        Review History
      </h1>

      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by employee name..."
          className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700"
        >
          Search
        </button>
        {search && (
          <button
            type="button"
            onClick={() => {
              setSearch("");
              fetchReviews();
            }}
            className="text-sm text-gray-500 hover:text-gray-700 px-2"
          >
            Clear
          </button>
        )}
      </form>

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
                  Score:{" "}
                  <span className="font-medium">{review.performance_score}</span>
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
