import { useMemo } from "react";
import { useParams } from "react-router-dom";

import Navbar from "../components/Navbar";
import RevivalArcBar from "../components/RevivalArcBar";
import { useAgents } from "../hooks/useAgents";
import { useAuth } from "../hooks/useAuth";
import { useRevival } from "../hooks/useRevival";

function ActivityChart({ status }) {
  const human = status?.human_posts || 0;
  const agent = status?.agent_posts || 0;
  const total = Math.max(human + agent, 1);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Activity</h2>
      <div className="mt-4 space-y-3">
        <div>
          <div className="mb-1 flex justify-between text-xs"><span>Human posts</span><span>{human}</span></div>
          <div className="h-2 rounded bg-slate-100"><div className="h-2 rounded bg-emerald-500" style={{ width: `${(human / total) * 100}%` }} /></div>
        </div>
        <div>
          <div className="mb-1 flex justify-between text-xs"><span>Agent posts</span><span>{agent}</span></div>
          <div className="h-2 rounded bg-slate-100"><div className="h-2 rounded bg-blue-500" style={{ width: `${(agent / total) * 100}%` }} /></div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { slug } = useParams();
  const { token } = useAuth();
  const { status, advancePhase } = useRevival(slug, token);
  const { agents, retireAgent } = useAgents(slug, token);

  const controls = useMemo(
    () => [
      ["pull", "Advance to Pull"],
      ["handoff", "Advance to Handoff"],
      ["complete", "Advance to Complete"],
    ],
    []
  );

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="font-display text-4xl text-slateink">Revival Dashboard</h1>
        <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
          <section className="space-y-4">
            <RevivalArcBar phase={status?.phase} ratio={status?.human_activity_ratio || 0} size="large" />
            <ActivityChart status={status} />
            <div className="rounded-2xl border border-slate-200 bg-white p-5">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Demo Controls</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {controls.map(([phase, label]) => (
                  <button key={phase} className="btn-secondary" onClick={() => advancePhase(phase)}>{label}</button>
                ))}
              </div>
            </div>
          </section>

          <aside className="space-y-3">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Agents</h2>
              <div className="mt-3 space-y-3">
                {agents.map((agent) => (
                  <div key={agent.id} className="rounded-xl border border-ember-100 p-3">
                    <p className="font-semibold text-slateink">{agent.name}</p>
                    <p className="mt-1 text-xs text-slate-600">{agent.backstory}</p>
                    <p className="mt-1 text-xs text-slate-500">Status: {agent.status}</p>
                    {agent.status !== "retired" && (
                      <button className="mt-2 rounded-lg bg-slateink px-3 py-1 text-xs font-semibold text-white" onClick={() => retireAgent(agent.id)}>
                        Retire Agent
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
