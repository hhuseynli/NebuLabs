import { createContext, useContext, useMemo, useState } from "react";

import { api } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("kindling_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem("kindling_token"));
  const [loading, setLoading] = useState(false);

  async function signup(payload) {
    setLoading(true);
    try {
      const data = await api.signup(payload);
      setUser(data.user);
      setToken(data.token);
      localStorage.setItem("kindling_user", JSON.stringify(data.user));
      localStorage.setItem("kindling_token", data.token);
      return data;
    } finally {
      setLoading(false);
    }
  }

  async function login(payload) {
    setLoading(true);
    try {
      const data = await api.login(payload);
      setUser(data.user);
      setToken(data.token);
      localStorage.setItem("kindling_user", JSON.stringify(data.user));
      localStorage.setItem("kindling_token", data.token);
      return data;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setUser(null);
    setToken(null);
    localStorage.removeItem("kindling_user");
    localStorage.removeItem("kindling_token");
  }

  const value = useMemo(() => ({ user, token, loading, signup, login, logout }), [user, token, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("AuthContext unavailable");
  return ctx;
}
