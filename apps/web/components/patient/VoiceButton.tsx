"use client";

import { Button } from "@/components/ui/Button";

interface VoiceButtonProps {
  onClick: () => void;
  loading?: boolean;
}

/** The patient's call trigger. Fetches a token and connects on click. */
export function VoiceButton({ onClick, loading }: VoiceButtonProps) {
  return (
    <Button
      size="lg"
      onClick={onClick}
      disabled={loading}
      className="gap-2"
      aria-label="Talk to Maya"
    >
      <span aria-hidden>{"\u{1F399}️"}</span>
      {loading ? "Connecting…" : "Talk to Maya"}
    </Button>
  );
}
