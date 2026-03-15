function formatCountdown(totalSeconds) {
  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;
  return `${mins}:${String(secs).padStart(2, "0")}`;
}

export default function SentimentDashboard({ report, loading, error, onRefresh, canRefresh = true, secondsUntilRefresh = 0, lastFetched = null }) {
  if (loading) {
    return <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500">Analysing community health...</div>;
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
        <button className="btn-secondary" onClick={onRefresh} disabled={!canRefresh}>
          {canRefresh ? "Refresh Report" : `Refresh in ${formatCountdown(secondsUntilRefresh)}`}
        </button>
      </div>

      <div className="mt-4 rounded-xl border border-ember-100 bg-ember-50 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-500">Health Score</p>
        <p className="mt-1 text-3xl font-bold text-slateink">{report.score}</p>
        <p className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
          report.score >= 70 ? "bg-emerald-100 text-emerald-700" : report.score >= 40 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
        }`}>{report.label}</p>
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
        {(report.friction_signals || []).length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">No friction signals detected</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {(report.friction_signals || []).map((signal) => (
              <li key={signal}>⚠ {signal}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Churn Risk Members</p>
        {(report.churn_risk_members || []).length === 0 ? (
          <div className="mt-2 text-sm text-slate-700">No churn risk detected</div>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {(report.churn_risk_members || []).map((username) => (
              <a key={username} href={`/u/${String(username).replace(/^u\//, "")}`} className="rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700">
                {username} At risk
              </a>
            ))}
          </div>
        )}
      </div>

      {lastFetched ? <p className="mt-4 text-xs text-slate-500">Last updated recently</p> : null}
    </section>
  );
}
