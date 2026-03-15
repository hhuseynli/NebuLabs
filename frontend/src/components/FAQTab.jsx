import { useState } from "react";
import { Link } from "react-router-dom";

import { useFAQ } from "../hooks/useFAQ";

export default function FAQTab({ slug }) {
  const [question, setQuestion] = useState("");
  const { result, loading, error, ask, history } = useFAQ(slug);
  const confidence = Number(result?.confidence || 0);
  const confident = confidence >= 0.7;
  const lowConfidence = confidence < 0.4;

  return (
    <section className="rounded-2xl border border-ember-100 bg-white p-5">
      <h2 className="font-display text-2xl text-slateink">Community FAQ</h2>
      <p className="mt-1 text-sm text-slate-600">Ask the community anything...</p>
      <div className="mt-4 flex gap-2">
        <input
          className="input"
          placeholder="Ask the community anything..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="btn-primary" onClick={() => ask(question)} disabled={loading || !question.trim()}>
          {loading ? "Searching community knowledge..." : "Ask"}
        </button>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          {lowConfidence ? (
            <>
              <p className="text-sm text-slate-600">Couldn't find a confident answer in the community yet.</p>
              <Link to={`/r/${slug}`} className="mt-2 inline-block text-sm font-semibold text-ember-700">Ask in the community →</Link>
            </>
          ) : (
            <p className="text-sm text-slate-700">{result.answer}</p>
          )}
          <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">
            <span>Confidence: {(confidence * 100).toFixed(0)}%</span>
            {result.source_post_id && confident && (
              <Link to={`/r/${slug}/post/${result.source_post_id}`} className="text-ember-700">From source post</Link>
            )}
          </div>
          <div className="mt-2 h-2 rounded-full bg-slate-200">
            <div className={`h-2 rounded-full ${confident ? "bg-emerald-500" : "bg-amber-500"}`} style={{ width: `${Math.round(confidence * 100)}%` }} />
          </div>
          {result.source_excerpt && <p className="mt-2 text-xs text-slate-500">{result.source_excerpt}</p>}
        </div>
      )}

      {history.length > 0 && (
        <details className="mt-4 rounded-xl border border-slate-200 p-3">
          <summary className="cursor-pointer text-sm font-medium text-slate-700">Previous Q&As</summary>
          <div className="mt-3 space-y-2">
            {history.map((item, index) => (
              <div key={`${item.question}-${index}`} className="rounded-lg bg-slate-50 p-2 text-sm">
                <p className="font-medium text-slateink">Q: {item.question}</p>
                <p className="mt-1 text-slate-600">A: {item.answer}</p>
              </div>
            ))}
          </div>
        </details>
      )}
    </section>
  );
}
