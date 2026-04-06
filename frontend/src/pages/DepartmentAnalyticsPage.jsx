import { useState, useEffect } from "react";
import {
  getOverviewStats,
  getDepartmentStats,
  getEmployees,
  getEmployeeTrend,
} from "../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
} from "recharts";

const RATING_LABELS = {
  1: "Unsatisfactory",
  2: "Below Expectations",
  3: "Meets Expectations",
  4: "Exceeds Expectations",
  5: "Exceptional",
};

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
      <p className="text-2xl font-semibold text-gray-800">{value}</p>
      <p className="text-sm text-gray-400">{label}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

function SentimentBarChart({ data }) {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));
  const COLORS = { Positive: "#22c55e", Negative: "#ef4444", Neutral: "#6b7280" };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-sm font-medium text-gray-500 mb-3">Sentiment Distribution</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#6b7280" }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#6b7280" }} />
          <Tooltip
            contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 13 }}
          />
          <Bar
            dataKey="value"
            radius={[4, 4, 0, 0]}
            fill="#6366f1"
            barSize={40}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function HorizontalBarChart({ title, data, color }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 flex-1">
      <h3 className="text-sm font-medium text-gray-500 mb-3">{title}</h3>
      {data.length === 0 ? (
        <p className="text-sm text-gray-400">No data available</p>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={data} layout="vertical" margin={{ left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: "#6b7280" }} />
            <YAxis
              type="category"
              dataKey="skill"
              width={100}
              tick={{ fontSize: 11, fill: "#6b7280" }}
            />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 13 }}
            />
            <Bar dataKey="count" fill={color} radius={[0, 4, 4, 0]} barSize={20} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

function TrendLineChart({ data }) {
  const chartData = data.map((d) => ({
    ...d,
    date: new Date(d.date).toLocaleDateString(),
  }));

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-sm font-medium text-gray-500 mb-3">Rating Trend Over Time</h3>
      {chartData.length === 0 ? (
        <p className="text-sm text-gray-400">No trend data available</p>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <YAxis domain={[0, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 12, fill: "#6b7280" }} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 13 }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="behavioral_rating"
              name="Behavioral"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="performance_rating"
              name="Performance"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default function DepartmentAnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Employees & trend
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [trendData, setTrendData] = useState([]);

  // Department filter
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState("");
  const [deptStats, setDeptStats] = useState(null);

  useEffect(() => {
    getOverviewStats()
      .then((res) => setOverview(res.data))
      .catch(() => setError("Failed to load overview"))
      .finally(() => setLoading(false));

    getEmployees()
      .then((res) => {
        setEmployees(res.data);
        // Extract unique departments
        const depts = [...new Set(res.data.map((e) => e.department))];
        setDepartments(depts);
      })
      .catch(() => {});
  }, []);

  const handleEmployeeSelect = async (e) => {
    const name = e.target.value;
    setSelectedEmployee(name);
    if (!name) {
      setTrendData([]);
      return;
    }
    try {
      const res = await getEmployeeTrend(name);
      setTrendData(res.data);
    } catch {
      setTrendData([]);
    }
  };

  const handleDeptSelect = async (e) => {
    const dept = e.target.value;
    setSelectedDept(dept);
    if (!dept) {
      setDeptStats(null);
      return;
    }
    try {
      const res = await getDepartmentStats(dept);
      setDeptStats(res.data);
    } catch {
      setDeptStats(null);
    }
  };

  // Use department-scoped data if selected, otherwise overview
  const activeData = selectedDept && deptStats ? deptStats : overview;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Analytics Dashboard</h1>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 mb-4">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : activeData ? (
        <>
          {/* Summary Bar */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <StatCard
              label="Total Reviews"
              value={activeData.total_reviews}
            />
            <StatCard
              label="Avg Behavioral Rating"
              value={activeData.average_behavioral_rating?.toFixed(1) || "0.0"}
              sub={RATING_LABELS[Math.round(activeData.average_behavioral_rating)] || ""}
            />
            <StatCard
              label="Avg Performance Rating"
              value={activeData.average_performance_rating?.toFixed(1) || "0.0"}
              sub={RATING_LABELS[Math.round(activeData.average_performance_rating)] || ""}
            />
          </div>

          {/* Sentiment Chart */}
          {activeData.sentiment_distribution && (
            <div className="mb-6">
              <SentimentBarChart data={activeData.sentiment_distribution} />
            </div>
          )}

          {/* Skills & Gaps */}
          <div className="flex gap-4 mb-6">
            <HorizontalBarChart
              title="Top 5 Skills"
              data={activeData.top_skills || []}
              color="#22c55e"
            />
            <HorizontalBarChart
              title="Top 5 Gaps"
              data={activeData.top_gaps || []}
              color="#ef4444"
            />
          </div>

          {/* Department Filter */}
          <div className="mb-6 bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Filter by Department</h3>
            <select
              value={selectedDept}
              onChange={handleDeptSelect}
              className="w-full max-w-sm border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500 bg-white"
            >
              <option value="">All Departments (Overview)</option>
              {departments.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Employee Trend */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Employee Rating Trend</h3>
            <select
              value={selectedEmployee}
              onChange={handleEmployeeSelect}
              className="w-full max-w-sm border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500 bg-white mb-4"
            >
              <option value="">Select an employee...</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.name}>
                  {emp.name} — {emp.department}
                </option>
              ))}
            </select>
            {selectedEmployee && <TrendLineChart data={trendData} />}
          </div>
        </>
      ) : null}
    </div>
  );
}
