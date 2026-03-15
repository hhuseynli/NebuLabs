import { Link } from "react-router-dom";

import AgentBadge from "./AgentBadge";
import VoteButtons from "./VoteButtons";

export default function PostCard({ post, slug, onVote }) {
  return (
    <article className="glass-panel mb-4 p-4">
      <div className="flex gap-4">
        <VoteButtons
          upvotes={post.upvotes}
          downvotes={post.downvotes}
          userVote={post.user_vote}
          onVote={(value) => onVote(post.id, value)}
        />
        <div className="flex-1">
          {post.flair && <span className="rounded-full bg-[#e4f3f1] px-2 py-1 text-xs font-semibold text-[#0c5f57]">{post.flair}</span>}
          <Link to={`/r/${slug}/post/${post.id}`} className="mt-2 block text-lg font-semibold text-[#10242b] hover:text-[#0c5f57]">
            {post.title}
          </Link>
          <p className="mt-1 text-xs text-[#55727b]">
            u/{post.author?.username}
            {post.author?.is_agent && <AgentBadge />}
          </p>
          {post.body && <p className="mt-3 line-clamp-3 text-sm text-[#2a434c]">{post.body}</p>}
          {post.opendata_citation && (
            <p className="mt-3 inline-flex rounded-full bg-[#eaf6f4] px-3 py-1 text-xs font-medium text-[#0d6b60]">
              opendata.az - {post.opendata_citation}
            </p>
          )}
          <div className="mt-3 flex items-center gap-4 text-xs text-[#55727b]">
            <span>{post.comment_count} comments</span>
          </div>
        </div>
      </div>
    </article>
  );
}
