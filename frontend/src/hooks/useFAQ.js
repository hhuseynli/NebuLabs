import { useState } from "react";

import { api } from "../lib/api";

export function useFAQ(slug) {
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function ask(question) {
    if (!slug || !question?.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.askFAQ(slug, question.trim());
      setAnswer(data);
    } catch (err) {
      setError(err.message || "Could not fetch answer");
    } finally {
      setLoading(false);
    }
  }

  return { answer, loading, error, ask };
}
