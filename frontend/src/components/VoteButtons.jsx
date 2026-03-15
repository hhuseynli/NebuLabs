export default function VoteButtons({ upvotes, downvotes, userVote, onVote, orientation = "vertical" }) {
  const score = (upvotes || 0) - (downvotes || 0);
  const vertical = orientation === "vertical";

  return (
    <div className={`flex ${vertical ? "flex-col" : "flex-row"} items-center gap-2`}>
      <button
        onClick={() => onVote(userVote === 1 ? 0 : 1)}
        className={`h-8 w-8 rounded-full text-sm ${userVote === 1 ? "bg-[#ffe6dc] text-[#d14e1f]" : "bg-[#eaf2f4] text-[#59727a]"}`}
      >
        ▲
      </button>
      <span className="min-w-8 text-center text-sm font-bold text-[#1f3a43]">{score}</span>
      <button
        onClick={() => onVote(userVote === -1 ? 0 : -1)}
        className={`h-8 w-8 rounded-full text-sm ${userVote === -1 ? "bg-[#e0edf9] text-[#2d68a2]" : "bg-[#eaf2f4] text-[#59727a]"}`}
      >
        ▼
      </button>
    </div>
  );
}
