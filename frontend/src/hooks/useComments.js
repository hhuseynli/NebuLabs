import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function useComments(postId, token) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchComments = useCallback(async () => {
    if (!postId) return;
    setLoading(true);
    try {
      const data = await api.getComments(postId, token);
      setComments(data.comments || []);
    } finally {
      setLoading(false);
    }
  }, [postId, token]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  async function createComment(payload) {
    await api.createComment(token, postId, payload);
    await fetchComments();
  }

  async function voteComment(commentId, value) {
    await api.voteComment(token, commentId, value);
    await fetchComments();
  }

  return { comments, loading, createComment, voteComment, refetch: fetchComments };
}
