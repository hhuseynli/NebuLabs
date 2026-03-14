import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/useAuth";

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [error, setError] = useState("");

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-md px-4 py-16">
        <div className="rounded-3xl border border-ember-100 bg-white p-8 shadow-lg">
          <h1 className="font-display text-3xl text-slateink">Create account</h1>
          <form
            className="mt-6 space-y-4"
            onSubmit={async (e) => {
              e.preventDefault();
              setError("");
              try {
                await signup(form);
                navigate("/home");
              } catch (err) {
                setError(err.message);
              }
            }}
          >
            <input className="input" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input className="input" placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            <input className="input" placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button className="btn-primary w-full">Sign Up</button>
          </form>
          <p className="mt-4 text-sm text-slate-600">
            Have an account? <Link className="text-ember-700" to="/login">Login</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
