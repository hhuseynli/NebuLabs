import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="border-b border-ember-100/40 bg-white/70 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="font-display text-2xl font-bold text-ember-700">Kindling</Link>
        <nav className="flex items-center gap-4 text-sm font-medium text-slateink">
          <Link to="/home" className="hover:text-ember-700">Home</Link>
          <Link to="/create-community" className="hover:text-ember-700">Create Community</Link>
          {user ? (
            <>
              <Link to={`/u/${user.username}`} className="rounded-full bg-ember-100 px-3 py-1.5 text-ember-700">
                u/{user.username}
              </Link>
              <button
                className="rounded-full border border-ember-300 px-3 py-1.5 text-ember-700"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/signup" className="rounded-full bg-ember-500 px-3 py-1.5 text-white">Sign Up</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
