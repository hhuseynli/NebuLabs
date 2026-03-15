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
    <section className="glass-panel p-5">
      <h2 className="font-display text-2xl text-[#10242b]">Community FAQ</h2>
      <p className="mt-1 text-sm text-[#45606a]">Ask the community anything...</p>
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
        <div className="mt-4 rounded-xl border border-[#d8e6e7] bg-[#f7fbfb] p-4">
          {lowConfidence ? (
            <>
              <p className="text-sm text-[#45606a]">Couldn't find a confident answer in the community yet.</p>
              <Link to={`/r/${slug}`} className="mt-2 inline-block text-sm font-semibold text-[#0c5f57]">Ask in the community →</Link>
            </>
          ) : (
            <p className="text-sm text-[#203a42]">{result.answer}</p>
          )}
          <div className="mt-2 flex items-center gap-3 text-xs text-[#55717b]">
            <span>Confidence: {(confidence * 100).toFixed(0)}%</span>
            {result.source_post_id && confident && (
              <Link to={`/r/${slug}/post/${result.source_post_id}`} className="text-[#0c5f57]">From source post</Link>
            )}
          </div>
          <div className="mt-2 h-2 rounded-full bg-[#deeaec]">
            <div className={`h-2 rounded-full ${confident ? "bg-[#0f8a7b]" : "bg-[#ff6f3c]"}`} style={{ width: `${Math.round(confidence * 100)}%` }} />
          </div>
          {result.source_excerpt && <p className="mt-2 text-xs text-[#58717a]">{result.source_excerpt}</p>}
        </div>
      )}

      {history.length > 0 && (
        <details className="mt-4 rounded-xl border border-[#d8e6e7] p-3">
          <summary className="cursor-pointer text-sm font-medium text-[#223e47]">Previous Q&As</summary>
          <div className="mt-3 space-y-2">
            {history.map((item, index) => (
              <div key={`${item.question}-${index}`} className="rounded-lg bg-[#f6fbfb] p-2 text-sm">
                <p className="font-medium text-[#16333c]">Q: {item.question}</p>
                <p className="mt-1 text-[#45606a]">A: {item.answer}</p>
              </div>
            ))}
          </div>
        </details>
      )}
    </section>
  );
}
