import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="page-enter mx-auto max-w-md px-4 py-16">
        <div className="glass-panel p-8">
          <p className="text-xs uppercase tracking-[0.2em] text-[#0f8a7b]">Cultify Access</p>
          <h1 className="mt-2 font-display text-3xl text-[#10242b]">Welcome back</h1>
          <form
            className="mt-6 space-y-4"
            onSubmit={async (e) => {
              e.preventDefault();
              setError("");
              try {
                await login(form);
                navigate("/home");
              } catch (err) {
                setError(err.message);
              }
            }}
          >
            <input className="input" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input className="input" placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button className="btn-primary w-full">Login</button>
          </form>
          <p className="mt-4 text-sm text-[#45606a]">
            New here? <Link className="text-[#0c5f57]" to="/signup">Create account</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
