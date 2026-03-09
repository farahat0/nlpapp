import { useLocation, Link } from "react-router-dom";

export default function ResultsPage() {
  const location = useLocation();
  const data = location.state;

  if (!data) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <p className="text-gray-500">
          No results to display.{" "}
          <Link to="/submit" className="text-blue-600 hover:underline">
            Submit a review
          </Link>
        </p>
      </div>
    );
  }

  const { result, employeeName, department } = data;

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-xl font-semibold text-gray-800 mb-2">
        Analysis Results
      </h1>
      <p className="text-sm text-gray-500 mb-6">
        {employeeName} — {department}
      </p>

      <div className="space-y-4">
        {/* Sentiment */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-500 mb-1">Sentiment</h2>
          <p className="text-lg font-semibold text-gray-800">
            {result.sentiment.label}
          </p>
          <p className="text-sm text-gray-400">
            Confidence: {(result.sentiment.confidence * 100).toFixed(0)}%
          </p>
        </div>

        {/* Performance Score */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-500 mb-1">
            Performance Score
          </h2>
          <p className="text-lg font-semibold text-gray-800">
            {result.performance_score.score}
          </p>
          <p className="text-sm text-gray-400">
            Confidence: {(result.performance_score.confidence * 100).toFixed(0)}%
          </p>
        </div>

        {/* Skills Found */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-500 mb-2">
            Skills Identified
          </h2>
          <div className="flex flex-wrap gap-2">
            {result.skills_found.map((skill, i) => (
              <span
                key={i}
                className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-500 mb-1">
            Recommendations
          </h2>
          <p className="text-sm text-gray-700 leading-relaxed">
            {result.recommendations}
          </p>
        </div>
      </div>

      <div className="mt-6 flex gap-4">
        <Link
          to="/submit"
          className="text-sm text-blue-600 hover:underline"
        >
          Submit another review
        </Link>
        <Link
          to="/history"
          className="text-sm text-blue-600 hover:underline"
        >
          View history
        </Link>
      </div>
    </div>
  );
}
