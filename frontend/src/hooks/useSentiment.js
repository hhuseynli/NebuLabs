import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function useSentiment(slug, token) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    if (!slug || !token) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.getSentiment(token, slug);
      setReport(data);
    } catch (err) {
      setError(err.message || "Unable to load sentiment report");
    } finally {
      setLoading(false);
    }
  }, [slug, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { report, loading, error, refresh };
}
