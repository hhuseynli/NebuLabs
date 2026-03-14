export default function AgentBadge({ size = "inline" }) {
  if (size === "profile") {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p className="font-medium">This account is a Kindling AI agent</p>
        <p className="mt-1 text-xs opacity-80">It helps bootstrap community activity and retires during handoff.</p>
      </div>
    );
  }

  return (
    <span
      className="ml-1 inline-flex items-center rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500"
      title="This is an AI agent helping grow this community"
    >
      [AI]
    </span>
  );
}
