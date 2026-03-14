const phases = ["spark", "pull", "handoff", "complete"];

export default function RevivalArcBar({ phase = "spark", ratio = 0, size = "small" }) {
  const current = phases.indexOf(phase);
  const compact = size === "small";
  const paddingClass = compact ? "p-4" : "p-6";

  return (
    <div className={`rounded-2xl border border-ember-100 bg-white ${paddingClass} shadow-sm`}>
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs uppercase tracking-widest text-slate-500">Revival Arc</p>
        <p className="text-xs font-semibold text-ember-700">Human ratio: {Math.round(ratio * 100)}%</p>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-xs font-semibold uppercase tracking-wide">
        {phases.map((item, idx) => {
          const active = idx === current;
          const done = idx < current;
          return (
            <div
              key={item}
              className={`rounded-lg px-2 py-2 ${done ? "bg-ember-100 text-ember-700" : active ? "animate-pulse bg-ember-500 text-white" : "bg-slate-100 text-slate-400"}`}
            >
              {item}
            </div>
          );
        })}
      </div>
    </div>
  );
}
