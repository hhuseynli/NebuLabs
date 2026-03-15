import { useCallback, useEffect, useState } from "react";

import { api } from "../lib/api";

export function useComments(postId, token) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);

  const applyVoteToComments = useCallback((nodes, commentId, nextVote) => {
    return (nodes || []).map((comment) => {
      if (comment.id === commentId) {
        const prevVote = Number(comment.user_vote || 0);
        let upvotes = Number(comment.upvotes || 0);
        let downvotes = Number(comment.downvotes || 0);

        if (prevVote === 1) upvotes = Math.max(0, upvotes - 1);
        if (prevVote === -1) downvotes = Math.max(0, downvotes - 1);
        if (nextVote === 1) upvotes += 1;
        if (nextVote === -1) downvotes += 1;

        return {
          ...comment,
          upvotes,
          downvotes,
          user_vote: nextVote,
          replies: applyVoteToComments(comment.replies || [], commentId, nextVote),
        };
      }

      return {
        ...comment,
        replies: applyVoteToComments(comment.replies || [], commentId, nextVote),
      };
    });
  }, []);

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
    const nextVote = Number(value || 0);
    const previousComments = comments;

    setComments((current) => applyVoteToComments(current, commentId, nextVote));

    try {
      await api.voteComment(token, commentId, nextVote);
    } catch (error) {
      setComments(previousComments);
      throw error;
    }
  }

  return { comments, loading, createComment, voteComment, refetch: fetchComments };
}
