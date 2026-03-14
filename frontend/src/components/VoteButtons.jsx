export default function VoteButtons({ upvotes, downvotes, userVote, onVote, orientation = "vertical" }) {
  const score = (upvotes || 0) - (downvotes || 0);
  const vertical = orientation === "vertical";

  return (
    <div className={`flex ${vertical ? "flex-col" : "flex-row"} items-center gap-2`}>
      <button
        onClick={() => onVote(userVote === 1 ? 0 : 1)}
        className={`h-8 w-8 rounded-full text-sm ${userVote === 1 ? "bg-orange-100 text-orange-600" : "bg-slate-100 text-slate-600"}`}
      >
        ▲
      </button>
      <span className="min-w-8 text-center text-sm font-bold text-slate-700">{score}</span>
      <button
        onClick={() => onVote(userVote === -1 ? 0 : -1)}
        className={`h-8 w-8 rounded-full text-sm ${userVote === -1 ? "bg-blue-100 text-blue-600" : "bg-slate-100 text-slate-600"}`}
      >
        ▼
      </button>
    </div>
  );
}
