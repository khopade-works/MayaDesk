"use client";

import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";

import { CallPanel } from "@/components/patient/CallPanel";
import { VoiceButton } from "@/components/patient/VoiceButton";
import { useVoiceCall } from "@/hooks/useVoiceCall";

export default function PatientPage() {
  const { phase, session, error, start, end } = useVoiceCall();

  if (phase === "active" && session) {
    return (
      <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-12">
        <LiveKitRoom
          token={session.token}
          serverUrl={session.url}
          connect
          audio
          video={false}
          onDisconnected={end}
        >
          <RoomAudioRenderer />
          <CallPanel onEnd={end} />
        </LiveKitRoom>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center gap-10 px-6 py-16 text-center">
      <section className="flex flex-col items-center gap-4">
        <span className="rounded-full border border-border bg-muted px-3 py-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          AI front desk
        </span>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Meet Maya, your AI front desk
        </h1>
        <p className="max-w-xl text-muted-foreground">
          Maya answers calls, books appointments, and routes emergencies so your
          practice never misses a patient. Click below and start talking.
        </p>
      </section>

      <section className="flex flex-col items-center gap-3">
        <VoiceButton onClick={start} loading={phase === "connecting"} />
        {error && (
          <p role="alert" className="max-w-md text-sm text-danger">
            {error}
          </p>
        )}
        <p className="text-xs text-muted-foreground">
          Your browser will ask for microphone access.
        </p>
      </section>
    </main>
  );
}
