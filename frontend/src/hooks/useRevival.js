import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function useRevival(slug, token) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = useCallback(async () => {
    if (!slug) return;
    setLoading(true);
    try {
      setStatus(await api.getRevival(slug));
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchStatus();
    const id = setInterval(fetchStatus, 10000);
    return () => clearInterval(id);
  }, [fetchStatus]);

  async function advancePhase(toPhase) {
    await api.advanceRevival(token, slug, toPhase);
    await fetchStatus();
  }

  return { status, loading, advancePhase, refetch: fetchStatus };
}
