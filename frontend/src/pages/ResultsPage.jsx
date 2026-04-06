import { useLocation, Link } from "react-router-dom";

const RATING_LABELS = {
  1: "Unsatisfactory",
  2: "Below Expectations",
  3: "Meets Expectations",
  4: "Exceeds Expectations",
  5: "Exceptional",
};

function RatingCard({ title, value }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h2 className="text-sm font-medium text-gray-500 mb-1">{title}</h2>
      <p className="text-2xl font-semibold text-gray-800">{value}/5</p>
      <p className="text-sm text-gray-400">{RATING_LABELS[value] || "N/A"}</p>
    </div>
  );
}

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

        {/* Behavioral & Performance Ratings */}
        <div className="grid grid-cols-2 gap-4">
          <RatingCard title="Behavioral Rating" value={result.behavioral_rating} />
          <RatingCard title="Performance Rating" value={result.performance_rating} />
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
                className="bg-green-50 text-green-700 text-sm px-3 py-1 rounded-full border border-green-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Skill Gaps */}
        {result.skill_gaps && result.skill_gaps.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h2 className="text-sm font-medium text-gray-500 mb-2">
              Skill Gaps
            </h2>
            <div className="flex flex-wrap gap-2">
              {result.skill_gaps.map((gap, i) => (
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
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-500 mb-1">
            Recommendations
          </h2>
          <p className="text-sm text-gray-700 leading-relaxed">
            {result.recommendations}
          </p>
        </div>

        {/* Created By */}
        {result.created_by && (
          <div className="text-sm text-gray-400">
            Created by: <span className="font-medium text-gray-500">{result.created_by}</span>
          </div>
        )}
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
