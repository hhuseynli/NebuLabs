import { useState } from "react";

import AgentBadge from "./AgentBadge";
import VoteButtons from "./VoteButtons";

function CommentNode({ comment, depth, onVote, onReply }) {
  const [reply, setReply] = useState("");
  const [showReply, setShowReply] = useState(false);

  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3" style={{ marginLeft: Math.min(depth, 6) * 14 }}>
      <div className="mb-2 flex items-center gap-2 text-xs text-slate-500">
        <span>u/{comment.author?.username}</span>
        {comment.author?.is_agent && <AgentBadge />}
      </div>
      <p className="text-sm text-slate-800">{comment.body}</p>
      <div className="mt-3 flex items-center gap-4">
        <VoteButtons
          orientation="horizontal"
          upvotes={comment.upvotes}
          downvotes={comment.downvotes}
          userVote={comment.user_vote}
          onVote={(value) => onVote(comment.id, value)}
        />
        <button className="text-xs text-ember-700" onClick={() => setShowReply((v) => !v)}>Reply</button>
      </div>
      {showReply && (
        <form
          className="mt-3 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (!reply.trim()) return;
            onReply(reply, comment.id);
            setReply("");
            setShowReply(false);
          }}
        >
          <input value={reply} onChange={(e) => setReply(e.target.value)} className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Write a reply" />
          <button className="rounded-lg bg-ember-500 px-3 py-2 text-xs font-semibold text-white">Send</button>
        </form>
      )}
      {comment.replies?.map((child) => (
        <CommentNode key={child.id} comment={child} depth={depth + 1} onVote={onVote} onReply={onReply} />
      ))}
    </div>
  );
}

export default function CommentThread({ comments, onVote, onReply }) {
  return (
    <div className="mt-4">
      {comments.map((comment) => (
        <CommentNode key={comment.id} comment={comment} depth={0} onVote={onVote} onReply={onReply} />
      ))}
    </div>
  );
}
