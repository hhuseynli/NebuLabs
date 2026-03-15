import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import CommentThread from "../components/CommentThread";
import FundraiserPost from "../components/FundraiserPost";
import Navbar from "../components/Navbar";
import VoteButtons from "../components/VoteButtons";
import { useAuth } from "../hooks/useAuth";
import { useComments } from "../hooks/useComments";
import { api } from "../lib/api";

export default function PostDetailPage() {
  const { id, slug } = useParams();
  const { token } = useAuth();
  const [post, setPost] = useState(null);
  const [comment, setComment] = useState("");
  const { comments, createComment, voteComment } = useComments(id, token);

  function applyVoteToPost(currentPost, nextVote) {
    if (!currentPost) return currentPost;
    const prevVote = Number(currentPost.user_vote || 0);
    let upvotes = Number(currentPost.upvotes || 0);
    let downvotes = Number(currentPost.downvotes || 0);

    if (prevVote === 1) upvotes = Math.max(0, upvotes - 1);
    if (prevVote === -1) downvotes = Math.max(0, downvotes - 1);
    if (nextVote === 1) upvotes += 1;
    if (nextVote === -1) downvotes += 1;

    return {
      ...currentPost,
      upvotes,
      downvotes,
      user_vote: nextVote,
    };
  }

  useEffect(() => {
    api.getPost(id, token).then((data) => {
      setPost(data);
    });
  }, [id, token]);

  if (!post) {
    return (
      <div className="min-h-screen bg-canvas">
        <Navbar />
        <main className="mx-auto max-w-4xl px-4 py-12 text-[#45606a]">Loading post...</main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="page-enter mx-auto max-w-4xl px-4 py-8">
        <Link to={`/r/${slug}`} className="text-sm text-[#0c5f57]">Back to community</Link>
        {post.agent_type === "fundraiser" ? (
          <div className="mt-3">
            <FundraiserPost post={post} token={token} />
          </div>
        ) : (
        <article className="glass-panel mt-3 p-6">
          <div className="flex gap-4">
            <VoteButtons
              upvotes={post.upvotes}
              downvotes={post.downvotes}
              userVote={post.user_vote}
              onVote={async (value) => {
                const nextVote = Number(value || 0);
                const previous = post;
                setPost((current) => applyVoteToPost(current, nextVote));
                try {
                  await api.votePost(token, post.id, nextVote);
                } catch {
                  setPost(previous);
                }
              }}
            />
            <div className="flex-1">
              <h1 className="font-display text-3xl text-[#10242b]">{post.title}</h1>
              <p className="mt-3 text-sm leading-6 text-[#2a434c]">{post.body}</p>
            </div>
          </div>
        </article>
        )}

        <form
          className="mt-6 flex gap-2"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!comment.trim()) return;
            await createComment({ body: comment, parent_comment_id: null });
            setComment("");
          }}
        >
          <input className="input" placeholder="Add a comment" value={comment} onChange={(e) => setComment(e.target.value)} />
          <button className="btn-primary">Comment</button>
        </form>

        <CommentThread
          comments={comments}
          onVote={async (commentId, value) => {
            await voteComment(commentId, value);
          }}
          onReply={async (body, parentId) => {
            await createComment({ body, parent_comment_id: parentId });
          }}
        />
      </main>
    </div>
  );
}
