import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function usePosts(slug, sort, token) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchPosts = useCallback(async () => {
    if (!slug) return;
    setLoading(true);
    try {
      const data = await api.getCommunityPosts(slug, sort, token);
      setPosts(data.posts || []);
    } finally {
      setLoading(false);
    }
  }, [slug, sort, token]);

  useEffect(() => {
    fetchPosts();
    const id = setInterval(fetchPosts, 30000);
    return () => clearInterval(id);
  }, [fetchPosts]);

  async function createPost(payload) {
    await api.createPost(token, slug, payload);
    await fetchPosts();
  }

  return { posts, loading, createPost, refetch: fetchPosts };
}
