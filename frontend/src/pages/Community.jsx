import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import FAQTab from "../components/FAQTab";
import Navbar from "../components/Navbar";
import PostCard from "../components/PostCard";
import { useAuth } from "../hooks/useAuth";
import { usePosts } from "../hooks/usePosts";
import { api } from "../lib/api";

export default function CommunityPage() {
  const { slug } = useParams();
  const { token, user } = useAuth();
  const [tab, setTab] = useState("posts");
  const [sort, setSort] = useState("hot");
  const [community, setCommunity] = useState(null);
  const [form, setForm] = useState({ title: "", body: "", flair: "" });

  const { posts, loading, createPost, votePost } = usePosts(slug, sort, token);

  useEffect(() => {
    api.getCommunity(slug).then(setCommunity).catch(() => setCommunity(null));
  }, [slug]);

  async function handleVote(postId, value) {
    if (!token) return;
    await votePost(postId, value);
  }

  async function submitPost(e) {
    e.preventDefault();
    if (!form.title || !form.body) return;
    await createPost(form);
    setForm({ title: "", body: "", flair: "" });
  }

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <section>
            <div className="mb-4 rounded-2xl border border-ember-100 bg-white p-5">
              <h1 className="font-display text-3xl text-slateink">r/{community?.slug || slug}</h1>
              <p className="mt-1 text-sm text-slate-600">{community?.description || "Loading..."}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {[
                  ["posts", "Posts"],
                  ["faq", "FAQ"],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    className={`rounded-full px-3 py-1.5 text-xs font-semibold ${tab === key ? "bg-slateink text-white" : "bg-slate-100 text-slate-600"}`}
                    onClick={() => setTab(key)}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {tab === "posts" && (
              <div className="mt-4 flex gap-2">
                {[
                  ["hot", "Hot"],
                  ["new", "New"],
                  ["top", "Top"],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    className={`rounded-full px-3 py-1.5 text-xs font-semibold ${sort === key ? "bg-ember-500 text-white" : "bg-slate-100 text-slate-600"}`}
                    onClick={() => setSort(key)}
                  >
                    {label}
                  </button>
                ))}
              </div>
              )}
            </div>

            {tab === "posts" && user && (
              <form onSubmit={submitPost} className="mb-6 rounded-2xl border border-ember-100 bg-white p-4">
                <input className="input mb-2" placeholder="Post title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
                <textarea className="input mb-2 min-h-20" placeholder="Share something" value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
                <input className="input mb-3" placeholder="Flair (optional)" value={form.flair} onChange={(e) => setForm({ ...form, flair: e.target.value })} />
                <button className="btn-primary">Create Post</button>
              </form>
            )}

            {tab === "posts" && (
              <>
                {loading && <p className="text-sm text-slate-500">Loading posts...</p>}
                {posts.map((post) => (
                  <PostCard key={post.id} post={post} slug={slug} onVote={handleVote} />
                ))}
              </>
            )}

            {tab === "faq" && <FAQTab slug={slug} />}
          </section>

          <aside className="space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Rules</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-700">
                {(community?.rules || []).map((rule) => (
                  <li key={rule.title}>
                    <p className="font-semibold">{rule.title}</p>
                    <p>{rule.body}</p>
                  </li>
                ))}
              </ul>
            </div>
            <Link to={`/r/${slug}/dashboard`} className="block rounded-2xl bg-slateink px-4 py-3 text-center text-sm font-semibold text-white">Open Organizer Dashboard</Link>
          </aside>
        </div>
      </main>
    </div>
  );
}
