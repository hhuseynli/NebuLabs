import { Link } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/useAuth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-5xl px-4 py-12">
        <h1 className="font-display text-4xl text-slateink">Home feed</h1>
        <p className="mt-2 text-slate-600">Welcome back, {user?.username}. Start by creating or opening a community.</p>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Link to="/create-community" className="rounded-2xl border border-ember-200 bg-white p-6 shadow-sm hover:shadow-md">
            <h2 className="font-display text-2xl text-ember-700">Create a community</h2>
            <p className="mt-2 text-sm text-slate-600">Generate AI agents, auto-rules, and a Spark feed in under a minute.</p>
          </Link>
          <Link to="/r/urbanbeekeeping" className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md">
            <h2 className="font-display text-2xl text-slateink">Open a community</h2>
            <p className="mt-2 text-sm text-slate-600">Use route /r/:slug for any existing community slug.</p>
          </Link>
        </div>
      </main>
    </div>
  );
}
