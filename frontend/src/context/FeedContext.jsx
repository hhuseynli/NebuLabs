import { createContext, useContext, useMemo, useState } from "react";

const FeedContext = createContext(null);

export function FeedProvider({ children }) {
  const [posts, setPosts] = useState([]);

  function addPost(post) {
    setPosts((prev) => [post, ...prev.filter((p) => p.id !== post.id)]);
  }

  function updatePost(postId, updater) {
    setPosts((prev) => prev.map((p) => (p.id === postId ? updater(p) : p)));
  }

  const value = useMemo(() => ({ posts, setPosts, addPost, updatePost }), [posts]);

  return <FeedContext.Provider value={value}>{children}</FeedContext.Provider>;
}

export function useFeedContext() {
  const ctx = useContext(FeedContext);
  if (!ctx) throw new Error("FeedContext unavailable");
  return ctx;
}
