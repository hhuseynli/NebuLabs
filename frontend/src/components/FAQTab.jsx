import { useState } from "react";

import { useFAQ } from "../hooks/useFAQ";

export default function FAQTab({ slug }) {
  const [question, setQuestion] = useState("");
  const { answer, loading, error, ask } = useFAQ(slug);

  return (
    <section className="rounded-2xl border border-ember-100 bg-white p-5">
      <h2 className="font-display text-2xl text-slateink">Community FAQ</h2>
      <p className="mt-1 text-sm text-slate-600">Ask a question and get an answer synthesized from community posts and comments.</p>
      <div className="mt-4 flex gap-2">
        <input
          className="input"
          placeholder="How do I get started with Flutter?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="btn-primary" onClick={() => ask(question)} disabled={loading || !question.trim()}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {answer && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm text-slate-700">{answer.answer}</p>
          <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">
            <span>Confidence: {(Number(answer.confidence || 0) * 100).toFixed(0)}%</span>
            {answer.source_post_id && <span>Source post: {answer.source_post_id}</span>}
          </div>
        </div>
      )}
    </section>
  );
}
