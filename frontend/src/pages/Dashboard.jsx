import { useParams } from "react-router-dom";
import { useState } from "react";

import Navbar from "../components/Navbar";
import SentimentDashboard from "../components/SentimentDashboard";
import { useAuth } from "../hooks/useAuth";
import { useSentiment } from "../hooks/useSentiment";
import { api } from "../lib/api";

export default function DashboardPage() {
  const { slug } = useParams();
  const { token } = useAuth();
  const { report, loading, error, refresh, canRefresh, secondsUntilRefresh, lastFetched } = useSentiment(slug, token);
  const [seeding, setSeeding] = useState("");
  const [seedResult, setSeedResult] = useState(null);
  const [seedError, setSeedError] = useState("");
  const [scanLoading, setScanLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [scanError, setScanError] = useState("");

  async function runScenario(scenario) {
    if (!token || !slug) return;
    setSeeding(scenario);
    setSeedError("");
    try {
      const result = await api.seedDemoScenario(token, slug, scenario);
      setSeedResult(result);
      await refresh();
    } catch (err) {
      setSeedError(err.message || "Failed to seed demo scenario");
    } finally {
      setSeeding("");
    }
  }

  async function runFundraiserScan() {
    if (!token || !slug) return;
    setScanLoading(true);
    setScanError("");
    try {
      const result = await api.scanFundraiser(token, slug);
      setScanResult(result);
    } catch (err) {
      setScanError(err.message || "Failed to scan fundraiser needs");
    } finally {
      setScanLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="font-display text-4xl text-slateink">Organizer Dashboard</h1>
        <p className="mt-1 text-sm text-slate-600">Track community health with sentiment insights, friction signals, and churn risk indicators.</p>

        <div className="mt-6">
          <SentimentDashboard
            report={report}
            loading={loading}
            error={error}
            onRefresh={refresh}
            canRefresh={canRefresh}
            secondsUntilRefresh={secondsUntilRefresh}
            lastFetched={lastFetched}
          />
        </div>

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5">
          <h2 className="font-display text-2xl text-slateink">Fundraiser Agent</h2>
          <p className="mt-1 text-sm text-slate-600">Run a manual scan to detect community funding needs and create a fundraiser post.</p>
          <button className="btn-secondary mt-3" onClick={runFundraiserScan} disabled={scanLoading}>
            {scanLoading ? "Scanning..." : "Run Fundraiser Scan"}
          </button>
          {scanError && <p className="mt-2 text-sm text-red-600">{scanError}</p>}
          {scanResult && <p className="mt-2 text-sm text-slate-700">{scanResult.message}</p>}
        </section>

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5">
          <h2 className="font-display text-2xl text-slateink">Demo Scenario Seeder</h2>
          <p className="mt-1 text-sm text-slate-600">Populate this community with realistic demo activity scenarios.</p>

          <div className="mt-4 flex flex-wrap gap-2">
            <button className="btn-secondary" onClick={() => runScenario("regular")} disabled={!!seeding}>
              {seeding === "regular" ? "Seeding..." : "1) Regular Sentiment"}
            </button>
            <button className="btn-secondary" onClick={() => runScenario("uptrend")} disabled={!!seeding}>
              {seeding === "uptrend" ? "Seeding..." : "2) Growth Uptrend"}
            </button>
            <button className="btn-secondary" onClick={() => runScenario("decline")} disabled={!!seeding}>
              {seeding === "decline" ? "Seeding..." : "3) Attention Decline"}
            </button>
          </div>

          {seedError && <p className="mt-3 text-sm text-red-600">{seedError}</p>}
          {seedResult && (
            <p className="mt-3 text-sm text-slate-700">
              Seeded {seedResult.scenario}: {seedResult.posts_created} posts, {seedResult.comments_created} comments, {seedResult.post_votes_submitted} post votes.
            </p>
          )}
        </section>
      </main>
    </div>
  );
}
