"use client";

import { useEffect, useState } from "react";
import { supabase, ResearchSession } from "@/lib/supabase";
import SessionLog from "@/components/SessionLog";
import ReportPane from "@/components/ReportPane";

const API_URL = process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "");

export default function Home() {
  const [topic, setTopic] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [active, setActive] = useState<ResearchSession | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    const refresh = async () => {
      if (!API_URL) return;
      try {
        const response = await fetch(`${API_URL}/sessions`);
        if (!response.ok) throw new Error("Could not load saved inquiries.");
        const data = (await response.json()) as ResearchSession[];
        if (cancelled) return;
        setSessions(data);
        setActive((current) => current ? data.find((s) => s.id === current.id) ?? current : current);
        setError("");
      } catch {
        if (!cancelled) setError("Connect the API and Supabase to load or run research.");
      }
    };
    void refresh();
    const poll = window.setInterval(refresh, 4000);

    const channel = supabase
      ? supabase
          .channel("research_sessions_changes")
          .on("postgres_changes", { event: "*", schema: "public", table: "research_sessions" }, (payload) => {
            const row = payload.new as ResearchSession;
            if (!row?.id) return;
            setSessions((prev) => {
              const exists = prev.some((s) => s.id === row.id);
              return exists ? prev.map((s) => s.id === row.id ? row : s) : [row, ...prev];
            });
            setActive((prev) => prev?.id === row.id ? row : prev);
          })
          .subscribe()
      : null;

    return () => {
      cancelled = true;
      window.clearInterval(poll);
      if (channel) void supabase?.removeChannel(channel);
    };
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim()) return;
    if (!API_URL) {
      setError("Set NEXT_PUBLIC_API_URL in the frontend hosting settings before starting research.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Could not start the research job.");
      const session = data as ResearchSession;
      setSessions((prev) => [session, ...prev]);
      setActive(session);
      setTopic("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start the research job.");
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
            required
            minLength={4}
            maxLength={300}
            className="w-full mt-2 bg-white/70 border border-rule rounded-none p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-amber"
          />
          <button
            type="submit"
            disabled={submitting}
            className="mt-3 w-full bg-ink text-paper py-2.5 text-sm font-mono tracking-wide hover:bg-amber transition-colors disabled:opacity-50"
          >
            {submitting ? "Dispatching crew…" : "Dispatch crew"}
          </button>
          {error && <p role="status" className="mt-3 text-sm text-rust">{error}</p>}
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
