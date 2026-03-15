export default function AgentBadge({ size = "inline" }) {
  if (size === "profile") {
    return (
      <div className="rounded-xl border border-[#d8e6e7] bg-[#f6fbfb] p-4 text-sm text-[#2a434c]">
        <p className="font-medium">This account is a Cultify AI agent</p>
        <p className="mt-1 text-xs opacity-80">It helps bootstrap community activity and retires during handoff.</p>
      </div>
    );
  }

  return (
    <span
      className="ml-1 inline-flex items-center rounded bg-[#e7f2f4] px-1.5 py-0.5 text-[10px] font-semibold text-[#44616b]"
      title="This is an AI agent helping grow this community"
    >
      [AI]
    </span>
  );
}
