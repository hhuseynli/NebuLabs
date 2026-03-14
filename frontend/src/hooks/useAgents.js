import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function useAgents(slug, token) {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAgents = useCallback(async () => {
    if (!slug) return;
    setLoading(true);
    try {
      const data = await api.getAgents(slug);
      setAgents(data.agents || []);
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchAgents();
    const id = setInterval(fetchAgents, 15000);
    return () => clearInterval(id);
  }, [fetchAgents]);

  async function retireAgent(agentId) {
    await api.updateAgent(token, slug, agentId, "retired");
    await fetchAgents();
  }

  return { agents, loading, retireAgent, refetch: fetchAgents };
}
