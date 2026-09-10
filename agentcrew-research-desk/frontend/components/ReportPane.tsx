"use client";

import { ResearchSession } from "@/lib/supabase";

export default function ReportPane({ session }: { session: ResearchSession | null }) {
  if (!session) {
    return (
      <div className="h-full flex items-center justify-center text-ink-soft text-sm">
        Select an inquiry from the log, or start a new one.
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <p className="font-mono text-xs text-ink-soft uppercase tracking-wide">
        Inquiry
      </p>
      <h2 className="text-3xl mt-1 mb-6 leading-snug">{session.topic}</h2>

      {session.status === "running" && (
        <div className="flex items-center gap-3 text-amber font-mono text-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber opacity-60" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber" />
          </span>
          Researcher, Writer and Critic agents are working…
        </div>
      )}

      {session.status === "failed" && (
        <p className="text-rust font-mono text-sm">{session.result}</p>
      )}

      {session.status === "completed" && session.result && (
        <article className="prose-sm whitespace-pre-wrap leading-relaxed text-ink border-t border-rule pt-6">
          {session.result}
        </article>
      )}
    </div>
  );
}
