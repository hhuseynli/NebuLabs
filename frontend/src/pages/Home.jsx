import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";

export default function HomePage() {
  const { user } = useAuth();
  const [communities, setCommunities] = useState([]);
  const [loadingCommunities, setLoadingCommunities] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadCommunities() {
      setLoadingCommunities(true);
      try {
        const data = await api.listCommunities(8, 0);
        if (active) {
          setCommunities(Array.isArray(data.communities) ? data.communities : []);
        }
      } catch {
        if (active) {
          setCommunities([]);
        }
      } finally {
        if (active) {
          setLoadingCommunities(false);
        }
      }
    }

    loadCommunities();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="page-enter mx-auto max-w-5xl px-4 py-12">
        <section className="glass-panel p-6 md:p-8">
          <h1 className="font-display text-4xl text-[#10242b]">Welcome back, {user?.username}</h1>
          <p className="mt-2 text-[#45606a]">Build momentum with AI-assisted community operations in one place.</p>
        </section>

        <div className="mt-6">
          <Link to="/create-community" className="glass-panel block p-6 transition hover:-translate-y-0.5">
            <p className="text-xs uppercase tracking-[0.18em] text-[#ff6f3c]">Organizer</p>
            <h2 className="mt-2 font-display text-2xl text-[#0c5f57]">Create a community</h2>
            <p className="mt-2 text-sm text-[#45606a]">Set up your space, launch rules, and unlock FAQ + sentiment dashboards.</p>
          </Link>
        </div>

        <section className="glass-panel mt-6 p-6">
          <p className="text-xs uppercase tracking-[0.18em] text-[#ff6f3c]">Dashboard</p>
          <h2 className="mt-2 font-display text-2xl text-[#10242b]">Communities</h2>
          <p className="mt-2 text-sm text-[#45606a]">Browse your communities and jump into feed or organizer tools.</p>

          <div className="mt-4 space-y-3">
            {loadingCommunities && <p className="text-sm text-[#45606a]">Loading communities...</p>}

            {!loadingCommunities && communities.length === 0 && (
              <p className="text-sm text-[#45606a]">No communities yet. Create your first one above.</p>
            )}

            {!loadingCommunities && communities.map((community) => (
              <div
                key={community.id}
                className="rounded-xl border border-[#d5e5e9] bg-white/70 p-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="font-semibold text-[#14323a]">{community.name || `r/${community.slug}`}</p>
                    <p className="text-xs text-[#5a7480]">r/{community.slug} • {community.member_count || 0} members</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/r/${community.slug}`}
                      className="rounded-lg bg-[#edf4f6] px-3 py-1.5 text-xs font-semibold text-[#24414a] transition hover:bg-[#dcecf0]"
                    >
                      Open Feed
                    </Link>
                    <Link
                      to={`/r/${community.slug}/dashboard`}
                      className="rounded-lg bg-[#10242b] px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-[#0c1c22]"
                    >
                      Organizer Dashboard
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
