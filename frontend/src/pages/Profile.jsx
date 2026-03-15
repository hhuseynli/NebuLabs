import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Navbar from "../components/Navbar";
import { api } from "../lib/api";

export default function ProfilePage() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError("");

    api.getProfile(username)
      .then((data) => {
        if (!mounted) return;
        setProfile(data);
      })
      .catch((err) => {
        if (!mounted) return;
        setProfile(null);
        setError(err.message || "Profile not found");
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [username]);

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-8">
        {loading ? (
          <p>Loading profile...</p>
        ) : !profile ? (
          <p className="text-sm text-slate-600">{error || "Profile not found."}</p>
        ) : (
          <>
            <div className="rounded-2xl border border-ember-100 bg-white p-6">
              <h1 className="font-display text-4xl text-slateink">u/{profile.username}</h1>
              <p className="mt-2 text-slate-600">{profile.bio}</p>
              <p className="mt-2 text-sm text-ember-700">Karma: {profile.karma}</p>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <section className="rounded-2xl border border-slate-200 bg-white p-4">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Recent Posts</h2>
                <ul className="mt-3 space-y-2 text-sm">
                  {profile.recent_posts.map((post) => (
                    <li key={post.id}>
                      {post.community_slug ? (
                        <Link className="text-ember-700" to={`/r/${post.community_slug}/post/${post.id}`}>{post.title}</Link>
                      ) : (
                        <span className="text-slate-500">{post.title}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
              <section className="rounded-2xl border border-slate-200 bg-white p-4">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Recent Comments</h2>
                <ul className="mt-3 space-y-2 text-sm text-slate-700">
                  {profile.recent_comments.map((comment) => (
                    <li key={comment.id}>{comment.body}</li>
                  ))}
                </ul>
              </section>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
