import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function useSentiment(slug, token) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastFetched, setLastFetched] = useState(null);
  const [secondsUntilRefresh, setSecondsUntilRefresh] = useState(0);

  const refresh = useCallback(async () => {
    if (!slug || !token) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.getSentiment(token, slug);
      setReport(data);
      setLastFetched(Date.now());
    } catch (err) {
      setError(err.message || "Unable to load sentiment report");
    } finally {
      setLoading(false);
    }
  }, [slug, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const id = setInterval(() => {
      if (!lastFetched) {
        setSecondsUntilRefresh(0);
        return;
      }
      const elapsed = Math.floor((Date.now() - lastFetched) / 1000);
      const remaining = Math.max(0, 300 - elapsed);
      setSecondsUntilRefresh(remaining);
    }, 1000);
    return () => clearInterval(id);
  }, [lastFetched]);

  return { report, loading, error, refresh, canRefresh: secondsUntilRefresh === 0, secondsUntilRefresh, lastFetched };
}
