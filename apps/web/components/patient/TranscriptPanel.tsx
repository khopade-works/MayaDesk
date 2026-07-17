"use client";

import { useEffect, useRef } from "react";
import { useTranscriptions } from "@livekit/components-react";

import { cn } from "@/lib/utils";

function speakerOf(identity: string): { label: string; isPatient: boolean } {
  const isPatient = identity.startsWith("patient");
  return { label: isPatient ? "You" : "Maya", isPatient };
}

export function TranscriptPanel() {
  const transcriptions = useTranscriptions();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcriptions.length]);

  return (
    <div className="flex h-72 flex-col gap-3 overflow-y-auto rounded-lg border border-border bg-muted/30 p-4">
      {transcriptions.length === 0 && (
        <p className="m-auto text-sm text-muted-foreground">
          Your conversation with Maya will appear here.
        </p>
      )}
      {transcriptions.map((t, i) => {
        const { label, isPatient } = speakerOf(t.participantInfo.identity);
        return (
          <div
            key={`${t.participantInfo.identity}-${i}`}
            className={cn("flex flex-col", isPatient ? "items-end" : "items-start")}
          >
            <span className="text-xs text-muted-foreground">{label}</span>
            <span
              className={cn(
                "mt-1 max-w-[85%] rounded-2xl px-3 py-2 text-sm",
                isPatient
                  ? "bg-primary text-primary-foreground"
                  : "bg-card text-card-foreground border border-border"
              )}
            >
              {t.text}
            </span>
          </div>
        );
      })}
      <div ref={endRef} />
    </div>
  );
}
