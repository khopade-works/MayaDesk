"use client";

import { useEmergencies } from "@/hooks/useDashboard";
import { formatTimeAgo } from "@/lib/format";

export function EmergencyBanner() {
  const { data: emergencies = [] } = useEmergencies();

  if (emergencies.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
        No active emergencies.
      </div>
    );
  }

  return (
    <div
      role="alert"
      className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-danger"
    >
      <p className="text-sm font-semibold">
        {emergencies.length} emergency{emergencies.length > 1 ? " callbacks" : " callback"} awaiting response
      </p>
      <ul className="mt-2 space-y-1 text-sm">
        {emergencies.map((e) => (
          <li key={e.id} className="flex items-center justify-between gap-4">
            <span>
              <span className="font-medium">{e.patient_name ?? "Unidentified caller"}</span>
              {" — "}
              {e.reason}
            </span>
            <span className="shrink-0 text-xs opacity-80">{formatTimeAgo(e.created_at)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
