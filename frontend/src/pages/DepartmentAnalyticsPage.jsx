import { useState, useEffect } from "react";
import { getOverviewStats, getDepartmentStats } from "../services/api";

export default function DepartmentAnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [deptName, setDeptName] = useState("");
  const [deptStats, setDeptStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getOverviewStats()
      .then((res) => setOverview(res.data))
      .catch(() => setError("Failed to load overview"))
      .finally(() => setLoading(false));
  }, []);

  const handleDeptSearch = async (e) => {
    e.preventDefault();
    if (!deptName.trim()) return;
    setError("");
    try {
      const res = await getDepartmentStats(deptName.trim());
      setDeptStats(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load department stats");
      setDeptStats(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Analytics</h1>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 mb-4">
          {error}
        </p>
      )}

      {/* Overview */}
      {loading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : overview ? (
        <div className="mb-8">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Overview</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold text-gray-800">
                {overview.total_reviews}
              </p>
              <p className="text-sm text-gray-400">Total Reviews</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold text-gray-800">
                {overview.total_employees}
              </p>
              <p className="text-sm text-gray-400">Employees</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold text-gray-800">
                {overview.total_departments}
              </p>
              <p className="text-sm text-gray-400">Departments</p>
            </div>
          </div>

          {overview.sentiment_distribution &&
            Object.keys(overview.sentiment_distribution).length > 0 && (
              <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500 mb-2">
                  Sentiment Distribution
                </h3>
                <div className="flex gap-4">
                  {Object.entries(overview.sentiment_distribution).map(
                    ([label, count]) => (
                      <span key={label} className="text-sm text-gray-600">
                        {label}:{" "}
                        <span className="font-medium">{count}</span>
                      </span>
                    )
                  )}
                </div>
              </div>
            )}
        </div>
      ) : null}

      {/* Department Search */}
      <div>
        <h2 className="text-sm font-medium text-gray-500 mb-3">
          Department Stats
        </h2>
        <form onSubmit={handleDeptSearch} className="flex gap-2 mb-4">
          <input
            type="text"
            value={deptName}
            onChange={(e) => setDeptName(e.target.value)}
            placeholder="Enter department name..."
            className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700"
          >
            Search
          </button>
        </form>

        {deptStats && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-800 mb-2">
              {deptStats.department}
            </h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-400">Total Reviews:</span>{" "}
                <span className="text-gray-700 font-medium">
                  {deptStats.total_reviews}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Most Common Sentiment:</span>{" "}
                <span className="text-gray-700 font-medium">
                  {deptStats.most_common_sentiment}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Avg Sentiment Conf:</span>{" "}
                <span className="text-gray-700 font-medium">
                  {(deptStats.average_sentiment_confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                <span className="text-gray-400">Avg Score Conf:</span>{" "}
                <span className="text-gray-700 font-medium">
                  {(deptStats.average_score_confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            {deptStats.top_skills.length > 0 && (
              <div className="mt-3">
                <span className="text-sm text-gray-400">Top Skills: </span>
                {deptStats.top_skills.map((skill, i) => (
                  <span
                    key={i}
                    className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full mr-1"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
