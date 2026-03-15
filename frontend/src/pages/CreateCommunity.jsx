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

  function validate(values) {
    const name = values.name.trim();
    const description = values.description.trim();
    const ideal = values.ideal_member_description.trim();

    if (!name || !description || !ideal) {
      return "All fields are required.";
    }
    if (name.length < 3 || name.length > 80) {
      return "Community name must be between 3 and 80 characters.";
    }
    if (description.length < 10 || description.length > 500) {
      return "Description must be between 10 and 500 characters.";
    }
    if (ideal.length < 10 || ideal.length > 300) {
      return "Ideal member description must be between 10 and 300 characters.";
    }

    return "";
  }

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="page-enter mx-auto max-w-3xl px-4 py-12">
        <div className="glass-panel p-8">
          <p className="text-xs uppercase tracking-[0.2em] text-[#0f8a7b]">Organizer Setup</p>
          <h1 className="mt-2 font-display text-4xl text-[#10242b]">Create Community</h1>
          <p className="mt-2 text-sm text-[#45606a]">Cultify will generate starter rules and configure AI community tools automatically.</p>
          <form
            className="mt-6 space-y-4"
            onSubmit={async (e) => {
              e.preventDefault();
              setError("");

              const validationError = validate(form);
              if (validationError) {
                setError(validationError);
                return;
              }

              setLoading(true);
              try {
                const data = await api.createCommunity(token, {
                  name: form.name.trim(),
                  description: form.description.trim(),
                  ideal_member_description: form.ideal_member_description.trim(),
                });
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
