"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { useCallbacks } from "@/hooks/useDashboard";
import { formatTimeAgo } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { CallbackPriority } from "@/types";

const priorityBadge: Record<CallbackPriority, string> = {
  emergency: "bg-danger/15 text-danger",
  urgent: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  normal: "bg-muted text-muted-foreground",
};

export function CallbackQueue() {
  const { data: callbacks = [], isLoading } = useCallbacks();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Callback Queue</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {!isLoading && callbacks.length === 0 && (
          <p className="text-sm text-muted-foreground">No pending callbacks.</p>
        )}
        {callbacks.map((c) => (
          <div
            key={c.id}
            className="flex items-start justify-between gap-4 rounded-md border border-border p-3"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">
                {c.patient_name ?? "Unidentified caller"}
              </p>
              <p className="truncate text-sm text-muted-foreground">{c.reason}</p>
              {c.patient_phone && (
                <p className="text-xs text-muted-foreground">{c.patient_phone}</p>
              )}
            </div>
            <div className="flex shrink-0 flex-col items-end gap-1">
              <span
                className={cn(
                  "rounded-full px-2 py-0.5 text-xs font-medium capitalize",
                  priorityBadge[c.priority]
                )}
              >
                {c.priority}
              </span>
              <span className="text-xs text-muted-foreground">
                {formatTimeAgo(c.created_at)}
              </span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
