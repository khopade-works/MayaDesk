"use client";

import { useConnectionState } from "@livekit/components-react";
import { ConnectionState } from "livekit-client";

import { cn } from "@/lib/utils";

const CONFIG: Record<ConnectionState, { label: string; dot: string; text: string }> = {
  [ConnectionState.Disconnected]: {
    label: "Disconnected",
    dot: "bg-muted-foreground",
    text: "text-muted-foreground",
  },
  [ConnectionState.Connecting]: {
    label: "Connecting…",
    dot: "bg-amber-500 animate-pulse",
    text: "text-amber-600 dark:text-amber-400",
  },
  [ConnectionState.Connected]: {
    label: "Connected",
    dot: "bg-emerald-500",
    text: "text-emerald-600 dark:text-emerald-400",
  },
  [ConnectionState.Reconnecting]: {
    label: "Reconnecting…",
    dot: "bg-amber-500 animate-pulse",
    text: "text-amber-600 dark:text-amber-400",
  },
  [ConnectionState.SignalReconnecting]: {
    label: "Reconnecting…",
    dot: "bg-amber-500 animate-pulse",
    text: "text-amber-600 dark:text-amber-400",
  },
};

export function ConnectionIndicator() {
  const state = useConnectionState();
  const cfg = CONFIG[state] ?? CONFIG[ConnectionState.Disconnected];

  return (
    <div className={cn("inline-flex items-center gap-2 text-sm font-medium", cfg.text)}>
      <span className={cn("h-2.5 w-2.5 rounded-full", cfg.dot)} />
      {cfg.label}
    </div>
  );
}
