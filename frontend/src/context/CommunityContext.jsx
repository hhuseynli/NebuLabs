import { createContext, useContext, useMemo, useState } from "react";

const CommunityContext = createContext(null);

export function CommunityProvider({ children }) {
  const [community, setCommunity] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const value = useMemo(() => ({ community, setCommunity, isLoading, setIsLoading }), [community, isLoading]);

  return <CommunityContext.Provider value={value}>{children}</CommunityContext.Provider>;
}

export function useCommunityContext() {
  const ctx = useContext(CommunityContext);
  if (!ctx) throw new Error("CommunityContext unavailable");
  return ctx;
}
