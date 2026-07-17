"use client";

import { BarVisualizer, useVoiceAssistant } from "@livekit/components-react";
import type { AgentState } from "@livekit/components-react";

import { Button } from "@/components/ui/Button";
import { ConnectionIndicator } from "@/components/patient/ConnectionIndicator";
import { TranscriptPanel } from "@/components/patient/TranscriptPanel";

const STATE_LABEL: Partial<Record<AgentState, string>> = {
  connecting: "Connecting to Maya…",
  initializing: "Maya is getting ready…",
  listening: "Maya is listening",
  thinking: "Maya is thinking…",
  speaking: "Maya is speaking",
};

export function CallPanel({ onEnd }: { onEnd: () => void }) {
  const { state, audioTrack } = useVoiceAssistant();

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-6">
      <div className="flex items-center justify-between">
        <ConnectionIndicator />
        <span className="text-sm text-muted-foreground">
          {STATE_LABEL[state] ?? "In call"}
        </span>
      </div>

      <div className="flex h-32 items-center justify-center rounded-lg border border-border bg-card">
        <BarVisualizer
          state={state}
          track={audioTrack}
          barCount={7}
          className="h-16 w-48"
        />
      </div>

      <TranscriptPanel />

      <Button variant="danger" size="lg" onClick={onEnd} className="w-full">
        End call
      </Button>
    </div>
  );
}
