import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import CommentThread from "../components/CommentThread";
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
  const { comments, createComment, voteComment, refetch } = useComments(id, token);

  useEffect(() => {
    api.getPost(id, token).then((data) => {
      setPost(data);
    });
  }, [id, token]);

  if (!post) {
    return (
      <div className="min-h-screen bg-canvas">
        <Navbar />
        <main className="mx-auto max-w-4xl px-4 py-12">Loading post...</main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <Link to={`/r/${slug}`} className="text-sm text-ember-700">Back to community</Link>
        <article className="mt-3 rounded-2xl border border-ember-100 bg-white p-6 shadow-sm">
          <div className="flex gap-4">
            <VoteButtons
              upvotes={post.upvotes}
              downvotes={post.downvotes}
              userVote={post.user_vote}
              onVote={async (value) => {
                await api.votePost(token, post.id, value);
                setPost(await api.getPost(id, token));
              }}
            />
            <div className="flex-1">
              <h1 className="font-display text-3xl text-slateink">{post.title}</h1>
              <p className="mt-3 text-sm leading-6 text-slate-700">{post.body}</p>
              {post.has_factcheck && (
                <p className="mt-4 rounded-lg border border-spruce/30 bg-spruce/10 px-3 py-2 text-xs font-semibold text-spruce">
                  A claim in this thread was fact-checked with opendata.az.
                </p>
              )}
            </div>
          </div>
        </article>

        <form
          className="mt-6 flex gap-2"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!comment.trim()) return;
            await createComment({ body: comment, parent_comment_id: null });
            setComment("");
            await refetch();
          }}
        >
          <input className="input" placeholder="Add a comment" value={comment} onChange={(e) => setComment(e.target.value)} />
          <button className="btn-primary">Comment</button>
        </form>

        <CommentThread
          comments={comments}
          onVote={async (commentId, value) => {
            await voteComment(commentId, value);
            await refetch();
          }}
          onReply={async (body, parentId) => {
            await createComment({ body, parent_comment_id: parentId });
            await refetch();
          }}
        />
      </main>
    </div>
  );
}
