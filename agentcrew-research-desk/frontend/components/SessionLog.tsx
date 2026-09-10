"use client";

import { ResearchSession } from "@/lib/supabase";

const statusColor: Record<ResearchSession["status"], string> = {
  running: "text-amber",
  completed: "text-moss",
  failed: "text-rust",
};

const statusLabel: Record<ResearchSession["status"], string> = {
  running: "in progress",
  completed: "done",
  failed: "failed",
};

export default function SessionLog({
  sessions,
  activeId,
  onSelect,
}: {
  sessions: ResearchSession[];
  activeId: string | null;
  onSelect: (s: ResearchSession) => void;
}) {
  if (sessions.length === 0) {
    return (
      <p className="text-sm text-ink-soft mt-6">
        No inquiries yet. Enter a topic to start the crew.
      </p>
    );
  }

  return (
    <ol className="mt-6 divide-y divide-rule border-t border-rule">
      {sessions.map((s, i) => (
        <li key={s.id}>
          <button
            onClick={() => onSelect(s)}
            className={`w-full text-left py-3 group ${
              activeId === s.id ? "bg-white/60" : ""
            }`}
          >
            <div className="flex items-baseline gap-3 px-1">
              <span className="font-mono text-xs text-ink-soft w-6 shrink-0">
                {String(sessions.length - i).padStart(2, "0")}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate group-hover:text-amber transition-colors">
                  {s.topic}
                </p>
                <p className={`font-mono text-xs mt-0.5 ${statusColor[s.status]}`}>
                  {statusLabel[s.status]}
                </p>
              </div>
            </div>
          </button>
        </li>
      ))}
    </ol>
  );
}
