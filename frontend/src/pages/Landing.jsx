import { Link } from "react-router-dom";

import Navbar from "../components/Navbar";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="page-enter mx-auto grid max-w-6xl gap-8 px-4 py-16 md:grid-cols-[1.1fr_0.9fr] md:items-center">
        <section className="glass-panel p-8 md:p-10">
          <p className="mb-3 text-xs uppercase tracking-[0.22em] text-[#0f8a7b]">Cultify</p>
          <h1 className="font-display text-5xl leading-tight text-[#10242b]">
            Keep tech communities alive before momentum fades.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-[#34505a]">
            Cultify combines Reddit-style discussion with AI copilots for FAQ, sentiment, and fundraising so organizers spend less time firefighting and more time building real community.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/signup" className="btn-primary px-6 py-3 text-sm">Start a Community</Link>
            <Link to="/login" className="rounded-full border border-[#bad6d3] px-6 py-3 text-sm font-semibold text-[#0c5f57]">Log In</Link>
          </div>
        </section>

        <section className="space-y-4">
          <article className="glass-panel p-6">
            <p className="text-xs font-semibold uppercase tracking-widest text-[#ff6f3c]">AI FAQ</p>
            <h2 className="mt-2 font-display text-2xl text-[#10242b]">Answer repeat questions instantly</h2>
            <p className="mt-2 text-sm text-[#45606a]">Members ask once. Cultify answers from your own threads with confidence and source context.</p>
          </article>
          <article className="glass-panel p-6">
            <p className="text-xs font-semibold uppercase tracking-widest text-[#ff6f3c]">Health Signal</p>
            <h2 className="mt-2 font-display text-2xl text-[#10242b]">See community sentiment in one view</h2>
            <p className="mt-2 text-sm text-[#45606a]">Track friction, topic trends, and churn risk before your core members silently drop off.</p>
          </article>
          <article className="glass-panel p-6">
            <p className="text-xs font-semibold uppercase tracking-widest text-[#ff6f3c]">Fundraiser Agent</p>
            <h2 className="mt-2 font-display text-2xl text-[#10242b]">Turn needs into coordinated action</h2>
            <p className="mt-2 text-sm text-[#45606a]">Detect real funding gaps, publish a goal post, and collect pledges directly from engaged members.</p>
          </article>
        </section>
      </main>
    </div>
  );
}
