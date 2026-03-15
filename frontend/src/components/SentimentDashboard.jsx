export default function SentimentDashboard({ report, loading, error, onRefresh }) {
  if (loading) {
    return <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500">Loading sentiment report...</div>;
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
        <p className="text-sm text-red-700">{error}</p>
        <button className="btn-secondary mt-3" onClick={onRefresh}>Retry</button>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-2xl text-slateink">Sentiment Dashboard</h2>
        <button className="btn-secondary" onClick={onRefresh}>Refresh Report</button>
      </div>

      <div className="mt-4 rounded-xl border border-ember-100 bg-ember-50 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-500">Health Score</p>
        <p className="mt-1 text-3xl font-bold text-slateink">{report.score}</p>
        <p className="mt-1 text-sm text-slate-600">{report.label}</p>
      </div>

      <p className="mt-4 text-sm text-slate-700">{report.summary}</p>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Trending Topics</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {(report.trending_topics || []).map((topic) => (
            <span key={topic} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">{topic}</span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Friction Signals</p>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
          {(report.friction_signals || []).map((signal) => (
            <li key={signal}>{signal}</li>
          ))}
        </ul>
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Churn Risk Members</p>
        <div className="mt-2 text-sm text-slate-700">{(report.churn_risk_members || []).join(", ") || "No clear churn-risk members detected."}</div>
      </div>
    </section>
  );
}
