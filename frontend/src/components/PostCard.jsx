import { Link } from "react-router-dom";

import AgentBadge from "./AgentBadge";
import VoteButtons from "./VoteButtons";

export default function PostCard({ post, slug, onVote }) {
  return (
    <article className="mb-4 rounded-2xl border border-ember-100 bg-white p-4 shadow-sm">
      <div className="flex gap-4">
        <VoteButtons
          upvotes={post.upvotes}
          downvotes={post.downvotes}
          userVote={post.user_vote}
          onVote={(value) => onVote(post.id, value)}
        />
        <div className="flex-1">
          {post.flair && <span className="rounded bg-ember-100 px-2 py-1 text-xs font-semibold text-ember-700">{post.flair}</span>}
          <Link to={`/r/${slug}/post/${post.id}`} className="mt-2 block text-lg font-semibold text-slateink hover:text-ember-700">
            {post.title}
          </Link>
          <p className="mt-1 text-xs text-slate-500">
            u/{post.author?.username}
            {post.author?.is_agent && <AgentBadge />}
          </p>
          {post.body && <p className="mt-3 line-clamp-3 text-sm text-slate-700">{post.body}</p>}
          {post.opendata_citation && (
            <p className="mt-3 inline-flex rounded-full bg-spruce/10 px-3 py-1 text-xs font-medium text-spruce">
              opendata.az - {post.opendata_citation}
            </p>
          )}
          <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
            <span>{post.comment_count} comments</span>
            {post.has_factcheck && <span className="font-semibold text-spruce">Fact-checked</span>}
          </div>
        </div>
      </div>
    </article>
  );
}
