"use client";

import { useCallback, useState } from "react";

import { voiceApi } from "@/services/voice";
import type { VoiceToken } from "@/types";

export type CallPhase = "idle" | "connecting" | "active" | "error";

export interface VoiceCall {
  phase: CallPhase;
  session: VoiceToken | null;
  error: string | null;
  start: () => Promise<void>;
  end: () => void;
}

/** Owns the token-fetch + call lifecycle for the patient page. */
export function useVoiceCall(): VoiceCall {
  const [phase, setPhase] = useState<CallPhase>("idle");
  const [session, setSession] = useState<VoiceToken | null>(null);
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(async () => {
    setPhase("connecting");
    setError(null);
    try {
      const token = await voiceApi.token();
      setSession(token);
      setPhase("active");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start the call.");
      setPhase("error");
    }
  }, []);

  const end = useCallback(() => {
    setSession(null);
    setPhase("idle");
  }, []);

  return { phase, session, error, start, end };
}
