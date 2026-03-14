import { useEffect, useState } from "react";

import { api } from "../lib/api";

export function useFeed(slug, onEvent) {
  const [connected, setConnected] = useState(false);
  const [latestEvent, setLatestEvent] = useState(null);

  useEffect(() => {
    if (!slug) return;

    const source = new EventSource(api.streamUrl(slug));
    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);

    ["new_post", "new_comment", "factcheck_fired", "phase_change", "agent_retired"].forEach((type) => {
      source.addEventListener(type, (event) => {
        let parsed = {};
        try {
          parsed = JSON.parse(event.data || "{}");
        } catch {
          parsed = {};
        }
        const payload = { type, data: parsed };
        setLatestEvent(payload);
        if (onEvent) onEvent(payload);
      });
    });

    return () => source.close();
  }, [slug, onEvent]);

  return { connected, latestEvent };
}
