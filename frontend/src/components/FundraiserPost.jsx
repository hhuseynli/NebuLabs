import { useMemo, useState } from "react";

import { useFundraiser } from "../hooks/useFundraiser";

export default function FundraiserPost({ post, token }) {
  const [open, setOpen] = useState(false);
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("Happy to help!");
  const [error, setError] = useState("");

  const { pledges, pledgeCount, totalPledged, goalAmount, userPledge, pledge, retract, loading } = useFundraiser(post.id, token);

  const progress = useMemo(() => {
    if (!goalAmount) return 0;
    return Math.min(100, Math.round((Number(totalPledged || 0) / Number(goalAmount || 1)) * 100));
  }, [goalAmount, totalPledged]);

  const deadlineText = useMemo(() => {
    const deadline = post.fundraiser_meta?.deadline;
    if (!deadline) return "";
    const ms = new Date(deadline).getTime() - Date.now();
    if (ms <= 0) return "Goal closed";
    const days = Math.ceil(ms / (1000 * 60 * 60 * 24));
    return `Goal closes in ${days} day${days === 1 ? "" : "s"}`;
  }, [post.fundraiser_meta]);

  async function submitPledge(e) {
    e.preventDefault();
    setError("");
    if (!message.trim()) return;
    try {
      const parsedAmount = amount.trim() ? Number(amount.trim()) : null;
      await pledge(Number.isFinite(parsedAmount) ? parsedAmount : null, message.trim());
      setOpen(false);
      setAmount("");
      setMessage("Happy to help!");
    } catch (err) {
      setError(err.message || "Could not submit pledge");
    }
  }

  return (
    <article className="mb-4 overflow-hidden rounded-2xl border border-[#b8ddd6] bg-white/90 shadow-sm">
      <div className="bg-[#d8efe9] px-4 py-2 text-xs font-semibold text-[#0f5e55]">🎯 Community Goal</div>
      <div className="p-4">
        <h3 className="text-xl font-semibold text-[#10242b]">{post.title}</h3>
        <p className="mt-2 text-sm leading-6 text-[#2a434c]">{post.body}</p>

        <div className="mt-4 rounded-xl border border-[#c9e5df] bg-[#f2faf8] p-3">
          <p className="text-xs uppercase tracking-wide text-[#56717a]">Goal</p>
          <p className="mt-1 text-lg font-semibold text-[#10242b]">AZN {goalAmount || post.fundraiser_meta?.goal_amount || 0}</p>
          <div className="mt-2 h-2 rounded-full bg-white">
            <div className="h-2 rounded-full bg-[#0f8a7b]" style={{ width: `${progress}%` }} />
          </div>
          <p className="mt-2 text-xs text-[#45606a]">{pledgeCount} members pledged · AZN {totalPledged} committed</p>
        </div>

        <div className="mt-3 flex items-center gap-3 text-sm">
          {userPledge ? (
            <>
              <span className="rounded-full bg-[#d8efe9] px-3 py-1 text-[#0f5e55]">✓ Pledged</span>
              <button className="text-[#c94f1f] underline" onClick={() => retract()} disabled={loading}>Retract</button>
            </>
          ) : (
            <button className="btn-primary" onClick={() => setOpen(true)} disabled={loading}>Pledge Support</button>
          )}
          {deadlineText && <span className="text-xs text-[#58717a]">{deadlineText}</span>}
        </div>

        <details className="mt-4 rounded-xl border border-[#d8e6e7] p-3">
          <summary className="cursor-pointer text-sm text-[#2a434c]">{pledgeCount} members pledged</summary>
          <div className="mt-3 space-y-2 text-sm">
            {pledges.map((p) => (
              <div key={p.id} className="rounded-lg bg-[#f6fbfb] p-2">
                <p className="font-medium text-[#10242b]">u/{p.username}</p>
                <p className="text-[#45606a]">{p.message}</p>
                {p.amount_suggested ? <p className="text-xs text-[#58717a]">AZN {p.amount_suggested}</p> : null}
              </div>
            ))}
          </div>
        </details>

        <p className="mt-3 text-xs text-[#58717a]">Posted by Cultify Fundraiser Agent</p>

        {open && (
          <div className="mt-4 rounded-xl border border-[#d8e6e7] bg-[#f6fbfb] p-3">
            <form className="space-y-2" onSubmit={submitPledge}>
              <input
                className="input"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Amount (AZN, optional)"
                inputMode="numeric"
              />
              <input
                className="input"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Happy to contribute!"
                maxLength={140}
              />
              {error && <p className="text-xs text-red-600">{error}</p>}
              <div className="flex gap-2">
                <button className="btn-primary" type="submit">Pledge Support</button>
                <button className="btn-secondary" type="button" onClick={() => setOpen(false)}>Cancel</button>
              </div>
            </form>
          </div>
        )}
      </div>
    </article>
  );
}
