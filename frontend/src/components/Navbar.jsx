import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-lg font-semibold text-gray-800">
          HR NLP
        </Link>

        {user && (
          <div className="flex items-center gap-6">
            <Link
              to="/submit"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Submit Review
            </Link>
            <Link
              to="/history"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              History
            </Link>
            <Link
              to="/analytics"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Analytics
            </Link>
            <span className="text-sm text-gray-400">|</span>
            <span className="text-sm text-gray-500">{user.username}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 hover:text-red-600"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
