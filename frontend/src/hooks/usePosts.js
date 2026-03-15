import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function usePosts(slug, sort, token) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);

  const applyVoteToPost = useCallback((list, postId, nextVote) => {
    return list.map((post) => {
      if (post.id !== postId) return post;

      const prevVote = Number(post.user_vote || 0);
      let upvotes = Number(post.upvotes || 0);
      let downvotes = Number(post.downvotes || 0);

      if (prevVote === 1) upvotes = Math.max(0, upvotes - 1);
      if (prevVote === -1) downvotes = Math.max(0, downvotes - 1);
      if (nextVote === 1) upvotes += 1;
      if (nextVote === -1) downvotes += 1;

      return {
        ...post,
        upvotes,
        downvotes,
        user_vote: nextVote,
      };
    });
  }, []);

  const fetchPosts = useCallback(async () => {
    if (!slug) {
      console.log("[usePosts] No slug provided, skipping fetch");
      return;
    }
    console.log(`[usePosts] Fetching posts for slug=${slug}, sort=${sort}`);
    setLoading(true);
    try {
      const data = await api.getCommunityPosts(slug, sort, token);
      console.log(`[usePosts] Fetched ${data.posts?.length || 0} posts`);
      setPosts(data.posts || []);
    } catch (err) {
      console.error("[usePosts] Fetch failed:", err.message);
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

  async function votePost(postId, value) {
    const nextVote = Number(value || 0);
    const previousPosts = posts;

    setPosts((current) => applyVoteToPost(current, postId, nextVote));

    try {
      await api.votePost(token, postId, nextVote);
    } catch (error) {
      setPosts(previousPosts);
      throw error;
    }
  }

  return { posts, loading, createPost, votePost, refetch: fetchPosts };
}
