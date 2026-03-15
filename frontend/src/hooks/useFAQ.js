import { useState } from "react";

import { api } from "../lib/api";

export function useFAQ(slug) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  async function ask(question) {
    if (!slug || !question?.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.askFAQ(slug, question.trim());
      const next = { question: question.trim(), ...data };
      setResult(next);
      setHistory((prev) => [next, ...prev].slice(0, 5));
    } catch (err) {
      setError(err.message || "Could not fetch answer");
    } finally {
      setLoading(false);
    }
  }

  return { ask, result, loading, error, history };
}
