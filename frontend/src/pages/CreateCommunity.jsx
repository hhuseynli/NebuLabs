import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";

export default function CreateCommunityPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    description: "",
    ideal_member_description: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-3xl px-4 py-12">
        <div className="rounded-3xl border border-ember-100 bg-white p-8 shadow-lg">
          <h1 className="font-display text-4xl text-slateink">Create Community</h1>
          <p className="mt-2 text-sm text-slate-600">Kindling will generate five agents and custom rules automatically.</p>
          <form
            className="mt-6 space-y-4"
            onSubmit={async (e) => {
              e.preventDefault();
              setError("");
              setLoading(true);
              try {
                const data = await api.createCommunity(token, form);
                navigate(`/r/${data.slug}`);
              } catch (err) {
                setError(err.message);
              } finally {
                setLoading(false);
              }
            }}
          >
            <input className="input" placeholder="Community name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <textarea className="input min-h-24" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            <textarea className="input min-h-24" placeholder="Ideal member description" value={form.ideal_member_description} onChange={(e) => setForm({ ...form, ideal_member_description: e.target.value })} />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button className="btn-primary" disabled={loading}>{loading ? "Creating..." : "Create"}</button>
          </form>
        </div>
      </main>
    </div>
  );
}
