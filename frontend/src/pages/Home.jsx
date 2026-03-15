import { Link } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/useAuth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="page-enter mx-auto max-w-5xl px-4 py-12">
        <section className="glass-panel p-6 md:p-8">
          <h1 className="font-display text-4xl text-[#10242b]">Welcome back, {user?.username}</h1>
          <p className="mt-2 text-[#45606a]">Build momentum with AI-assisted community operations in one place.</p>
        </section>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Link to="/create-community" className="glass-panel p-6 transition hover:-translate-y-0.5">
            <p className="text-xs uppercase tracking-[0.18em] text-[#ff6f3c]">Organizer</p>
            <h2 className="mt-2 font-display text-2xl text-[#0c5f57]">Create a community</h2>
            <p className="mt-2 text-sm text-[#45606a]">Set up your space, launch rules, and unlock FAQ + sentiment dashboards.</p>
          </Link>
          <Link to="/r/urbanbeekeeping" className="glass-panel p-6 transition hover:-translate-y-0.5">
            <p className="text-xs uppercase tracking-[0.18em] text-[#ff6f3c]">Member</p>
            <h2 className="mt-2 font-display text-2xl text-[#10242b]">Open a community</h2>
            <p className="mt-2 text-sm text-[#45606a]">Join discussions, ask FAQ questions, and support fundraiser goals.</p>
          </Link>
        </div>
      </main>
    </div>
  );
}
