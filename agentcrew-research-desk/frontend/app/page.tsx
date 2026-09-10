"use client";

import { useEffect, useState } from "react";
import { supabase, ResearchSession } from "@/lib/supabase";
import SessionLog from "@/components/SessionLog";
import ReportPane from "@/components/ReportPane";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [topic, setTopic] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [active, setActive] = useState<ResearchSession | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/sessions`)
      .then((r) => r.json())
      .then((data: ResearchSession[]) => setSessions(data))
      .catch(() => {});

    const channel = supabase
      .channel("research_sessions_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "research_sessions" },
        (payload) => {
          const row = payload.new as ResearchSession;
          setSessions((prev) => {
            const exists = prev.some((s) => s.id === row.id);
            return exists
              ? prev.map((s) => (s.id === row.id ? row : s))
              : [row, ...prev];
          });
          setActive((prev) => (prev && prev.id === row.id ? row : prev));
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      const session: ResearchSession = await res.json();
      setSessions((prev) => [session, ...prev]);
      setActive(session);
      setTopic("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen grid grid-cols-1 md:grid-cols-[340px_1px_1fr]">
      <aside className="p-8 pr-6">
        <h1 className="text-2xl leading-tight">
          AgentCrew
          <br />
          Research Desk
        </h1>
        <p className="text-sm text-ink-soft mt-2 max-w-xs">
          Three local agents — researcher, writer, critic — investigate a
          topic and hand you a sourced report.
        </p>

        <form onSubmit={handleSubmit} className="mt-8">
          <label className="font-mono text-xs uppercase tracking-wide text-ink-soft">
            New inquiry
          </label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. the current state of solid-state batteries"
            rows={3}
            className="w-full mt-2 bg-white/70 border border-rule rounded-none p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-amber"
          />
          <button
            type="submit"
            disabled={submitting}
            className="mt-3 w-full bg-ink text-paper py-2.5 text-sm font-mono tracking-wide hover:bg-amber transition-colors disabled:opacity-50"
          >
            {submitting ? "Dispatching crew…" : "Dispatch crew"}
          </button>
        </form>

        <SessionLog sessions={sessions} activeId={active?.id ?? null} onSelect={setActive} />
      </aside>

      <div className="hidden md:block bg-rule" />

      <section className="p-10 md:p-14">
        <ReportPane session={active} />
      </section>
    </main>
  );
}
