import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 border-b border-[#d8e6e7] bg-white/72 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="font-display text-2xl font-bold text-[#0c5f57]">
          Cultify
        </Link>
        <nav className="flex items-center gap-4 text-sm font-semibold text-[#14313a]">
          <Link to="/home" className="hover:text-[#0f8a7b]">Home</Link>
          <Link to="/create-community" className="hover:text-[#0f8a7b]">Create Community</Link>
          {user ? (
            <>
              <Link to={`/u/${user.username}`} className="rounded-full bg-[#e4f3f1] px-3 py-1.5 text-[#0c5f57]">
                u/{user.username}
              </Link>
              <button
                className="rounded-full border border-[#bad6d3] px-3 py-1.5 text-[#0c5f57]"
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
              <Link to="/signup" className="rounded-full bg-[#0f8a7b] px-3 py-1.5 text-white">Sign Up</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
