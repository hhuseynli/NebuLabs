import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "../lib/api";

export function useFundraiser(postId, token) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetch = useCallback(async () => {
    if (!postId || !token) return;
    setLoading(true);
    try {
      const data = await api.getPledges(token, postId);
      setSummary(data);
    } finally {
      setLoading(false);
    }
  }, [postId, token]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const userPledge = useMemo(() => {
    const username = JSON.parse(localStorage.getItem("kindling_user") || "null")?.username;
    if (!username || !summary?.pledges) return null;
    return summary.pledges.find((pledge) => pledge.username === username) || null;
  }, [summary]);

  async function pledge(amount_suggested, message) {
    if (!postId || !token) return;
    await api.createPledge(token, postId, { amount_suggested, message });
    await fetch();
  }

  async function retract() {
    if (!postId || !token) return;
    await api.retractPledge(token, postId);
    await fetch();
  }

  return {
    pledges: summary?.pledges || [],
    pledgeCount: summary?.pledge_count || 0,
    totalPledged: summary?.total_pledged || 0,
    goalAmount: summary?.goal_amount || 0,
    userPledge,
    pledge,
    retract,
    loading,
    fetch,
  };
}
